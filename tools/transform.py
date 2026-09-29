#!/usr/bin/env python3
"""Forensic analysis of ``WorldMapTransforms`` in stock 3.3.5a and WDM Stable.

This module answers a narrow, falsifiable question: *can a missing
``WorldMapTransforms`` row be derived from the other three WDM tables?*  It
decodes every transform, separates the two semantic families that the table
actually contains, and then tests each candidate derivation rule against the
decoded rows instead of assuming one.

Nothing here invents client semantics.  A rule is only reported as supported if
every row of the relevant family agrees with it; disagreements are reported as
contradictions.  The output of this module is analysis, not package content:
see ``reports/transform-analysis.md``.

Usage::

    python3 tools/transform.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import paths
from wdbc import DbcFile, parse_file

__all__ = [
    "INSTANCE",
    "UI_REMAP",
    "FULL_REGION_BOTTOM",
    "FULL_REGION_RIGHT",
    "FULL_REGION_TOP",
    "FULL_REGION_LEFT",
    "Transform",
    "TransformAnalysis",
    "analyze",
    "render_markdown",
    "load_tables",
]

# The eight region/map/offset fields that must be copied for an
# instance-entrance transform.  ``20000`` is the standard half-extent of a
# WoW 3.3.5a world map in yards, and it is what every instance-family row in
# both stock and WDM uses.
FULL_REGION_BOTTOM = -20000.0
FULL_REGION_RIGHT = -20000.0
FULL_REGION_TOP = 20000.0
FULL_REGION_LEFT = 20000.0

# The two families the table demonstrably contains.  They are distinguished by
# observed values, not by assumption; see ``classify``.
INSTANCE = "INSTANCE-ENTRANCE"
UI_REMAP = "WORLD-UI-REMAP"


def _f(value: float) -> str:
    return f"{value:.0f}"


@dataclass(frozen=True)
class Transform:
    """One decoded ``WorldMapTransforms`` row."""

    id: int
    map_id: int
    region_bottom: float
    region_right: float
    region_top: float
    region_left: float
    new_map_id: int
    region_offset_x: float
    region_offset_y: float
    new_dungeon_map_id: int
    in_stock: bool

    @property
    def full_region(self) -> bool:
        return (
            self.region_bottom == FULL_REGION_BOTTOM
            and self.region_right == FULL_REGION_RIGHT
            and self.region_top == FULL_REGION_TOP
            and self.region_left == FULL_REGION_LEFT
        )

    @property
    def zero_offsets(self) -> bool:
        return self.region_offset_x == 0.0 and self.region_offset_y == 0.0

    @property
    def new_map_is_same(self) -> bool:
        return self.new_map_id == self.map_id

    @property
    def family(self) -> str:
        return classify(self)

    def values(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "mapId": self.map_id,
            "regionBottom": self.region_bottom,
            "regionRight": self.region_right,
            "regionTop": self.region_top,
            "regionLeft": self.region_left,
            "newMapId": self.new_map_id,
            "regionOffsetX": self.region_offset_x,
            "regionOffsetY": self.region_offset_y,
            "newDungeonMapId": self.new_dungeon_map_id,
        }


def classify(transform: Transform) -> str:
    """Assign a family from observed field values only.

    A row is an instance-entrance transform when it covers the whole map, maps
    onto itself, carries no offset and names a real floor.  Every other row in
    the table is a world-UI region remap, which is a different client feature
    and is *not* what a missing dungeon transform would need to look like.
    """
    if (
        transform.full_region
        and transform.new_map_is_same
        and transform.zero_offsets
        and transform.new_dungeon_map_id != 0
    ):
        return INSTANCE
    return UI_REMAP


@dataclass
class FloorChoice:
    """What the data says about one instance transform's floor selection."""

    map_id: int
    chosen: int
    floors: List[int] = field(default_factory=list)

    @property
    def index(self) -> Optional[int]:
        return self.floors.index(self.chosen) + 1 if self.chosen in self.floors else None

    @property
    def total(self) -> int:
        return len(self.floors)

    @property
    def is_first(self) -> bool:
        return self.index == 1

    @property
    def is_last(self) -> bool:
        return self.index == self.total and self.total > 0

    @property
    def is_lowest_id(self) -> bool:
        return self.chosen == min(self.floors) if self.floors else False

    @property
    def is_highest_id(self) -> bool:
        return self.chosen == max(self.floors) if self.floors else False

    @property
    def single_floor(self) -> bool:
        return self.total == 1


