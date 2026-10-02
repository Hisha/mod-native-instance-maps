#!/usr/bin/env python3
"""Test suite for the native instance map tooling.

Run from the repository root::

    python3 tests/run_tests.py            # everything
    python3 tests/run_tests.py -k golden  # one pattern

The suite is dependency-free (``unittest`` only) so it runs anywhere the
generator runs. Stock 3.3.5a and WDM inputs are repository-owned. The one test
that compares a mod-content-manager fixture is skipped loudly when that declared
integration is absent.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import unittest
from unittest import mock
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import floornames  # noqa: E402
import paths  # noqa: E402
import semantic  # noqa: E402
from instances import (  # noqa: E402
    SAFE,
    UNSAFE,
    UNSAFE_REASONS,
    discover,
    tile_target_name,
)
from package import (  # noqa: E402
    FIXED_TIME,
    RELEASE_PACKAGE,
    STOCK_TOC_MEMBER,
    build_release,
    build_epf,
    build_selected,
    clean_outputs,
    combined_manifest_for,
    floor_label_locales,
    manifest_for,
    publish_slugs,
    published_candidates,
    select_published,
    serialise,
    stock_toc_sha256,
)
from transform import (  # noqa: E402
    FULL_REGION_BOTTOM,
    FULL_REGION_LEFT,
    FULL_REGION_RIGHT,
    FULL_REGION_TOP,
    INSTANCE,
    UI_REMAP,
    analyze,
    render_markdown,
)
from wdbc import TABLES, WdbcError, build_bytes, parse_bytes, parse_file  # noqa: E402

FIXTURE_MISSING = "mod-content-manager fixture not present"

require_fixture = unittest.skipUnless(
    paths.deadmines_golden_fixture().is_file(), FIXTURE_MISSING
)

DEADMINES = "TheDeadmines"


class _DiscoveryMixin:
    """Discovery is expensive; build it once and share it."""

    discovery = None

    @classmethod
    def setUpClass(cls) -> None:
        if cls.discovery is None:
            cls.discovery = discover(
                paths.wdm_dbc_dir(), paths.wdm_artwork_dir(), paths.stock_dbc_dir()
            )

    def candidate(self, internal_name: str):
        for item in self.discovery.candidates:
            if item.internal_name == internal_name:
                return item
        raise AssertionError(f"no candidate named {internal_name!r}")


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


class TestParser(unittest.TestCase):
    """The reader is the foundation: if it is lenient, every number after it
    is fiction."""

    def roundtrip(self, table: str, records, string_block: bytes = b"\x00"):
        spec = TABLES[table]
        return parse_bytes(build_bytes(spec, records, string_block), spec)

    def test_parses_every_table_layout(self):
        for name, spec in TABLES.items():
            with self.subTest(table=name):
                data = (paths.wdm_dbc_dir() / f"{name}.dbc").read_bytes()
                document = parse_bytes(data, spec)
                self.assertEqual(document.record_count, len(document.records))
                self.assertEqual(document.trailing_bytes, 0)
                self.assertEqual(
                    document.expected_size,
                    20 + document.record_count * document.record_size
                    + document.string_block_size,
                )

    def test_rejects_wrong_magic(self):
        spec = TABLES["DungeonMap"]
        data = bytearray(build_bytes(spec, [(1, 1, 1, 0, 0, 0, 0, 0)]))
        data[0:4] = b"XXXX"
        with self.assertRaisesRegex(WdbcError, "bad magic"):
            parse_bytes(bytes(data), spec)

    def test_rejects_field_count_mismatch(self):
        spec = TABLES["DungeonMap"]
        data = bytearray(build_bytes(spec, [(1, 1, 1, 0, 0, 0, 0, 0)]))
        data[8:12] = (spec.field_count + 1).to_bytes(4, "little")
        with self.assertRaisesRegex(WdbcError, "field_count"):
            parse_bytes(bytes(data), spec)

    def test_rejects_record_size_mismatch(self):
        spec = TABLES["DungeonMap"]
        data = bytearray(build_bytes(spec, [(1, 1, 1, 0, 0, 0, 0, 0)]))
        data[12:16] = (spec.record_size + 4).to_bytes(4, "little")
        with self.assertRaisesRegex(WdbcError, "record_size"):
            parse_bytes(bytes(data), spec)

    def test_rejects_truncated_body(self):
        spec = TABLES["DungeonMap"]
        data = build_bytes(spec, [(1, 1, 1, 0, 0, 0, 0, 0)])
        with self.assertRaisesRegex(WdbcError, "truncated body"):
            parse_bytes(data[:-4], spec)

    def test_rejects_trailing_bytes(self):
        spec = TABLES["DungeonMap"]
        data = build_bytes(spec, [(1, 1, 1, 0, 0, 0, 0, 0)])
        with self.assertRaisesRegex(WdbcError, "trailing"):
            parse_bytes(data + b"\x00\x00\x00\x00", spec)

    def test_rejects_zero_record_id(self):
        spec = TABLES["DungeonMap"]
        with self.assertRaisesRegex(WdbcError, "zero ID"):
            parse_bytes(build_bytes(spec, [(0, 1, 1, 0, 0, 0, 0, 0)]), spec)

    def test_rejects_duplicate_ids(self):
        spec = TABLES["DungeonMap"]
        row = (7, 36, 1, 0, 0, 0, 0, 0)
        data = build_bytes(spec, [row, row])
        with self.assertRaisesRegex(WdbcError, "duplicate record ID"):
            parse_bytes(data, spec)
        # The report is still reachable for tooling that wants to inspect rather
        # than refuse.
        lenient = parse_bytes(data, spec, require_unique_ids=False)
        self.assertEqual(list(lenient.duplicate_ids), [7])

    def test_rejects_string_offset_past_end_of_block(self):
        spec = TABLES["WorldMapArea"]
        record = (1, 36, 1581, 9999, 0, 0, 0, 0, -1, 0, 0)
        with self.assertRaisesRegex(WdbcError, "string"):
            parse_bytes(build_bytes(spec, [record], b"\x00"), spec)

    def test_rejects_unterminated_string(self):
        """A run of bytes with no NUL terminator is not a string."""
        spec = TABLES["WorldMapArea"]
        record = (1, 36, 1581, 1, 0, 0, 0, 0, -1, 0, 0)
        with self.assertRaises(WdbcError):
            parse_bytes(build_bytes(spec, [record], b"\x00TheDeadmines"), spec)

    def test_rejects_string_offset_one_past_the_block(self):
        spec = TABLES["WorldMapArea"]
        block = b"\x00A\x00"
        record = (1, 36, 1581, len(block), 0, 0, 0, 0, -1, 0, 0)
        with self.assertRaises(WdbcError):
            parse_bytes(build_bytes(spec, [record], block), spec)

    def test_string_offset_zero_is_the_empty_string(self):
        spec = TABLES["WorldMapArea"]
        record = (1, 36, 1581, 0, 0, 0, 0, 0, -1, 0, 0)
        document = parse_bytes(build_bytes(spec, [record], b"\x00"), spec)
        self.assertEqual(document.records[0].value("internal_name"), "")

    def test_string_roundtrip_preserves_offsets(self):
        spec = TABLES["WorldMapArea"]
        block = b"\x00TheDeadmines\x00\x00"
        record = (756, 36, 1581, 1, 0, 0, 0, 0, -1, 0, 0)
        document = parse_bytes(build_bytes(spec, [record], block), spec)
        self.assertEqual(document.records[0].value("internal_name"), "TheDeadmines")

    def test_float32_roundtrip_is_exact(self):
        spec = TABLES["DungeonMap"]
        for value in (-796.6220092773438, 1966.6666259765625, -10000.0, 0.0):
            with self.subTest(value=value):
                packed = int.from_bytes(
                    __import__("struct").pack("<f", value), "little"
                )
                document = self.roundtrip(
                    "DungeonMap", [(1, 36, 1, packed, packed, packed, packed, 39)]
                )
                self.assertEqual(document.records[0].value("field3"), value)

    def test_signed_fields_decode_negative(self):
        spec = TABLES["WorldMapArea"]
        record = (756, 36, 1581, 0, 0, 0, 0, 0, 0xFFFFFFFF, 0xFFFFFFFF, 0)
        document = parse_bytes(build_bytes(spec, [record], b"\x00"), spec)
        self.assertEqual(document.records[0].value("virtual_map_id"), -1)
        self.assertEqual(document.records[0].value("dungeonMap_id"), -1)

    def test_records_keep_declaration_order(self):
        spec = TABLES["DungeonMapChunk"]
        ids = [2521, 2524, 2528, 2527, 2518]
        document = self.roundtrip(
            "DungeonMapChunk", [(i, 36, 100 + n, 166, 0) for n, i in enumerate(ids)]
        )
        self.assertEqual([r.id for r in document.records], ids)
        self.assertEqual([r.index for r in document.records], list(range(len(ids))))

    def test_raw_bytes_are_preserved_verbatim(self):
        data = (paths.wdm_dbc_dir() / "DungeonMapChunk.dbc").read_bytes()
        document = parse_bytes(data, TABLES["DungeonMapChunk"])
        start = 20
        for record in document.records:
            self.assertEqual(
                record.raw, data[start + record.index * document.record_size :][: document.record_size]
            )


# ---------------------------------------------------------------------------
# Discovery and classification
# ---------------------------------------------------------------------------


class TestDiscovery(_DiscoveryMixin, unittest.TestCase):
    def test_every_reason_code_is_declared(self):
        """Reason codes are a closed set, so reports cannot grow a new code that
        nothing has classified."""
        for item in self.discovery.candidates:
            for code in item.reason_codes:
                with self.subTest(name=item.internal_name, code=code):
                    self.assertIn(code, UNSAFE_REASONS)

    def test_classification_follows_from_the_reason_codes(self):
        for item in self.discovery.candidates:
            with self.subTest(name=item.internal_name):
                if item.reason_codes:
                    self.assertEqual(item.classification, UNSAFE)
                else:
                    self.assertEqual(item.classification, SAFE)

    def test_every_candidate_is_classified(self):
        """No candidate is left undecided."""
        for item in self.discovery.candidates:
            with self.subTest(name=item.internal_name):
                self.assertIn(item.classification, (SAFE, UNSAFE))
                if item.classification != SAFE:
                    self.assertTrue(item.reason_codes, "non-SAFE needs a reason")
                    self.assertTrue(item.findings)

    def test_safe_candidates_have_no_reasons(self):
        for item in self.discovery.by_classification(SAFE):
            with self.subTest(name=item.internal_name):
                self.assertEqual(item.reason_codes, [])
                # Coherent in one of two ways: floors with the chunks that draw
                # them, or neither, in which case the WorldMapArea row and the
                # tiles are the whole map.  See TestFloorless.
                if item.floor_ids:
                    self.assertTrue(item.chunk_ids)
                else:
                    self.assertEqual(item.chunk_ids, [])
                self.assertTrue(item.blps)

    def test_no_transform_is_not_a_reason_code(self):
        """A missing WorldMapTransforms row is source data, not a defect.

        Stock 3.3.5a and WDM Stable both ship multi-floor instance maps with no
        transform row, and mod-content-manager treats ``worldMaps[].transform`` as
        optional, so the code must not exist in the closed reason set at all.
        """
        self.assertNotIn("no-transform", UNSAFE_REASONS)
        for item in self.discovery.candidates:
            with self.subTest(name=item.internal_name):
                self.assertNotIn("no-transform", item.reason_codes)

    def test_a_map_with_no_transform_can_be_safe(self):
        """The direct inversion of the rule this project previously encoded."""
        without = [
            item
            for item in self.discovery.by_classification(SAFE)
            if not item.transform_ids
        ]
        self.assertTrue(without, "expected SAFE candidates that carry no transform")
        for item in without:
            with self.subTest(name=item.internal_name):
                self.assertEqual(item.reason_codes, [])
                # A transform-less map is coherent in one of two ways: it owns
                # floors and the chunks that draw them, or it owns neither and
                # is drawn from its WorldMapArea row and artwork alone.
                if item.floor_ids:
                    self.assertTrue(item.chunk_ids)
                else:
                    self.assertEqual(item.chunk_ids, [])
                    self.assertEqual(item.area_dungeon_map_id, 0)
                    self.assertTrue(item.blps)

    def test_a_map_missing_anything_else_is_not_safe(self):
        """Removing no-transform must not have promoted a candidate that still
        carries an independent structural problem."""
        for item in self.discovery.candidates:
            for code in (
                "no-chunks",
                "floorless-chunk-reference",
                "floorless-transform-reference",
                "floorless-dungeon-map-id",
                "no-world-map-area",
                "no-artwork",
                "artwork-name-ambiguous",
                "duplicate-artwork-alias",
                "stock-mutation-required",
            ):
                if code in item.reason_codes:
                    with self.subTest(name=item.internal_name, code=code):
                        self.assertNotEqual(item.classification, SAFE)

    def test_map_id_is_unique_per_candidate(self):
        seen: dict = {}
        for item in self.discovery.candidates:
            if item.map_id is None:
                continue
            with self.subTest(name=item.internal_name):
                # Two artwork dirs may name one map (BlackFathomDeeps casing);
                # the map itself must still be represented once.
                self.assertIsNone(seen.get(item.map_id, None), "map claimed twice")
                seen[item.map_id] = item.internal_name

    # -- artwork spelling ---------------------------------------------------

    #: The two dungeons whose WDM artwork directory is spelled with different
    #: capitals than the ``WorldMapArea.internal_name`` that owns it, and the
    #: spelling WDM uses on disk.
    ARTWORK_ALIASES = {
        "BlackfathomDeeps": "BlackFathomDeeps",
        "MagtheridonsLair": "Magtheridonslair",
    }

    def test_only_the_two_known_artwork_spellings_differ(self):
        """The whole re-casing mechanism is driven by data, not by a hardcoded
        list of two maps.  Anything new that needs it shows up as a third entry
        here and fails, so the case cannot be widened by accident."""
        differing = {
            item.internal_name: item.source_dir
            for item in self.discovery.candidates
            if item.source_dir != item.internal_name
        }
        self.assertEqual(differing, self.ARTWORK_ALIASES)

    def test_a_differently_spelled_directory_is_bound_to_its_area(self):
        for internal_name, source_dir in self.ARTWORK_ALIASES.items():
            with self.subTest(name=internal_name):
                item = self.candidate(internal_name)
                self.assertEqual(item.source_dir, source_dir)
                self.assertEqual(item.artwork_aliases, [source_dir])
                self.assertTrue(item.blps, "no tiles resolved through the alias")
                self.assertEqual(item.classification, SAFE)

    def test_the_artwork_spelling_itself_is_not_a_candidate(self):
        """WDM declares no WorldMapArea row for the artwork spelling, so it names
        no map of its own and its tiles ship with the map that does."""
        for internal_name, source_dir in self.ARTWORK_ALIASES.items():
            with self.subTest(name=source_dir):
                item = self.candidate(source_dir)
                self.assertEqual(item.artwork_claimed_by, internal_name)
                self.assertEqual(item.reason_codes, ["duplicate-artwork-alias"])
                self.assertEqual(item.classification, UNSAFE)
                self.assertIsNone(item.map_id)
                # Exactly one of the two spellings is packageable, so the tiles
                # are not shipped twice under two names.
                self.assertEqual(self.candidate(internal_name).classification, SAFE)

    def test_tile_targets_are_rebuilt_from_the_internal_name(self):
        """The client derives the tile name from ``internal_name``; the package
        installs WDM's bytes at exactly that name."""
        for internal_name, source_dir in self.ARTWORK_ALIASES.items():
            with self.subTest(name=internal_name):
                item = self.candidate(internal_name)
                for source, target in zip(item.blps, item.tile_targets):
                    self.assertTrue(target.startswith(internal_name))
                    self.assertEqual(
                        target, internal_name + source[len(source_dir) :]
                    )
                # Nothing else in the name changes: the floor and tile indices are
                # WDM's, only the leading name is rebuilt.
                self.assertEqual(
                    sorted(target[len(internal_name) :] for target in item.tile_targets),
                    sorted(source[len(source_dir) :] for source in item.blps),
                )

    def test_tile_target_name_only_rewrites_a_case_variant_prefix(self):
        """Anything that is not a case variant of the area name is left alone, so
        a genuine naming defect still surfaces as a defect."""
        self.assertEqual(
            tile_target_name("Karazhan", "Karazhan", "Karazhan1_1.blp"),
            "Karazhan1_1.blp",
        )
        self.assertEqual(
            tile_target_name("BlackfathomDeeps", "BlackFathomDeeps", "BlackFathomDeeps1_1.blp"),
            "BlackfathomDeeps1_1.blp",
        )
        # A different directory name is not a case variant, so nothing is rewritten.
        self.assertEqual(
            tile_target_name("AhnQiraj", "RuinsofAhnQiraj", "RuinsofAhnQiraj1_1.blp"),
            "RuinsofAhnQiraj1_1.blp",
        )
        # Same directory, unrelated leaf: untouched.
        self.assertEqual(
            tile_target_name("BlackfathomDeeps", "BlackFathomDeeps", "readme.txt"),
            "readme.txt",
        )

    def test_alias_artwork_is_present_where_the_package_reads_it(self):
        """The bytes a package installs under the rebuilt name are files WDM
        actually ships, at the path WDM actually ships them from.  The payload
        identity itself is checked against the built EPF in ``TestEpf``."""
        root = paths.wdm_artwork_dir()
        for internal_name, source_dir in self.ARTWORK_ALIASES.items():
            with self.subTest(name=internal_name):
                item = self.candidate(internal_name)
                renamed = item.artwork_renames
                self.assertTrue(renamed)
                self.assertEqual(len(renamed), len(item.blps))
                for source, target in renamed.items():
                    self.assertEqual(
                        target, tile_target_name(internal_name, source_dir, source)
                    )
                    original = root / source_dir / source
                    self.assertTrue(original.is_file(), original)
                    self.assertGreater(original.stat().st_size, 0)

    #: A client dungeon tile is ``<internalName><floor>_<tile>.blp``.
    TILE = re.compile(r"^(?P<prefix>.+?)(?P<floor>\d+)_(?P<tile>\d+)\.blp$", re.IGNORECASE)

    def test_every_safe_candidate_has_a_complete_tile_grid(self):
        """A floor the client cannot draw is a silent failure, so the tile set must
        be a complete 1..N run per floor.

        Some WDM directories also carry flat ``<name><n>.blp`` files alongside the
        grid; those name no floor, so they are excluded here and are not the tiles
        the client asks for.
        """
        for item in self.discovery.by_classification(SAFE):
            with self.subTest(name=item.internal_name):
                grid: dict = {}
                for leaf in item.tile_targets:
                    match = self.TILE.match(leaf)
                    if match is None:
                        continue
                    self.assertEqual(match.group("prefix").casefold(), item.internal_name.casefold())
                    grid.setdefault(int(match.group("floor")), []).append(
                        int(match.group("tile"))
                    )
                self.assertEqual(len(grid), len(item.floor_ids), "floor count")
                for floor, tiles in grid.items():
                    self.assertEqual(
                        sorted(tiles), list(range(1, len(tiles) + 1)), f"floor {floor} gap"
                    )

    def test_wailing_caverns_is_unsafe(self):
        item = self.candidate("WailingCaverns")
        self.assertEqual(item.classification, UNSAFE)
        self.assertIn("stock-mutation-required", item.reason_codes)

    def test_every_wdm_added_row_is_shipped_or_accounted_for(self):
        """The coverage claim the reports make, checked rather than asserted."""
        for entry in self.discovery.coverage():
            with self.subTest(table=entry["table"]):
                self.assertEqual(
                    entry["shipped"] + len(entry["heldBack"]) + len(entry["unowned"]),
                    entry["added"],
                )

    def test_a_safe_candidate_only_claims_rows_wdm_added(self):
        for item in self.discovery.by_classification(SAFE):
            with self.subTest(name=item.internal_name):
                for table, ids in (
                    ("DungeonMap", item.floor_ids),
                    ("DungeonMapChunk", item.chunk_ids),
                    ("WorldMapArea", item.world_map_area_ids),
                    ("WorldMapTransforms", item.transform_ids),
                ):
                    self.assertEqual(
                        set(ids) & self.discovery.stock_ids[table], set(), table
                    )

    def test_no_two_safe_candidates_claim_the_same_row(self):
        for table in ("DungeonMap", "DungeonMapChunk", "WorldMapArea", "WorldMapTransforms"):
            owner: dict = {}
            for item in self.discovery.by_classification(SAFE):
                for identifier in self.discovery.claimed_ids(table) & set(
                    self._rows(item, table)
                ):
                    with self.subTest(table=table, name=item.internal_name, row=identifier):
                        self.assertNotIn(identifier, owner)
                        owner[identifier] = item.internal_name

    @staticmethod
    def _rows(item, table):
        return {
            "DungeonMap": item.floor_ids,
            "DungeonMapChunk": item.chunk_ids,
            "WorldMapArea": item.world_map_area_ids,
            "WorldMapTransforms": item.transform_ids,
        }[table]

    def test_transform_presence_is_preserved_not_derived(self):
        """WDM's transform table is authoritative and is never extended.

        A candidate's transform set is exactly the set of ``WorldMapTransforms``
        rows WDM declares for its map -- no candidate has a transform WDM does not
        supply, and no map WDM supplies a transform for is missing it.
        """
        transforms = self.discovery.tables["WorldMapTransforms"]
        by_map: dict = {}
        for record in transforms.records:
            by_map.setdefault(record.map_id(), []).append(record.id)
        for item in self.discovery.candidates:
            if item.map_id is None:
                continue
            with self.subTest(name=item.internal_name):
                self.assertEqual(item.transform_ids, by_map.get(item.map_id, []))
        # No candidate carries a transform WDM does not have, and every candidate
        # for a map WDM *does* transform carries it.  WDM transforms some maps
        # that are not candidates at all (the stock raid floors have a
        # WorldMapArea but no shipped artwork directory), so equality with the
        # full key set is not expected -- only containment.
        supplied = {item.map_id for item in self.discovery.candidates if item.transform_ids}
        self.assertTrue(supplied)
        self.assertTrue(supplied <= set(by_map))

    def test_stock_mutations_are_reported(self):
        found = {(m["table"], m["id"]): m["change"] for m in self.discovery.stock_mutations}
        self.assertEqual(found.get(("DungeonMap", 28)), "modified")
        self.assertEqual(found.get(("DungeonMapChunk", 1237)), "removed")
        self.assertEqual(found.get(("DungeonMapChunk", 1238)), "removed")
        self.assertEqual(found.get(("WorldMapArea", 609)), "modified")

    def test_no_safe_candidate_depends_on_a_mutated_stock_row(self):
        mutated = {
            (m["table"], m["id"]) for m in self.discovery.stock_mutations
        }
        for item in self.discovery.by_classification(SAFE):
            with self.subTest(name=item.internal_name):
                for area in item.world_map_area_ids:
                    self.assertNotIn(("WorldMapArea", area), mutated)
                for floor in item.floor_ids:
                    self.assertNotIn(("DungeonMap", floor), mutated)
                for chunk in item.chunk_ids:
                    self.assertNotIn(("DungeonMapChunk", chunk), mutated)
                for transform in item.transform_ids:
                    self.assertNotIn(("WorldMapTransforms", transform), mutated)

    def test_every_safe_row_is_additive(self):
        for item in self.discovery.by_classification(SAFE):
            with self.subTest(name=item.internal_name):
                self.assertTrue(all(item.world_map_area_additive))
                self.assertTrue(all(item.floor_additive))
                self.assertTrue(all(item.chunk_additive))
                # Vacuously true for a map WDM gives no transform to: an empty
                # list is not a non-additive row.
                self.assertTrue(all(item.transform_additive))


