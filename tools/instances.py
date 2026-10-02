#!/usr/bin/env python3
"""Discover and classify the native instance maps that WDM Stable represents.

Candidates are discovered mechanically from the two things WDM Stable actually
ships -- the four DBCs and the ``Interface/WorldMap/<internalName>/`` artwork
directories -- so no hand-maintained table of instances is involved.  A small
optional metadata file supplies human-readable titles and package slugs only.

Every candidate is then put through the same battery of checks, and the battery
is deliberately asymmetric: it is easy to be SAFE and very hard to stay there.
A candidate is SAFE only when the whole package can be expressed as *additive*
``worldMaps[]`` data whose every row already exists, byte for byte, in WDM
Stable and whose every reference resolves inside the package.

Every candidate reaches a terminal verdict.  There is no "a human should look at
this later" level, because every question this battery can ask has been asked and
answered against the vendored data; a candidate that is not SAFE records exactly
which row, artwork or reference is missing, and why no package can be built from
it without either authoring data WDM does not ship or replacing a row the stock
client already has.

Artwork is resolved case-insensitively against the declared ``internal_name``,
because WDM Stable ships two dungeon artwork directories whose casing disagrees
with the ``WorldMapArea.internal_name`` they belong to.  See
:func:`tile_target_name`.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from wdbc import DbcFile, DbcRecord, parse_file
import paths

__all__ = [
    "SAFE",
    "TABLES",
    "UNSAFE",
    "Candidate",
    "Discovery",
    "discover",
    "artwork_files",
    "tile_target_name",
]

#: The four client tables a native instance map composes into, in the order the
#: coverage audit and the reports list them.
TABLES = ("DungeonMap", "DungeonMapChunk", "WorldMapArea", "WorldMapTransforms")

#: A complete, additive package can be built from WDM Stable alone.
SAFE = "SAFE"

#: No package can be built.  Either WDM Stable ships nothing additive for the map,
#: or the only package that would work has to replace a row the stock client
#: already has.  Every UNSAFE candidate carries the reason codes that say which.
UNSAFE = "UNSAFE"

_NATURAL = re.compile(r"(\d+)")
_DIGITS = re.compile(r"^\d+$")


def natural_key(name: str) -> Tuple[Tuple[int, object], ...]:
    """``a2`` sorts before ``a10``; total order, so the result is deterministic."""
    parts = [part for part in _NATURAL.split(name) if part != ""]
    return tuple(
        (0, int(part)) if _DIGITS.match(part) else (1, part) for part in parts
    )


def artwork_files(directory: Path) -> List[str]:
    """Sorted ``.blp`` file names in one ``Interface/WorldMap/<name>`` directory."""
    if not directory.is_dir():
        return []
    return sorted(
        (entry.name for entry in directory.iterdir() if entry.is_file()),
        key=natural_key,
    )


def tile_target_name(internal_name: str, source_dir: Optional[str], leaf: str) -> str:
    """The tile file name the client looks for, given a WDM artwork leaf name.

    The client derives a tile's name from the ``WorldMapArea.internal_name`` of
    the area it is drawing, and WDM's artwork directory is not always spelled with
    those same capitals: it ships ``BlackFathomDeeps/BlackFathomDeeps1_1.blp`` for
    the area whose ``internal_name`` is ``BlackfathomDeeps``, and
    ``Magtheridonslair/`` for ``MagtheridonsLair``.

    That inconsistency is WDM's, and it only resolves at all because the client
    runs on a case-insensitive filesystem.  A package does not need the filesystem
    to rescue it: the name is rebuilt from the client-baked ``internal_name`` the
    DBC row carries, which is the identity the client actually uses.  Only the
    path changes -- the BLP bytes are copied verbatim, and the ``<floor>_<tile>``
    tail is WDM's own, so no tile is added, dropped, reordered or renumbered.

    Scope is deliberately the directory name.  A leaf that is not the area's own
    name in different capitals -- including WDM's own inconsistent casing *within*
    a directory, and flat ``<name><n>.blp`` world tiles -- is returned unchanged,
    so a genuine naming defect still reaches the caller as a defect instead of
    being silently rewritten.
    """
    if leaf.startswith(internal_name):
        return leaf
    if source_dir and source_dir.casefold() == internal_name.casefold():
        if leaf.startswith(source_dir):
            return internal_name + leaf[len(source_dir) :]
    return leaf

    match = _DUNGEON_TILE.match(leaf)
    if match and match.group("prefix").casefold() == internal_name.casefold():
        return internal_name + match.group("tail")
    return leaf


def artwork_alias_matches(artwork_dirs: Dict[str, Path], internal_name: str) -> List[str]:
    """WDM artwork directories that differ from ``internal_name`` only by case.

    Sorted so a candidate's artwork source is deterministic.  An empty list means
    the area either has its own directory or has no artwork at all; more than one
    entry means the spelling is genuinely ambiguous and nothing may be bound.
    """
    folded = internal_name.casefold()
    return sorted(
        name for name in artwork_dirs if name.casefold() == folded and name != internal_name
    )


def _all_entries(directory: Path) -> List[str]:
    if not directory.is_dir():
        return []
    return sorted(
        (entry.name for entry in directory.iterdir() if entry.is_file()),
        key=natural_key,
    )


@dataclass
class Candidate:
    """One discovered instance map plus the verdict computed for it."""

    internal_name: str
    map_id: Optional[int]
    slug: str
    title: str
    artwork_dir: str
    blps: List[str] = field(default_factory=list)
    artwork_entries: List[str] = field(default_factory=list)
    #: The WDM directory the tiles are read from.  Equal to ``internal_name``
    #: except where WDM's artwork directory casing disagrees with the
    #: ``WorldMapArea`` row that owns it; ``None`` until :func:`discover` binds it.
    artwork_source: Optional[str] = None
    #: WDM directory names that case-fold to this candidate's ``internal_name``.
    #: Empty is the ordinary case, one entry is a bound alias, more than one is
    #: an ambiguous spelling nothing may be bound to.
    artwork_aliases: List[str] = field(default_factory=list)
    #: Set when another candidate's ``internal_name`` is this candidate's only
    #: spelling difference away, i.e. this directory is that map's artwork.
    artwork_claimed_by: Optional[str] = None
    reason_codes: List[str] = field(default_factory=list)
    world_map_area_ids: List[int] = field(default_factory=list)
    world_map_area_additive: List[bool] = field(default_factory=list)
    floor_ids: List[int] = field(default_factory=list)
    floor_additive: List[bool] = field(default_factory=list)
    chunk_ids: List[int] = field(default_factory=list)
    chunk_additive: List[bool] = field(default_factory=list)
    transform_ids: List[int] = field(default_factory=list)
    transform_additive: List[bool] = field(default_factory=list)
    #: ``WorldMapArea.dungeonMap_id`` exactly as WDM wrote it, decoded as a
    #: signed 32-bit integer.  This is a *reference* the client reads, not a row
    #: this package owns, so it is recorded for fidelity and never rewritten.
    area_dungeon_map_id: Optional[int] = None
    classification: str = UNSAFE
    findings: List[str] = field(default_factory=list)

    @property
    def package_key(self) -> str:
        return paths.package_key(self.slug)

    @property
    def source_dir(self) -> str:
        """The WDM directory name the tiles are read from."""
        return self.artwork_source or self.internal_name

    @property
    def tile_targets(self) -> List[str]:
        """Tile file names the client derives from ``internal_name``, in WDM order."""
        return [
            tile_target_name(self.internal_name, self.source_dir, leaf)
            for leaf in self.blps
        ]

    @property
    def artwork_renames(self) -> Dict[str, str]:
        """``source leaf -> target leaf`` for the tiles WDM mis-cased, if any."""
        return {
            source: target
            for source, target in zip(self.blps, self.tile_targets)
            if source != target
        }

    @property
    def artwork_targets(self) -> List[str]:
        prefix = f"Interface/WorldMap/{self.internal_name}/"
        return [prefix + leaf for leaf in self.tile_targets]

    def to_json(self) -> Dict[str, object]:
        return {
            "internalName": self.internal_name,
            "title": self.title,
            "slug": self.slug,
            "package": self.package_key,
            "mapId": self.map_id,
            "artworkDirectory": self.artwork_dir,
            "artworkSource": self.source_dir,
            "artworkLeafRenames": self.artwork_renames,
            "artworkNameAliases": list(self.artwork_aliases),
            "artworkClaimedBy": self.artwork_claimed_by,
            "blpCount": len(self.blps),
            "worldMapArea": [
                {"id": identifier, "additive": additive}
                for identifier, additive in zip(
                    self.world_map_area_ids, self.world_map_area_additive
                )
            ],
            "floors": [
                {"id": identifier, "additive": additive}
                for identifier, additive in zip(self.floor_ids, self.floor_additive)
            ],
            "chunks": [
                {"id": identifier, "additive": additive}
                for identifier, additive in zip(self.chunk_ids, self.chunk_additive)
            ],
            "transforms": [
                {"id": identifier, "additive": additive}
                for identifier, additive in zip(
                    self.transform_ids, self.transform_additive
                )
            ],
            "areaDungeonMapId": self.area_dungeon_map_id,
            "classification": self.classification,
            "reasonCodes": list(self.reason_codes),
            "findings": list(self.findings),
        }


@dataclass
class Discovery:
    candidates: List[Candidate]
    tables: Dict[str, DbcFile]
    unmapped_wdm_only_areas: List[Dict[str, object]]
    floors_without_area: List[Dict[str, object]]
    stock_mutations: List[Dict[str, object]]
    #: WDM-added row IDs per table, and the stock baseline's ID set.  Populated by
    #: :func:`discover`; :meth:`coverage` and the reports read them so the numbers
    #: have exactly one source.
    added_ids: Dict[str, set] = field(default_factory=dict)
    stock_ids: Dict[str, set] = field(default_factory=dict)

    def by_classification(self, level: str) -> List[Candidate]:
        return [item for item in self.candidates if item.classification == level]

    def counts(self) -> Dict[str, int]:
        return {
            "candidates": len(self.candidates),
            SAFE: len(self.by_classification(SAFE)),
            UNSAFE: len(self.by_classification(UNSAFE)),
        }

    def claimed_ids(self, table: str, level: Optional[str] = None) -> set:
        """Every row ID the given classification claims in one table.

        ``level=None`` means every candidate, which is what the coverage audit
        needs to tell "held back by a decided UNSAFE map" apart from "belongs to no
        map this project could package at all".
        """
        accessor = {
            "DungeonMap": lambda item: item.floor_ids,
            "DungeonMapChunk": lambda item: item.chunk_ids,
            "WorldMapArea": lambda item: item.world_map_area_ids,
            "WorldMapTransforms": lambda item: item.transform_ids,
        }[table]
        out: set = set()
        for item in self.candidates:
            if level is not None and item.classification != level:
                continue
            out.update(accessor(item))
        return out

    def coverage(self) -> List[Dict[str, object]]:
        """Reconcile WDM's added rows against what the SAFE set actually ships.

        The three numbers per table are the whole claim this project makes, so
        they are computed rather than asserted:

        ``shipped``
            added rows a SAFE candidate owns.  Every one of these becomes a
            composer request, a lease and a composed row.
        ``heldBack``
            added rows a decided UNSAFE candidate owns, with the reason codes
            that stopped it.
        ``unowned``
            added rows no candidate claims, because the map they belong to has no
            artwork directory and no additive area or floor to package.
        """
        out: List[Dict[str, object]] = []
        for table in TABLES:
            added = self.added_ids[table]
            shipped = self.claimed_ids(table, SAFE) & added
            unsafe = self.claimed_ids(table, UNSAFE) & added
            owners: Dict[int, List[str]] = {}
            accessor = {
                "DungeonMap": lambda item: item.floor_ids,
                "DungeonMapChunk": lambda item: item.chunk_ids,
                "WorldMapArea": lambda item: item.world_map_area_ids,
                "WorldMapTransforms": lambda item: item.transform_ids,
            }[table]
            for item in self.by_classification(UNSAFE):
                for identifier in set(accessor(item)) & added:
                    owners.setdefault(identifier, []).append(item.internal_name)
            out.append(
                {
                    "table": table,
                    "added": len(added),
                    "shipped": len(shipped),
                    "heldBack": {identifier: names for identifier, names in sorted(owners.items())},
                    "unowned": sorted(added - shipped - set(owners)),
                }
            )
        return out


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def _load_tables(wdm_dbc: Path) -> Dict[str, DbcFile]:
    return {
        table: parse_file(wdm_dbc / f"{table}.dbc", table)
        for table in TABLES
    }


class StockView:
    """Stock-baseline membership, plus what WDM did to each stock row.

    Three states matter for a package decision:

    ``added``
        the ID is new in WDM -- exactly the rows that can be appended.
    ``stock``
        the ID exists in stock and WDM leaves it byte for byte identical, so the
        client already has it and there is nothing additive to contribute.
    ``mutated``
        the ID exists in stock and WDM changed or deleted the row.  A
        mod-content-manager package can never express this: the composer refuses
        any declared ID that is occupied in the verified stock baseline, and it
        must, because appending a second row with a live ID is not an append.
    """

    def __init__(self, documents: Dict[str, DbcFile]):
        self.documents = documents
        self.wdm_documents: Dict[str, DbcFile] = {}
        self.ids: Dict[str, set] = {
            table: {record.id for record in document.records}
            for table, document in documents.items()
        }
        self.mutated: Dict[str, set] = {}
        self.removed: Dict[str, set] = {}

    def attach_wdm(self, documents: Dict[str, DbcFile]) -> None:
        self.wdm_documents = documents
        for table, document in self.documents.items():
            wdm = documents[table]
            self.mutated[table] = {
                record.id
                for record in document.records
                if record.id in wdm.by_id and wdm.by_id[record.id].raw != record.raw
            }
            self.removed[table] = {
                record.id for record in document.records if record.id not in wdm.by_id
            }

    def status(self, table: str, identifier: int) -> str:
        if identifier in self.removed[table]:
            return "mutated"
        if identifier in self.mutated[table]:
            return "mutated"
        if identifier in self.ids[table]:
            return "stock"
        return "added"

    def dungeon_map_status(self, identifier: int) -> str:
        return self.status("DungeonMap", identifier)

    def dungeon_map_chunk_status(self, identifier: int) -> str:
        return self.status("DungeonMapChunk", identifier)

    def world_map_area_status(self, identifier: int) -> str:
        return self.status("WorldMapArea", identifier)

    def world_map_transforms_status(self, identifier: int) -> str:
        return self.status("WorldMapTransforms", identifier)


def _stock_view(stock_dbc: Path, wdm_dbc: Path) -> "StockView":
    view = StockView(
        {
            table: parse_file(stock_dbc / f"{table}.dbc", table)
            for table in TABLES
        }
    )
    view.attach_wdm(
        {
            table: parse_file(wdm_dbc / f"{table}.dbc", table)
            for table in TABLES
        }
    )
    return view


def stock_mutation_records(
    stock: "StockView", tables: Dict[str, DbcFile], wdm_dbc: Path
) -> List[Dict[str, object]]:
    """Every place WDM changes or drops a row the stock client already has."""
    out: List[Dict[str, object]] = []
    for table in TABLES:
        document = tables[table]
        for identifier in sorted(stock.mutated[table] | stock.removed[table]):
            if identifier in stock.removed[table]:
                before = stock.documents[table].get(identifier)
                out.append(
                    {
                        "table": table,
                        "id": identifier,
                        "change": "removed",
                        "stockRecord": {
                            item.name: before.value(item.name)
                            for item in document.spec.fields
                        },
                    }
                )
                continue
            before = stock.documents[table].get(identifier)
            after = document.get(identifier)
            # Compare decoded values, not raw words, so a float32 geometry change
            # reads as a coordinate instead of its IEEE-754 bit pattern.
            deltas = [
                {
                    "field": item.name,
                    "stock": before.value(item.name),
                    "wdm": after.value(item.name),
                }
                for index, item in enumerate(document.spec.fields)
                if before.words[index] != after.words[index]
            ]
            out.append(
                {
                    "table": table,
                    "id": identifier,
                    "change": "modified",
                    "fieldDeltas": deltas,
                }
            )
    return out


def _load_titles(path: Path) -> Dict[str, Dict[str, str]]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {key: dict(value) for key, value in data.items()}


def discover(
    wdm_dbc: Path,
    wdm_artwork: Path,
    stock_dbc: Path,
    titles_path: Path | None = None,
) -> Discovery:
    """Group WDM Stable into candidates and classify each one."""
    tables = _load_tables(wdm_dbc)
    stock = _stock_view(stock_dbc, wdm_dbc)
    stock_ids = stock.ids
    titles = _load_titles(titles_path or (paths.REPO_ROOT / "content" / "titles.json"))

    areas: DbcFile = tables["WorldMapArea"]
    floors_table: DbcFile = tables["DungeonMap"]
    chunks_table: DbcFile = tables["DungeonMapChunk"]
    transforms_table: DbcFile = tables["WorldMapTransforms"]

    floors_by_map: Dict[int, List[DbcRecord]] = {}
    for record in floors_table.records:
        floors_by_map.setdefault(record.map_id(), []).append(record)
    chunk_records = list(chunks_table.records)
    transforms_by_map: Dict[int, List[DbcRecord]] = {}
    for record in transforms_table.records:
        transforms_by_map.setdefault(record.map_id(), []).append(record)
        areas_by_name: Dict[str, List[DbcRecord]] = {}
    for record in areas.records:
        areas_by_name.setdefault(str(record.value("internal_name")), []).append(record)

    artwork_dirs = {
        entry.name: entry
        for entry in sorted(wdm_artwork.iterdir())
        if entry.is_dir()
    } if wdm_artwork.is_dir() else {}

    # A candidate is every artwork directory WDM ships plus every WorldMapArea
    # row WDM adds.  Nothing is hand-listed.
    names: List[str] = list(artwork_dirs)
    added_areas = [record for record in areas.records if record.id not in stock_ids["WorldMapArea"]]
    for record in added_areas:
        name = str(record.value("internal_name"))
        if name not in artwork_dirs:
            names.append(name)
    names = sorted(set(names), key=natural_key)

    candidates: List["Candidate"] = []
    covered_maps: set = set()
    for name in names:
        meta = titles.get(name, {})
        area_rows = areas_by_name.get(name, [])
        map_id = area_rows[0].map_id() if area_rows else None
        if map_id is not None:
            covered_maps.add(map_id)
        # Artwork is looked up by the exact directory first and by a case-only
        # variant second, so an area whose WorldMapArea row is spelled with
        # different capitals than its own artwork directory still finds its
        # tiles.  Nothing is bound when the spelling is ambiguous.
        aliases = artwork_alias_matches(artwork_dirs, name)
        directory = artwork_dirs.get(name)
        if directory is None and len(aliases) == 1:
            directory = artwork_dirs[aliases[0]]
        candidate = Candidate(
            internal_name=name,
            map_id=map_id,
            slug=meta.get("slug") or paths.slugify(name),
            title=meta.get("title") or name,
            artwork_dir=f"Interface/WorldMap/{name}",
            blps=artwork_files(directory) if directory else [],
            artwork_entries=_all_entries(directory) if directory else [],
            artwork_source=directory.name if directory else None,
            artwork_aliases=aliases,
        )
        candidate.world_map_area_ids = [record.id for record in area_rows]
        candidate.world_map_area_additive = [
            record.id not in stock_ids["WorldMapArea"] for record in area_rows
        ]
        # Recorded verbatim, signed.  WDM writes 0, -1 and references to floors of
        # other maps here, and all three are legitimate source values.
        if len(area_rows) == 1:
            candidate.area_dungeon_map_id = int(area_rows[0].value("dungeonMap_id"))
        if map_id is not None:
            floors = floors_by_map.get(map_id, [])
            candidate.floor_ids = [record.id for record in floors]
            candidate.floor_additive = [
                record.id not in stock_ids["DungeonMap"] for record in floors
            ]
            floor_set = {record.id for record in floors}
            # WDM's physical record order, filtered to this map's floors.  The
            # client walks tiles in declaration order, so regrouping by floor
            # here would silently renumber the instance: the WDM Deadmines
            # chunk order interleaves floors 166 and 167, and sorting or
            # grouping by DungeonMapID produces a different DBC.
            chunks = [
                record
                for record in chunk_records
                if record.map_id() == map_id and record.uint("DungeonMapID") in floor_set
            ]
            candidate.chunk_ids = [record.id for record in chunks]
            candidate.chunk_additive = [
                record.id not in stock_ids["DungeonMapChunk"] for record in chunks
            ]
            transforms = transforms_by_map.get(map_id, [])
            candidate.transform_ids = [record.id for record in transforms]
            candidate.transform_additive = [
                record.id not in stock_ids["WorldMapTransforms"]
                for record in transforms
            ]
        candidates.append(candidate)

    unmapped = [
        {
            "id": record.id,
            "mapId": record.map_id(),
            "areaId": record.uint("area_id"),
            "internalName": str(record.value("internal_name")),
        }
        for record in added_areas
        if str(record.value("internal_name")) not in artwork_dirs
        and not artwork_alias_matches(artwork_dirs, str(record.value("internal_name")))
    ]
    floors_without_area = [
        {
            "mapId": map_id,
            "floors": [record.id for record in records],
        }
        for map_id, records in sorted(floors_by_map.items())
        if map_id not in covered_maps
    ]

    # An artwork directory whose name is only a case variant of a *different*
    # candidate's ``internal_name`` is that candidate's artwork, not a map of its
    # own: the area row that would make it a map does not exist.  Recorded so the
    # duplicate spelling is reported instead of being counted twice.
    owners = {
        candidate.internal_name: candidate
        for candidate in candidates
        if candidate.world_map_area_ids
    }
    for candidate in candidates:
        if candidate.world_map_area_ids:
            continue
        for owner_name, owner in owners.items():
            if owner_name.casefold() == candidate.internal_name.casefold():
                candidate.artwork_claimed_by = owner.internal_name
                break

    discovery = Discovery(
        candidates=candidates,
        tables=tables,
        unmapped_wdm_only_areas=unmapped,
        floors_without_area=floors_without_area,
        stock_mutations=stock_mutation_records(stock, tables, wdm_dbc),
        added_ids={
            table: {record.id for record in document.records} - stock.ids[table]
            for table, document in tables.items()
        },
        stock_ids={table: set(ids) for table, ids in stock.ids.items()},
    )
    for candidate in candidates:
        _classify(candidate, tables, stock)
    return discovery


# ---------------------------------------------------------------------------
# Reason codes
# ---------------------------------------------------------------------------
#
# A closed set: every reason a candidate is not SAFE is one of these, and each
# one states which of the three things a package needs is missing or contradictory:
#
# ``no-*-row``
#     WDM Stable does not ship a row the map cannot exist without.  Filling the
#     gap would mean authoring data WDM does not have, which is invention.
#
# ``stock-*-untouched`` / ``stock-mutation-required``
#     The row already exists in the verified stock baseline.  Untouched, there is
#     nothing additive to append.  Mutated or deleted, the only working package
#     would replace a row the client already has, which mod-content-manager's
#     append-only composer must refuse.
#
# ``*-unreadable``
#     The client would be handed artwork or a row it cannot read back.
#
# Two codes that earlier revisions of this file carried are deliberately absent:
#
# ``no-transform``
#     A missing ``WorldMapTransforms`` row is not a defect.  The four tables
#     describe a native instance map completely without it: stock 3.3.5a and WDM
#     Stable both ship large multi-floor instances with no transform row at all
#     (Karazhan, map 532, is seventeen floors with none), and
#     mod-content-manager treats ``worldMaps[].transform`` as optional.  A
#     transform is source data: WDM's rows are preserved byte for byte when it
#     has one, and when it has none the key is simply absent.  Nothing is derived,
#     defaulted or allocated here.
#
# ``area-floor-reference-unresolvable``
#     ``WorldMapArea.dungeonMap_id`` is a signed *reference* the client reads,
#     not a row this package owns.  WDM writes 0, writes -1 as an explicit
#     sentinel, and points at least one area (Ahn'Qiraj, map 531) at a
#     ``DungeonMap`` row belonging to a different map.  All three are legitimate
#     source values, so requiring the reference to name a floor of the same map
#     rejected real content.  The value is carried through verbatim instead.
UNSAFE_REASONS = frozenset(
    {
        "stock-mutation-required",
        "artwork-not-blp",
        "artwork-name-ambiguous",
        "duplicate-artwork-alias",
        "no-world-map-area",
        "ambiguous-world-map-area",
        "no-artwork",
        "no-chunks",
        "floorless-dungeon-map-id",
        "floorless-chunk-reference",
        "floorless-transform-reference",
        "floor-zero",
        "chunk-field2-zero",
        "chunk-floor-reference-unresolvable",
        "ambiguous-transform",
        "stock-transform",
        "stock-world-map-area",
        "stock-floor",
        "stock-chunk",
        "transform-new-map-zero",
        "transform-target-not-a-floor",
        "virtual-map-pinned",
    }
)


@dataclass
class _Check:
    """Collects reason codes while building the human-readable findings."""

    codes: set = field(default_factory=set)
    findings: List[str] = field(default_factory=list)

    def fail(self, code: str, message: str) -> None:
        self.codes.add(code)
        self.findings.append(message)


def _classify(candidate: Candidate, tables: Dict[str, DbcFile], stock: "StockView") -> None:
    check = _Check()
    areas: DbcFile = tables["WorldMapArea"]
    floors: DbcFile = tables["DungeonMap"]
    chunks: DbcFile = tables["DungeonMapChunk"]
    transforms: DbcFile = tables["WorldMapTransforms"]

    # ---- a second spelling of a map that already has one --------------------
    # WDM Stable spells two dungeon artwork directories with different capitals
    # than the ``WorldMapArea.internal_name`` they belong to, and names no
    # ``WorldMapArea`` row for the artwork spelling at all.  That directory is
    # therefore one map's artwork, not a map of its own, and every other check
    # would be noise around this one root cause.
    if candidate.artwork_claimed_by:
        check.fail(
            "duplicate-artwork-alias",
            f"Interface/WorldMap/{candidate.source_dir}/ is the artwork of "
            f"{candidate.artwork_claimed_by} -- the same name in different capitals. "
            f"WDM Stable declares no WorldMapArea row for {candidate.internal_name!r}, "
            "so it names no map of its own; these tiles ship with "
            f"{candidate.artwork_claimed_by} and are not a separate candidate",
        )
        _finish(candidate, check)
        return

    # ---- artwork -----------------------------------------------------------
    if not candidate.artwork_entries:
        if len(candidate.artwork_aliases) > 1:
            check.fail(
                "artwork-name-ambiguous",
                f"WDM Stable ships {len(candidate.artwork_aliases)} artwork directories "
                f"that differ from {candidate.internal_name!r} only by case "
                f"({', '.join(candidate.artwork_aliases)}); none of them can be chosen "
                "without inventing which one the client reads",
            )
        else:
            check.fail(
                "no-artwork",
                f"WDM Stable ships no artwork for {candidate.internal_name!r}; the client "
                f"draws the map from {candidate.artwork_dir}/, so the package would be "
                "invisible",
            )
    else:
        strays = [
            name for name in candidate.artwork_entries if not name.lower().endswith(".blp")
        ]
        if strays:
            check.fail(
                "artwork-not-blp",
                f"{candidate.artwork_dir} holds non-.blp entries: {', '.join(strays)}",
            )
        if not candidate.blps:
            check.fail(
                "no-artwork",
                f"{candidate.artwork_dir} holds no .blp tiles",
            )

    # ---- WorldMapArea ------------------------------------------------------
    if not candidate.world_map_area_ids:
        check.fail(
            "no-world-map-area",
            "WDM Stable has no WorldMapArea row whose internal_name is "
            f"{candidate.internal_name!r}; there is nothing for the client to attach "
            "the artwork directory to, and authoring one would be invention",
        )
    elif len(candidate.world_map_area_ids) > 1:
        check.fail(
            "ambiguous-world-map-area",
            "ambiguous: WorldMapArea "
            + ", ".join(map(str, candidate.world_map_area_ids))
            + f" all name {candidate.internal_name!r}; a package must pick exactly one",
        )
    else:
        identifier = candidate.world_map_area_ids[0]
        if stock.world_map_area_status(identifier) == "mutated":
            check.fail(
                "stock-mutation-required",
                f"WorldMapArea {identifier} is a stock row that WDM mutates; shipping "
                "it would replace a client-baked identity",
            )
        elif not candidate.world_map_area_additive[0]:
            check.fail(
                "stock-world-map-area",
                f"WorldMapArea {identifier} is a stock row that WDM leaves untouched; "
                "the client already has it and there is nothing additive to ship",
            )
        area = areas.get(identifier)
        if int(area.value("virtual_map_id")) == 0:
            check.fail(
                "virtual-map-pinned",
                f"WorldMapArea {identifier} pins virtual_map_id to 0, a live world map; "
                "the composer would need to know which parent map supplies it",
            )

    # ---- floors ------------------------------------------------------------
    if candidate.map_id is None:
        # Artwork directory with no WorldMapArea row.  Every other check is
        # downstream of a map identity that WDM never supplies, so reporting
        # them would just be noise around one root cause.
        _finish(candidate, check)
        return
    # A map that owns no DungeonMap row is a real 3.3.5a client shape, not a gap
    # in the source data.  Stock build 12340 already ships 48 such WorldMapArea
    # rows -- WorldMapArea 531 / MapID 615 TheObsidianSanctum, 602 / 658
    # PitofSaron and 609 / 724 TheRubySanctum among them -- and WDM Stable
    # ships 55, including Zul'Farrak (686 / 209).  WDM's own LibMapData records
    # `floors = 0` for every one of them.  The client draws such a map from its
    # WorldMapArea row and its artwork alone, so mod-content-manager expresses
    # it as an area with an empty `floors` array: it then requests, leases and
    # composes no DungeonMap, DungeonMapChunk or WorldMapTransforms row, and
    # those three DBCs are reproduced stock byte for byte.
    #
    # Accepting the shape must not accept anything alongside it, so what is
    # checked is only that no reference the area could not satisfy survives.
    # A DungeonMapChunk names a floor and a WorldMapTransforms names a floor of
    # its own map, so a floorless map owns neither; and every floorless row in
    # stock and in WDM carries dungeonMapId exactly 0, so 0 is the only accepted
    # spelling here.
    floorless = not candidate.floor_ids
    if floorless:
        if candidate.chunk_ids:
            check.fail(
                "floorless-chunk-reference",
                f"map {candidate.map_id} owns no DungeonMap floor, so its "
                f"DungeonMapChunk row(s) {_join(candidate.chunk_ids[:8], '...')} have "
                "no floor to name",
            )
        if candidate.transform_ids:
            check.fail(
                "floorless-transform-reference",
                f"WorldMapTransforms "
                f"{_join(candidate.transform_ids[:8], '...')} name a floor of map "
                f"{candidate.map_id}, but that map owns none",
            )
        if candidate.area_dungeon_map_id not in (0, None):
            check.fail(
                "floorless-dungeon-map-id",
                f"WorldMapArea {candidate.world_map_area_ids[0]} owns no "
                f"DungeonMap floor, so dungeonMapId must be 0 but is "
                f"{candidate.area_dungeon_map_id}; every floorless row in stock and "
                "in WDM carries 0",
            )
    else:
        for identifier in candidate.floor_ids:
            status = stock.dungeon_map_status(identifier)
            if status == "mutated":
                check.fail(
                    "stock-mutation-required",
                    f"DungeonMap floor {identifier} is a stock row that WDM mutates; the "
                    "instance only works with WDM's replacement geometry, and the "
                    "append-only composer cannot express that",
                )
            elif status == "stock":
                check.fail(
                    "stock-floor",
                    f"DungeonMap floor {identifier} is already a stock row; the client "
                    "already has this floor and there is nothing additive to ship",
                )
        zero_floors = [
            record.id for record in (floors.get(i) for i in candidate.floor_ids)
            if record.uint("Floor") == 0
        ]
        if zero_floors:
            check.fail(
                "floor-zero",
                f"DungeonMap floor(s) {_join(zero_floors)} declare Floor 0, which "
                "mod-content-manager rejects for every row",
            )

    # ---- chunks ------------------------------------------------------------
    if floorless:
        # A chunk belongs to a floor, so a floorless map owns none.  The check
        # is reported above, next to the floor evidence it follows from.
        pass
    elif not candidate.chunk_ids:
        check.fail(
            "no-chunks",
            f"WDM Stable declares no DungeonMapChunk for the floors of map {candidate.map_id}",
        )
    else:
        stock_rows: List[int] = []
        mutated_rows: List[int] = []
        for identifier in candidate.chunk_ids:
            status = stock.dungeon_map_chunk_status(identifier)
            if status == "mutated":
                mutated_rows.append(identifier)
            elif status == "stock":
                stock_rows.append(identifier)
        if mutated_rows:
            check.fail(
                "stock-mutation-required",
                f"DungeonMapChunk row(s) {_join(mutated_rows[:8], '...')} are stock rows "
                "WDM mutates; the tile set is not additive",
            )
        if stock_rows:
            check.fail(
                "stock-chunk",
                f"DungeonMapChunk row(s) {_join(stock_rows[:8], '...')} already exist in "
                "the stock client; the client already has this tile set and there is "
                "nothing additive to ship",
            )
        floor_set = set(candidate.floor_ids)
        dangling = sorted(
            {
                record.uint("DungeonMapID")
                for record in (chunks.get(i) for i in candidate.chunk_ids)
                if record.uint("DungeonMapID") not in floor_set
            }
        )
        if dangling:
            check.fail(
                "chunk-floor-reference-unresolvable",
                f"DungeonMapChunk rows reference DungeonMap {_join(dangling)}, which is "
                f"not a floor of map {candidate.map_id}",
            )
        zero_field2 = [
            record.id
            for record in (chunks.get(i) for i in candidate.chunk_ids)
            if record.uint("field2") == 0
        ]
        if zero_field2:
            check.fail(
                "chunk-field2-zero",
                f"DungeonMapChunk row(s) {_join(zero_field2[:8], '...')} declare field2 0, "
                "which mod-content-manager rejects for every row",
            )

    # ---- transform ---------------------------------------------------------
    # WDM supplying no transform is the ordinary case for a native instance map
    # and is not a defect: the semantic projection omits the key and
    # mod-content-manager then requests, leases and composes no transform row.
    # What is checked here is only the integrity of a transform that *is* there.
    # A floorless map is already reported above, so repeating the same root cause
    # here would only add a second, downstream code.
    if floorless or not candidate.transform_ids:
        pass
    elif len(candidate.transform_ids) > 1:
        check.fail(
            "ambiguous-transform",
            "ambiguous: WorldMapTransforms "
            + ", ".join(map(str, candidate.transform_ids))
            + f" all name map {candidate.map_id}; a package declares one transform per map",
        )
    else:
        identifier = candidate.transform_ids[0]
        if stock.world_map_transforms_status(identifier) == "mutated":
            check.fail(
                "stock-mutation-required",
                f"WorldMapTransforms {identifier} is a stock row that WDM mutates",
            )
        elif not candidate.transform_additive[0]:
            check.fail(
                "stock-transform",
                f"WorldMapTransforms {identifier} is a stock row; the client already has "
                "this transform and there is nothing additive to ship",
            )
        transform = transforms.get(identifier)
        if transform.uint("NewMapID") == 0:
            check.fail(
                "transform-new-map-zero",
                f"WorldMapTransforms {identifier} has NewMapID 0, which "
                "mod-content-manager rejects for every row",
            )
        if transform.uint("NewDungeonMapID") not in set(candidate.floor_ids):
            check.fail(
                "transform-target-not-a-floor",
                f"WorldMapTransforms {identifier} points NewDungeonMapID "
                f"{transform.uint('NewDungeonMapID')} at a row that is not a floor of "
                f"map {candidate.map_id}",
            )

    _finish(candidate, check)


def _finish(candidate: Candidate, check: _Check) -> None:
    """Record the verdict.  No reason code means SAFE; any code means UNSAFE."""
    candidate.reason_codes = sorted(check.codes)
    candidate.findings = check.findings
    unknown = check.codes - UNSAFE_REASONS
    if unknown:
        raise AssertionError(
            f"{candidate.internal_name} carries undeclared reason code(s) "
            f"{sorted(unknown)}; UNSAFE_REASONS is the closed set"
        )
    candidate.classification = UNSAFE if check.codes else SAFE


def _join(values: Sequence[int], ellipsis: str = "") -> str:
    text = ", ".join(str(value) for value in values)
    return f"{text}{ellipsis}" if ellipsis and len(values) > 8 else text