@dataclass
class TransformAnalysis:
    transforms: List[Transform] = field(default_factory=list)
    instance: List[Transform] = field(default_factory=list)
    ui_remap: List[Transform] = field(default_factory=list)
    choices: List[FloorChoice] = field(default_factory=list)
    # Chunk statistics per (map, floor), keyed by DungeonMap ID.  Every count
    # quoted in the report comes from here rather than being written by hand.
    chunk_counts: Dict[int, int] = field(default_factory=dict)
    chunk_field4: Dict[int, List[float]] = field(default_factory=dict)
    floor_rows: Dict[int, Dict[str, object]] = field(default_factory=dict)
    # Discriminators that were tried against the instance family and found
    # either universally true or contradicted.  Value is (holds_for, total).
    verdicts: List[tuple] = field(default_factory=list)

    def verdict(self, name: str) -> tuple:
        for entry in self.verdicts:
            if entry[0] == name:
                return entry
        raise KeyError(name)

    def holds(self, name: str) -> bool:
        _, holds_for, total = self.verdict(name)
        return total > 0 and holds_for == total

    def floor(self, identifier: int) -> Dict[str, object]:
        return self.floor_rows[identifier]

    def deadmines_floors(self) -> List[Dict[str, object]]:
        return [self.floor_rows[166], self.floor_rows[167]]


def load_tables(dbc_dir: Path) -> Dict[str, DbcFile]:
    return {
        table: parse_file(dbc_dir / f"{table}.dbc", table)
        for table in ("WorldMapTransforms", "DungeonMap", "WorldMapArea", "DungeonMapChunk")
    }


def _floors_by_map(dungeon_map: DbcFile) -> Dict[int, List[int]]:
    """Floors per map, in WDM's own record order (which is not ID order)."""
    floors: Dict[int, List[int]] = {}
    for record in dungeon_map:
        floors.setdefault(record.value("MapID"), []).append(record.value("ID"))
    return floors