# ---------------------------------------------------------------------------
# Semantics
# ---------------------------------------------------------------------------


class TestSemantic(_DiscoveryMixin, unittest.TestCase):
    def declaration(self, name: str) -> dict:
        item = self.candidate(name)
        return semantic.world_map_declaration(
            self.discovery.tables,
            item.map_id,
            item.world_map_area_ids,
            item.floor_ids,
            item.chunk_ids,
            item.transform_ids[0] if item.transform_ids else None,
        )

    @require_fixture
    def test_deadmines_matches_golden_fixture(self):
        """Every field the reviewed fixture states must still match, exactly.

        ``floorNames`` is compared separately in :class:`TestFloorNames`, against
        WDM's own strings, because the reviewed fixture predates floor labels and
        cannot be the oracle for them.  Everything else must be byte-identical, so
        a future projection change still fails here.
        """
        golden = json.loads(paths.deadmines_golden_fixture().read_text())["worldMaps"][0]
        self.assertEqual(len(golden["areas"]), 1)
        self.assertNotIn("floorNames", golden["areas"][0], "the reviewed fixture grew floor labels")
        (declaration,) = [self.declaration(DEADMINES)]
        (area,) = declaration["areas"]
        self.assertIn("floorNames", area)
        self.assertEqual(
            {**declaration, "areas": [{k: v for k, v in area.items() if k != "floorNames"}]},
            golden,
        )

    # -- the two transform cases are both valid source shapes --------------

    def test_present_transform_is_projected_exactly(self):
        """When WDM has a row, every field is copied and nothing is added."""
        declaration = self.declaration(DEADMINES)
        record = self.discovery.tables["WorldMapTransforms"].get(11)
        self.assertIn("transform", declaration)
        self.assertEqual(declaration["transform"]["id"], 11)
        for source, key in semantic.TRANSFORM_FIELDS:
            with self.subTest(field=source):
                self.assertEqual(declaration["transform"][key], record.value(source))
        self.assertEqual(
            set(declaration["transform"]),
            {"id"} | {key for _, key in semantic.TRANSFORM_FIELDS},
            "no extra and no missing transform key",
        )

    def test_absent_transform_is_omitted_not_null(self):
        """When WDM has no row, the key is absent -- not null, not zeroed."""
        declaration = self.declaration("Karazhan")
        self.assertNotIn("transform", declaration)
        self.assertNotIn("null", json.dumps(declaration))
        self.assertNotIn("newDungeonMapId", json.dumps(declaration))
        # Present and spelled out: the key set is exactly mapId + areas.
        self.assertEqual(set(declaration), {"mapId", "areas"})

    def test_transform_key_absence_follows_the_source_table(self):
        """For every candidate, the key exists iff WDM supplies a row."""
        for item in self.discovery.candidates:
            if item.classification != SAFE:
                continue
            with self.subTest(name=item.internal_name):
                declaration = self.declaration(item.internal_name)
                self.assertEqual("transform" in declaration, bool(item.transform_ids))

    # -- dungeonMapId is a reference, not an owned row --------------------

    def test_dungeon_map_id_is_preserved_signed(self):
        """0, -1 and a cross-map reference all survive verbatim.

        The field is written through to the record, so the importer must not
        clamp a negative to zero, wrap it to 4294967295, or resolve it into a
        same-map floor.
        """
        seen = {}
        for item in self.discovery.candidates:
            if len(item.world_map_area_ids) != 1:
                continue
            record = self.discovery.tables["WorldMapArea"].get(
                item.world_map_area_ids[0]
            )
            with self.subTest(name=item.internal_name):
                self.assertEqual(
                    item.area_dungeon_map_id, int(record.value("dungeonMap_id"))
                )
                if item.classification == SAFE:
                    self.assertEqual(
                        self.declaration(item.internal_name)["areas"][0]["dungeonMapId"],
                        int(record.value("dungeonMap_id")),
                    )
            seen[item.internal_name] = int(record.value("dungeonMap_id"))
        values = set(seen.values())
        self.assertIn(0, values, "expected a WDM area with dungeonMapId 0")
        self.assertIn(-1, values, "expected a WDM area with the -1 sentinel")
        self.assertTrue(
            any(value > 0 for value in values),
            "expected a WDM area referencing a positive DungeonMap row",
        )

    def test_dungeon_map_id_zero_is_preserved(self):
        self.assertEqual(self.candidate("Karazhan").area_dungeon_map_id, 0)
        self.assertEqual(
            self.declaration("Karazhan")["areas"][0]["dungeonMapId"], 0
        )

    def test_dungeon_map_id_sentinel_is_preserved(self):
        item = self.candidate("BlackTemple")
        self.assertEqual(item.area_dungeon_map_id, -1)
        self.assertEqual(self.declaration("BlackTemple")["areas"][0]["dungeonMapId"], -1)

    def test_external_dungeon_map_id_does_not_create_ownership(self):
        """Ahn'Qiraj names DungeonMap 2, which belongs to another map entirely.

        That is legitimate source data, so it is not a reason code at all and not an
        ownership claim: the package's floors stay exactly the map's own floors.
        """
        item = self.candidate("AhnQiraj")
        self.assertEqual(item.area_dungeon_map_id, 2)
        self.assertEqual(item.classification, SAFE)
        self.assertNotIn("area-floor-reference-unresolvable", UNSAFE_REASONS)
        declaration = self.declaration("AhnQiraj")
        self.assertEqual(declaration["areas"][0]["dungeonMapId"], 2)
        # The referenced row is not a floor of map 531 and is never declared as
        # one, so the package cannot own another map's geometry.
        self.assertNotIn(2, [floor["id"] for floor in declaration["areas"][0]["floors"]])
        self.assertNotIn(2, [c["dungeonMapId"] for c in declaration["areas"][0]["chunks"]])

    def test_dungeon_map_id_stays_a_signed_integer(self):
        """The field is read as a typed int32, never as a float or a string."""
        for item in self.discovery.candidates:
            if item.area_dungeon_map_id is None:
                continue
            with self.subTest(name=item.internal_name):
                value = item.area_dungeon_map_id
                self.assertIsInstance(value, int)
                self.assertNotIsInstance(value, bool)
                self.assertGreaterEqual(value, -(2 ** 31))
                self.assertLess(value, 2 ** 31)

    def test_chunk_order_follows_wdm_not_id_order(self):
        declaration = self.declaration(DEADMINES)
        ids = [chunk["id"] for chunk in declaration["areas"][0]["chunks"]]
        self.assertNotEqual(ids, sorted(ids), "the fixture is deliberately not ID-sorted")
        physical = [
            record.id
            for record in self.discovery.tables["DungeonMapChunk"].records
            if record.map_id() == 36
        ]
        self.assertEqual(ids, physical)

    def test_chunk_order_interleaves_floors(self):
        """Grouping by floor would be wrong; WDM interleaves them."""
        declaration = self.declaration(DEADMINES)
        floors = [c["dungeonMapId"] for c in declaration["areas"][0]["chunks"]]
        runs = sum(1 for a, b in zip(floors, floors[1:]) if a != b)
        self.assertGreater(runs, 1, "expected interleaved floor references")

    def test_floors_keep_declaration_order(self):
        declaration = self.declaration(DEADMINES)
        self.assertEqual(
            [f["id"] for f in declaration["areas"][0]["floors"]], [166, 167]
        )

    def test_fixed_ids_are_preserved_exactly(self):
        declaration = self.declaration(DEADMINES)
        self.assertEqual(declaration["mapId"], 36)
        self.assertEqual(declaration["transform"]["id"], 11)
        self.assertEqual(declaration["transform"]["newDungeonMapId"], 167)
        self.assertEqual(declaration["areas"][0]["id"], 756)
        self.assertEqual(declaration["areas"][0]["areaId"], 1581)
        self.assertEqual(declaration["areas"][0]["internalName"], DEADMINES)

    def test_declared_values_match_the_source_rows(self):
        declaration = self.declaration(DEADMINES)
        tables = self.discovery.tables
        area = tables["WorldMapArea"].get(756)
        self.assertEqual(declaration["areas"][0]["y1"], area.value("y1"))
        self.assertEqual(declaration["areas"][0]["x2"], area.value("x2"))
        transform = tables["WorldMapTransforms"].get(11)
        self.assertEqual(declaration["transform"]["regionBottom"], transform.value("RegionBottom"))
        chunk = tables["DungeonMapChunk"].get(2521)
        self.assertEqual(
            declaration["areas"][0]["chunks"][0]["field4"], chunk.value("field4")
        )

    def test_digest_is_stable_and_content_sensitive(self):
        first = semantic.semantic_digest(self.declaration(DEADMINES))
        self.assertEqual(first, semantic.semantic_digest(self.declaration(DEADMINES)))
        mutated = self.declaration(DEADMINES)
        mutated["areas"][0]["chunks"][0]["field4"] = 1.0
        self.assertNotEqual(first, semantic.semantic_digest(mutated))

    def test_deadmines_chunk_order_matches_vendored_wdm_dbc(self):
        """Cross-check the projection against vendored WDM Stable bytes."""
        golden = parse_file(
            paths.wdm_dbc_dir() / "DungeonMapChunk.dbc",
            "DungeonMapChunk",
        )
        physical = [r.id for r in golden.records if r.map_id() == 36]
        declaration = self.declaration(DEADMINES)
        self.assertEqual(
            [c["id"] for c in declaration["areas"][0]["chunks"]], physical
        )


