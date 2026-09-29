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
    "REVIEW",
    "UNSAFE",
    "Candidate",
    "Discovery",
    "discover",
    "artwork_files",
]

SAFE = "SAFE"
REVIEW = "REVIEW"
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
    artwork_alias: Optional[str] = None
    reason_codes: List[str] = field(default_factory=list)
    world_map_area_ids: List[int] = field(default_factory=list)
    world_map_area_additive: List[bool] = field(default_factory=list)
    floor_ids: List[int] = field(default_factory=list)
    floor_additive: List[bool] = field(default_factory=list)
    chunk_ids: List[int] = field(default_factory=list)
    chunk_additive: List[bool] = field(default_factory=list)
    transform_ids: List[int] = field(default_factory=list)
    transform_additive: List[bool] = field(default_factory=list)
    classification: str = REVIEW
    findings: List[str] = field(default_factory=list)

    @property
    def package_key(self) -> str:
        return paths.package_key(self.slug)

    @property
    def artwork_targets(self) -> List[str]:
        prefix = f"Interface/WorldMap/{self.internal_name}/"
        return [prefix + name for name in self.blps]

    def to_json(self) -> Dict[str, object]:
        return {
            "internalName": self.internal_name,
            "title": self.title,
            "slug": self.slug,
            "package": self.package_key,
            "mapId": self.map_id,
            "artworkDirectory": self.artwork_dir,
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
            "artworkNameAlias": self.artwork_alias,
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

    def by_classification(self, level: str) -> List[Candidate]:
        return [item for item in self.candidates if item.classification == level]

    def counts(self) -> Dict[str, int]:
        return {
            "candidates": len(self.candidates),
            SAFE: len(self.by_classification(SAFE)),
            REVIEW: len(self.by_classification(REVIEW)),
            UNSAFE: len(self.by_classification(UNSAFE)),
        }


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def _load_tables(wdm_dbc: Path) -> Dict[str, DbcFile]:
    return {
        table: parse_file(wdm_dbc / f"{table}.dbc", table)
        for table in ("DungeonMap", "DungeonMapChunk", "WorldMapArea", "WorldMapTransforms")
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

    TABLES = ("DungeonMap", "DungeonMapChunk", "WorldMapArea", "WorldMapTransforms")

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
            for table in StockView.TABLES
        }
    )
    view.attach_wdm(
        {
            table: parse_file(wdm_dbc / f"{table}.dbc", table)
            for table in StockView.TABLES
        }
    )
    return view


def stock_mutation_records(
    stock: "StockView", tables: Dict[str, DbcFile], wdm_dbc: Path
) -> List[Dict[str, object]]:
    """Every place WDM changes or drops a row the stock client already has."""
    out: List[Dict[str, object]] = []
    for table in StockView.TABLES:
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
        directory = artwork_dirs.get(name)
        candidate = Candidate(
            internal_name=name,
            map_id=map_id,
            slug=meta.get("slug") or paths.slugify(name),
            title=meta.get("title") or name,
            artwork_dir=f"Interface/WorldMap/{name}",
            blps=artwork_files(directory) if directory else [],
            artwork_entries=_all_entries(directory) if directory else [],
        )
        candidate.world_map_area_ids = [record.id for record in area_rows]
        candidate.world_map_area_additive = [
            record.id not in stock_ids["WorldMapArea"] for record in area_rows
        ]
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
    ]
    floors_without_area = [
        {
            "mapId": map_id,
            "floors": [record.id for record in records],
        }
        for map_id, records in sorted(floors_by_map.items())
        if map_id not in covered_maps
    ]

    for candidate in candidates:
        if not candidate.artwork_entries:
            folded = candidate.internal_name.casefold()
            aliases = [name for name in artwork_dirs if name.casefold() == folded]
            if aliases and aliases[0] != candidate.internal_name:
                candidate.artwork_alias = aliases[0]

    discovery = Discovery(
        candidates=candidates,
        tables=tables,
        unmapped_wdm_only_areas=unmapped,
        floors_without_area=floors_without_area,
        stock_mutations=stock_mutation_records(stock, tables, wdm_dbc),
    )
    for candidate in candidates:
        _classify(candidate, tables, stock)
    return discovery


# ---------------------------------------------------------------------------
# Reason codes
# ---------------------------------------------------------------------------
#
# Every rejection is one of these.  ``UNSAFE`` codes mean the package cannot be
# built without breaking mod-content-manager's append-only contract (an
# existing stock row would have to be replaced, or the client would be handed
# artwork it cannot read).  ``REVIEW`` codes mean WDM's own rows are additive
# and self-consistent but the package cannot be completed from them alone, so a
# human has to decide whether the gap may be closed at all.

