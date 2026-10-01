# mod-native-instance-maps

Native pre-Cataclysm instance maps for AzerothCore, delivered as
[mod-content-manager](https://github.com/) packages.

This repository is **not** a DBC patcher and **not** a runtime module. It reads
the vendored [WDM-patch](https://github.com/Trimitor/WDM-patch) tables, decides
which instance maps can be contributed safely, and emits one
`mod-content-manager` manifest (and EPF) per accepted map. Composing the four
world-map DBCs is `mod-content-manager`'s job, not this repository's.

## What ships today

**43 packages, all validated against `mod-content-manager`'s real pipeline** —
`ContentPackage::Validate()`, `StageInto()`, `WorldMapDbcComposer`
`AppendRequests`/`Compose`/`Stage` against the verified stock baseline,
`ContentFrameXml::ComposeLua`/`ComposeToc`/`Stage`, and
`ContentServerBundle::VerifyParity()`. All 43 also compose together into one
`dist/mod-native-instance-maps.epf`.

| Package | Map | Area | Floors | Chunks | Transform | Tiles | Floor labels |
|---|---:|---|---:|---:|---|---:|---|
| `mod-native-instance-maps.ahnqiraj` | 531 | `AhnQiraj` | 3 | 50 | WDM 13 | 36 | 11 locales |
| `mod-native-instance-maps.auchenai-crypts` | 558 | `AuchenaiCrypts` | 2 | 14 | none in WDM | 24 | 11 locales |
| `mod-native-instance-maps.black-temple` | 564 | `BlackTemple` | 7 | 40 | none in WDM | 96 | 11 locales |
| `mod-native-instance-maps.blackfathom-deeps` | 48 | `BlackfathomDeeps`<br>(artwork `BlackFathomDeeps`) | 3 | 26 | none in WDM | 36 | 11 locales |
| `mod-native-instance-maps.blackrock-depths` | 230 | `BlackrockDepths` | 2 | 52 | none in WDM | 24 | 11 locales |
| `mod-native-instance-maps.blackrock-spire` | 229 | `BlackrockSpire` | 7 | 75 | none in WDM | 84 | 11 locales |
| `mod-native-instance-maps.blackwing-lair` | 469 | `BlackwingLair` | 4 | 22 | none in WDM | 48 | 11 locales |
| `mod-native-instance-maps.coilfang-reservoir` | 548 | `CoilfangReservoir` | 1 | 12 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.deeprun-tram` | 369 | `DeeprunTram` | 2 | 7 | WDM 12 | 24 | 11 locales |
| `mod-native-instance-maps.dire-maul` | 429 | `DireMaul` | 6 | 73 | none in WDM | 84 | 11 locales |
| `mod-native-instance-maps.gnomeregan` | 90 | `Gnomeregan` | 4 | 79 | none in WDM | 48 | 11 locales |
| `mod-native-instance-maps.gruuls-lair` | 565 | `GruulsLair` | 1 | 4 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.hellfire-ramparts` | 543 | `HellfireRamparts` | 1 | 3 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.karazhan` | 532 | `Karazhan` | 17 | 86 | none in WDM | 204 | 11 locales |
| `mod-native-instance-maps.magisters-terrace` | 585 | `MagistersTerrace` | 2 | 19 | none in WDM | 24 | 11 locales |
| `mod-native-instance-maps.magtheridons-lair` | 544 | `MagtheridonsLair`<br>(artwork `Magtheridonslair`) | 1 | 7 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.mana-tombs` | 557 | `ManaTombs` | 1 | 14 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.maraudon` | 349 | `Maraudon` | 2 | 43 | none in WDM | 24 | 11 locales |
| `mod-native-instance-maps.molten-core` | 409 | `MoltenCore` | 1 | 12 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.onyxias-lair` | 249 | `OnyxiasLair` | 1 | 8 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.ragefire-chasm` | 389 | `Ragefire` | 1 | 6 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.razorfen-downs` | 129 | `RazorfenDowns` | 1 | 11 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.razorfen-kraul` | 47 | `RazorfenKraul` | 1 | 25 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.scarlet-monastery` | 189 | `ScarletMonastery` | 4 | 89 | none in WDM | 48 | 11 locales |
| `mod-native-instance-maps.scholomance` | 289 | `Scholomance` | 4 | 26 | none in WDM | 48 | 11 locales |
| `mod-native-instance-maps.sethekk-halls` | 556 | `SethekkHalls` | 2 | 19 | none in WDM | 24 | 11 locales |
| `mod-native-instance-maps.shadow-labyrinth` | 555 | `ShadowLabyrinth` | 1 | 21 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.shadowfang-keep` | 33 | `ShadowfangKeep` | 7 | 79 | none in WDM | 84 | 11 locales |
| `mod-native-instance-maps.stratholme` | 329 | `Stratholme` | 2 | 80 | none in WDM | 24 | 11 locales |
| `mod-native-instance-maps.sunwell-plateau` | 580 | `SunwellPlateau` | 1 | 2 | none in WDM | 24 | 11 locales |
| `mod-native-instance-maps.tempest-keep` | 550 | `TempestKeep` | 1 | 16 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.temple-of-atal-hakkar` | 109 | `TheTempleOfAtalHakkar` | 3 | 75 | WDM 14 | 36 | 11 locales |
| `mod-native-instance-maps.the-arcatraz` | 552 | `TheArcatraz` | 3 | 21 | none in WDM | 36 | 11 locales |
| `mod-native-instance-maps.the-blood-furnace` | 542 | `TheBloodFurnace` | 1 | 7 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.the-botanica` | 553 | `TheBotanica` | 1 | 6 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.the-deadmines` | 36 | `TheDeadmines` | 2 | 29 | WDM 11 | 24 | 11 locales |
| `mod-native-instance-maps.the-mechanar` | 554 | `TheMechanar` | 2 | 15 | none in WDM | 24 | 11 locales |
| `mod-native-instance-maps.the-shattered-halls` | 540 | `TheShatteredHalls` | 1 | 12 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.the-slave-pens` | 547 | `TheSlavePens` | 1 | 5 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.the-steamvault` | 545 | `TheSteamvault` | 2 | 10 | none in WDM | 24 | 11 locales |
| `mod-native-instance-maps.the-stockade` | 34 | `TheStockade` | 1 | 57 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.the-underbog` | 546 | `TheUnderbog` | 1 | 1 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.uldaman` | 70 | `Uldaman` | 2 | 52 | none in WDM | 24 | 11 locales |

Every map's floors are named in all eleven locales WDM publishes, taken verbatim
from WDM-addons' own `DUNGEON_FLOOR_<INSTANCE><n>` strings. Karazhan's seventeen
read `Servant's Quarters`, `Upper Livery Stables`, `The Banquet Hall` and so on
instead of the stock `Floor 1`…`Floor 17`. See
[Dungeon floor names](#dungeon-floor-names).

Karazhan carries no `WorldMapTransforms` row because WDM has none for it. The
manifest omits the key entirely, so `mod-content-manager` requests no row, leases
no ID, and composes nothing. 39 of the 43 packages take this path; the other four
declare the transform WDM supplies, and the composed `WorldMapTransforms.dbc`
gains exactly those 4 rows over the verified stock file.

Two packages install their artwork under a name WDM does not use on disk. The
client derives the artwork directory from the `WorldMapArea.internal_name` in the
DBC row, and for these two maps WDM's directory is spelled with different
capitals — `BlackFathomDeeps` for `BlackfathomDeeps`, `Magtheridonslair` for
`MagtheridonsLair`. The package installs WDM's bytes at the DBC spelling, which
is the only name the client can ask for. Nothing else about the 1392 tiles changes.

**The backlog is closed.** All 43 SAFE maps are published, listed explicitly in
`content/publish.json`; the other 15 discovered maps are UNSAFE and each carries
the reason codes that rejected it. See
[reports/instance-candidates.md](reports/instance-candidates.md) for the per-map
verdict and reasoning; [reports/wdm-stable-audit.md](reports/wdm-stable-audit.md)
records the stock-versus-WDM forensics, and
[reports/transform-analysis.md](reports/transform-analysis.md) records what can and
cannot be derived about a missing `WorldMapTransforms` row.

## Quick start

```bash
make help
make epf MAP=karazhan   # one approved individual EPF
make epf MAP=all        # all approved individual EPFs
make release            # one combined dist/mod-native-instance-maps.epf
make check              # comprehensive developer verification
```

Every SAFE map has an individual slug, listed in `content/publish.json` — the
`slug` column is the package directory, so `BlackfathomDeeps` is
`blackfathom-deeps` and `MagtheridonsLair` is `magtheridons-lair`. Both
single-map selection and `MAP=all` are resolved through that allowlist;
classification as SAFE alone never makes a map selectable. A bare `make epf`
prints usage instead of choosing a publication scope.

`MAP=all` creates the 43 approved EPFs separately. `make release` instead
creates one ordinary Content Manager package containing those maps and their
resources directly; it does not nest the individual ZIPs. The combined package
is the canonical owner and explicitly migrates retained allocations from the
historical `mod-native-instance-maps.karazhan` and
`mod-deadmines-dungeon-map` packages. Individual-map packages do not declare a
replacement, so installing one later cannot steal allocations back from the
combined package.

Canonical tool equivalents and developer commands:

```bash
python3 tools/report.py            # reports/
python3 tools/package.py --map karazhan
python3 tools/package.py --all-approved
python3 tools/package.py --release
python3 tests/run_tests.py         # project unit/regression suite, stdlib only
python3 tests/validate_epfs.py     # needs a mod-content-manager checkout
make verify                        # CI gate: committed artifacts are current
make clean                         # remove generated dist/*.epf only
```

All WDM and stock build inputs are repository-owned. The only external
integration is `mod-content-manager`, selected explicitly or as a sibling
checkout:

| Variable | Default | Used for |
|---|---|---|
| `MOD_CONTENT_MANAGER_DIR` | sibling `mod-content-manager` checkout | validation harness and golden fixture |

The four stock build-12340 DBCs live under
`upstream/wow-3.3.5a-build-12340/DBFilesClient/`. Every build entry point
verifies their complete `SHA256SUMS` manifest before using them. Deadmines byte
ordering is checked directly against the vendored WDM Stable DBC; no external
WDM checkout or compatibility environment variable is consulted.

## How a map becomes a package

```
upstream/WDM-patch/Stable/enUS/DBFilesClient/*.dbc
        │  tools/wdbc.py        strict WDBC reader
        ▼
   DbcFile  (records keep WDM's declaration order; raw bytes retained)
        │  tools/instances.py   group by WorldMapArea.internalName
        ▼
   Candidate  ── classify ──▶ SAFE / UNSAFE
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

### SAFE / UNSAFE

Two levels answer "can this ship?", not "is this data good?". There is no
third level: a map is either publishable from the vendored source or it is
blocked, and each blocked map carries the reason codes that blocked it.

- **SAFE** — WDM supplies every row the map needs, all of them are additive
  against the verified stock baseline, every reference is preserved as WDM
  wrote it, and the artwork directory the client derives from `internalName`
  exists. A `WorldMapTransforms` row is optional; its absence is not a defect.
- **UNSAFE** — the package would either contradict WDM's own data (it depends on
  a stock row that WDM mutates or deletes) or be built from source that does not
  add up to one. Every rejection names its causes:

| Reason | Meaning |
| --- | --- |
| `no-area` | WDM adds no `WorldMapArea` row, so the map is not addressable. |
| `no-floors` | WDM adds no `DungeonMap` row, so there is no floor to enter. |
| `no-chunks` | WDM adds no `DungeonMapChunk` row, so the floor has no geometry. |
| `stock-world-map-area` | The area is a stock row WDM mutates or deletes. |
| `stock-floor` | A floor is a stock `DungeonMap` row WDM mutates or deletes. |
| `stock-chunk` | A chunk is a stock row WDM mutates or deletes. |
| `stock-transform` | The transform is a stock row WDM mutates. |
| `ambiguous-transform` | The transform names more than one floor choice. |
| `duplicate-artwork-alias` | The artwork directory names a map some other candidate already owns. |
| `no-artwork` | The client would look for artwork WDM does not ship. |
| `stock-mutation-required` | A composite of the `stock-*` causes above. |

The current backlog is 43 SAFE and 15 UNSAFE:

- 11 blocked on `no-floors` — WDM gives them an area and artwork but no
  `DungeonMap` row, so there is nothing to enter. Publishing them would mean
  inventing a floor.
- `Northrend` — every row it needs is a stock row WDM mutates.
- `WailingCaverns` — needs WDM's rewritten `DungeonMap 28` and its two deleted
  chunk rows.
- `BlackFathomDeeps` and `Magtheridonslair` — artwork directories that name a map
  the `BlackfathomDeeps` and `MagtheridonsLair` rows already own. They ship
  inside those two packages instead of as packages of their own.

## Dungeon floor names

The stock client's floor dropdown numbers a map's floors `Floor 1`…`Floor N`.
The client has the names; they are just not where the dropdown looks. WDM-addons
publishes them as ordinary Lua globals, and this project ships them:

    DUNGEON_FLOOR_KARAZHAN1 = "Servant's Quarters";
    DUNGEON_FLOOR_KARAZHAN7 = "Lower Broken Stair";

Those strings are read verbatim from the vendored WDM-addons locale tables and
declared per area as `worldMaps[].areas[].floorNames`, keyed by the same index
the stock dropdown loop produces. Nothing is retyped, translated, or inferred.

**Only one stock function is replaced.** A package declaring floor labels
carries `clientFrameXml` and requests `protected-framexml`. At build time
`mod-content-manager` generates one Lua module that overrides
`WorldMapLevelDropDown_Initialize` and delegates back to the stock function for
any map or locale it has no label for. The stock table of contents travels in the
EPF unmodified, digest-pinned, and exactly one module line is inserted into it.
`GlobalStrings.lua` and `WorldMapFrame.lua` are never read, replaced or
required — see [THIRD_PARTY.md](THIRD_PARTY.md) for the stock file's provenance.

A map whose locale tables WDM does not publish keeps the stock label for that
locale. WDM ships no `itIT` or `ptBR` table, so those two locales keep stock
labels everywhere — that is stock behaviour, not a gap in the import.

## Transforms are optional, and never derived

A `WorldMapTransforms` row tells the client that a world map's region resolves
to an instance floor. `mod-content-manager` treats it as optional source data:
a `worldMaps[]` entry may omit it, and then no row is requested, no ID is leased,
and the composed file is the verified stock file unchanged. WDM supplies only
four such rows — 11, 12, 13 and 14, covering exactly the maps WDM itself had to
fix. Karazhan is not one of them, and now ships anyway.

**A transform this project derives is not the same thing as a WDM transform.**
A WDM transform is upstream data with an upstream ID, carried through verbatim.
A derived transform would be data *this project authors*, carrying an ID this
project chooses, naming a floor the source never designated. The two are never
mixed, and **no transform is ever derived here** — the `transform` key is either
WDM's own row or absent.

### What the evidence shows

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

The remaining field, `NewDungeonMapID`, **cannot be derived** for any map with
more than one floor. It is not the first floor (3 of 6), not the last (0 of 6),
not the lowest or highest ID, and not recoverable from `DungeonMap.dbc` record
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

That refutation is now a statement about what this project *does not do*, rather
than about which maps it can publish. Karazhan has 17 floors and no derivable
default; it ships with no transform at all, because no transform is required for
a row to be complete.

A `NewDungeonMapID` would also need an identity, and `mod-content-manager` will
not supply one. `worldmap.world-map-transforms.id` is routed through
`ContentResourceAllocator::PlanFixed()`, which throws when a request declares no
value and never searches for a free candidate (`src/ContentResourceAllocator.h:14`,
`:46`; `src/ContentResourceAllocator.cpp:145`; used at
`src/ContentBuildService.cpp:402`). `docs/WORLD_MAP_DBC.md:131` puts it plainly:
*"There is no allocator for these rows."* Freezing permanent public identities by
hand is a project-owner decision, not something the tooling should decide
silently.

**No derived transform is in-game proven, because none has been published, and
none will be.** Nothing in this repository should be read as evidence that a
derived transform would work on PTR.

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
4. **References are references.** `WorldMapArea.dungeonMapId` is preserved
   exactly as WDM wrote it, including `0`, `-1`, and a reference to a floor this
   package does not own. It never becomes a request, a lease or a row of its own.
5. **No invented transforms.** A `WorldMapTransforms` row is WDM's or absent.
   `NewDungeonMapID` is never guessed from a floor, and no transform ID is ever
   allocated.
6. **No DBCs in packages.** A package ships artwork and a manifest. The four
   world-map DBCs are composed at build time by `mod-content-manager`; shipping
   one would be a competing composer by the back door.
7. **Deterministic output.** Manifests are canonical JSON; EPFs are
   uncompressed ZIPs with `manifest.json` first, artwork in manifest order, and
   a fixed 1980 timestamp. Identical inputs produce identical bytes.
8. **Upstream is immutable.** `upstream/` is vendored, checksummed against
   `upstream/WDM-patch/SHA256SUMS` (17,072 entries),
   `upstream/WDM-addons/SHA256SUMS` and
   both checksum manifests under `upstream/wow-3.3.5a-build-12340/`, and never
   edited.
9. **Artwork paths are generated, not typed.** Targets are always
   `Interface/WorldMap/<internalName>/<leaf>`, the directory the client derives
   from the `WorldMapArea` row. `mod-content-manager` rejects anything else.
10. **Floor names are WDM's words.** A label is copied verbatim from a vendored
    `DUNGEON_FLOOR_<INSTANCE><n>` global. A locale WDM does not publish gets no
    label, and the stock client text stays. Nothing is translated, abbreviated
    or padded to fill a gap.
11. **One stock function, never the file.** Floor labels replace
    `WorldMapLevelDropDown_Initialize` and nothing else. The stock
    `FrameXML.toc` is shipped unmodified and digest-pinned; the generated module
    is added to it as one line.

## Layout

```
content/<slug>/manifest.json   committed, reviewed as a diff
content/publish.json          the maps that may be generated (publication gate)
content/titles.json           display names and package slugs
reports/                      generated audit + candidate inventory
dist/*.epf                    build products (gitignored)
tools/wdbc.py                 strict WDBC reader
tools/forensics.py            stock-versus-WDM comparison
tools/instances.py            candidate discovery and classification
tools/semantic.py             DBC rows -> mod-content-manager manifest keys
tools/floornames.py           WDM locale tables -> dungeon floor labels
tools/report.py               report generation
tools/package.py              manifest + EPF generation
tests/run_tests.py            the suite
tests/validate_epf.cpp        harness: runs EPFs through the real CM pipeline
tests/validate_epfs.py        builds and runs the harness
upstream/WDM-patch/           vendored source data (immutable)
upstream/WDM-addons/          vendored WDM locale tables (immutable)
upstream/wow-3.3.5a-build-12340/
                             vendored stock FrameXML.toc + four DBCs (immutable)
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
  candidate depends on a mutated stock row and no SAFE row is non-additive; a
  missing transform is never a reason code; publication is a strict subset of
  SAFE.
- **Source provenance** — the vendored WDM tree is pinned to a recorded,
  unmodified upstream revision; all four stock baseline tables are provenance
  recorded and SHA-256 verified; required build logic is rejected if it gains a
  developer-specific absolute path or legacy external-WDM override.
- **Semantics** — Deadmines equals the `mod-content-manager` golden fixture;
  chunk order matches both the fixture and WDM's shipped DBC; floors interleave
  across chunk rows; fixed IDs survive; every declared value equals its source
  row; the digest is stable and content-sensitive.
- **Karazhan source fidelity** — the raw WDM `DungeonMap`, `DungeonMapChunk`,
  `WorldMapArea` and `WorldMapTransforms` rows are compared field for field
  against the generated declaration, the 17/86/1/0/204 counts are re-derived from
  the source tables, the 204 artwork payloads are compared by SHA-256, and no
  transform key or synthesised identity appears anywhere in the manifest.
- **Packages** — committed manifests equal regenerated manifests; no non-SAFE
  candidate has one; the three pre-existing manifests are byte-stable; schema and
  required keys; artwork targets sit under the declared directory; **path
  traversal** is rejected; targets are unique and `.dbc`-free;
  `dbcRows`/server keys are absent.
- **EPFs** — `manifest.json` first; stored entries with a fixed timestamp;
  byte-reproducible; member order follows manifest order; payloads equal the
  WDM artwork; no DBC.
- **Floor names** — the vendored locale tables match their recorded SHA-256s;
  Karazhan resolves to floors 1..17 with no gap in every published locale;
  every emitted label equals the WDM global it came from; unpublished locales
  are absent rather than invented; a level-0 global is skipped, never shifted to
  1; an instance WDM names only as an instance yields no labels; the token fold
  matches the client's upper-case fold and refuses non-ASCII.
- **Stock FrameXML** — the vendored `FrameXML.toc` matches its recorded hash,
  still carries exactly one `## add new modules above here` marker ahead of
  `LocalizationPost.xml`, and the Karazhan manifest pin equals that hash.

Run one group with `python3 tests/run_tests.py TestParser` or `-k golden`.

`tests/validate_epfs.py` is the one step that compiles C++. It builds a
throwaway binary from the `mod-content-manager` sources (read-only) and drives
every EPF through the pipeline the build service uses:

```
Validate -> StageInto -> FrameXml ComposeLua/ComposeToc/Stage
         -> AppendRequests -> PlanFixed -> Compose -> Stage -> VerifyParity
```

against the verified stock 3.3.5a build-12340 baseline. It checks that each
stock row and string byte survives composition untouched, that every appended row
is leased at its declared ID and reads back identically, that no contributed ID
collides with a stock ID, and that the parity artifact verifies. For a package
with no transform it additionally asserts that
`WorldMapTransforms.dbc` composes to the stock file byte for byte, and runs a
counterfactual showing that supplying a transform *would* have produced a
request, a lease and a row — so the zeroes are measured, not unchecked.

For floor labels it additionally asserts that the stock table of contents read
back from the package composes to stock **plus exactly one CRLF-terminated module
line**, that the generated module delegates to `FLOOR_NUMBER` and calls no loader
(`dofile`, `loadfile`, `require`, `LoadAddOn`, `SetAddOn`), that both generated
files stage and read back identically, and that their SHA-256s reach the parity
artifact.

## Known limitations

- **15 maps are withheld**, each with the reason codes that rejected it. Eleven
  have no `DungeonMap` floor rows and no chunk rows in WDM at all, so there is
  nothing to enter; `Expansion01` additionally has two transforms for one map.
  `Northrend` and `WailingCaverns` need stock rows WDM mutates or deletes, which
  an append-only package cannot claim. `BlackFathomDeeps` and `Magtheridonslair`
  are artwork directories that name no map of their own; their tiles ship inside
  the two packages that do. These are source-data gaps, not schema limits.
- **`dungeonMapId = -1`** is WDM's "not an instance" sentinel, used by
  `BlackTemple` and `SunwellPlateau`. It is a reference like any other, so it is
  preserved verbatim and requests nothing. `mod-content-manager` accepts it.
- **`AhnQiraj`** (map 531) points `WorldMapArea 766` at `DungeonMap 2`, a stock
  row belonging to map 574. That reference cannot resolve and the ID is not
  re-leasable, but it is not this package's to resolve: the value is preserved
  exactly and no DungeonMap 2 row is contributed.
- **Two WDM casing quirks are re-cased, one is not.** The client derives the
  artwork directory from `internalName`, and for `BlackfathomDeeps` and
  `MagtheridonsLair` WDM's directory disagrees in letter case, so those two
  packages install WDM's bytes at the DBC spelling. Inside
  `TheTempleOfAtalHakkar`, WDM spells its three floors three different ways; that
  one is left alone, because it already resolves on a case-insensitive client and
  re-casing it would rewrite a released package to fix nothing. A test pins both
  behaviours.
- **Two WDM chunk rows ship nowhere.** 1828 and 1829 belong to map 631 (*Icecrown
  Citadel*), which has a stock area, no WDM area, no WDM floors and no WDM
  artwork, so it is not a candidate. Every other row WDM adds is either shipped or
  held back by a rejected map; `reports/final-report.md` tabulates the split.
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