class TestFloorless(_DiscoveryMixin, unittest.TestCase):
    """A map that owns no ``DungeonMap`` row is a native client shape.

    Stock build 12340 already ships 48 such ``WorldMapArea`` rows -- WorldMapArea
    531 / MapID 615 ``TheObsidianSanctum``, 602 / 658 ``PitofSaron`` and
    609 / 724 ``TheRubySanctum`` among them -- and WDM Stable ships 55.  The
    client draws such a map from its ``WorldMapArea`` row and its artwork alone,
    so the package declares ``"floors": []`` and Content Manager composes no
    ``DungeonMap``, ``DungeonMapChunk`` or ``WorldMapTransforms`` row for it.

    Every assertion here compares against stock or WDM bytes.  Nothing asserts
    that a floorless map *can* exist: the DBC evidence below is what establishes
    it, and the invariants are what keep the accepted set from widening.
    """

    #: The candidates this project found with no DungeonMap floor, and what
    #: became of each.  A floorless candidate is not SAFE by being floorless; it
    #: is SAFE only when WDM also *adds* the WorldMapArea row, so a package has
    #: an identity to own.
    FLOORLESS = {
        "ZulFarrak": SAFE,
        "ZulGurub": SAFE,
        "ZulAman": SAFE,
        "RuinsofAhnQiraj": SAFE,
        "CoTTheBlackMorass": SAFE,
        "CoTHillsbradFoothills": SAFE,
        "CoTMountHyjal": SAFE,
        "ArathiBasin": UNSAFE,
        "WarsongGulch": UNSAFE,
        "NetherstormArena": UNSAFE,
        "Expansion01": UNSAFE,
    }

    def floorless(self) -> list:
        return [
            item
            for item in self.discovery.candidates
            if item.map_id is not None and not item.floor_ids
        ]

    def declaration(self, item) -> dict:
        return semantic.world_map_declaration(
            self.discovery.tables,
            item.map_id,
            item.world_map_area_ids,
            item.floor_ids,
            item.chunk_ids,
            item.transform_ids[0] if item.transform_ids else None,
        )

    def test_the_candidate_set_is_exactly_the_one_this_change_was_made_for(self):
        """Guard the table above against silently going stale."""
        self.assertEqual(
            sorted(item.internal_name for item in self.floorless()),
            sorted(self.FLOORLESS),
        )

    def test_stock_already_ships_floorless_instance_maps(self):
        """The evidence that makes the shape native rather than invented.

        Three stock instance maps own no DungeonMap row at all, are drawn from a
        single WorldMapArea row, and carry ``dungeonMapId`` 0 -- so the client
        has always had a way to render a map with no floor.  Read straight from
        the verified stock baseline so an upstream change surfaces here.
        """
        stock = parse_file(paths.stock_dbc_dir() / "DungeonMap.dbc", "DungeonMap")
        floors_per_map: dict = {}
        for record in stock.records:
            floors_per_map.setdefault(record.map_id(), []).append(record.id)
        areas = parse_file(
            paths.stock_dbc_dir() / "WorldMapArea.dbc", "WorldMapArea"
        )
        proven = {
            "TheObsidianSanctum": (615, 531),
            "PitofSaron": (658, 602),
            "TheRubySanctum": (724, 609),
        }
        for name, (map_id, area_id) in proven.items():
            with self.subTest(internal_name=name):
                self.assertNotIn(map_id, floors_per_map, f"map {map_id} grew a floor")
                row = areas.get(area_id)
                self.assertEqual(row.value("internal_name"), name)
                self.assertEqual(row.map_id(), map_id)
                self.assertEqual(int(row.value("dungeonMap_id")), 0)
                # A non-zero rectangle is what places the map's tiles; the stock
                # floorless rows are rect-placed rather than left at the origin.
                self.assertNotEqual(
                    [row.value(k) for k in ("y1", "y2", "x1", "x2")],
                    [0.0, 0.0, 0.0, 0.0],
                )

    def test_wdm_adds_the_area_and_the_artwork_for_a_floorless_map(self):
        """Zul'Farrak, field for field, against the WDM bytes."""
        item = self.candidate("ZulFarrak")
        wdm_areas = self.discovery.tables["WorldMapArea"]
        stock_areas = parse_file(
            paths.stock_dbc_dir() / "WorldMapArea.dbc", "WorldMapArea"
        )
        self.assertEqual(item.world_map_area_ids, [686])
        self.assertEqual(item.map_id, 209)
        row = wdm_areas.get(686)
        self.assertEqual(row.value("internal_name"), "ZulFarrak")
        self.assertEqual(row.map_id(), 209)
        self.assertEqual(int(row.value("area_id")), 1176)
        self.assertEqual(int(row.value("virtual_map_id")), -1)
        self.assertEqual(int(row.value("dungeonMap_id")), 0)
        # parentMapID names another WorldMapArea (Tanaris), not a MapID.
        self.assertEqual(int(row.value("parentMapID")), 161)
        self.assertEqual(wdm_areas.get(161).value("internal_name"), "Tanaris")
        # Stock describes no area of this map, so the package owns a new
        # identity rather than restating one the client already has.
        self.assertNotIn(209, {r.map_id() for r in stock_areas.records})
        # No floor and no transform for the map in WDM or in stock.  A chunk is
        # reachable only through a floor's DungeonMapID, and there is no floor,
        # so a floorless map owns no chunk by construction -- `chunk_ids` is
        # derived from that and asserted in the tests below.
        for table in ("DungeonMap", "WorldMapTransforms"):
            with self.subTest(table=table):
                self.assertEqual(
                    [r.id for r in self.discovery.tables[table].records if r.map_id() == 209],
                    [],
                    f"WDM {table} has a row for map 209",
                )
                self.assertEqual(
                    [r.id for r in self.stock_table(table).records if r.map_id() == 209],
                    [],
                    f"stock {table} has a row for map 209",
                )

    def stock_table(self, table: str):
        return parse_file(paths.stock_dbc_dir() / f"{table}.dbc", table)

    def test_the_projection_states_the_floorless_shape_explicitly(self):
        """`floors` and `chunks` stay present and empty, never omitted.

        Omitting a key is still an error in Content Manager, so the projection
        has to write the empty arrays rather than leave them out.  A floor
        label is omitted for the opposite reason: WDM ships locale strings for
        many zone maps, but with no floor there is no dropdown row to rename.
        """
        for name, verdict in self.FLOORLESS.items():
            with self.subTest(internal_name=name):
                item = self.candidate(name)
                self.assertEqual(item.classification, verdict)
                declaration = self.declaration(item)
                (area,) = declaration["areas"]
                self.assertIn("floors", area)
                self.assertIn("chunks", area)
                self.assertEqual(area["floors"], [])
                self.assertEqual(area["chunks"], [])
                self.assertNotIn("floorNames", area)
                self.assertEqual(area["dungeonMapId"], 0)
                if verdict is SAFE:
                    # A map with no transform contributes no transform row, so
                    # the key is absent rather than null or empty.
                    self.assertNotIn("transform", declaration)

    def test_a_floorless_candidate_is_rejected_only_for_independent_reasons(self):
        """The four still-UNSAFE candidates fail on evidence unrelated to floors.

        Each keeps a decisive structural reason, so nothing rests on the
        floorless rule and no rejection depends on it.
        """
        expected = {
            "ArathiBasin": {"stock-world-map-area"},
            "WarsongGulch": {"stock-world-map-area"},
            "NetherstormArena": {"stock-world-map-area"},
            "Expansion01": {"stock-world-map-area", "floorless-transform-reference"},
        }
        for name, codes in expected.items():
            with self.subTest(internal_name=name):
                item = self.candidate(name)
                self.assertEqual(item.classification, UNSAFE)
                self.assertEqual(set(item.reason_codes), codes)

    def test_no_floorless_candidate_invents_a_row_to_look_floored(self):
        """A published floorless package owns exactly one row in one table.

        Only the SAFE candidates are asserted here.  The UNSAFE ones are
        rejected precisely because they are *not* empty in this sense -- a
        floorless map that still ships a transform is the contradiction the
        `floorless-transform-reference` code exists to catch.
        """
        safe = [n for n, v in self.FLOORLESS.items() if v is SAFE]
        self.assertTrue(safe)
        for name in safe:
            with self.subTest(internal_name=name):
                item = self.candidate(name)
                self.assertEqual(item.floor_ids, [])
                self.assertEqual(item.chunk_ids, [])
                self.assertEqual(item.transform_ids, [])
                # Artwork is the only other thing such a map needs, and it is
                # present: without it the client would have nothing to draw.
                self.assertTrue(item.blps, "a floorless map still needs its tiles")

    def test_a_floorless_map_that_ships_a_transform_is_refused(self):
        """The counterfactual, checked against Expansion01's real WDM rows.

        WDM declares two WorldMapTransforms rows for the Outland continent, which
        owns no DungeonMap row, so both name a floor the map does not have.  That
        is refused rather than composed, and the map is rejected for a second,
        independent reason as well.
        """
        item = self.candidate("Expansion01")
        self.assertEqual(item.floor_ids, [])
        self.assertEqual(len(item.transform_ids), 2)
        self.assertEqual(item.classification, UNSAFE)
        self.assertIn("floorless-transform-reference", item.reason_codes)