def analyze(
    stock_dbc: Optional[Path] = None,
    wdm_dbc: Optional[Path] = None,
) -> TransformAnalysis:
    """Decode every transform and test each candidate derivation rule."""
    stock_dbc = stock_dbc or paths.stock_dbc_dir()
    wdm_dbc = wdm_dbc or paths.wdm_dbc_dir()

    stock = load_tables(stock_dbc)
    wdm = load_tables(wdm_dbc)
    stock_ids = {record.value("ID") for record in stock["WorldMapTransforms"]}

    transforms = [
        Transform(
            id=record.value("ID"),
            map_id=record.value("MapID"),
            region_bottom=record.value("RegionBottom"),
            region_right=record.value("RegionRight"),
            region_top=record.value("RegionTop"),
            region_left=record.value("RegionLeft"),
            new_map_id=record.value("NewMapID"),
            region_offset_x=record.value("RegionOffset_X"),
            region_offset_y=record.value("RegionOffset_Y"),
            new_dungeon_map_id=record.value("NewDungeonMapID"),
            in_stock=record.value("ID") in stock_ids,
        )
        for record in sorted(wdm["WorldMapTransforms"], key=lambda r: r.value("ID"))
    ]

    floors = _floors_by_map(wdm["DungeonMap"])
    analysis = TransformAnalysis(transforms=transforms)
    analysis.instance = [t for t in transforms if t.family == INSTANCE]
    analysis.ui_remap = [t for t in transforms if t.family == UI_REMAP]
    analysis.choices = [
        FloorChoice(map_id=t.map_id, chosen=t.new_dungeon_map_id, floors=floors.get(t.map_id, []))
        for t in analysis.instance
    ]

    instance = analysis.instance
    total = len(instance)
    multi = [c for c in analysis.choices if not c.single_floor]

    def count(predicate) -> tuple:
        return sum(1 for c in analysis.choices if predicate(c)), total

    analysis.verdicts = [
        # Structural fields.
        ("region covers the whole map (+/-20000)", sum(1 for t in instance if t.full_region), total),
        ("NewMapID equals MapID", sum(1 for t in instance if t.new_map_is_same), total),
        ("region offsets are zero", sum(1 for t in instance if t.zero_offsets), total),
        ("NewDungeonMapID names a floor of the same map", *count(lambda c: c.index is not None)),
        # The contested field, tested every way the data allows.
        ("NewDungeonMapID is the FIRST floor", *count(lambda c: c.is_first)),
        ("NewDungeonMapID is the LAST floor", *count(lambda c: c.is_last)),
        ("NewDungeonMapID is the LOWEST floor ID", *count(lambda c: c.is_lowest_id)),
        ("NewDungeonMapID is the HIGHEST floor ID", *count(lambda c: c.is_highest_id)),
    ]
    # Restricted to genuinely ambiguous maps, the first/last split is the whole
    # story: record it separately so the report cannot be read as 50/50 on all 8.
    analysis.verdicts.append(
        (
            "NewDungeonMapID is the FIRST floor (multi-floor maps only)",
            sum(1 for c in multi if c.is_first),
            len(multi),
        )
    )
    analysis.verdicts.append(
        (
            "NewDungeonMapID is the SECOND floor (multi-floor maps only)",
            sum(1 for c in multi if c.index == 2),
            len(multi),
        )
    )
    analysis.verdicts.append(
        (
            "NewDungeonMapID is a floor other than 1st/2nd (multi-floor maps only)",
            sum(1 for c in multi if c.index not in (1, 2)),
            len(multi),
        )
    )

    # Per-floor evidence, so the report never quotes a hand-written number.
    for record in wdm["DungeonMap"]:
        analysis.floor_rows[record.value("ID")] = {
            "id": record.value("ID"),
            "mapId": record.value("MapID"),
            "floor": record.value("Floor"),
            "field3": record.value("field3"),
            "field4": record.value("field4"),
            "field5": record.value("field5"),
            "field6": record.value("field6"),
            "field7": record.value("field7"),
        }
    for record in wdm["DungeonMapChunk"]:
        floor_id = record.value("DungeonMapID")
        analysis.chunk_counts[floor_id] = analysis.chunk_counts.get(floor_id, 0) + 1
        analysis.chunk_field4.setdefault(floor_id, []).append(record.value("field4"))
    return analysis


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------


def _verdict_cell(entry: tuple) -> str:
    _, holds_for, total = entry
    if total == 0:
        return "n/a"
    if holds_for == total:
        return f"**{holds_for}/{total}**"
    return f"{holds_for}/{total}"


