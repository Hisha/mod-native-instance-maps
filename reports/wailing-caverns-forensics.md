# Wailing Caverns forensics and stock-mutation design

Investigation only. Nothing in this report is implemented in
`mod-content-manager`, nothing is published, and no stock baseline was
modified. Wailing Caverns remains UNSAFE under the current append-only
contract.

## Sources

- Stock 3.3.5a build-12340 baseline:
  `upstream/wow-3.3.5a-build-12340/DBFilesClient/{DungeonMap,DungeonMapChunk,WorldMapArea,WorldMapTransforms}.dbc`
- WDM Stable (enUS representative tree):
  `upstream/WDM-patch/Stable/enUS/DBFilesClient/`
- WDM artwork: `upstream/WDM-patch/Stable/enUS/Interface/WorldMap/WailingCaverns/`
- Field semantics: build-12340 descriptors in
  `mod-content-manager/src/DbcDescriptor.cpp`; corroborated against the
  wowdev/TrinityCore 3.3.5a DBC structures
  (`DB/DungeonMap`, `DB/DungeonMapChunk`).
- Not available in the workspace: stock `Map.dbc`, stock `AreaTable.dbc`, and
  `WorldMapFrame.lua`. Behaviour that depends on them is marked as requiring a
  live client.

---

## 1. Descriptor field names actually used

The build-12340 descriptors in `mod-content-manager` name words that the
repository cannot prove, so they are deliberately neutral. The published
3.3.5a wowdev/TrinityCore structures give the client-side names. Both are
listed; this report uses the neutral names for byte-exact work and the
published names for interpretation.

`DungeonMap.dbc` — 8 fields, 32-byte records, no strings:

| Word | Descriptor name | Published name | Type |
|---|---|---|---|
| 0 | `ID` | `ID` | uint32 |
| 1 | `MapID` | `MapID` → `Map.dbc/0` | uint32 |
| 2 | `Floor` | `FloorIndex` | uint32 |
| 3 | `field3` | `MinX` | float32 |
| 4 | `field4` | `MaxX` | float32 |
| 5 | `field5` | `MinY` | float32 |
| 6 | `field6` | `MaxY` | float32 |
| 7 | `field7` | `ParentWorldMapID` → `WorldMapArea.dbc/0` | uint32 |

`DungeonMapChunk.dbc` — 5 fields, 20-byte records, no strings:

| Word | Descriptor name | Published name | Type |
|---|---|---|---|
| 0 | `ID` | `ID` | uint32 |
| 1 | `MapID` | `MapID` → `Map.dbc/0` | uint32 |
| 2 | `field2` | `WMOGroupID` → `WMOAreaTable.WMOGroupID` | uint32 |
| 3 | `DungeonMapID` | `DungeonMapID` → `DungeonMap.dbc/0` | uint32 |
| 4 | `field4` | `MinZ` | float32 |

`WorldMapArea.dbc` (DungeonMap 28 is referenced only by chunks, but WMA 749 is
part of the package): `ID`, `map_id`, `area_id`, `internal_name`, `y1`/`y2`/
`x1`/`x2` (`LocLeft`/`LocRight`/`LocTop`/`LocBottom`), `virtual_map_id`
(`DisplayMapID`), `dungeonMap_id` (`DefaultDungeonFloor`), `parentMapID`
(`ParentWorldMapID`).

## 2. `DungeonMap` 28 — complete stock row

```
word           raw         value
ID             1c000000    28
MapID          2b000000    43
Floor          01000000    1
field3/MinX    1779cdc3    -410.9460144042969
field4/MaxX    dbe11444    595.5289916992188
field5/MinY    50bdf1c3    -483.47900390625
field6/MaxY    06813b43    187.50399780273438
field7/Parent  00000000    0
raw record    1c0000002b000000010000001779cdc3dbe1144450bdf1c306813b4300000000
sha256[:16]   4bd70a151146f566
```

## 3. `DungeonMap` 28 — complete WDM row

```
word           raw         value
ID             1c000000    28
MapID          2b000000    43
Floor          01000000    1
field3/MinX    17f9bbc3    -375.9460144042969
field4/MaxX    db210c44    560.5289916992188
field5/MinY    b012cdc3    -410.14599609375
field6/MaxY    852b5643    214.1699981689453
field7/Parent  0b000000    11
raw record    1c0000002b0000000100000017f9bbc3db210c44b012cdc3852b56430b000000
sha256[:16]   71a8e2701b681640
```