# ---------------------------------------------------------------------------
# Packages
# ---------------------------------------------------------------------------


class TestPackages(_DiscoveryMixin, unittest.TestCase):
    #: A client dungeon tile is ``<internalName><floor>_<tile>.blp``.
    TILE = re.compile(r"^(?P<prefix>.+?)(?P<floor>\d+)_(?P<tile>\d+)\.blp$", re.IGNORECASE)
    def manifests(self) -> dict:
        out = {}
        for item in published_candidates(self.discovery):
            path = paths.CONTENT_DIR / item.slug / "manifest.json"
            self.assertTrue(path.is_file(), f"missing {path}")
            out[item.internal_name] = json.loads(path.read_text())
        return out

    def test_committed_manifests_match_generation(self):
        for item in published_candidates(self.discovery):
            with self.subTest(name=item.internal_name):
                path = paths.CONTENT_DIR / item.slug / "manifest.json"
                self.assertEqual(
                    path.read_bytes(), serialise(manifest_for(item, self.discovery))
                )

    def test_only_published_safe_candidates_are_manifested(self):
        """Publication is a separate decision from classification.

        Correcting the classifier promoted many more maps to SAFE; none of them may
        acquire a manifest or an EPF without an explicit entry in
        ``content/publish.json``.
        """
        published = {item.internal_name for item in published_candidates(self.discovery)}
        self.assertTrue(published)
        for item in self.discovery.candidates:
            path = paths.CONTENT_DIR / item.slug / "manifest.json"
            if item.internal_name in published:
                self.assertTrue(path.is_file(), f"missing {path}")
            else:
                with self.subTest(name=item.internal_name):
                    self.assertFalse(
                        path.is_file(),
                        "a candidate absent from content/publish.json must not have "
                        "a committed manifest",
                    )

    def test_publish_list_only_names_safe_candidates(self):
        for item in published_candidates(self.discovery):
            with self.subTest(name=item.internal_name):
                self.assertEqual(item.classification, SAFE)

    def test_publish_list_slug_agrees_with_titles(self):
        for internal_name, slug in publish_slugs().items():
            with self.subTest(name=internal_name):
                self.assertEqual(self.candidate(internal_name).slug, slug)

    def test_manifest_uses_schema_3_and_required_keys(self):
        for name, manifest in self.manifests().items():
            with self.subTest(name=name):
                self.assertEqual(manifest["schema"], 3)
                for key in ("package", "name", "version", "content", "worldMaps"):
                    self.assertIn(key, manifest)
                self.assertEqual(
                    manifest["package"],
                    paths.package_key(self.candidate(name).slug),
                )

    def test_one_world_map_entry_per_package(self):
        for name, manifest in self.manifests().items():
            with self.subTest(name=name):
                self.assertEqual(len(manifest["worldMaps"]), 1)

    def test_artwork_targets_live_under_the_declared_area_directory(self):
        for name, manifest in self.manifests().items():
            internal = manifest["worldMaps"][0]["areas"][0]["internalName"]
            prefix = f"Interface/WorldMap/{internal}/"
            for entry in manifest["content"]:
                with self.subTest(name=name, target=entry["target"]):
                    self.assertTrue(entry["target"].startswith(prefix))

    def test_targets_reject_traversal(self):
        for name, manifest in self.manifests().items():
            for entry in manifest["content"]:
                with self.subTest(name=name, target=entry["target"]):
                    target = entry["target"]
                    self.assertNotIn("..", target)
                    self.assertNotIn("\\", target)
                    self.assertFalse(target.startswith("/"))
                    self.assertNotIn("//", target)

    def test_no_content_entry_escapes_the_package_prefix(self):
        for name, manifest in self.manifests().items():
            for entry in manifest["content"]:
                with self.subTest(name=name, source=entry["source"]):
                    self.assertTrue(entry["source"].startswith("artwork/"))
                    self.assertNotIn("..", entry["source"])

    def test_targets_are_unique(self):
        for name, manifest in self.manifests().items():
            with self.subTest(name=name):
                targets = [e["target"] for e in manifest["content"]]
                self.assertEqual(len(targets), len(set(targets)))

    def test_declared_artwork_exists_in_the_wdm_tree(self):
        for name, manifest in self.manifests().items():
            item = self.candidate(name)
            for entry in manifest["content"]:
                leaf = Path(entry["source"]).name
                with self.subTest(name=name, leaf=leaf):
                    # The source path is where WDM keeps the file, which is not
                    # always spelled the way the area's internal_name is.
                    source = paths.wdm_artwork_dir() / item.source_dir / leaf
                    self.assertTrue(source.is_file(), f"missing {source}")
                    self.assertGreater(source.stat().st_size, 0)

    def test_artwork_targets_are_the_names_the_client_derives(self):
        """Every target is ``Interface/WorldMap/<internalName>/<leaf>``.

        The directory always comes from the area row.  The leaf is WDM's own,
        except where the artwork directory is spelled with different capitals than
        the ``internal_name`` it serves: there the leaf is rebuilt in the client's
        capitals, which is the only spelling the client can ask for.
        """
        for name, manifest in self.manifests().items():
            item = self.candidate(name)
            prefix = f"Interface/WorldMap/{item.internal_name}/"
            aliased = item.source_dir != item.internal_name
            for entry, target in zip(manifest["content"], item.tile_targets):
                source_leaf = Path(entry["source"]).name
                with self.subTest(name=name, leaf=target):
                    self.assertEqual(entry["target"], prefix + target)
                    self.assertTrue(entry["target"].startswith(prefix))
                    if aliased:
                        self.assertTrue(target.startswith(item.internal_name))
                    else:
                        # Untouched: WDM's spelling is the client's here.
                        self.assertEqual(target, source_leaf)

    def test_no_manifest_ships_a_dbc(self):
        """Composition is mod-content-manager's job; shipping a DBC would be a
        competing composer by the back door."""
        for name, manifest in self.manifests().items():
            for entry in manifest["content"]:
                with self.subTest(name=name, target=entry["target"]):
                    self.assertFalse(entry["target"].lower().endswith(".dbc"))

    def test_manifest_omits_dbc_rows_and_server_keys(self):
        for name, manifest in self.manifests().items():
            with self.subTest(name=name):
                for key in ("dbcRows", "serverRows", "spells", "creatureSpawns"):
                    self.assertNotIn(key, manifest)

    def test_manifest_agrees_with_the_source_about_a_transform(self):
        """The description and the declaration must not disagree.

        A map WDM gives no transform must not advertise one, and a map WDM does
        give one must name it, so the human-readable text cannot drift away from
        the machine-readable entry.
        """
        for name, manifest in self.manifests().items():
            item = self.candidate(name)
            declaration = manifest["worldMaps"][0]
            with self.subTest(name=name):
                if item.transform_ids:
                    self.assertEqual(
                        declaration["transform"]["id"], item.transform_ids[0]
                    )
                    # A map WDM transforms keeps the wording it has always
                    # shipped with, so regenerating an existing package leaves
                    # its committed manifest byte-identical.
                    self.assertIn(
                        "the instance WorldMapTransforms row",
                        manifest["description"],
                    )
                    # NewDungeonMapID is WDM's own choice, projected verbatim, and
                    # it names a floor this package declares.
                    area = declaration["areas"][0]
                    declared = {floor["id"] for floor in area["floors"]}
                    self.assertIn(
                        declaration["transform"]["newDungeonMapId"], declared
                    )
                else:
                    self.assertNotIn("transform", declaration)
                    self.assertIn("no WorldMapTransforms row", manifest["description"])

    def test_existing_package_manifests_are_unchanged(self):
        """The four packages that shipped before the expansion must not have moved.

        The remaining 39 manifests are new, but a change to the description builder
        or to the semantic projection would rewrite these four silently, so their
        exact bytes are pinned here.
        """
        import json as _json

        expected = {
            "DeeprunTram": "deeprun-tram",
            "Karazhan": "karazhan",
            "TheDeadmines": "the-deadmines",
            "TheTempleOfAtalHakkar": "temple-of-atal-hakkar",
        }
        #: These three carry a WDM instance transform; Karazhan has none, which is
        #: the multi-floor-no-transform case the transform report exists for.
        with_transform = {
            "DeeprunTram",
            "TheDeadmines",
            "TheTempleOfAtalHakkar",
        }
        published = {
            name: slug
            for name, slug in (
                (item.internal_name, item.slug) for item in published_candidates(self.discovery)
            )
            if name in expected
        }
        self.assertEqual(published, expected)
        for name, slug in expected.items():
            with self.subTest(name=name):
                manifest = _json.loads(
                    (paths.CONTENT_DIR / slug / "manifest.json").read_text()
                )
                self.assertEqual(manifest["package"], paths.package_key(slug))
                if name in with_transform:
                    self.assertIn("transform", manifest["worldMaps"][0])
                    self.assertIn(
                        "the instance WorldMapTransforms row", manifest["description"]
                    )
                else:
                    self.assertNotIn("transform", manifest["worldMaps"][0])
                    self.assertIn(
                        "no WorldMapTransforms row", manifest["description"]
                    )
                # Regenerating must reproduce the committed bytes exactly.
                self.assertEqual(
                    (paths.CONTENT_DIR / slug / "manifest.json").read_bytes(),
                    serialise(manifest_for(self.candidate(name), self.discovery)),
                )

    def test_wdm_is_inconsistent_about_casing_inside_one_directory(self):
        """Recorded, not repaired.

        WDM's ``TheTempleOfAtalHakkar/`` spells floor 1 as the area's
        ``internal_name``, floor 2 with a lower-case ``f`` in ``of``, and floor 3
        with a lower-case ``f`` and ``h``.  Re-casing is scoped to the directory
        name, so this map's manifest keeps WDM's leaf names -- which is what ships
        today and resolves on a case-insensitive client.  Renaming them would
        rewrite a released package to fix something that is not broken, so the
        inconsistency is pinned here instead of being silently rewritten.
        """
        item = self.candidate("TheTempleOfAtalHakkar")
        self.assertEqual(item.source_dir, item.internal_name)
        self.assertEqual(item.artwork_renames, {})
        by_floor: dict = {}
        for leaf in item.blps:
            match = self.TILE.match(leaf)
            self.assertIsNotNone(match, leaf)
            by_floor.setdefault(match.group("floor"), []).append(match.group("prefix"))
        self.assertEqual(sorted(by_floor), ["1", "2", "3"])
        self.assertEqual(
            {prefix for prefixes in by_floor.values() for prefix in prefixes},
            {
                "TheTempleOfAtalHakkar",
                "TheTempleofAtalHakkar",
                "TheTempleofAtalhakkar",
            },
        )

    def test_package_keys_are_unique(self):
        keys = [m["package"] for m in self.manifests().values()]
        self.assertEqual(len(keys), len(set(keys)))

    def test_every_safe_candidate_is_published(self):
        """The backlog is exhausted: nothing the classifier cleared is left out of
        the release, and nothing undecided is in it."""
        safe = {item.internal_name for item in self.discovery.by_classification(SAFE)}
        unsafe = {item.internal_name for item in self.discovery.by_classification(UNSAFE)}
        self.assertEqual(set(self.manifests()), safe)
        self.assertEqual(set(publish_slugs()), safe)
        self.assertEqual(unsafe & safe, set())
        # An UNSAFE map names no package directory, so none can drift back in.
        for item in self.discovery.by_classification(UNSAFE):
            with self.subTest(name=item.internal_name):
                self.assertFalse((paths.CONTENT_DIR / item.slug).exists())

    def test_published_tiles_never_collide(self):
        """Two maps must never install the same file, which the combined release
        could not detect on its own after they were merged."""
        owner: dict = {}
        for name, manifest in self.manifests().items():
            for entry in manifest["content"]:
                with self.subTest(name=name, target=entry["target"]):
                    self.assertNotIn(entry["target"], owner, owner.get(entry["target"]))
                    owner[entry["target"]] = name
        self.assertEqual(len(owner), sum(len(m["content"]) for m in self.manifests().values()))

    def test_published_rows_never_collide(self):
        owner: dict = {}
        for name, manifest in self.manifests().items():
            declaration = manifest["worldMaps"][0]
            area = declaration["areas"][0]
            claimed = (
                [("WorldMapArea", a["id"]) for a in declaration["areas"]]
                + [("DungeonMap", f["id"]) for a in declaration["areas"] for f in a["floors"]]
                + [("DungeonMapChunk", c["id"]) for a in declaration["areas"] for c in a["chunks"]]
                + ([("WorldMapTransforms", declaration["transform"]["id"])]
                   if "transform" in declaration else [])
            )
            for key in claimed:
                with self.subTest(name=name, row=key):
                    self.assertNotIn(key, owner, owner.get(key))
                    owner[key] = name