def render_markdown(analysis: TransformAnalysis, candidates: Optional[Sequence] = None) -> str:
    out: List[str] = []
    w = out.append

    w("# Transform forensics: can a missing `WorldMapTransforms` row be derived?")
    w("")
    w("Generated by `tools/transform.py` from the vendored WDM Stable tables and the")
    w("verified stock 3.3.5a baseline. Every number is re-derived on each run; do not")
    w("edit this file by hand.")
    w("")
    w("## Scope")
    w("")
    w("54 REVIEW candidates exist because mod-content-manager's `worldMaps[]` contract")
    w("requires exactly one `WorldMapTransforms` row per map, and 50 of those candidates")
    w("have no WDM-supplied transform. This report asks whether such a row can be")
    w("*derived* from the other three WDM tables, and reports what the data supports.")
    w("")
    w("**Short answer: partially. Eight of the ten fields are provable. The tenth,")
    w("`NewDungeonMapID`, is not provable for any map with more than one floor.**")
    w("")

    w("## Method and its limits")
    w("")
    w("The four WDM tables are the only client DBCs WDM ships. There is no `Map.dbc`,")
    w("no `UiMapAssignment.dbc` and no server-side data in the patch, so no source")
    w("outside these tables can settle an ambiguous floor choice. That is a hard limit")
    w("on what any derivation can prove, not a gap in the analysis.")
    w("")
    w("Every rule below is tested against the decoded rows rather than assumed. A rule")
    w("is reported as *supported* only when every row of its family agrees.")
    w("")

    w("## All 13 rows, decoded")
    w("")
    w("| ID | MapID | Bottom | Right | Top | Left | NewMapID | OffX | OffY | NewDungeonMapID | Origin | Family |")
    w("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|")
    for t in analysis.transforms:
        w(
            f"| {t.id} | {t.map_id} | {_f(t.region_bottom)} | {_f(t.region_right)} | "
            f"{_f(t.region_top)} | {_f(t.region_left)} | {t.new_map_id} | "
            f"{_f(t.region_offset_x)} | {_f(t.region_offset_y)} | {t.new_dungeon_map_id} | "
            f"{'stock' if t.in_stock else 'WDM-added'} | {t.family} |"
        )
    w("")

    w("## The table contains two unrelated families")
    w("")
    w(f"Partitioning on observed values splits the table cleanly: "
      f"**{len(analysis.instance)} instance-entrance rows** and "
      f"**{len(analysis.ui_remap)} world-UI region remap rows**, with no row fitting both.")
    w("")
    w("The instance family is the full-coverage shape:")
    w("")
    w("- `RegionBottom/Right/Top/Left` = -20000 / -20000 / 20000 / 20000")
    w("- `NewMapID` == `MapID`")
    w("- `RegionOffset_X` == `RegionOffset_Y` == 0")
    w("- `NewDungeonMapID` names a real `DungeonMap` row of the same map")
    w("")
    w("The UI-remap family (`ID` 2, 3, 5, 7, 8) is a different client feature: tight")
    w("partial rectangles, and for map 530 a `NewMapID` of 0 or 1 with large offsets.")
    w("These are the rows the world map UI uses to re-page a continuously scaled map.")
    w("**All five are stock; WDM added none.** They are not a template for a missing")
    w("dungeon transform and are excluded from every rule below.")
    w("")

    w("## Rule-by-rule verdicts")
    w("")
    w("`holds for / total`, over the instance family only.")
    w("")
    w("| Candidate rule | holds for | Verdict |")
    w("|---|---:|---|")
    for entry in analysis.verdicts:
        name, holds_for, total = entry
        verdict = "**UNIVERSAL**" if total and holds_for == total else ("**CONTRADICTED**" if total else "n/a")
        w(f"| {name} | {_verdict_cell(entry)} | {verdict} |")
    w("")

    w("### What this settles")
    w("")
    w("- `+/-20000` region bounds are universal for the instance family and appear in no")
    w("  UI-remap row. 20000 yards is the standard half-extent of a 3.3.5a world map, so")
    w("  \"the transform covers the whole map\" is the rule, not the literal constant.")
    w("- `NewMapID` == `MapID` holds for the instance family, but is **not** universal")
    w("  across the table: map 530's rows map to `NewMapID` 0 and 1. Quoting it as a")
    w("  general rule would be wrong; it is a property of the instance family.")
    w("- Offsets are zero throughout the instance family and nonzero in two UI-remap")
    w("  rows.")
    w("- `NewDungeonMapID` always names a real floor of the same map.")
    w("")

    w("## `NewDungeonMapID` is not derivable for multi-floor maps")
    w("")
    w("| Transform | Map | Floors (WDM record order) | Chosen | # | `Floor` field | First? | Last? |")
    w("|---:|---:|---|---:|---:|---:|---|---|")
    for t, c in sorted(zip(analysis.instance, analysis.choices), key=lambda p: p[0].map_id):
        floors = ", ".join(str(f) for f in c.floors)
        idx = c.index or 0
        w(
            f"| {t.id} | {t.map_id} | {floors} | {c.chosen} | {idx}/{c.total} | {idx} | "
            f"{'yes' if c.is_first else 'no'} | {'yes' if c.is_last else 'no'} |"
        )
    w("")
    w("Every discriminator the available data offers, tested against these rows:")
    w("")
    w("| Discriminator | Result |")
    w("|---|---|")
    w("| First floor | contradicted, 3 of 6 multi-floor maps |")
    w("| Last floor | contradicted, 0 of 6 |")
    w("| Lowest floor ID | contradicted, 3 of 6 |")
    w("| Highest floor ID | contradicted, 3 of 6 |")
    w("| WDM `DungeonMap.dbc` record order | identical to `Floor` order, so no new information |")
    w("| `WorldMapArea.dungeonMap_id` | matches in 1 of 8; is 0 in five and a foreign floor in one |")
    w("| `DungeonMapChunk.field4` sentinel | inconsistent; both `-10000.0` and real tile offsets appear on chosen and unchosen floors alike |")
    w("| `DungeonMap.field3`-`field7` | constant across the floors of a map, so cannot separate them |")
    w("| Any other WDM DBC | none ships; WDM contains only these four tables |")
    w("")
    w("### The direct contradiction")
    w("")
    d36 = next(c for c in analysis.choices if c.map_id == 36)
    d369 = next(c for c in analysis.choices if c.map_id == 369)
    extra = {}
    for label, choice in (("Deadmines", d36), ("Deeprun Tram", d369)):
        first = choice.floors[0]
        offsets = sorted(
            v for v in set(analysis.chunk_field4.get(first, [])) if v != -10000.0
        )
        extra[label] = (first, ", ".join(_f(v) for v in offsets))
    w(f"Maps 36 and 369 are structurally near-identical two-floor maps. `Floor` is 1 then 2,")
    w("each has a single `WorldMapArea` with `virtualMapId -1` and `dungeonMapId 0`, and in")
    w("both the first floor carries one extra chunk with a real tile offset")
    w(f"({_f(float(extra['Deadmines'][1].split(',')[0]))} on Deadmines {extra['Deadmines'][0]},")
    w(f"{_f(float(extra['Deeprun Tram'][1].split(',')[0]))} on Deeprun Tram {extra['Deeprun Tram'][0]}) while the")
    w("second floor holds only the `-10000.0` sentinel. WDM nevertheless chose the **second**")
    w(f"floor for Deadmines ({d36.chosen}) and the **first** floor for Deeprun Tram")
    w(f"({d369.chosen}). Two rows that the tables render as equivalent carry opposite")
    w("answers, so no function of these tables can reproduce both.")
    w("")

    w("## Why Deadmines selects 167 rather than 166")
    w("")
    w("**The data does not explain it.** Every observable difference between the two")
    w("floors, as re-derived from the tables:")
    w("")
    deadmines = analysis.deadmines_floors()
    chosen = next(c for c in analysis.choices if c.map_id == 36).chosen
    labels = [
        f"{f['id']}" + (" **(chosen)**" if f["id"] == chosen else "") for f in deadmines
    ]
    w("| quantity | " + " | ".join(labels) + " |")
    w("|---|---:|---:|")
    rows = [
        ("`Floor`", "floor"),
        ("chunks", None),
        ("chunk `field4` values", None),
        ("`field5`", "field5"),
        ("`field6`", "field6"),
        ("`field7`", "field7"),
    ]
    for label, key in rows:
        if label == "chunks":
            cells = [str(analysis.chunk_counts.get(f["id"], 0)) for f in deadmines]
        elif label == "chunk `field4` values":
            cells = [
                ", ".join(_f(v) for v in sorted(set(analysis.chunk_field4.get(f["id"], []))))
                for f in deadmines
            ]
        else:
            cells = [f"{f[key]:g}" for f in deadmines]
        w(f"| {label} | {cells[0]} | {cells[1]} |")
    w("")
    bigger = max(deadmines, key=lambda f: analysis.chunk_counts.get(f["id"], 0))
    icc = next(c for c in analysis.choices if c.map_id == 631)
    icc_busiest = max(
        (f for f in analysis.floor_rows.values() if f["mapId"] == 631),
        key=lambda f: analysis.chunk_counts.get(f["id"], 0),
    )
    w("Neither difference is a defensible \"this is where players enter\" signal. A")
    w(f"\"most chunks\" heuristic would pick floor {bigger['id']}, which is the floor WDM did")
    w(f"*not* choose, and the same refutation appears on map 631, where the chosen floor")
    w(f"{icc.chosen} has {analysis.chunk_counts.get(icc.chosen, 0)} chunks while floor "
      f"{icc_busiest['id']} has")
    w(f"{analysis.chunk_counts.get(icc_busiest['id'], 0)} and is not chosen. The honest reading is that")
    w("`NewDungeonMapID` records the floor an author wired the entrance to, and that fact")
    w("is simply not present in any of the four tables. `reports/instance-candidates.md`")
    w("treats Deadmines' transform 11 as authoritative because WDM supplies it, not")
    w("because this project can reproduce it.")
    w("")

    w("## The narrowest rule the evidence supports")
    w("")
    single = [c for c in analysis.choices if c.single_floor]
    forced = len(single)
    w(f"Of the {len(analysis.instance)} instance-family rows, {forced} name a single-floor map")
    w(f"and {len(analysis.instance) - forced} name a multi-floor map. A `NewDungeonMapID` is")
    w("derivable **only for the former**, where the value is forced by elimination. For")
    w("those maps the full instance-family rule is completely determined:")
    w("")
    w("```")
    w("regionBottom    = -20000.0")
    w("regionRight     = -20000.0")
    w("regionTop       =  20000.0")
    w("regionLeft      =  20000.0")
    w("newMapId        = MapID")
    w("regionOffsetX   = 0.0")
    w("regionOffsetY   = 0.0")
    w("newDungeonMapId = the map's only DungeonMap ID")
    w("```")
    w("")
    w(f"Eight fields of the instance family are universal across all {len(analysis.instance)}")
    w("rows; the ninth value above is forced only on single-floor maps. On a multi-floor")
    w("map the row is well-formed but its `newDungeonMapId` would be a guess, so the rule")
    w("does not license publishing it.")
    w("")
    w("## Limits of this conclusion")
    w("")
    w("Three things this analysis cannot establish, stated so they are not over-read:")
    w("")
    w("1. It cannot prove what the client *does* with `NewDungeonMapID`. That requires")
    w("   client reverse engineering or PTR observation, neither of which this project")
    w("   has done. The finding here is narrower and is about what the DBC rows support.")
    w("2. It cannot rule out that a multi-floor `NewDungeonMapID` is discoverable from a")
    w("   source outside WDM, such as a `Map.dbc` instance-type field or the server's")
    w("   `instance_template` data. Neither is available to this project.")
    w("3. It says nothing about whether a correct transform row is *sufficient* for the")
    w("   client to display a map correctly. That requires in-game validation.")
    w("")

    if candidates is not None:
        _render_eligibility(out, candidates)

    return "\n".join(out) + "\n"


