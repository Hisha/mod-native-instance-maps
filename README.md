# mod-native-instance-maps

Native pre-Cataclysm instance maps for AzerothCore, delivered as
[mod-content-manager](https://github.com/) packages.

This repository is **not** a DBC patcher and **not** a runtime module. It reads
the vendored [WDM-patch](https://github.com/Trimitor/WDM-patch) tables, decides
which instance maps can be contributed safely, and emits one
`mod-content-manager` manifest (and EPF) per accepted map. Composing the four
world-map DBCs is `mod-content-manager`'s job, not this repository's.

## What ships today

Three packages, all validated against `mod-content-manager`'s own
`ContentPackage::Validate()` and `StageInto()`:

| Package | Map | Area | Floors | Chunks | Tiles |
|---|---:|---|---:|---:|---:|
| `mod-native-instance-maps.deeprun-tram` | 369 | `DeeprunTram` | 2 | 7 | 24 |
| `mod-native-instance-maps.temple-of-atal-hakkar` | 109 | `TheTempleOfAtalHakkar` | 3 | 75 | 36 |
| `mod-native-instance-maps.the-deadmines` | 36 | `TheDeadmines` | 2 | 29 | 24 |

The other 55 discovered maps are deliberately **not** shipped. See
[reports/instance-candidates.md](reports/instance-candidates.md) for the
per-map verdict and reasoning; [reports/wdm-stable-audit.md](reports/wdm-stable-audit.md)
records the stock-versus-WDM forensics, and
[reports/transform-analysis.md](reports/transform-analysis.md) records what can and
cannot be derived about a missing `WorldMapTransforms` row.

## Quick start

```bash
make            # regenerate reports, manifests and EPFs, then run the tests
make check      # the above, plus validation against mod-content-manager
make verify     # CI gate: fail if any committed artifact is out of date
```

Individual steps:

```bash
python3 tools/report.py            # reports/
python3 tools/package.py           # content/ manifests + dist/ EPFs
python3 tests/run_tests.py         # 54 tests, stdlib only
python3 tests/validate_epfs.py     # needs a mod-content-manager checkout
```

External locations are resolved by `tools/paths.py` and can be overridden:

| Variable | Default | Used for |
|---|---|---|
| `MOD_NATIVE_INSTANCE_MAPS_STOCK_DBC` | `/home/smithkt/git/WDM-patch/wdm-stock-dbc` | stock 3.3.5a build-12340 baseline |
| `MOD_CONTENT_MANAGER_DIR` | `/home/smithkt/git/mod-content-manager` | validation harness and golden fixture |
| `WDM_PATCH_DIR` | `/home/smithkt/git/WDM-patch` | WDM's own minimal-Deadmines byte oracle |

Only `make check` and part of the test suite need these; report and manifest
generation work from the vendored tree alone.

## How a map becomes a package

```
upstream/WDM-patch/Stable/enUS/DBFilesClient/*.dbc
        │  tools/wdbc.py        strict WDBC reader
        ▼
   DbcFile  (records keep WDM's declaration order; raw bytes retained)
        │  tools/instances.py   group by WorldMapArea.internalName
        ▼
   Candidate  ── classify ──▶ SAFE / REVIEW / UNSAFE
        │  tools/transform.py   decode + test transform rules (analysis only)
        │  tools/semantic.py    project rows onto manifest keys
        ▼
   worldMaps[] declaration
        │  tools/package.py     write manifest.json, assemble the EPF
        ▼
content/<slug>/manifest.json  +  dist/<package>.epf
        │  tests/validate_epfs.py
        ▼
mod-content-manager  ──▶ append-only DBC composition
```

Nothing in that chain allocates an ID, renumbers a row, sorts a chunk list, or
drops a record. Those are exactly the operations that would make a package
wrong, and each one is pinned by a test.

### SAFE / REVIEW / UNSAFE

The three levels answer "can this ship?", not "is this data good?".

- **SAFE** — WDM supplies every row the map needs, all of them are additive
  against the verified stock baseline, every reference resolves inside the
  package, and the artwork directory the client derives from `internalName`
  exists. Shipped.
- **REVIEW** — WDM's rows are additive and self-consistent, but do not add up to
  a shippable package. Usually a required `WorldMapTransforms` row is absent:
  `mod-content-manager` requires exactly one per `worldMaps[]` entry, and
  authoring one would invent a client-baked row outside WDM's fixed ID space.
  A human decides whether the gap may be closed; the tool does not.
- **UNSAFE** — building it would contradict WDM's own data, because it depends
  on a stock row that WDM mutates or deletes. Not publishable.

Only one map is UNSAFE (`WailingCaverns`, which needs WDM's rewritten
`DungeonMap 28` and its two deleted chunk rows). The 54 REVIEW maps are blocked
on schema expressiveness, not on data quality.

## WDM-supplied versus derived transforms

A `WorldMapTransforms` row tells the client that a world map's region resolves
to an instance floor. `mod-content-manager` requires one per `worldMaps[]`
entry, and WDM supplies only four: transforms 11, 12, 13 and 14, covering
exactly the maps WDM itself had to fix. That is why 50 candidates are REVIEW.

**A derived transform is not the same thing as a WDM transform.** A WDM
transform is upstream data with an upstream ID and is treated as authoritative
throughout this repository. A derived transform would be data *this project
authors*, carrying an ID this project chooses. The two are never mixed, and no
derived transform is published today.

### What the evidence supports

`tools/transform.py` decodes all 13 rows in stock and WDM and tests each
candidate rule against them rather than assuming one. Full results, including
every discriminator that was tried and refuted, are in
[reports/transform-analysis.md](reports/transform-analysis.md).

The table splits cleanly into two unrelated families: 8 *instance-entrance*
rows (full `+/-20000` region, `NewMapID == MapID`, zero offsets, a real floor
in `NewDungeonMapID`) and 5 *world-UI region remap* rows, which are a different
client feature and are all stock. WDM added no UI-remap rows.

Within the instance family, **four rules are universal across all 8 rows**:

```
regionBottom/Right/Top/Left = -20000 / -20000 / 20000 / 20000
newMapId        = MapID
regionOffsetX   = 0.0
regionOffsetY   = 0.0
```

Those fields would be *copied from observed WDM rows*, not invented. The
remaining field, `NewDungeonMapID`, **cannot be derived** for any map with more
than one floor. It is not the first floor (3 of 6), not the last (0 of 6), not
the lowest or highest ID, and not recoverable from `DungeonMap.dbc` record
order, `WorldMapArea.dungeonMap_id`, chunk offsets, or the `DungeonMap` field
columns, which are constant across a map's floors. WDM ships no other client
DBC that could settle it.

The sharpest evidence is a direct contradiction. Deadmines (map 36) and Deeprun
Tram (map 369) are both two-floor maps that the tables render as equivalent,
and WDM chose the **second** floor for one (167) and the **first** for the
other (741). No function of these tables reproduces both. `NewDungeonMapID`
records the floor an author wired the entrance to, and that fact is not in the
data — which is also why this repository does not claim to reproduce Deadmines'
transform 11. It uses it because WDM supplies it.

The narrowest rule the evidence supports is therefore single-floor maps only,
where `NewDungeonMapID` is forced by elimination. Of the 35 candidates whose
only REVIEW reason is a missing transform, **17 are single-floor** and
value-derivable; 18 are multi-floor and are not. Karazhan, the brief's preferred
stress test, has 17 floors and falls in the non-derivable group.

### Why nothing was published anyway

`NewDungeonMapID` is only half the problem. The row also needs an identity, and
`mod-content-manager` will not supply one. `worldmap.world-map-transforms.id`
is routed through `ContentResourceAllocator::PlanFixed()`, which throws when a
request declares no value and never searches for a free candidate
(`src/ContentResourceAllocator.h:14`, `:46`; `src/ContentResourceAllocator.cpp:145`;
used at `src/ContentBuildService.cpp:402`). `docs/WORLD_MAP_DBC.md:131` puts it
plainly: *"There is no allocator for these rows."*

An authored transform is therefore representable and would be safely owned —
`PlanFixed` rejects an ID already in the stock baseline or leased by another
package, so a collision fails loudly — but the ID must be hand-picked and is
leased durably, making it effectively permanent. Freezing permanent public
identities by hand is a project-owner decision, not something the tooling
should decide silently, so the derived-transform path is stopped rather than
worked around. Resolving it means one of:

1. reserve a fixed ID range for authored transforms and accept permanence,
2. upstream a real allocator for world-map rows into `mod-content-manager`, or
3. keep the published set limited to maps WDM already supplies a transform for.

**No derived-transform map is in-game proven, because none have been published.**
Nothing in this repository should be read as evidence that a derived transform
would work on PTR.

## Hard constraints this repository honours

1. **Append-only.** `mod-content-manager` owns composition. Its composer
   refuses any declared ID already present in the verified stock baseline, so
   a package can only ever *add* rows. WDM's mutations of stock rows
   (`DungeonMap 28`, `WorldMapArea 609`, the deletion of `DungeonMapChunk`
   1237/1238) are therefore reported, never shipped.
2. **Fixed IDs.** Manifests carry WDM's own IDs verbatim. Nothing is renumbered
   and no WDM row is renumbered to make a package fit.
3. **Order is data.** `DungeonMapChunk` order is preserved exactly as WDM
   declares it. Deadmines interleaves floors 166 and 167 and is not ID-sorted;
   sorting or grouping by floor produces a different, wrong DBC. Two tests
   pin this against both the golden manifest and WDM's own shipped bytes.
4. **No DBCs in packages.** A package ships artwork and a manifest. The four
   world-map DBCs are composed at build time by `mod-content-manager`; shipping
   one would be a competing composer by the back door.
5. **Deterministic output.** Manifests are canonical JSON; EPFs are
   uncompressed ZIPs with `manifest.json` first, artwork in manifest order, and
   a fixed 1980 timestamp. Identical inputs produce identical bytes.
6. **Upstream is immutable.** `upstream/` is vendored, checksummed against
   `upstream/WDM-patch/SHA256SUMS` (17,072 entries), and never edited.
7. **Artwork paths are generated, not typed.** Targets are always
   `Interface/WorldMap/<internalName>/<leaf>`, the directory the client derives
   from the `WorldMapArea` row. `mod-content-manager` rejects anything else.

## Layout

```
content/<slug>/manifest.json   committed, reviewed as a diff
content/titles.json            display names and package slugs
reports/                       generated audit + candidate inventory
dist/*.epf                     build products (gitignored)
tools/wdbc.py                  strict WDBC reader
tools/forensics.py             stock-versus-WDM comparison
tools/instances.py             candidate discovery and classification
tools/semantic.py              DBC rows -> mod-content-manager manifest keys
tools/report.py                report generation
tools/package.py               manifest + EPF generation
tests/run_tests.py             the suite
tests/validate_epf.cpp         harness: runs EPFs through ContentPackage
tests/validate_epfs.py         builds and runs the harness
upstream/WDM-patch/            vendored source data (immutable)
```

## Testing

`tests/run_tests.py` is stdlib-only and covers the parts where a silent bug
would be invisible in review:

- **Parser** — magic, `field_count`, `record_size`, truncation, trailing bytes,
  zero IDs, **duplicate IDs**, string offsets (out of range, unterminated,
  offset 0), float32 exactness, signed-field decoding, record order, raw-byte
  preservation.
- **Classification** — reason codes are a closed set and classification follows
  from them; every candidate carries a level and a reason; no SAFE
  candidate depends on a mutated stock row, no SAFE row is non-additive, no map
  lacking a transform is ever SAFE.
- **Semantics** — Deadmines equals the `mod-content-manager` golden fixture;
  chunk order matches both the fixture and WDM's shipped DBC; floors interleave
  across chunk rows; fixed IDs survive; every declared value equals its source
  row; the digest is stable and content-sensitive.
- **Packages** — committed manifests equal regenerated manifests; no non-SAFE
  candidate has one; schema and required keys; artwork targets sit under the
  declared directory; **path traversal** is rejected; targets are unique and
  `.dbc`-free; `dbcRows`/server keys are absent.
- **EPFs** — `manifest.json` first; stored entries with a fixed timestamp;
  byte-reproducible; member order follows manifest order; payloads equal the
  WDM artwork; no DBC.

Run one group with `python3 tests/run_tests.py TestParser` or `-k golden`.

`tests/validate_epfs.py` is the one step that compiles C++. It builds a
throwaway binary from the `mod-content-manager` sources (read-only) and runs
every EPF through the real `ContentPackage::Validate()`, then `StageInto()` a
scratch workspace to confirm the artwork lands exactly where the manifest says,
that no `DBFilesClient` tree is written, and that re-staging is refused.

## Known limitations

- **54 maps are withheld**, mostly because WDM ships no `WorldMapTransforms`
  row for them and `mod-content-manager` mandates one per map. Closing that gap
  is a policy decision, not a code change.
- **`dungeonMapId = -1`** is WDM's "not an instance" sentinel, used by
  `BlackTemple` and `SunwellPlateau`. `mod-content-manager` treats any
  non-zero `dungeonMapId` as a reference and rejects the package, so those maps
  cannot be expressed without changing the value.
- **`AhnQiraj`** (map 531) points `WorldMapArea 766` at `DungeonMap 2`, which is
  a stock row belonging to map 574. The reference cannot resolve, and the ID is
  not re-leasable.
- **Two WDM casing quirks** — `BlackfathomDeeps`/`BlackFathomDeeps` and
  `MagtheridonsLair`/`Magtheridonslair`. The client derives the artwork
  directory from `internalName`, so the declared name and the shipped directory
  disagree. Not corrected here; correcting either side would change a
  client-baked identity.
- **Floors with no `WorldMapArea`** (22 maps, the stock raid floors) have
  geometry but no map identity, so they are not candidates at all. Tabulated in
  the audit report.
- **Build 12340 only.** No post-Cataclysm `Map.dbc`/`MapArea` support exists in
  `mod-content-manager`, so none is attempted here.
- **`enUS` is representative.** All WDM locales ship byte-identical
  `DBFilesClient` tables; the artwork is taken from `enUS`.

## Provenance

Original map data and artwork come from WDM-patch by Trimitor, vendored under
`upstream/WDM-patch/` at revision
`5e7e9d1957211f40c9636a9f417901d153b40d4d`. See
[upstream/WDM-patch/SOURCE.md](upstream/WDM-patch/SOURCE.md) and
[THIRD_PARTY.md](THIRD_PARTY.md). This repository claims no authorship over
that data.

## License

See [LICENSE](LICENSE).