class TestEpf(_DiscoveryMixin, unittest.TestCase):
    """The EPF is a build product; these tests pin the properties that make it
    reviewable: fixed member order, stored entries, no clock, no DBC."""

    def setUp(self):
        import shutil
        import tempfile

        self.scratch = Path(tempfile.mkdtemp(prefix="nim-epf-"))
        self._shutil = shutil

    def tearDown(self):
        self._shutil.rmtree(self.scratch, ignore_errors=True)

    def build(self, internal_name: str, output_name: str = "out.epf"):
        """Stage the candidate's artwork into scratch, then build an EPF."""
        item = self.candidate(internal_name)
        manifest_path = paths.CONTENT_DIR / item.slug / "manifest.json"
        self.assertTrue(manifest_path.is_file(), f"missing {manifest_path}")

        manifest = json.loads(manifest_path.read_text())
        # Stage the artwork the way the build reads it: WDM's own layout, under the
        # directory name WDM actually uses.
        root = self.scratch / "Interface" / "WorldMap"
        (root / item.source_dir).mkdir(parents=True, exist_ok=True)
        for entry in manifest["content"]:
            self._shutil.copyfile(
                paths.wdm_artwork_dir() / item.source_dir / Path(entry["source"]).name,
                root / item.source_dir / Path(entry["source"]).name,
            )
        output = self.scratch / output_name
        return item, build_epf(item, manifest_path, output, artwork_root=root)

    def test_epf_is_a_zip_with_manifest_first(self):
        import zipfile

        saw_toc = False
        saw_no_toc = False
        for item in published_candidates(self.discovery):
            with self.subTest(name=item.internal_name):
                _, output = self.build(item.internal_name)
                with zipfile.ZipFile(output) as archive:
                    names = archive.namelist()
                self.assertEqual(names[0], "manifest.json")
                # The stock table of contents rides along only when the manifest
                # declares clientFrameXml, which a map declares only when it has
                # floor labels.  A floorless map has no dropdown row to rename, so
                # it carries no FrameXML change and no TOC.
                manifest = json.loads(
                    (paths.CONTENT_DIR / item.slug / "manifest.json").read_text()
                )
                declares_toc = "clientFrameXml" in manifest
                self.assertEqual(declares_toc, bool(item.floor_ids))
                saw_toc = saw_toc or declares_toc
                saw_no_toc = saw_no_toc or not declares_toc
                expected = 2 + len(item.blps) if declares_toc else 1 + len(item.blps)
                self.assertEqual(len(names), expected)
                if declares_toc:
                    self.assertEqual(names[1], STOCK_TOC_MEMBER)
        # The suite must exercise both shapes, or a change that quietly dropped
        # the TOC from every package would still pass.
        self.assertTrue(saw_toc and saw_no_toc)

    def test_epf_entries_are_stored_with_a_fixed_timestamp(self):
        import zipfile

        for item in published_candidates(self.discovery):
            with self.subTest(name=item.internal_name):
                _, output = self.build(item.internal_name)
                with zipfile.ZipFile(output) as archive:
                    for info in archive.infolist():
                        self.assertEqual(info.compress_type, zipfile.ZIP_STORED)
                        self.assertEqual(info.date_time, FIXED_TIME)

    def test_epf_is_byte_reproducible(self):
        import hashlib

        for item in published_candidates(self.discovery):
            with self.subTest(name=item.internal_name):
                _, first = self.build(item.internal_name, "a.epf")
                _, second = self.build(item.internal_name, "b.epf")
                self.assertEqual(
                    hashlib.sha256(first.read_bytes()).hexdigest(),
                    hashlib.sha256(second.read_bytes()).hexdigest(),
                )

    def test_epf_member_order_follows_manifest_content_order(self):
        import zipfile

        for item in published_candidates(self.discovery):
            with self.subTest(name=item.internal_name):
                manifest = json.loads(
                    (paths.CONTENT_DIR / item.slug / "manifest.json").read_text()
                )
                expected = ["manifest.json"] + [
                    e["source"] for e in manifest["content"]
                ]
                # The stock TOC sits between the manifest and the artwork, in the
                # order build_epf writes it, and never in artwork order.  It is
                # written only when the manifest declares clientFrameXml, so a
                # map with no floor labels has nothing between the two.
                if "clientFrameXml" in manifest:
                    expected.insert(1, STOCK_TOC_MEMBER)
                _, output = self.build(item.internal_name)
                with zipfile.ZipFile(output) as archive:
                    self.assertEqual(archive.namelist(), expected)

    def test_epf_payloads_match_the_wdm_artwork(self):
        """The only thing a package changes about an artwork file is where it is
        installed -- every byte in the EPF is the byte WDM ships."""
        import zipfile

        for item in published_candidates(self.discovery):
            with self.subTest(name=item.internal_name):
                _, output = self.build(item.internal_name)
                # Member name is the target leaf; the file it came from is WDM's.
                renamed = {target: source for source, target in item.artwork_renames.items()}
                with zipfile.ZipFile(output) as archive:
                    for name in archive.namelist():
                        if name in ("manifest.json", STOCK_TOC_MEMBER):
                            continue
                        leaf = Path(name).name
                        source_leaf = renamed.get(leaf, leaf)
                        expected = (
                            paths.wdm_artwork_dir() / item.source_dir / source_leaf
                        ).read_bytes()
                        self.assertEqual(archive.read(name), expected)

    def test_epf_carries_no_manifest_for_a_non_safe_candidate(self):
        item = self.candidate("WailingCaverns")
        with self.assertRaises(SystemExit):
            manifest_for(item, self.discovery)

    def test_epf_contains_no_dbc(self):
        import zipfile

        for item in published_candidates(self.discovery):
            with self.subTest(name=item.internal_name):
                _, output = self.build(item.internal_name)
                with zipfile.ZipFile(output) as archive:
                    for name in archive.namelist():
                        self.assertFalse(name.lower().endswith(".dbc"))