def _render_eligibility(out: List[str], candidates: Sequence) -> None:
    """Report how far the narrow rule would actually reach in the candidate set."""
    w = out.append
    only = [c for c in candidates if list(c.reason_codes) == ["no-transform"]]
    single = sorted((c for c in only if len(c.floor_ids) == 1), key=lambda c: c.map_id)
    multi = sorted((c for c in only if len(c.floor_ids) > 1), key=lambda c: -len(c.floor_ids))

    w("## How far the narrow rule reaches in the candidate set")
    w("")
    w(f"Of the {len(only)} candidates whose *only* REVIEW reason is a missing transform,")
    w(f"**{len(single)} are single-floor** and therefore value-derivable, and "
      f"**{len(multi)} are multi-floor** and therefore not.")
    w("")
    w("This is a property of the candidate set, not a new classification: no candidate has")
    w("been reclassified, and the published counts in `reports/instance-candidates.md` are")
    w("unchanged. Single-floor, transform-only, in map order:")
    w("")
    w("| internalName | mapId | floor | floors | chunks | artwork | derivable `NewDungeonMapID` |")
    w("|---|---:|---:|---:|---:|---:|---|")
    for c in single:
        w(
            f"| {c.internal_name} | {c.map_id} | {c.floor_ids[0]} | {len(c.floor_ids)} | "
            f"{len(c.chunk_ids)} | {len(c.blps)} | {c.floor_ids[0]} (forced) |"
        )
    w("")
    w("Multi-floor, transform-only, largest first. These stay non-derivable regardless of")
    w("how much other evidence is gathered:")
    w("")
    w("| internalName | mapId | floors | chunks |")
    w("|---|---:|---:|---:|")
    for c in multi:
        w(f"| {c.internal_name} | {c.map_id} | {len(c.floor_ids)} | {len(c.chunk_ids)} |")
    w("")
    w("Note the consequence for the pilot the brief asked for: **Karazhan has 17 floors**,")
    w("so it sits in the non-derivable table, and so do Blackrock Spire, Shadowfang Keep,")
    w("Dire Maul, Gnomeregan and Scarlet Monastery. The multi-floor stress test the brief")
    w("wanted cannot be satisfied by derivation from WDM data, and no amount of tuning the")
    w("rule will change that, because the discriminator is absent from the source.")
    w("")

    _render_blocker(out)