WDM **modifies** the stock row in place. The identity fields (`ID`, `MapID`,
`Floor`) are unchanged; only the extent and the parent reference move.

## 4. Exact `DungeonMap` 28 delta

| Field | Stock | WDM | Delta |
|---|---:|---:|---:|
| `field3`/MinX | -410.9460144043 | -375.9460144043 | **+35.0000000000** |
| `field4`/MaxX | 595.5289916992 | 560.5289916992 | **-35.0000000000** |
| `field5`/MinY | -483.4790039062 | -410.1459960938 | **+73.3330078125** |
| `field6`/MaxY | 187.5039978027 | 214.1699981689 | **+26.6660003662** |
| `field7`/Parent | 0 | 11 | **+11** |

Stock extent: 1006.48 × 670.98 (3:2). WDM extent: 936.48 × 624.32 (3:2). WDM
shrinks the footprint to ~93% of stock and re-centres it, preserving the 3:2
aspect. MinX/MaxX move symmetrically by ±35; MinY/MaxY move by +73.333 and
+26.666 (the Y window shifts up and narrows by 46.667).

## 5. `field7` is `ParentWorldMapID`, and 11 is `The Barrens`

This is now proven from data, not assumed:

- WMA 11 = `Barrens` (`map_id` 1, `area_id` 17) in both stock and WDM.
- Wailing Caverns is physically located in the Barrens, so a
  `ParentWorldMapID` of 11 is the containing zone.
- Every one of the 113 WDM-added `DungeonMap` rows sets `field7` to the
  `WorldMapArea` ID of the zone that contains the dungeon, and each of those
  maps also gets its own additive WDM `WorldMapArea` (e.g. map 47 Razorfen
  Kraul → `field7` 11 Barrens, own WMA 761; map 36 Deadmines → `field7` 39
  Westfall, own WMA 756; map 533 Naxxramas → `field7` 488 Dragonblight).
- Stock rows follow the same convention (maps 574/575 → 491 Howling Fjord;
  maps 599/602/603 → 495 The Storm Peaks; maps 631/632/649/650/668 → 492
  Icecrown Glacier; map 624 → 501 Lake Wintergrasp).

So stock `DungeonMap` 28 had `field7 = 0` because stock never associated the
Wailing Caverns floor with a world-map zone. WDM sets it to the Barrens.

## 6. `WorldMapArea` 749 — complete WDM row (stock has none)

```
ID 749, map_id 43, area_id 718 ('WailingCaverns' sub-zone),
internal_name 'WailingCaverns',
y1 0, y2 0, x1 0, x2 0,
virtual_map_id -1, dungeonMap_id 0, parentMapID 0
```

Stock `WorldMapArea` has no row with `map_id = 43` and no row named
`WailingCaverns`, so 749 is genuinely additive and is the only additive row in
the candidate. It does **not** reference floor 28 (`dungeonMap_id = 0`), so the
floor binding is implicit through `Map.dbc` (map 43) and
`DungeonMap.MapID = 43`, not through the WMA.

## 7. WMA 749 has zero `Loc` bounds — why that matters

Roughly 30 of WDM's 51 added WMAs carry all-zero `Loc` bounds (749 among them);
the rest copy their instance extent. A WMA with zero bounds cannot itself drive
scaling, so the client falls back to the `DungeonMap` floor bounds
(`MinX..MaxY`) for the instance map. For Wailing Caverns the only floor is stock
28, which means **the mutated `DungeonMap` 28 bounds are the extent used to draw
WDM's artwork**. That is the strongest static argument that the bounds mutation
is functional rather than cosmetic, not just a tidy-up.

Caveat: this fallback is inferred from the data and the published field
descriptions, not observed. `WorldMapFrame.lua` is not in the workspace.

## 8. Artwork inventory

`Interface/WorldMap/WailingCaverns/` contains exactly 12 BLPs,
`WailingCaverns1_1.blp` … `WailingCaverns1_12.blp` — a single floor (`1`), 12
tiles. 12 tiles is a 4×3 (or 3×4) montage, consistent with the 3:2 extent of
floor 28. The artwork is additive and carries no stock collision.

## 9. Complete reference inventory for `DungeonMap` 28

| Table | Rows referencing floor 28 |
|---|---|
| `DungeonMapChunk` (`DungeonMapID = 28`, `MapID = 43`) | stock 39, WDM 37 |
| `WorldMapArea` (`dungeonMap_id = 28`) | 0 stock, 0 WDM |
| `WorldMapTransforms` (`NewDungeonMapID = 28` or `NewMapID = 43`) | 0 stock, 0 WDM |
| `DungeonMap` rows for `MapID = 43` | exactly one: ID 28 |