class TestBuildWorkflow(_DiscoveryMixin, unittest.TestCase):
    """Human selectors stay on the publication allowlist and remain reproducible."""

    def setUp(self):
        import shutil
        import tempfile

        self.scratch = Path(tempfile.mkdtemp(prefix="nim-workflow-"))
        self._shutil = shutil

    def tearDown(self):
        self._shutil.rmtree(self.scratch, ignore_errors=True)

    def test_single_map_builds_only_the_selected_approved_epf(self):
        selected = select_published(self.discovery, "karazhan")
        outputs = build_selected(self.discovery, selected, self.scratch)
        self.assertEqual(
            [path.name for path in outputs],
            ["mod-native-instance-maps.karazhan.epf"],
        )
        self.assertEqual(sorted(path.name for path in self.scratch.glob("*.epf")),
                         ["mod-native-instance-maps.karazhan.epf"])

    def test_all_builds_all_and_only_the_publication_allowlist(self):
        approved = published_candidates(self.discovery)
        outputs = build_selected(self.discovery, approved, self.scratch)
        expected = sorted(f"{paths.package_key(item.slug)}.epf" for item in approved)
        self.assertEqual(sorted(path.name for path in outputs), expected)
        self.assertEqual(sorted(path.name for path in self.scratch.glob("*.epf")),
                         expected)
        self.assertEqual({item.slug for item in approved}, set(publish_slugs().values()))

    def test_unknown_maps_are_not_selectable(self):
        with self.assertRaisesRegex(SystemExit, "unknown or unapproved"):
            select_published(self.discovery, "not-a-map")

    def test_unsafe_maps_are_not_selectable(self):
        """A map the classifier rejected must not be buildable by name, however
        correct its name looks."""
        published = set(publish_slugs().values())
        unsafe = [
            item for item in self.discovery.by_classification(UNSAFE)
            if item.slug and item.slug not in published
        ]
        self.assertTrue(unsafe, "expected rejected maps to exercise")
        for item in unsafe:
            with self.subTest(name=item.internal_name):
                with self.assertRaisesRegex(SystemExit, "unknown or unapproved"):
                    select_published(self.discovery, item.slug)

    def test_single_and_all_karazhan_are_byte_identical(self):
        one = self.scratch / "one"
        all_dir = self.scratch / "all"
        single = build_selected(
            self.discovery, select_published(self.discovery, "karazhan"), one
        )[0]
        build_selected(self.discovery, published_candidates(self.discovery), all_dir)
        from_all = all_dir / single.name
        self.assertEqual(single.read_bytes(), from_all.read_bytes())

    def test_combined_release_is_direct_and_deterministic(self):
        import zipfile

        first = build_release(self.discovery, self.scratch / "first.epf")
        second = build_release(self.discovery, self.scratch / "second.epf")
        self.assertEqual(first.read_bytes(), second.read_bytes())
        approved = published_candidates(self.discovery)
        expected_maps = {item.map_id for item in approved}
        with zipfile.ZipFile(first) as archive:
            names = archive.namelist()
            manifest = json.loads(archive.read("manifest.json"))
        self.assertEqual(manifest["package"], RELEASE_PACKAGE)
        self.assertEqual(
            manifest["replaces"],
            [
                "mod-deadmines-dungeon-map",
                "mod-native-instance-maps.karazhan",
            ],
        )
        self.assertEqual({item["mapId"] for item in manifest["worldMaps"]}, expected_maps)
        self.assertEqual(len(manifest["worldMaps"]), len(approved))
        self.assertFalse(any(name.lower().endswith(".epf") for name in names))
        self.assertEqual(names[0:2], ["manifest.json", STOCK_TOC_MEMBER])
        self.assertEqual(names[2:], [item["source"] for item in manifest["content"]])

    def test_individual_packages_cannot_replace_canonical_owner(self):
        for candidate in published_candidates(self.discovery):
            manifest = manifest_for(candidate, self.discovery)
            self.assertNotIn("replaces", manifest)

    def test_combined_manifest_refuses_resource_conflicts(self):
        approved = published_candidates(self.discovery)
        # Repeating one approved component creates both source and target conflicts;
        # the ordinary archive writer must reject it rather than hide ownership.
        manifest = combined_manifest_for([approved[0], approved[0]], self.discovery)
        with self.assertRaisesRegex(SystemExit, "duplicate package source"):
            from package import _write_epf
            payloads = [(item["source"], b"x") for item in manifest["content"]]
            _write_epf(
                manifest, serialise(manifest), payloads,
                self.scratch / "conflict.epf", "test combined release",
            )

    def test_clean_removes_only_generated_epfs(self):
        generated = self.scratch / "generated.epf"
        unrelated = self.scratch / "keep.txt"
        generated.write_bytes(b"generated")
        unrelated.write_bytes(b"keep")
        toc_before = paths.STOCK_FRAMEXML_TOC.read_bytes()
        self.assertEqual(clean_outputs(self.scratch), [generated])
        self.assertFalse(generated.exists())
        self.assertEqual(unrelated.read_bytes(), b"keep")
        self.assertEqual(paths.STOCK_FRAMEXML_TOC.read_bytes(), toc_before)


class TestTransformForensics(_DiscoveryMixin, unittest.TestCase):
    """Can a missing ``WorldMapTransforms`` row be derived?

    These tests pin the forensic *result*, including the negative one.  A future
    upstream change that made multi-floor selection derivable should fail
    ``test_floor_selection_is_not_derivable`` on purpose, prompting the rule and
    the reports to be revisited.

    The result now settles what this project does **not** do -- it never authors a
    transform -- rather than which maps it can publish.  A transform is optional
    source data, so a map WDM ships without one is complete without it.
    """

    analysis = None

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.analysis = analyze(paths.stock_dbc_dir(), paths.wdm_dbc_dir())

    def by_id(self, identifier: int):
        for item in self.analysis.transforms:
            if item.id == identifier:
                return item
        raise AssertionError(f"no transform with ID {identifier}")

    # -- decoding ---------------------------------------------------------

    def test_every_wdm_transform_decodes(self):
        self.assertEqual(len(self.analysis.transforms), 13)
        for item in self.analysis.transforms:
            with self.subTest(id=item.id):
                self.assertGreater(item.id, 0)
                self.assertGreater(item.map_id, 0)
                self.assertIn(item.family, (INSTANCE, UI_REMAP))

    def test_deadmines_transform_decodes_to_the_known_row(self):
        item = self.by_id(11)
        self.assertEqual(item.map_id, 36)
        self.assertEqual(item.region_bottom, -20000.0)
        self.assertEqual(item.region_right, -20000.0)
        self.assertEqual(item.region_top, 20000.0)
        self.assertEqual(item.region_left, 20000.0)
        self.assertEqual(item.new_map_id, 36)
        self.assertEqual(item.region_offset_x, 0.0)
        self.assertEqual(item.region_offset_y, 0.0)
        self.assertEqual(item.new_dungeon_map_id, 167)

    def test_wdm_supplied_transforms_are_marked_as_wdm_supplied(self):
        added = [t.id for t in self.analysis.transforms if not t.in_stock]
        self.assertEqual(sorted(added), [11, 12, 13, 14])

    def test_stock_transforms_are_marked_as_stock(self):
        stock = [t.id for t in self.analysis.transforms if t.in_stock]
        self.assertEqual(sorted(stock), [2, 3, 4, 5, 6, 7, 8, 9, 10])

    # -- family separation ------------------------------------------------

    def test_families_partition_every_row(self):
        total = len(self.analysis.instance) + len(self.analysis.ui_remap)
        self.assertEqual(total, len(self.analysis.transforms))
        self.assertEqual(len(self.analysis.instance), 8)
        self.assertEqual(len(self.analysis.ui_remap), 5)

    def test_every_wdm_added_transform_is_an_instance_entrance(self):
        for item in self.analysis.transforms:
            if not item.in_stock:
                with self.subTest(id=item.id):
                    self.assertEqual(item.family, INSTANCE)

    def test_structural_fields_are_universal_within_the_instance_family(self):
        for name in (
            "region covers the whole map (+/-20000)",
            "NewMapID equals MapID",
            "region offsets are zero",
            "NewDungeonMapID names a floor of the same map",
        ):
            with self.subTest(rule=name):
                self.assertTrue(self.analysis.holds(name), f"{name} is not universal")

    def test_new_map_id_is_not_universal_across_the_whole_table(self):
        """The rule holds for the instance family only; quoting it generally
        would be wrong, because the map-530 rows remap to 0 and 1."""
        remapped = [t for t in self.analysis.transforms if t.new_map_id != t.map_id]
        self.assertEqual(sorted(t.id for t in remapped), [2, 3])
        for item in remapped:
            with self.subTest(id=item.id):
                self.assertEqual(item.family, UI_REMAP)

    # -- the contested field ---------------------------------------------

    def test_floor_selection_is_not_derivable(self):
        """The headline negative result, pinned deliberately."""
        for name in (
            "NewDungeonMapID is the FIRST floor",
            "NewDungeonMapID is the LAST floor",
            "NewDungeonMapID is the LOWEST floor ID",
            "NewDungeonMapID is the HIGHEST floor ID",
        ):
            with self.subTest(rule=name):
                self.assertFalse(
                    self.analysis.holds(name), f"{name} unexpectedly became universal"
                )

    def test_multi_floor_selection_splits_evenly(self):
        def split(suffix: str) -> tuple:
            _, holds_for, total = self.analysis.verdict(suffix)
            return holds_for, total

        self.assertEqual(split("NewDungeonMapID is the FIRST floor (multi-floor maps only)"), (3, 6))
        self.assertEqual(split("NewDungeonMapID is the SECOND floor (multi-floor maps only)"), (3, 6))
        self.assertEqual(
            split("NewDungeonMapID is a floor other than 1st/2nd (multi-floor maps only)"), (0, 6)
        )

    def test_deadmines_and_deeprun_tram_contradict_each_other(self):
        """Two structurally equivalent two-floor maps, opposite answers."""
        deadmines = next(c for c in self.analysis.choices if c.map_id == 36)
        deeprun = next(c for c in self.analysis.choices if c.map_id == 369)
        self.assertEqual(deadmines.total, 2)
        self.assertEqual(deeprun.total, 2)
        self.assertEqual(deadmines.chosen, 167)
        self.assertEqual(deeprun.chosen, 741)
        self.assertEqual(deadmines.index, 2)
        self.assertEqual(deeprun.index, 1)

    def test_every_choice_names_a_real_floor_of_its_map(self):
        for choice in self.analysis.choices:
            with self.subTest(map=choice.map_id):
                self.assertIsNotNone(choice.index)
                self.assertIn(choice.chosen, choice.floors)

    # -- the narrow rule --------------------------------------------------

    def test_multi_floor_maps_without_a_transform_are_still_not_derivable(self):
        """The negative result, restated against the current candidate set.

        These maps now ship *without* a transform rather than being blocked by
        one, so the question this pins is narrower: no map with more than one
        floor has a derivable ``NewDungeonMapID``.  Nothing here may be used to
        justify authoring a row.
        """
        multi = [
            c
            for c in self.discovery.candidates
            if c.map_id is not None and len(c.floor_ids) > 1 and not c.transform_ids
        ]
        self.assertTrue(multi, "expected multi-floor maps with no WDM transform")
        for item in multi:
            with self.subTest(name=item.internal_name):
                # A choice exists in the source and it is not derivable: at
                # least one of first/last/lowest/highest would have to be
                # wrong, so no rule can pick it.
                floors = item.floor_ids
                self.assertGreater(len(floors), 1)
                self.assertNotIn(item.map_id, {c.map_id for c in self.analysis.choices})

    def test_karazhan_is_multi_floor_and_has_no_transform(self):
        karazhan = self.candidate("Karazhan")
        self.assertEqual(karazhan.map_id, 532)
        self.assertEqual(len(karazhan.floor_ids), 17)
        self.assertEqual(len(karazhan.chunk_ids), 86)
        self.assertEqual(karazhan.transform_ids, [])
        self.assertEqual(karazhan.reason_codes, [])
        self.assertEqual(karazhan.classification, SAFE)
        # Its floor choice is exactly the case the analysis refutes.
        self.assertNotIn(532, {c.map_id for c in self.analysis.choices})

    def test_publication_is_exactly_the_safe_set(self):
        """Publication is the classifier's output, with nothing added or held back."""
        published = {item.internal_name for item in published_candidates(self.discovery)}
        safe = {item.internal_name for item in self.discovery.by_classification(SAFE)}
        self.assertEqual(published, safe)
        self.assertIn("Karazhan", published)

    # -- region constants -------------------------------------------------

    def test_region_constants_match_the_observed_rows(self):
        for item in self.analysis.instance:
            with self.subTest(id=item.id):
                self.assertEqual(item.region_bottom, FULL_REGION_BOTTOM)
                self.assertEqual(item.region_right, FULL_REGION_RIGHT)
                self.assertEqual(item.region_top, FULL_REGION_TOP)
                self.assertEqual(item.region_left, FULL_REGION_LEFT)

    def test_region_constants_never_appear_in_the_ui_remap_family(self):
        for item in self.analysis.ui_remap:
            with self.subTest(id=item.id):
                self.assertFalse(item.full_region)

    # -- report determinism ----------------------------------------------

    def test_report_is_deterministic(self):
        self.assertEqual(
            render_markdown(self.analysis, self.discovery.candidates),
            render_markdown(self.analysis, self.discovery.candidates),
        )

    def test_report_on_disk_is_current(self):
        target = paths.REPORTS_DIR / "transform-analysis.md"
        if not target.is_file():
            self.skipTest("transform analysis report not generated")
        self.assertEqual(
            target.read_text(encoding="utf-8"),
            render_markdown(self.analysis, self.discovery.candidates),
        )

    def test_report_states_why_no_transform_is_authored(self):
        target = paths.REPORTS_DIR / "transform-analysis.md"
        if not target.is_file():
            self.skipTest("transform analysis report not generated")
        text = target.read_text(encoding="utf-8")
        self.assertIn("There is no allocator for these rows", text)
        self.assertIn("PlanFixed", text)
        # The report must not still claim the transform is a package requirement.
        self.assertNotIn("requires exactly one `WorldMapTransforms` row", text)

    def test_report_does_not_overclaim_runtime_semantics(self):
        target = paths.REPORTS_DIR / "transform-analysis.md"
        if not target.is_file():
            self.skipTest("transform analysis report not generated")
        text = target.read_text(encoding="utf-8")
        self.assertIn("client reverse engineering", text)
        self.assertIn("unproven hypothesis", text)

    # -- per-floor evidence behind the report's numbers ------------------

    def test_deadmines_floor_chunk_counts(self):
        """Pins the numbers the report quotes, so they cannot silently drift."""
        self.assertEqual(self.analysis.chunk_counts[166], 18)
        self.assertEqual(self.analysis.chunk_counts[167], 11)
        self.assertEqual(self.analysis.chunk_counts[166] + self.analysis.chunk_counts[167], 29)

    def test_most_chunks_heuristic_is_refuted_on_both_maps(self):
        for map_id, chosen in ((36, 167), (631, 104)):
            with self.subTest(map=map_id):
                floors = next(c for c in self.analysis.choices if c.map_id == map_id).floors
                busiest = max(floors, key=lambda f: self.analysis.chunk_counts.get(f, 0))
                self.assertNotEqual(busiest, chosen)

    def test_deadmines_and_deeprun_first_floors_share_the_same_shape(self):
        """The structural similarity that makes their opposite answers a
        contradiction rather than a coincidence."""
        for first_floor in (166, 741):
            with self.subTest(floor=first_floor):
                offsets = set(self.analysis.chunk_field4[first_floor])
                self.assertIn(-10000.0, offsets)
                real = [v for v in offsets if v != -10000.0]
                self.assertEqual(len(real), 1)

    def test_deadmines_floor_field_columns_are_available(self):
        for floor_id in (166, 167):
            with self.subTest(floor=floor_id):
                row = self.analysis.floor(floor_id)
                self.assertEqual(row["mapId"], 36)
                self.assertEqual(row["field7"], 39)