# The only two states a package genuinely cannot be built from.  Both mean the
# client would end up holding something WDM's own data contradicts.
UNSAFE_REASONS = frozenset(
    {
        "stock-mutation-required",
        "artwork-not-blp",
    }
)

# Everything else is additive-but-incomplete: WDM's rows are consistent and
# safe to append, they just do not add up to a shippable package.  A human has
# to decide whether the gap may be closed, and how.
REVIEW_REASONS = frozenset(
    {
        "no-world-map-area",
        "ambiguous-world-map-area",
        "no-artwork",
        "artwork-name-mismatch",
        "no-floors",
        "no-chunks",
        "floor-zero",
        "chunk-field2-zero",
        "chunk-floor-reference-unresolvable",
        "no-transform",
        "ambiguous-transform",
        "stock-transform",
        "stock-world-map-area",
        "stock-floor",
        "stock-chunk",
        "transform-new-map-zero",
        "transform-target-not-a-floor",
        "area-floor-reference-unresolvable",
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

    # ---- artwork -----------------------------------------------------------
    if not candidate.artwork_entries:
        match = candidate.artwork_alias
        if match:
            check.fail(
                "artwork-name-mismatch",
                f"WDM Stable draws this map from Interface/WorldMap/{match}/, but the "
                f"WorldMapArea internal_name is {candidate.internal_name!r}; the client "
                "derives the directory from internal_name, and inventing or re-casing "
                "either name would change a client-baked identity",
            )
        else:
            check.fail(
                "no-artwork",
                f"WDM Stable ships no artwork under {candidate.artwork_dir}; the client "
                "draws the map from that directory, so the package would be invisible",
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
        candidate.reason_codes = sorted(check.codes)
        candidate.findings = check.findings
        candidate.classification = (
            UNSAFE
            if check.codes & UNSAFE_REASONS
            else REVIEW
            if check.codes
            else SAFE
        )
        return
    if not candidate.floor_ids:
        check.fail(
            "no-floors",
            f"WDM Stable declares no DungeonMap floor for map {candidate.map_id}; the "
            "instance has no floor geometry to compose",
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
    if not candidate.chunk_ids:
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
    if not candidate.transform_ids:
        check.fail(
            "no-transform",
            "WDM Stable supplies no WorldMapTransforms row for map "
            f"{candidate.map_id}; a mod-content-manager worldMaps[] entry requires "
            "exactly one, and authoring one would invent a client-baked row outside "
            "WDM's fixed ID space",
        )
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

    # ---- area -> floor reference -------------------------------------------
    if len(candidate.world_map_area_ids) == 1 and candidate.floor_ids:
        area = areas.get(candidate.world_map_area_ids[0])
        reference = int(area.value("dungeonMap_id"))
        if reference < 0:
            check.fail(
                "area-floor-reference-unresolvable",
                f"WorldMapArea {area.id} sets dungeonMap_id {reference}, WDM's "
                f"\"not an instance\" sentinel. mod-content-manager treats any non-zero "
                f"dungeonMapId as a reference (it casts to uint32 at ContentPackage.cpp:360, "
                f"so {reference} becomes {reference & 0xFFFFFFFF}) and rejects the package "
                f"unless it names a floor of map {candidate.map_id}; carrying the sentinel "
                "through and dropping the field are not the same row",
            )
        elif reference and reference not in set(candidate.floor_ids):
            owner = floors.by_id[reference].map_id() if reference in floors.by_id else None
            where = (
                f"DungeonMap {reference} belongs to map {owner}"
                if owner is not None
                else f"DungeonMap {reference} does not exist in WDM Stable"
            )
            lease = (
                " and is a stock row, so the fixed-ID allocator will never lease it again"
                if reference in stock.ids["DungeonMap"]
                else ""
            )
            check.fail(
                "area-floor-reference-unresolvable",
                f"WorldMapArea {area.id} references dungeonMap_id {reference}, but {where}"
                f"{lease}; mod-content-manager requires the reference to resolve to a "
                f"floor of map {candidate.map_id}",
            )

    candidate.reason_codes = sorted(check.codes)
    candidate.findings = check.findings
    candidate.classification = (
        UNSAFE
        if check.codes & UNSAFE_REASONS
        else REVIEW
        if check.codes
        else SAFE
    )


def _join(values: Sequence[int], ellipsis: str = "") -> str:
    text = ", ".join(str(value) for value in values)
    return f"{text}{ellipsis}" if ellipsis and len(values) > 8 else text