There is no transform for map 43 in either tree and no WMA that points at floor
28. Deleting the two chunks removes only chunk→floor references; it leaves no
dangling `DungeonMap`/WMA/transform reference. (A general mutation feature would
still need to *check* that; see §21.)

## 10. Stock chunk set for floor 28 — 39 rows

All 39 rows have `MapID = 43`, `DungeonMapID = 28`, `MinZ` (`field4`) =
`-10000.0`. `WMOGroupID` (`field2`) values, in table order:

```
1209:3314 1218:3315 1210:3316 1219:3317 1211:3318 1220:3319 1212:3320
1213:3321 1221:3322 1217:3323 1222:3324 1214:3325 1223:3326 1215:3327
1216:3328 1224:3330 1244:3332 1234:3333 1235:3334 1236:3335 1245:3336
1246:3337 1237:3338 1238:3339 1247:3342 1248:3343 1229:5692 1243:5693
1226:6384 1239:6416 1227:6417 1230:6418 1240:6419 1231:6420 1241:6421
1232:6422 1242:6423 1233:6424 1228:6680
```

The `WMOGroupID` run 3314–3343 is broken by gaps at 3329, 3331, 3340, 3341;
the two removed groups 3338/3339 sit inside this block, next to retained 1246
(3337), 1247 (3342) and 1248 (3343).

## 11. Chunks 1237 and 1238 — complete stock rows

```
1237: ID=1237 MapID=43 WMOGroupID=3338 DungeonMapID=28 MinZ=-10000.0
      raw d50400002b0000000a0d00001c00000000401cc6  (index 29)
1238: ID=1238 MapID=43 WMOGroupID=3339 DungeonMapID=28 MinZ=-10000.0
      raw d60400002b0000000b0d00001c00000000401cc6  (index 30)
```

Both are absent from WDM's `DungeonMapChunk.dbc`.

## 12. Ordering context

In stock table order the two rows are adjacent:
`… 1245, 1246, 1237, 1238, 1247, 1248 …`. They are the only two rows WDM
deletes from the entire `DungeonMapChunk` table (stock 622 → WDM 1932 =
1310 added + 620 unchanged − 2 deleted). Because `DungeonMapChunk` row order is
load-bearing in this project (`tools/semantic.py`), a deletion feature must
remove rows while preserving the relative order of retained rows, exactly as
WDM did.

## 13. Set diff for floor 28

```
retained (37): 1209,1210,1211,1212,1213,1214,1215,1216,1217,1218,1219,1220,
               1221,1222,1223,1224,1226,1227,1228,1229,1230,1231,1232,1233,
               1234,1235,1236,1239,1240,1241,1242,1243,1244,1245,1246,1247,1248
removed   (2): 1237, 1238
added     (0): —
```

## 14. Meaning of chunks 1237/1238

`field2` is `WMOGroupID`. Chunks 1237/1238 bind WMO groups 3338 and 3339 of
the Wailing Caverns world model into floor 28. They are *not* artwork tiles and
*not* coordinate pairs; they are per-WMO-group entries the client uses to place
the instance-map geometry/explored regions. `MinZ = -10000.0` means no vertical
clip.

## 15. There is no replacement

WDM adds no `DungeonMapChunk` row with `MapID = 43` or `DungeonMapID = 28`. The
two rows are removed outright, not superseded by new IDs. Nothing in WDM
re-adds WMO groups 3338/3339 under a different chunk ID.

## 16. Why WDM removed them (evidence vs inference)

- Proven: they are the only chunk deletions in the tree; they are adjacent; the
  IDs stay contiguous with retained rows on both sides.
- Inference (not proven): they are the WMO groups that fall outside or conflict
  with WDM's re-derived WC artwork/extent, so WDM dropped them so the instance
  map does not draw stale or overlapping geometry. A plausible alternative is
  that these two groups are not part of the renderable cave in the new map and
  were simply cleaned up.
- Not provable statically: whether keeping them produces a visible artifact.
  This is a PTR question (§24, experiments 5 and 6).

## 17. Why WDM changed the floor bounds (evidence vs inference)

- Proven: WDM rewrote MinX/MaxX/MinY/MaxY to a smaller, re-centred 3:2 window
  that matches the new 12-tile artwork's aspect, and set
  `ParentWorldMapID = 11` (Barrens).