# ---------------------------------------------------------------------------
# Karazhan: source fidelity
# ---------------------------------------------------------------------------


KARAZHAN = "Karazhan"
KARAZHAN_MAP_ID = 532
KARAZHAN_AREA_ID = 799
KARAZHAN_FLOORS = 17
KARAZHAN_CHUNKS = 86
KARAZHAN_TILES = 204


class TestSourceProvenance(_DiscoveryMixin, unittest.TestCase):
    """WDM is the authority.  Pin what authority was used.

    Every row, field and tile in a generated package comes from the vendored
    WDM Stable tree.  Without a recorded revision, a regenerated package could
    silently differ from the reviewed one and still pass every test below, so the
    provenance file and the tree it names are checked together.
    """

    def test_source_json_records_an_unmodified_revision(self):
        source = paths.UPSTREAM_PATCH_DIR / "SOURCE.json"
        self.assertTrue(source.is_file(), f"missing {source}")
        record = json.loads(source.read_text())
        self.assertEqual(record["dataset"], "Stable")
        self.assertFalse(
            record["modified"],
            "the vendored WDM copy is marked modified; it must be a pristine copy",
        )
        self.assertRegex(record["revision"], r"^[0-9a-f]{40}$")

    def test_the_wdm_tree_this_run_used_is_the_recorded_one(self):
        record = json.loads((paths.UPSTREAM_PATCH_DIR / "SOURCE.json").read_text())
        self.assertTrue(paths.UPSTREAM_PATCH_DIR.is_dir())
        self.assertTrue(paths.wdm_dbc_dir().is_dir(), "no vendored WDM Stable DBFilesClient")
        self.assertTrue(
            paths.wdm_artwork_dir().is_dir(), "no vendored WDM Stable WorldMap artwork"
        )
        # The copy must be self-consistent: the tables and artwork the tools read
        # are inside the tree SOURCE.json describes.
        for table in ("DungeonMap", "DungeonMapChunk", "WorldMapArea", "WorldMapTransforms"):
            with self.subTest(table=table):
                self.assertTrue((paths.wdm_dbc_dir() / f"{table}.dbc").is_file())
        self.assertEqual(record["project"], "WDM-patch")

    def test_stock_baseline_is_present_and_read_only_reference_data(self):
        stock = paths.stock_dbc_dir()
        for table in ("DungeonMap", "DungeonMapChunk", "WorldMapArea", "WorldMapTransforms"):
            with self.subTest(table=table):
                self.assertTrue((stock / f"{table}.dbc").is_file())

    def test_stock_baseline_provenance_and_hashes_are_repository_owned(self):
        self.assertTrue(paths.STOCK_DBC_SOURCE_JSON.is_file())
        source = json.loads(paths.STOCK_DBC_SOURCE_JSON.read_text())
        self.assertEqual(source["revision"], "build 12340 (enUS)")
        self.assertFalse(source["modified"])
        self.assertTrue(paths.STOCK_DBC_DIR.is_relative_to(paths.REPO_ROOT))
        # stock_dbc_dir() verifies the complete SHA256SUMS manifest before it
        # returns; reaching this assertion proves all four immutable inputs.
        self.assertEqual(paths.stock_dbc_dir(), paths.STOCK_DBC_DIR)


class TestPortableBuildInputs(unittest.TestCase):
    """Build entry points must never acquire a developer-checkout dependency."""

    def test_legacy_external_overrides_cannot_redirect_repository_inputs(self):
        poisoned = {
            "MOD_NATIVE_INSTANCE_MAPS_STOCK_DBC": "/definitely/missing/stock",
            "WDM_PATCH_DIR": "/definitely/missing/wdm",
        }
        with mock.patch.dict(os.environ, poisoned):
            self.assertEqual(paths.stock_dbc_dir(), paths.STOCK_DBC_DIR)
            self.assertEqual(
                paths.wdm_dbc_dir(),
                paths.UPSTREAM_STABLE_DIR / "enUS" / "DBFilesClient",
            )

    def test_required_build_logic_contains_no_developer_absolute_path(self):
        inputs = [paths.REPO_ROOT / "Makefile", paths.REPO_ROOT / "README.md"]
        inputs += sorted((paths.REPO_ROOT / "tools").glob("*.py"))
        inputs += [paths.REPO_ROOT / "tests" / "validate_epfs.py"]
        inputs += sorted((paths.REPO_ROOT / "reports").glob("*.md"))
        developer_path = re.compile(
            r"(?:/home/[^/]+|/Users/[^/]+|[A-Za-z]:\\\\Users\\\\)"
        )
        for source in inputs:
            with self.subTest(source=source.relative_to(paths.REPO_ROOT)):
                text = source.read_text(encoding="utf-8")
                self.assertIsNone(developer_path.search(text))
        production = "\n".join(
            source.read_text(encoding="utf-8")
            for source in [paths.REPO_ROOT / "Makefile", paths.REPO_ROOT / "README.md"]
            + sorted((paths.REPO_ROOT / "tools").glob("*.py"))
        )
        self.assertNotIn("MOD_NATIVE_INSTANCE_MAPS_STOCK_DBC", production)
        self.assertNotIn("WDM_PATCH_DIR", production)


class TestFloorNames(unittest.TestCase):
    """Floor labels are WDM's own strings, read from the vendored locale files.

    Nothing in this class invents a name.  Every assertion compares the importer's
    output against bytes in ``upstream/WDM-addons``, which are themselves pinned
    by ``SHA256SUMS``.
    """

    def test_vendored_locale_tables_match_their_recorded_hashes(self):
        recorded = {}
        for line in paths.WDM_LOCALE_SHA256SUMS.read_text().splitlines():
            digest, name = line.split(None, 1)
            recorded[name.strip()] = digest
        vendored = sorted(p.name for p in paths.wdm_locale_dir().glob("*.lua"))
        self.assertEqual(vendored, sorted(recorded), "SHA256SUMS covers every locale file")
        for name, digest in recorded.items():
            with self.subTest(locale=name):
                self.assertEqual(
                    hashlib.sha256(
                        (paths.wdm_locale_dir() / name).read_bytes()
                    ).hexdigest(),
                    digest,
                )

    def test_karazhan_reads_every_floor_in_every_published_locale(self):
        labels = floornames.floor_labels("Karazhan")
        expected = set(floornames.CLIENT_LOCALES) - set(
            floornames.missing_locales("Karazhan")
        )
        self.assertEqual(sorted(labels), sorted(expected))
        for locale, table in labels.items():
            with self.subTest(locale=locale):
                # Karazhan is 17 floors, so a complete table is 1..17 with no gap.
                self.assertEqual(
                    sorted(int(level) for level in table), list(range(1, 18))
                )

    def test_labels_are_wdms_own_strings_not_retyped(self):
        # Read straight from the vendored enUS file rather than restating it, so a
        # change upstream shows up as a test failure instead of a silent drift.
        table = floornames.read_locale_table(
            paths.wdm_locale_dir() / "enus.lua"
        )
        labels = floornames.floor_labels("Karazhan")
        for level, label in labels["enUS"].items():
            with self.subTest(level=level):
                self.assertEqual(label, table["KARAZHAN" + level])

    def test_missing_locales_are_absent_not_invented(self):
        labels = floornames.floor_labels("Karazhan")
        for locale in floornames.missing_locales("Karazhan"):
            with self.subTest(locale=locale):
                self.assertNotIn(locale, labels)

    def test_an_instance_named_only_as_an_instance_yields_no_labels(self):
        # WDM publishes DUNGEON_FLOOR_ZULFARRAK with no floor number.  Promoting it
        # to "floor 1" would be a mapping WDM's own code never makes, so Zul'Farrak
        # keeps the stock "Floor 1" label.
        self.assertEqual(floornames.floor_labels("ZulFarrak"), {})

    def test_floor_token_matches_the_clients_upper_case_fold(self):
        self.assertEqual(floornames.floor_token("Karazhan"), "KARAZHAN")
        self.assertEqual(
            floornames.floor_token("TheTempleOfAtalHakkar"), "THETEMPLEOFATALHAKKAR"
        )
        with self.assertRaises(floornames.FloorNameError):
            floornames.floor_token("Karazhán")
        with self.assertRaises(floornames.FloorNameError):
            floornames.floor_token("")

    def test_locales_with_identical_tables_stay_identical(self):
        # enUS, enGB, enCN and zhCN ship the same bytes upstream; a per-locale
        # transformation would silently diverge them.
        labels = floornames.floor_labels("Karazhan")
        self.assertEqual(labels["enUS"], labels["enGB"])
        self.assertEqual(len(labels["enUS"]), 17)