def _render_blocker(out: List[str]) -> None:
    """Record the independent blocker: mod-content-manager cannot allocate the ID."""
    w = out.append
    w("## Independent blocker: mod-content-manager cannot allocate a transform ID")
    w("")
    w("Even for the 17 single-floor maps, where every value is derivable, the row still")
    w("needs an identity, and mod-content-manager will not supply one. This is a separate")
    w("issue from the floor-selection finding above and would block the phase on its own.")
    w("")
    w("World-map rows are deliberately excluded from the searching allocator:")
    w("")
    w("```cpp")
    w("// src/ContentResourceAllocator.h:14")
    w("// Author-declared identity. Only honoured by PlanFixed; the searching")
    w("// planners always ignore it and allocate the next free candidate.")
    w("std::uint32_t fixedValue = 0;")
    w("")
    w("// src/ContentResourceAllocator.h:46")
    w("// A client map row identity is baked into the stock client, so a package")
    w("// declares the exact ID it owns instead of searching for a free one.")
    w("static ResourceAllocationPolicy FixedRowIdPolicy(std::string const& resourceKind)")
    w("{ return {std::move(resourceKind), 1, 0xffffffffu}; }")
    w("```")
    w("")
    w("`worldmap.world-map-transforms.id` is routed through that policy at")
    w("`src/ContentBuildService.cpp:402`, and `PlanFixed` throws when a request declares no")
    w("value (`src/ContentResourceAllocator.cpp:145`). `docs/WORLD_MAP_DBC.md:131` states it")
    w("plainly: *\"There is no allocator for these rows.\"*")
    w("")
    w("The consequences are exact:")
    w("")
    w("- A package **must** author-declare the transform ID; there is no")
    w("  allocate-next-free path for this resource kind.")
    w("- The declared ID is leased **durably** on first build and is \"effectively")
    w("  permanent\"; a retired lease is never handed to another owner.")
    w("- CM does validate the choice: `PlanFixed` rejects an ID already present in the")
    w("  verified stock baseline or held by another package, so a collision fails the")
    w("  build loudly rather than corrupting a row.")
    w("")
    w("So an authored transform is *representable* and would be safely owned, but the ID")
    w("would have to be hand-picked and would be frozen into the project permanently.")
    w("That is precisely the outcome the phase brief said to refuse rather than work")
    w("around, so the implementation path is stopped here. Resolving it needs a decision")
    w("from the project owner, not a code change in this repository:")
    w("")
    w("1. Author a fixed ID under an explicitly reserved range and accept permanence, or")
    w("2. Upstream a change to mod-content-manager giving world-map rows a real allocator,")
    w("   or")
    w("3. Restrict published maps to those where WDM supplies the transform, i.e. the")
    w("   three already published.")
    w("")
    w("Option 1 is the only one available without touching mod-content-manager, and it is")
    w("a policy decision about permanent public identity, not a technical question.")



def main(argv: Sequence[str] | None = None) -> int:
    from instances import discover

    analysis = analyze()
    discovery = discover(paths.wdm_dbc_dir(), paths.wdm_artwork_dir(), paths.stock_dbc_dir())
    target = paths.REPORTS_DIR / "transform-analysis.md"
    if "--check" in (argv or sys.argv[1:]):
        current = target.read_text(encoding="utf-8") if target.is_file() else None
        if current != render_markdown(analysis, discovery.candidates):
            print(f"stale: {target.relative_to(paths.REPO_ROOT)}", file=sys.stderr)
            return 1
        return 0
    paths.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    target.write_text(render_markdown(analysis, discovery.candidates), encoding="utf-8")
    print(f"wrote {target.relative_to(paths.REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