- Inference: because WMA 749 has zero `Loc` bounds, these `DungeonMap` bounds
  are what the client uses to scale WDM's artwork; the mutation is what makes
  the artwork line up and puts WC under the Barrens map. Without it, map 43
  would render with stock bounds.
- Not provable statically: whether the stock bounds visibly break the WDM
  artwork or merely render it slightly off. PTR question (§24,
  experiments 2–4).

## 18. Minimum required mutation — variants

| Variant | Contents | New rows | Stock mutations | Expressible today |
|---|---|---|---|---|
| **A** | WMA 749 + 12 BLPs only | WMA 749 | none | yes (WMA is additive) |
| **B** | A + `DungeonMap` 28 replace (fields 3–7) | WMA 749 | 1 replace | no |
| **C** | A + delete chunks 1237/1238 | WMA 749 | 2 delete | no |
| **D** | A + replace 28 + delete 1237/1238 (= WDM) | WMA 749 | 1 replace + 2 delete | no |
| **E** | Any re-encoding that dodges mutation (re-add chunks under new IDs; a transform; a second floor) | — | — | rejected: no new floor/chunk exists in WDM, and re-adding the same WMO groups under new IDs would double-draw the same geometry |

Two things fall out of this:

1. **A is structurally ship-able right now and is the only mutation-free
   option.** A package could declare WMA 749 + artwork and declare the
   `worldMaps` area as floorless (`dungeonMapId: 0`, `floors: []`,
   `chunks: []`). The client would use the stock `DungeonMap` 28 and stock
   chunks that already exist. Whether that renders WDM's artwork acceptably is
   the open PTR question. This report does **not** build that fixture; it is an
   experiment, not a proven publication.
2. B and D are what WDM actually did and cannot be expressed by an append-only
   package.

## 19. Proven from data vs requires a live client

Proven from data:

- every row value, raw record and delta in §2–§4, §10–§13;
- `field7 = ParentWorldMapID` and 11 = Barrens (§5);
- WMA 749 is additive, zero-bounds, and does not point at floor 28 (§6–§7);
- no replacement chunks and no transform; deletions are the only stock chunk
  change; identity fields are unchanged (§9, §15);
- floor 28 is the sole `DungeonMap` row for map 43 (§9).

Requires a live client (cannot be settled statically):

- that zero WMA bounds fall back to `DungeonMap` bounds;
- whether variant A renders acceptably (i.e. whether the bounds mutation is
  mandatory);
- whether keeping chunks 1237/1238 produces a visible artifact;
- whether `ParentWorldMapID = 11` is needed for WC to appear under the Barrens.

## 20. Why the candidate is UNSAFE today

`reports/instance-candidates.json` → `WailingCaverns`:

```
classification: UNSAFE
reasonCodes: ["stock-chunk", "stock-mutation-required"]
worldMapArea: [{id: 749, additive: true}]
floors:       [{id: 28,  additive: false}]
chunks:       37 entries, all additive:false
findings: ["DungeonMap floor 28 is a stock row that WDM mutates …",
           "DungeonMapChunk row(s) 1209, 1218, … already exist in the stock client …"]
```

The candidate's only additive row is WMA 749. Its floor and all 37 chunks are
stock rows WDM mutates or deletes, which the append-only composer refuses. This
is a real source-data dependency, not a schema limit.

## 21. Design: safe stock-mutation architecture (not implemented)

**Goal.** Let a package reproduce WDM's `DungeonMap` 28 and the two chunk
deletions *without* weakening the append-only guarantee that every stock row is
preserved unless a package explicitly and verifiably replaces or deletes it.

### 21.1 Manifest shape

Keep the existing additive surface untouched. Add two opt-in, top-level arrays
next to `worldMaps`:

```jsonc
"stockReplacements": [
  {
    "table": "DungeonMap",
    "id": 28,
    "expected": { "MapID": 43, "Floor": 1,
                  "MinX": -410.9460144042969, "MaxX": 595.5289916992188,
                  "MinY": -483.47900390625,  "MaxY": 187.50399780273438,
                  "ParentWorldMapID": 0 },
    "expectedRecordSha256": "4bd70a15…",
    "row":      { "MapID": 43, "Floor": 1,
                  "MinX": -375.9460144042969, "MaxX": 560.5289916992188,
                  "MinY": -410.14599609375,   "MaxY": 214.1699981689453,
                  "ParentWorldMapID": 11 }
  }
],
"stockDeletions": [
  { "table": "DungeonMapChunk", "id": 1237,
    "expected": { "MapID": 43, "WMOGroupID": 3338, "DungeonMapID": 28,
                  "MinZ": -10000.0 },
    "expectedRecordSha256": "…" },
  { "table": "DungeonMapChunk", "id": 1238,
    "expected": { "MapID": 43, "WMOGroupID": 3339, "DungeonMapID": 28,
                  "MinZ": -10000.0 },
    "expectedRecordSha256": "…" }
]
```