class TestStockFrameXml(unittest.TestCase):
    """The stock table of contents is shipped unmodified and digest-pinned."""

    def test_vendored_toc_matches_its_recorded_hash(self):
        recorded = {}
        for line in paths.STOCK_FRAMEXML_SHA256SUMS.read_text().splitlines():
            digest, name = line.split(None, 1)
            recorded[name.strip()] = digest
        self.assertEqual(stock_toc_sha256(), recorded["FrameXML.toc"])

    def test_vendored_toc_still_carries_the_insertion_marker(self):
        text = paths.STOCK_FRAMEXML_TOC.read_text(encoding="utf-8")
        marker = "## add new modules above here"
        self.assertEqual(text.count(marker), 1)
        # The generated module is a TOC line, so it must be inserted while the
        # marker that opens the stock load order is still present.
        self.assertLess(
            text.index(marker), text.index("LocalizationPost.xml")
        )

    def test_manifest_pin_matches_the_vendored_toc(self):
        self.assertEqual(
            json.loads(
                (paths.CONTENT_DIR / "karazhan" / "manifest.json").read_text()
            )["clientFrameXml"],
            {
                "stockTocSha256": stock_toc_sha256(),
                "stockTocSource": STOCK_TOC_MEMBER,
            },
        )

    def test_provenance_records_the_container_it_came_from(self):
        record = json.loads(paths.STOCK_FRAMEXML_SOURCE_JSON.read_text())
        self.assertEqual(record["sha256"], stock_toc_sha256())
        self.assertIn("FrameXML.toc", record["member"])
        self.assertFalse(record["modified"])


class TestKarazhanSource(_DiscoveryMixin, unittest.TestCase):
    """The generated declaration must be WDM's Karazhan, row for row.

    These tests read the preserved WDM Stable tables directly and compare them to
    the semantic output.  Nothing here trusts the importer's own intermediate
    state, so a projection that renumbered a row, reordered a chunk list,
    normalised a signed field or invented a transform would fail here.
    """

    def setUp(self):
        self.item = self.candidate(KARAZHAN)
        self.tables = self.discovery.tables
        self.declaration = self.discovery_declaration = semantic.world_map_declaration(
            self.tables,
            self.item.map_id,
            self.item.world_map_area_ids,
            self.item.floor_ids,
            self.item.chunk_ids,
            self.item.transform_ids[0] if self.item.transform_ids else None,
        )
        self.area = self.declaration["areas"][0]

    # -- counts -----------------------------------------------------------

    def test_wdm_source_counts(self):
        """The counts the ground truth fixes, re-derived from the source tables."""
        areas = [
            record
            for record in self.tables["WorldMapArea"].records
            if str(record.value("internal_name")) == KARAZHAN
        ]
        floors = [
            record
            for record in self.tables["DungeonMap"].records
            if record.map_id() == KARAZHAN_MAP_ID
        ]
        floor_ids = {record.id for record in floors}
        chunks = [
            record
            for record in self.tables["DungeonMapChunk"].records
            if record.map_id() == KARAZHAN_MAP_ID
            and record.uint("DungeonMapID") in floor_ids
        ]
        transforms = [
            record
            for record in self.tables["WorldMapTransforms"].records
            if record.map_id() == KARAZHAN_MAP_ID
        ]
        tiles = sorted(
            entry.name
            for entry in (paths.wdm_artwork_dir() / KARAZHAN).iterdir()
            if entry.is_file()
        )
        self.assertEqual(len(areas), 1)
        self.assertEqual(len(floors), KARAZHAN_FLOORS)
        self.assertEqual(len(chunks), KARAZHAN_CHUNKS)
        self.assertEqual(len(transforms), 0)
        self.assertEqual(len(tiles), KARAZHAN_TILES)

    def test_every_karazhan_chunk_belongs_to_a_karazhan_floor(self):
        floors = {record.id for record in self.tables["DungeonMap"].records_for_map(
            KARAZHAN_MAP_ID
        )}
        chunks = self.tables["DungeonMapChunk"].records_for_map(KARAZHAN_MAP_ID)
        self.assertEqual(len(chunks), KARAZHAN_CHUNKS)
        for record in chunks:
            with self.subTest(chunk=record.id):
                self.assertIn(record.uint("DungeonMapID"), floors)

    # -- identity ---------------------------------------------------------

    def test_map_id_and_area_id(self):
        self.assertEqual(self.item.map_id, KARAZHAN_MAP_ID)
        self.assertEqual(self.item.world_map_area_ids, [KARAZHAN_AREA_ID])
        self.assertEqual(self.declaration["mapId"], KARAZHAN_MAP_ID)
        self.assertEqual(self.area["id"], KARAZHAN_AREA_ID)
        self.assertEqual(self.area["internalName"], KARAZHAN)

    def test_area_row_is_copied_field_for_field(self):
        record = self.tables["WorldMapArea"].get(KARAZHAN_AREA_ID)
        self.assertEqual(record.map_id(), KARAZHAN_MAP_ID)
        for source, key in semantic.AREA_FIELDS:
            with self.subTest(field=source):
                self.assertEqual(self.area[key], record.value(source))
        # floorNames is not a WorldMapArea field: it is added from WDM's locale
        # tables and is projected in TestFloorNames, not here.
        self.assertEqual(
            set(self.area),
            {"id", "internalName", "floors", "chunks", "floorNames"}
            | {key for _, key in semantic.AREA_FIELDS},
        )
        for floor in self.area["floors"]:
            self.assertNotIn("floorNames", floor)

    def test_dungeon_map_id_is_preserved_not_normalised(self):
        record = self.tables["WorldMapArea"].get(KARAZHAN_AREA_ID)
        self.assertEqual(int(record.value("dungeonMap_id")), 0)
        self.assertEqual(self.item.area_dungeon_map_id, 0)
        self.assertEqual(self.area["dungeonMapId"], 0)
        # The reference is not turned into one of the map's own floors.
        self.assertNotIn(0, [floor["id"] for floor in self.area["floors"]])

    # -- floors and chunks -------------------------------------------------

    def test_floor_ids_and_fields_match_the_source_rows(self):
        declared = self.area["floors"]
        self.assertEqual(len(declared), KARAZHAN_FLOORS)
        physical = self.tables["DungeonMap"].records_for_map(KARAZHAN_MAP_ID)
        self.assertEqual([f["id"] for f in declared], [r.id for r in physical])
        for entry, record in zip(declared, physical):
            with self.subTest(floor=record.id):
                for source, key in semantic.FLOOR_FIELDS:
                    self.assertEqual(entry[key], record.value(source))
                self.assertEqual(
                    set(entry), {"id"} | {key for _, key in semantic.FLOOR_FIELDS}
                )
                self.assertNotEqual(entry["floor"], 0, "Floor 0 is refused by CM")

    def test_chunk_ids_and_fields_match_the_source_rows(self):
        declared = self.area["chunks"]
        self.assertEqual(len(declared), KARAZHAN_CHUNKS)
        floor_ids = {floor["id"] for floor in self.area["floors"]}
        physical = [
            record
            for record in self.tables["DungeonMapChunk"].records
            if record.map_id() == KARAZHAN_MAP_ID
            and record.uint("DungeonMapID") in floor_ids
        ]
        # WDM's physical order, not ID order: reordering would compose a
        # different DBC.
        self.assertEqual([c["id"] for c in declared], [r.id for r in physical])
        self.assertNotEqual(
            [c["id"] for c in declared], sorted(c["id"] for c in declared)
        )
        for entry, record in zip(declared, physical):
            with self.subTest(chunk=record.id):
                for source, key in semantic.CHUNK_FIELDS:
                    self.assertEqual(entry[key], record.value(source))
                self.assertEqual(
                    set(entry), {"id"} | {key for _, key in semantic.CHUNK_FIELDS}
                )
                self.assertIn(entry["dungeonMapId"], floor_ids)
                self.assertNotEqual(entry["field2"], 0, "field2 0 is refused by CM")

    def test_floats_survive_exactly(self):
        """A float32 written through JSON and back must be the same float."""
        for entry, record in zip(self.area["floors"], self.tables["DungeonMap"].records_for_map(KARAZHAN_MAP_ID)):
            for source, key in semantic.FLOOR_FIELDS:
                value = record.value(source)
                if isinstance(value, float):
                    with self.subTest(floor=record.id, field=source):
                        self.assertIsInstance(entry[key], float)
                        self.assertEqual(
                            entry[key].hex() if hasattr(entry[key], "hex") else entry[key],
                            value.hex() if hasattr(value, "hex") else value,
                        )

    # -- the transform must be absent ---------------------------------------

    def test_no_transform_key_and_no_invented_ids(self):
        self.assertEqual(self.item.transform_ids, [])
        self.assertNotIn("transform", self.declaration)
        self.assertEqual(set(self.declaration), {"mapId", "areas"})
        body = json.dumps(self.declaration)
        for token in ("newDungeonMapId", "newMapId", "regionOffset", "regionBottom"):
            with self.subTest(token=token):
                self.assertNotIn(token, body)

    def test_no_floor_is_promoted_to_a_transform_target(self):
        """The 17 floors stay floors; none is designated a default."""
        floors = [floor["id"] for floor in self.area["floors"]]
        self.assertEqual(len(floors), KARAZHAN_FLOORS)
        self.assertEqual(len(set(floors)), KARAZHAN_FLOORS)
        # Each floor is declared once, with WDM's own Floor value, and no
        # declaration singles one out as the map's default.
        physical = self.tables["DungeonMap"].records_for_map(KARAZHAN_MAP_ID)
        self.assertEqual(floors, [record.id for record in physical])
        self.assertEqual(
            [floor["floor"] for floor in self.area["floors"]],
            [record.value("Floor") for record in physical],
        )

    # -- artwork ------------------------------------------------------------

    def test_artwork_declaration_matches_the_wdm_directory(self):
        source_dir = paths.wdm_artwork_dir() / KARAZHAN
        leaves = sorted(
            (entry.name for entry in source_dir.iterdir() if entry.is_file()),
            key=lambda name: name,
        )
        self.assertEqual(len(leaves), KARAZHAN_TILES)
        manifest = json.loads(
            (paths.CONTENT_DIR / self.item.slug / "manifest.json").read_text()
        )
        self.assertEqual(len(manifest["content"]), KARAZHAN_TILES)
        for entry in manifest["content"]:
            with self.subTest(leaf=Path(entry["source"]).name):
                self.assertIn(Path(entry["source"]).name, leaves)
                self.assertEqual(
                    entry["target"],
                    f"Interface/WorldMap/{KARAZHAN}/{Path(entry['source']).name}",
                )

    def test_artwork_bytes_are_the_wdm_bytes(self):
        """Hash every tile: the package must carry WDM's payload unmodified."""
        import hashlib
        import zipfile

        source_dir = paths.wdm_artwork_dir() / KARAZHAN
        expected = {
            entry.name: hashlib.sha256(entry.read_bytes()).hexdigest()
            for entry in source_dir.iterdir()
            if entry.is_file()
        }
        self.assertEqual(len(expected), KARAZHAN_TILES)
        self.assertTrue(all(digest for digest in expected.values()))
        manifest = json.loads(
            (paths.CONTENT_DIR / self.item.slug / "manifest.json").read_text()
        )
        with zipfile.ZipFile(paths.DIST_DIR / f"{paths.package_key(self.item.slug)}.epf") as archive:
            payloads = {
                Path(name).name: hashlib.sha256(archive.read(name)).hexdigest()
                for name in archive.namelist()
                if name not in ("manifest.json", STOCK_TOC_MEMBER)
            }
            # The stock TOC is a separate payload with its own provenance, checked
            # against the vendored file in TestStockFrameXml rather than WDM's.
            toc = hashlib.sha256(archive.read(STOCK_TOC_MEMBER)).hexdigest()
        self.assertEqual(payloads, expected)
        self.assertEqual(toc, stock_toc_sha256())

    # -- determinism --------------------------------------------------------

    def test_generation_is_deterministic(self):
        """Same source, same revision, same bytes."""
        import hashlib
        import shutil
        import tempfile

        scratch = Path(tempfile.mkdtemp(prefix="nim-karazhan-"))
        try:
            first = build_epf(
                self.item,
                paths.CONTENT_DIR / self.item.slug / "manifest.json",
                scratch / "a.epf",
            )
            second = build_epf(
                self.item,
                paths.CONTENT_DIR / self.item.slug / "manifest.json",
                scratch / "b.epf",
            )
            digest = [
                hashlib.sha256(path.read_bytes()).hexdigest()
                for path in (first, second)
            ]
            self.assertEqual(digest[0], digest[1])
            committed = paths.DIST_DIR / f"{paths.package_key(self.item.slug)}.epf"
            if committed.is_file():
                self.assertEqual(
                    hashlib.sha256(committed.read_bytes()).hexdigest(), digest[0]
                )
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

    def test_committed_manifest_matches_generation(self):
        self.assertEqual(
            (paths.CONTENT_DIR / self.item.slug / "manifest.json").read_bytes(),
            serialise(manifest_for(self.item, self.discovery)),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