Identity fields (`ID`, `MapID`) are implied by `id` and the baseline row and may
not be changed by a replacement; only non-identity fields are authored.

### 21.2 Composition pipeline (extends the existing one)

```
load immutable stock baseline
validate additive manifests (unchanged)
validate stockReplacements / stockDeletions:
    table ∈ allowlist {DungeonMap, DungeonMapChunk, WorldMapArea, WorldMapTransforms}
    id exists in the baseline (else deterministic error: not a stock row)
    expected decoded values == baseline decoded values
    expectedRecordSha256 == hash(baseline raw record and its strings)
    replacement identity fields == baseline identity fields
    (table,id) not targeted twice
plan: sort mutation targets by (table order, id)
check conflicts:
    target id not also declared additively anywhere (append of a stock id already fails)
    no delete target is an FK target required by a surviving row
    (WMA.dungeonMap_id, chunk.DungeonMapID, transform.NewDungeonMapID)
apply onto the in-memory baseline copy:
    deletions first, then replacements (disjoint targets; fixed order for determinism)
    preserve relative order of retained rows
append additive rows (new stock IDs only)
serialize; verify parity; record per-target provenance
```

### 21.3 How the design meets the required properties

- **Exact-baseline match.** Enforced twice: descriptor-aware canonical field
  comparison (`expected`) *and* a raw-record+string SHA-256 pin
  (`expectedRecordSha256`). Any mismatch aborts composition. This is a
  deterministic failure, not a warning.
- **No normal generated ownership of mutated stock rows.** Mutations live in
  `stockReplacements`/`stockDeletions`, validated by a separate code path from
  the additive `worldMaps[]` builder. The additive builder still cannot claim a
  stock ID (it already refuses), and the mutation path cannot claim a
  non-stock ID.
- **Deterministic conflict failure.** Any two entries with the same
  `(table,id)`, any mutation of a non-stock id, any append of a mutated id, and
  any dangling-FK deletion abort with a named error.
- **Lifecycle.** A mutation is a *lease* of an existing row: `(table, id, op)`.
  Planner/parity account for it exactly as they account for append leases. It
  is active only while a package declaring it is in the release/installed set.
- **Natural revert on rebuild.** Mutations are declarative and re-derived from
  the immutable baseline on every composition. Dropping the array and
  recomposing restores the stock row; no incremental state is ever carried, so
  there is nothing to undo.
- **Composition-time only.** The baseline file on disk is opened read-only and
  never written; mutation happens on the in-memory copy that is serialized into
  the staged/EPF output. The baseline checksum manifest stays authoritative.
- **Immutable baselines.** Unchanged: the verified stock files and
  `SHA256SUMS` remain the only source. A replacement is always validated
  against, never derived from, mutable state.
- **Parity provenance.** The parity artifact records, per target: table, id,
  operation, `expectedRecordSha256`, result record SHA-256, and the resulting
  row count (`stock_untouched + replaced − deleted + appended`). Verification
  can re-check every expected value against the baseline without the package.
- **Existing append-only packages unchanged.** With the new arrays absent or
  empty the pipeline is byte-for-byte the current one; the existing
  byte-identical regression guarantee is unaffected.
- **No targeting appended/non-stock rows.** Deletions and replacements require
  `id ∈ baseline`; appends require `id ∉ baseline`. The two ID sets are
  disjoint by construction.
- **Explicit ordering/conflict.** Table order and id order are fixed; deletions
  precede replacements; retained row order is preserved; conflicts are errors,
  never last-writer-wins.

## 22. Verification method recommendation

Use all three, for different jobs:

1. **Raw fixed-size words** — the primary equality gate. DBC records are raw
   32-bit words; comparing baseline words to `expected` decoded from the
   manifest is exact and immune to float formatting. This is what actually
   gates composition.
2. **Descriptor-aware canonical values** — what the manifest stores in
   `expected`, so the JSON is readable and auditable against `DbcDescriptor`.
   Redundantly recomputed and cross-checked against the raw words.
3. **Raw-record SHA-256** — the tamper-evidence pin recorded in the manifest
   and in parity. Cheap, and catches string-block edits that a field-only
   comparison would miss.

Full decoded-row comparison alone is insufficient for `WorldMapArea` because it
has a string column whose offsets can differ while the text is equal; the raw
hash plus decoded string content covers that gap.

## 23. Guardrails this feature must keep

- Append-only stays the default; mutation is opt-in and explicit.
- The stock baseline and its `SHA256SUMS` stay read-only.
- No mutation may target a table outside the four world-map tables (extending
  the allowlist is a deliberate, reviewed change).
- No mutation may target a row WDM already treats as additive.
- Wailing Caverns stays UNSAFE and unpublished until a PTR pass confirms the
  mutation is both necessary and sufficient.

## 24. Minimal PTR experiment matrix

Run on a clean PTR with only the listed DBC/artwork deltas applied. Baseline
for every row: §2, §10, §11.

| # | Applied change | Expected DBC delta | Observe | Confirms / refutes |
|---|---|---|---|---|
| 1 | None (stock) | — | Opening map 43 shows no Wailing Caverns instance page, or a blank one | Baseline; proves WC has no usable page today |
| 2 | WMA 749 + 12 BLPs (variant A) | `WorldMapArea` +1 (749) | Does the WC map open? Is the artwork clipped/misaligned at the edges? | If clean → bounds mutation not required. If misaligned → bounds required |
| 3 | 2 + `DungeonMap` 28 MinX/MaxX/MinY/MaxY replace, `ParentWorldMapID` stays 0 | `DungeonMap` 28 fields 3–6 changed; row count unchanged | Does the artwork align? Does WC still *not* appear under the Barrens? | Separation of scaling from parenting |
| 4 | 3 + `ParentWorldMapID` → 11 | `DungeonMap` 28 field 7 = 11 | Does WC appear under the Barrens zone map? | Proves the parent reference is needed |
| 5 | 2 + delete chunks 1237/1238 only | `DungeonMapChunk` −2 | Any change to explored overlay / drawn geometry? | Proves whether the deletion is functional or cosmetic |
| 6 | Full WDM (variant D) | WMA +1, `DungeonMap` 28 replaced, `DungeonMapChunk` −2 | Compare 1:1 with WDM's own client | End-to-end equivalence |
| 7 | Chunks 1237/1238 kept, everything else = D | `DungeonMapChunk` ±0 vs D | Look for double-drawn or stale regions | Isolates the deletion's effect inside the full change |

For each experiment record: the exact composed DBC file hashes, the observed
map scale/alignment, whether WC appears under the Barrens, and any artifact in
the explored-overlay/geometry. That evidence decides whether the minimum
mutation is variant B/C/D or none (A).

## 25. Conclusion, residual unknowns, and repository state

- Wailing Caverns needs exactly one stock-row rewrite (`DungeonMap` 28) and two
  stock-row deletions (`DungeonMapChunk` 1237/1238). No additive row beyond WMA
  749 exists. Under the current append-only contract it cannot ship
  faithfully, which is correct behaviour, not a defect.
- `field7 = 11` is `ParentWorldMapID = The Barrens`, proven across the whole
  table family.
- The bounds change is almost certainly functional because WMA 749 has zero
  bounds and the client must scale from floor 28; this is the one conclusion
  that still wants a live confirmation (§24).
- The two deleted chunks bind WMO groups 3338/3339; no replacement exists; the
  deletion may be functional or cosmetic — unknown statically.
- Recommended path: keep Wailing Caverns UNSAFE and unpublished; run §24 to
  establish the true minimum; then implement §21 as an opt-in, separately
  validated stock-mutation path, and only then ship WC.
- A mutation-free "degraded" package (variant A, declared floorless + WMA 749 +
  artwork) is structurally possible today and is the cheapest experiment, but it
  is not proven to render correctly and is deliberately not published here.
- No stock DBC was modified and no package was built. `git status` shows only
  this new untracked report; nothing is staged, committed, or pushed.

### Residual unknowns

1. Client fallback from zero WMA bounds to `DungeonMap` bounds (no
   `WorldMapFrame.lua` available).
2. Whether variant A renders acceptably.
3. Whether keeping chunks 1237/1238 produces a visible artifact.
4. Stock `Map.dbc`/`AreaTable.dbc` cross-checks (not in the workspace);
   map 43 / area 718 are corroborated from WDM tables and LibMapData instead.
