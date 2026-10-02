# Zul'Farrak WDM forensic investigation

**Session ID:** ses_f06528860fferflkupaEdOJnrc
**Created:** 10/1/2026, 6:54:50 PM
**Updated:** 10/1/2026, 8:32:59 PM

---

## Assistant (Build · Big Pickle · 1.5s)

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && sed -n '49,60p' README.md"
}
```

**Output:**
```
is the only name the client can ask for. Nothing else about the 1392 tiles changes.

**The backlog is closed.** All 50 SAFE maps are published, listed explicitly in
`content/publish.json`; the other 8 discovered maps are UNSAFE and each carries
the reason codes that rejected it. See
[reports/instance-candidates.md](reports/instance-candidates.md) for the per-map
verdict and reasoning; [reports/wdm-stable-audit.md](reports/wdm-stable-audit.md)
records the stock-versus-WDM forensics, and
[reports/transform-analysis.md](reports/transform-analysis.md) records what can and
cannot be derived about a missing `WorldMapTransforms` row.

## Quick start

```

---

## Assistant (Build · Big Pickle · 3.8s)

**Tool: edit**

**Input:**
```json
{
  "oldString": "**The backlog is closed.** All 50 SAFE maps are published, listed explicitly in",
  "filePath": "/home/smithkt/git/mod-native-instance-maps/README.md",
  "newString": "Of the 50, seven are **floorless** maps: `hillsbrad-foothills`, `mount-hyjal`,\n`ruins-of-ahnqiraj`, `the-black-morass`, `zulaman`, `zulfarrak` and `zulgurub`.\nWDM gives them an area and artwork but no `DungeonMap` row, because the zone is\na single continuous world map rather than a set of floors. They declare\n`\"floors\": []` and `\"chunks\": []`, `dungeonMapId` `0`, and no `transform`; the\ncomposed `DungeonMap.dbc`, `DungeonMapChunk.dbc` and `WorldMapTransforms.dbc` are\nthe verified stock files byte for byte, and each package's only lease is its\n`WorldMapArea` row. They ship no floor labels because there is no floor dropdown\nrow to rename, so they do not request the `protected-framexml` capability at all.\n\n**The backlog is closed.** All 50 SAFE maps are published, listed explicitly in"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.6s)

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && grep -n \"43\\|fifteen\\|1392\\|no-floors\" README.md reports/final-report.md | head -30"
}
```

**Output:**
```
README.md:49:is the only name the client can ask for. Nothing else about the 1392 tiles changes.
reports/final-report.md:21:**43 of 58 discovered maps are shippable, and all 43 are published.** The
reports/final-report.md:27:| SAFE | 43 | every required row is additive, references are preserved as written, artwork present |
reports/final-report.md:44:| `mod-native-instance-maps.hellfire-ramparts` | 543 | 1 | 3 | none | 12 |
reports/final-report.md:49:| `mod-native-instance-maps.maraudon` | 349 | 2 | 43 | none | 24 |
reports/final-report.md:76:Totals: **113 floors, 1310 chunks, 43 areas, 4 transforms, 1392 tiles.** Each is a
reports/final-report.md:78:deterministic EPF in `dist/`, and all 43 compose into one release EPF. No DBC is
reports/final-report.md:98:`NewDungeonMapID` is never guessed from a floor. 39 of the 43 published maps carry
reports/final-report.md:177:The 43 individual packages and the combined release all pass. The release composes
reports/final-report.md:184:| `WorldMapArea` | 108 | 151 | 43 |
reports/final-report.md:206:1980 timestamp. `dist/` holds 44 files: 43 individual packages plus the combined
reports/final-report.md:217:| `mod-native-instance-maps.the-deadmines.epf` | `9f15c23875838f4d819b292c67e1b42a3036ab80cc6343ab05b3409d9001fb59` | 1,088,281 |
reports/final-report.md:252:1. **`DungeonMap 28`** (map 43, *Wailing Caverns*) — geometry rewritten
reports/final-report.md:256:2. **`DungeonMapChunk 1237`** — deleted (`MapID 43`, `DungeonMapID 28`).
reports/final-report.md:257:3. **`DungeonMapChunk 1238`** — deleted (`MapID 43`, `DungeonMapID 28`).
reports/final-report.md:269:| `ArathiBasin` | `no-chunks`, `no-floors`, `stock-world-map-area` |
reports/final-report.md:270:| `CoTHillsbradFoothills` | `no-chunks`, `no-floors` |
reports/final-report.md:271:| `CoTMountHyjal` | `no-chunks`, `no-floors` |
reports/final-report.md:272:| `CoTTheBlackMorass` | `no-chunks`, `no-floors` |
reports/final-report.md:273:| `Expansion01` | `ambiguous-transform`, `no-chunks`, `no-floors`, `stock-world-map-area` |
reports/final-report.md:274:| `NetherstormArena` | `no-chunks`, `no-floors`, `stock-world-map-area` |
reports/final-report.md:275:| `RuinsofAhnQiraj` | `no-chunks`, `no-floors` |
reports/final-report.md:276:| `WarsongGulch` | `no-chunks`, `no-floors`, `stock-world-map-area` |
reports/final-report.md:277:| `ZulAman` | `no-chunks`, `no-floors` |
reports/final-report.md:278:| `ZulFarrak` | `no-chunks`, `no-floors` |
reports/final-report.md:279:| `ZulGurub` | `no-chunks`, `no-floors` |
reports/final-report.md:285:The dominant cause is `no-floors` plus `no-chunks` on 11 maps: WDM gives them an
reports/final-report.md:314:| `WorldMapArea` | 51 | 43 | 8 | 0 |
reports/final-report.md:336:| All 43 published EPF payloads vs WDM artwork | byte-for-byte, including the 48 re-cased alias tiles |
reports/final-report.md:339:| No two published maps share a target or a row | 0 collisions, 1392 targets |

```

---

## Assistant (Build · Big Pickle · 1.9s)

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md",
  "limit": 50
}
```

**Output:**
```
<path>/home/smithkt/git/mod-native-instance-maps/reports/final-report.md</path>
<type>file</type>
<content>
1: # Final report
2: 
3: *Hand-written. The other files in `reports/` are generated by `tools/report.py`;
4: regenerate them instead of editing.*
5: 
6: ## Scope
7: 
8: Audit the vendored WDM-patch tables, decide which pre-Cataclysm instance maps
9: can be contributed to AzerothCore through `mod-content-manager`, and ship the
10: ones that can be shipped safely — without touching the client DBCs, the stock
11: data, or the upstream trees.
12: 
13: Three corrections led to this revision. A `WorldMapTransforms` row is
14: **optional** source data. A `WorldMapArea.dungeonMapId` is a **reference**, not a
15: row this package owns. And a `WorldMapArea.internal_name` is the **client-baked
16: identity** the artwork must be installed under, so a WDM artwork directory that
17: disagrees in letter case is a path to re-case, not a map to withhold.
18: 
19: ## Verdict
20: 
21: **43 of 58 discovered maps are shippable, and all 43 are published.** The
22: classifier is terminal — SAFE or UNSAFE — and each rejected map carries the reason
23: codes that rejected it.
24: 
25: | Level | Count | Meaning |
26: |---|---:|---|
27: | SAFE | 43 | every required row is additive, references are preserved as written, artwork present |
28: | UNSAFE | 15 | the source does not add up to a package, or the package would contradict WDM's own data |
29: 
30: | Published | Map | Floors | Chunks | Transform | Tiles |
31: |---|---:|---:|---:|---|---:|
32: | `mod-native-instance-maps.ahnqiraj` | 531 | 3 | 50 | WDM 13 | 36 |
33: | `mod-native-instance-maps.auchenai-crypts` | 558 | 2 | 14 | none | 24 |
34: | `mod-native-instance-maps.black-temple` | 564 | 7 | 40 | none | 96 |
35: | `mod-native-instance-maps.blackfathom-deeps` | 48 | 3 | 26 | none | 36 |
36: | `mod-native-instance-maps.blackrock-depths` | 230 | 2 | 52 | none | 24 |
37: | `mod-native-instance-maps.blackrock-spire` | 229 | 7 | 75 | none | 84 |
38: | `mod-native-instance-maps.blackwing-lair` | 469 | 4 | 22 | none | 48 |
39: | `mod-native-instance-maps.coilfang-reservoir` | 548 | 1 | 12 | none | 12 |
40: | `mod-native-instance-maps.deeprun-tram` | 369 | 2 | 7 | WDM 12 | 24 |
41: | `mod-native-instance-maps.dire-maul` | 429 | 6 | 73 | none | 84 |
42: | `mod-native-instance-maps.gnomeregan` | 90 | 4 | 79 | none | 48 |
43: | `mod-native-instance-maps.gruuls-lair` | 565 | 1 | 4 | none | 12 |
44: | `mod-native-instance-maps.hellfire-ramparts` | 543 | 1 | 3 | none | 12 |
45: | `mod-native-instance-maps.karazhan` | 532 | 17 | 86 | **none — WDM has none** | 204 |
46: | `mod-native-instance-maps.magisters-terrace` | 585 | 2 | 19 | none | 24 |
47: | `mod-native-instance-maps.magtheridons-lair` | 544 | 1 | 7 | none | 12 |
48: | `mod-native-instance-maps.mana-tombs` | 557 | 1 | 14 | none | 12 |
49: | `mod-native-instance-maps.maraudon` | 349 | 2 | 43 | none | 24 |
50: | `mod-native-instance-maps.molten-core` | 409 | 1 | 12 | none | 12 |

(Showing lines 1-50 of 409. Use offset=51 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 1.6s)

**Tool: read**

**Input:**
```json
{
  "offset": 51,
  "limit": 160,
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md"
}
```

**Output:**
```
<path>/home/smithkt/git/mod-native-instance-maps/reports/final-report.md</path>
<type>file</type>
<content>
51: | `mod-native-instance-maps.onyxias-lair` | 249 | 1 | 8 | none | 12 |
52: | `mod-native-instance-maps.ragefire-chasm` | 389 | 1 | 6 | none | 12 |
53: | `mod-native-instance-maps.razorfen-downs` | 129 | 1 | 11 | none | 12 |
54: | `mod-native-instance-maps.razorfen-kraul` | 47 | 1 | 25 | none | 12 |
55: | `mod-native-instance-maps.scarlet-monastery` | 189 | 4 | 89 | none | 48 |
56: | `mod-native-instance-maps.scholomance` | 289 | 4 | 26 | none | 48 |
57: | `mod-native-instance-maps.sethekk-halls` | 556 | 2 | 19 | none | 24 |
58: | `mod-native-instance-maps.shadow-labyrinth` | 555 | 1 | 21 | none | 12 |
59: | `mod-native-instance-maps.shadowfang-keep` | 33 | 7 | 79 | none | 84 |
60: | `mod-native-instance-maps.stratholme` | 329 | 2 | 80 | none | 24 |
61: | `mod-native-instance-maps.sunwell-plateau` | 580 | 1 | 2 | none | 24 |
62: | `mod-native-instance-maps.tempest-keep` | 550 | 1 | 16 | none | 12 |
63: | `mod-native-instance-maps.temple-of-atal-hakkar` | 109 | 3 | 75 | WDM 14 | 36 |
64: | `mod-native-instance-maps.the-arcatraz` | 552 | 3 | 21 | none | 36 |
65: | `mod-native-instance-maps.the-blood-furnace` | 542 | 1 | 7 | none | 12 |
66: | `mod-native-instance-maps.the-botanica` | 553 | 1 | 6 | none | 12 |
67: | `mod-native-instance-maps.the-deadmines` | 36 | 2 | 29 | WDM 11 | 24 |
68: | `mod-native-instance-maps.the-mechanar` | 554 | 2 | 15 | none | 24 |
69: | `mod-native-instance-maps.the-shattered-halls` | 540 | 1 | 12 | none | 12 |
70: | `mod-native-instance-maps.the-slave-pens` | 547 | 1 | 5 | none | 12 |
71: | `mod-native-instance-maps.the-steamvault` | 545 | 2 | 10 | none | 24 |
72: | `mod-native-instance-maps.the-stockade` | 34 | 1 | 57 | none | 12 |
73: | `mod-native-instance-maps.the-underbog` | 546 | 1 | 1 | none | 12 |
74: | `mod-native-instance-maps.uldaman` | 70 | 2 | 52 | none | 24 |
75: 
76: Totals: **113 floors, 1310 chunks, 43 areas, 4 transforms, 1392 tiles.** Each is a
77: `mod-content-manager` manifest in `content/<slug>/manifest.json` plus a
78: deterministic EPF in `dist/`, and all 43 compose into one release EPF. No DBC is
79: shipped; composition is `mod-content-manager`'s.
80: 
81: Per-map verdicts and reasons: [instance-candidates.md](instance-candidates.md).
82: Machine-readable form: [instance-candidates.json](instance-candidates.json).
83: 
84: ## What changed, and why
85: 
86: Three rules in `tools/instances.py` blocked maps that are in fact complete, and a
87: fourth change narrowed the classifier to a terminal two-level verdict.
88: 
89: ### 1. `no-transform` is no longer a reason code
90: 
91: A missing `WorldMapTransforms` row used to fail every map WDM does not transform.
92: `mod-content-manager` supports the opposite contract: a `worldMaps[]` entry may
93: omit `transform` entirely, in which case `AppendRequests` emits no
94: `WorldMapTransforms` request, `PlanFixed` issues no lease, and `Compose` leaves
95: the verified stock file byte for byte unchanged.
96: 
97: The manifest now omits the key rather than writing `null`, and
98: `NewDungeonMapID` is never guessed from a floor. 39 of the 43 published maps carry
99: no transform because WDM supplies none.
100: 
101: ### 2. `dungeonMapId` is a reference
102: 
103: `WorldMapArea.dungeonMapId` used to be resolved against the package's own floors,
104: and anything unresolvable was reported as a defect. That is the wrong model: the
105: field names another `DungeonMap` row and does not imply ownership of it. The
106: signed value is now carried through verbatim — `0`, `-1`, and a cross-map
107: reference alike — and never becomes a request, a lease or a row.
108: 
109: This is what unblocks `BlackTemple` and `SunwellPlateau` (`-1`) and `AhnQiraj`
110: (`DungeonMap 2`, a stock row belonging to map 574, which stays stock).
111: 
112: ### 3. A differently-cased artwork directory is a path, not a verdict
113: 
114: WDM's `internalName` and its artwork directory disagree in letter case for two
115: maps: `BlackfathomDeeps` / `BlackFathomDeeps` (36 tiles) and `MagtheridonsLair` /
116: `Magtheridonslair` (12 tiles). The client derives the artwork directory from the
117: `internal_name` in the DBC row, so the package must install the tiles at the DBC
118: spelling.
119: 
120: The bytes are WDM's, unmodified. Only the path changes, and the name is rebuilt
121: from the client-baked identity rather than from WDM's spelling of it — which is
122: the one identity the client can actually ask for. `tile_target_name` does this and
123: nothing more: a leaf that is not the area's own name in different capitals,
124: including WDM's own inconsistent casing *within* a directory
125: (`TheTempleOfAtalHakkar/`, which spells floor 2 `TheTempleofAtalHakkar` and floor 3
126: `TheTempleofAtalhakkar`), is returned unchanged. That inconsistency is recorded by
127: a test rather than repaired, because repairing it would rewrite an already-released
128: package to fix something that is not broken.
129: 
130: The artwork-only spellings `BlackFathomDeeps` and `Magtheridonslair` remain
131: UNSAFE, with reason `duplicate-artwork-alias`: they name no map of their own, and
132: their tiles ship inside the two packages that do.
133: 
134: ### 4. The verdict is terminal
135: 
136: `SAFE / REVIEW / UNSAFE` became `SAFE / UNSAFE`, with a closed
137: `UNSAFE_REASONS` set. A third level that nothing could leave was a backlog, not a
138: classification: a map is either publishable from the vendored source, or it is
139: blocked with the reason codes that blocked it.
140: 
141: ### What was *not* changed
142: 
143: No transform is derived, allocated or synthesized. The refutation in
144: [transform-analysis.md](transform-analysis.md) still stands: for a multi-floor map
145: the default floor is not recoverable from these tables, because Deadmines and
146: Deeprun Tram are indistinguishable here yet WDM chose different floors for each.
147: That analysis is now a statement about what this project will not do, rather than
148: about what it may ship.
149: 
150: ## Karazhan
151: 
152: Map 532, the multi-floor stress case the old rule excluded, and still the
153: largest single package in the release.
154: 
155: | Property | Value | Source |
156: |---|---|---|
157: | `WorldMapArea` rows | 1 (id 799, `areaId` 3457, `virtualMapId` -1, `dungeonMapId` 0) | WDM |
158: | `DungeonMap` floors | 17 (383, 385–391, 393, 398, 399, 401–406) | WDM |
159: | `DungeonMapChunk` rows | 86 | WDM |
160: | `WorldMapTransforms` rows | **0** | WDM |
161: | Artwork | 204 BLP files | WDM |
162: 
163: The declaration is compared field-for-field against the raw WDM rows, not against
164: the importer's own intermediate state, so a renumbered row, a reordered chunk
165: list, a normalized signed field or an invented transform fails the suite. All
166: 204 artwork payloads are compared by SHA-256 against the WDM directory.
167: 
168: ### Through mod-content-manager
169: 
170: `tests/validate_epfs.py` drives the real pipeline against the verified stock
171: 3.3.5a build-12340 baseline:
172: 
173: ```
174: Validate -> StageInto -> AppendRequests -> PlanFixed -> Compose -> Stage -> VerifyParity
175: ```
176: 
177: The 43 individual packages and the combined release all pass. The release composes
178: as:
179: 
180: | Table | Stock rows | Composed rows | Added |
181: |---|---:|---:|---:|
182: | `DungeonMap` | 55 | 168 | 113 |
183: | `DungeonMapChunk` | 622 | 1932 | 1310 |
184: | `WorldMapArea` | 108 | 151 | 43 |
185: | `WorldMapTransforms` | 9 | 13 | 4 |
186: 
187: Verified for every package, Karazhan included:
188: 
189: - no `WorldMapTransforms` request, no lease, no composed row, for the 39 maps WDM
190:   does not transform — so the composed table gains exactly WDM's 4 rows;
191: - every stock row and every stock string byte survives composition in place, so
192:   no verified row was edited;
193: - every appended row is leased at its declared WDM ID, and none collides with a
194:   stock ID;
195: - every authored row reads back out of the staged `DBFilesClient` file identical
196:   to the composed bytes;
197: - the parity artifact verifies, with a `WorldMapTransforms` hash recorded for
198:   the 4 transformed maps and none for the other 39 — because upstream refuses a
199:   hash for a table with no lease;
200: - a counterfactual confirms that supplying a transform *would* have produced one
201:   request, one lease and one row, so the zeroes are measured, not unchecked.
202: 
203: ## Artifacts
204: 
205: Deterministic EPFs, stored uncompressed with `manifest.json` first and a fixed
206: 1980 timestamp. `dist/` holds 44 files: 43 individual packages plus the combined
207: `dist/mod-native-instance-maps.epf` (63,086,428 bytes).
208: 
209: The four packages that shipped before the expansion are byte-pinned in
210: `tests/run_tests.py`, so a change to the description builder or the semantic

(Showing lines 51-210 of 409. Use offset=211 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 2.6s)

**Tool: read**

**Input:**
```json
{
  "offset": 211,
  "limit": 200,
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md"
}
```

**Output:**
```
<path>/home/smithkt/git/mod-native-instance-maps/reports/final-report.md</path>
<type>file</type>
<content>
211: projection cannot silently rewrite a released manifest:
212: 
213: | Package | SHA-256 | Bytes |
214: |---|---|---:|
215: | `mod-native-instance-maps.karazhan.epf` | `612feb7ecf66d52e297a667c785fc751f44fa18348c6c23b77fa60be82836e5a` | 9,220,306 |
216: | `mod-native-instance-maps.deeprun-tram.epf` | `20dc20ae161184d360bbd55f4c91046d8622fffa2832562da82a245832237154` | 1,085,559 |
217: | `mod-native-instance-maps.the-deadmines.epf` | `9f15c23875838f4d819b292c67e1b42a3036ab80cc6343ab05b3409d9001fb59` | 1,088,281 |
218: | `mod-native-instance-maps.temple-of-atal-hakkar.epf` | `512db08dcb246ca23b50e25540738470facb604c73bd13b4edf09ebd2c45ea27` | 1,637,085 |
219: 
220: Nothing was deployed. `dist/` is gitignored; the committed artifacts are the
221: manifests.
222: 
223: ## Provenance and integrity
224: 
225: - WDM-patch revision `5e7e9d1957211f40c9636a9f417901d153b40d4d`, vendored
226:   read-only under `upstream/WDM-patch/` and recorded in
227:   `upstream/WDM-patch/SOURCE.json` as `modified: false`.
228: - `sha256sum -c ../SHA256SUMS`, run from `upstream/WDM-patch/Stable`:
229:   **17,072 OK, 0 FAILED.**
230: - `git status --porcelain upstream/` reports **0 changes**.
231: - All WDM locales ship byte-identical `DBFilesClient` tables; `enUS` is the
232:   representative tree.
233: 
234: ## Forensics
235: 
236: Full detail in [wdm-stable-audit.md](wdm-stable-audit.md). Summary:
237: 
238: | Table | Stock | WDM | Added IDs | Removed | Modified | Byte-identical |
239: |---|---:|---:|---:|---:|---:|---:|
240: | `DungeonMap` | 55 | 168 | 113 | 0 | 1 | 54 |
241: | `DungeonMapChunk` | 622 | 1932 | 1312 | 2 | 0 | 620 |
242: | `WorldMapArea` | 108 | 159 | 51 | 0 | 1 | 107 |
243: | `WorldMapTransforms` | 9 | 13 | 4 | 0 | 0 | 9 |
244: 
245: ### The four places WDM diverges from stock
246: 
247: These are the reason the append-only contract matters. `mod-content-manager`'s
248: composer refuses any declared ID already present in the verified stock
249: baseline, so a package can only add rows. These four changes are therefore
250: reportable but not shippable.
251: 
252: 1. **`DungeonMap 28`** (map 43, *Wailing Caverns*) — geometry rewritten
253:    (`field3` `-410.946` → `-375.946`, `field4` `595.529` → `560.529`,
254:    `field5` `-483.479` → `-410.146`, `field6` `187.504` → `214.17`) and
255:    `field7` `0` → `11`.
256: 2. **`DungeonMapChunk 1237`** — deleted (`MapID 43`, `DungeonMapID 28`).
257: 3. **`DungeonMapChunk 1238`** — deleted (`MapID 43`, `DungeonMapID 28`).
258: 4. **`WorldMapArea 609`** (*The Ruby Sanctum*) — `parentMapID` `0` → `488`.
259: 
260: Consequence: *Wailing Caverns* is UNSAFE, because its instance only works with
261: WDM's rewritten floor and its deleted chunk rows.
262: 
263: ## Why 15 maps are withheld
264: 
265: Every rejection, with its reason codes:
266: 
267: | Map | Reason codes |
268: |---|---|
269: | `ArathiBasin` | `no-chunks`, `no-floors`, `stock-world-map-area` |
270: | `CoTHillsbradFoothills` | `no-chunks`, `no-floors` |
271: | `CoTMountHyjal` | `no-chunks`, `no-floors` |
272: | `CoTTheBlackMorass` | `no-chunks`, `no-floors` |
273: | `Expansion01` | `ambiguous-transform`, `no-chunks`, `no-floors`, `stock-world-map-area` |
274: | `NetherstormArena` | `no-chunks`, `no-floors`, `stock-world-map-area` |
275: | `RuinsofAhnQiraj` | `no-chunks`, `no-floors` |
276: | `WarsongGulch` | `no-chunks`, `no-floors`, `stock-world-map-area` |
277: | `ZulAman` | `no-chunks`, `no-floors` |
278: | `ZulFarrak` | `no-chunks`, `no-floors` |
279: | `ZulGurub` | `no-chunks`, `no-floors` |
280: | `Northrend` | `stock-chunk`, `stock-floor`, `stock-world-map-area` |
281: | `WailingCaverns` | `stock-chunk`, `stock-mutation-required` |
282: | `BlackFathomDeeps` | `duplicate-artwork-alias` |
283: | `Magtheridonslair` | `duplicate-artwork-alias` |
284: 
285: The dominant cause is `no-floors` plus `no-chunks` on 11 maps: WDM gives them an
286: area and artwork but no `DungeonMap` row, so there is nothing to enter and
287: publishing them would mean inventing a floor. `Expansion01` additionally has two
288: transforms (2 and 3) for map 530, so no default floor is derivable even if the
289: floors existed.
290: 
291: `Northrend` and `WailingCaverns` are the two maps whose rows are stock IDs WDM
292: mutates or deletes. The composer's append-only contract means neither can ship.
293: 
294: `BlackFathomDeeps` and `Magtheridonslair` name no map of their own — they are
295: artwork-only directories whose tiles ship inside the `BlackfathomDeeps` and
296: `MagtheridonsLair` packages. Publishing them separately would install the same
297: artwork twice under two names.
298: 
299: Additionally, 22 maps have `DungeonMap` floor geometry but no `WorldMapArea`
300: row at all (the stock raid floors — map 631 alone contributes eight). They have
301: no map identity to build a `worldMaps[]` entry around, so they are not
302: candidates; the full table with the stock/WDM-only split is in the audit report.
303: 
304: ## WDM rows the release does not ship
305: 
306: The classifier accounts for every row WDM adds, and the release is not all of
307: them. `Discovery.coverage()` reports each table as
308: `shipped + held back + unowned = added`, and a test asserts that identity.
309: 
310: | Table | WDM added | Shipped | Held back | Unowned |
311: |---|---:|---:|---:|---:|
312: | `DungeonMap` | 113 | 113 | 0 | 0 |
313: | `DungeonMapChunk` | 1312 | 1310 | 0 | 2 |
314: | `WorldMapArea` | 51 | 43 | 8 | 0 |
315: | `WorldMapTransforms` | 4 | 4 | 0 | 0 |
316: 
317: - **Unowned chunks 1828, 1829** belong to map 631 (*Icecrown Citadel*), which has
318:   a stock `WorldMapArea` (604), no WDM area, no WDM floors and no WDM artwork —
319:   so it is not a candidate and the chunks ship nowhere. This is the only
320:   unaccounted-for row set in the release.
321: - **Held-back areas 686, 697, 717, 733, 734, 749, 775, 781** (`ZulFarrak`,
322:   `ZulGurub`, `RuinsofAhnQiraj`, `CoTTheBlackMorass`, `CoTHillsbradFoothills`,
323:   `WailingCaverns`, `CoTMountHyjal`, `ZulAman`) belong to the withheld maps above.
324: 
325: ## Verification evidence
326: 
327: | Check | Result |
328: |---|---|
329: | `upstream/WDM-patch/SHA256SUMS` | 17,072 OK, 0 FAILED |
330: | `git status --porcelain upstream/` | 0 changes |
331: | `python3 tests/run_tests.py` | **149 tests, OK, 0 skipped** |
332: | Deadmines vs `mod-content-manager` golden fixture | exact match on `worldMaps` and `content` |
333: | Deadmines chunk order vs WDM's shipped DBC | exact match |
334: | Karazhan declaration vs raw WDM rows | field-for-field match, 17/86/1/0/204 |
335: | Karazhan artwork vs WDM payloads | 204/204 SHA-256 match |
336: | All 43 published EPF payloads vs WDM artwork | byte-for-byte, including the 48 re-cased alias tiles |
337: | Every WDM added row accounted for | `shipped + held back + unowned = added`, all four tables |
338: | No SAFE map claims a stock ID | 0 collisions across all four tables |
339: | No two published maps share a target or a row | 0 collisions, 1392 targets |
340: | Publication set == SAFE set | 43 == 43; no UNSAFE map has a `content/` directory |
341: | The four pre-existing manifests regenerated | byte-identical, no diff |
342: | `tests/validate_epfs.py` — all 44 EPFs through the full CM pipeline | valid, staged, composed, parity verified |
343: | `WorldMapTransforms` composition | +4 rows, all WDM's; stock rows untouched |
344: | `make check` | exit 0 |
345: 
346: The golden-fixture comparison remains the load-bearing one for Deadmines: its
347: manifest is derived *only* from WDM and then compared field-for-field, in order,
348: against a manifest authored independently. It matches exactly, on both the
349: semantic block and the artwork content block.
350: 
351: ## Constraints honoured
352: 
353: 1. **Append-only** — no package replaces, removes, or renumbers a stock row.
354:    The four WDM stock mutations are reported, never shipped.
355: 2. **Fixed IDs** — manifests carry WDM's IDs verbatim.
356: 3. **Order preserved** — `DungeonMapChunk` order is WDM's declaration order.
357:    Deadmines interleaves floors 166/167 and is not ID-sorted; grouping by floor
358:    produces a different DBC. This was a real bug caught during development and
359:    is now pinned by two tests.
360: 4. **References are references** — `dungeonMapId` is carried through signed and
361:    exact, and never becomes a row of its own.
362: 5. **No invented transforms** — a transform is WDM's or absent; `NewDungeonMapID`
363:    is never guessed and no transform ID is ever allocated.
364: 6. **No DBCs in packages** — a package ships artwork plus a manifest.
365: 7. **Deterministic** — canonical JSON manifests; uncompressed EPFs with a fixed
366:    1980 timestamp, verified byte-reproducible.
367: 8. **Upstream immutable** — vendored, checksummed, never edited.
368: 9. **Prohibited repos untouched** — `mod-content-manager`, `WDM-patch`,
369:    `wdm-stock-dbc/` and `upstream/` are all read-only inputs. Nothing was
370:    committed or pushed.
371: 
372: ## Recommendations
373: 
374: - **Verify the re-cased artwork on a live client.** `BlackfathomDeeps` and
375:   `MagtheridonsLair` are the only packages whose tile *paths* differ from WDM's
376:   layout. The reasoning is that `internal_name` is the client-baked identity and
377:   the DBC spelling is the only one the client can ask for, and the bytes are
378:   WDM's unchanged. That is a static argument; it is the one claim in this release
379:   most worth confirming in game.
380: - **Do not synthesise transforms.** A hand-written transform for, say,
381:   *Blackrock Spire* would be a guess about client-baked behaviour wearing WDM's
382:   fixed ID, and it would be indistinguishable, in the composed DBC, from real
383:   WDM data. A missing transform is a complete row set, not a gap to fill. 39 of the
384:   43 published maps have no transform, and that is the correct outcome.
385: - **Leave WDM's within-directory casing alone.** `TheTempleOfAtalHakkar` is
386:   spelled three different ways across its three floors in one directory. It works,
387:   because the client is case-insensitive. Re-casing it would rewrite a released
388:   package to fix a non-bug, so it is recorded by a test instead.
389: - **The `-1` sentinel was a `mod-content-manager` validator bug**, now fixed
390:   upstream: treating every non-zero `dungeonMapId` as an unresolvable reference
391:   made a legitimate client value unloadable.
392: - **Only Karazhan is runtime-proven.** The other 42 are byte-for-byte WDM's data
393:   composed by the same append-only path, which is the strongest claim the
394:   evidence supports. Whether the client renders each of them as WDM intends is a
395:   question only a live client can answer, and no such claim is made here.
396: - **Re-run `make check` after any upstream refresh.** The reports are generated,
397:   so `--check` turns a stale classification into a build failure rather than a
398:   silent drift.
399: 
400: ## Reproducing
401: 
402: ```bash
403: make check
404: ```
405: 
406: Regenerates `reports/`, `content/` and `dist/` from the vendored WDM tree, runs
407: the 149-test suite, and drives every EPF through the `mod-content-manager`
408: checkout. `make verify` is the CI gate: it writes nothing and fails if any
409: committed artifact is out of date.

(End of file - total 409 lines)
</content>
```

---

## Assistant (Build · Big Pickle · 3.6s)

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && python3 -c \"\nimport json,pathlib\nc=json.loads(pathlib.Path('reports/instance-candidates.json').read_text())\nprint(list(c)[:6])\n\" 2>/dev/null; python3 -c \"\nimport json,pathlib\nc=json.loads(pathlib.Path('reports/instance-candidates.json').read_text())\nitems=c['candidates'] if isinstance(c,dict) and 'candidates' in c else c\nprint('n=',len(items)); print(json.dumps(items[0],indent=1)[:600])\n\""
}
```

**Output:**
```
['candidates', 'counts', 'coverage', 'floorsWithoutArea', 'stockMutations', 'unmappedWdmOnlyAreas']
n= 58
{
 "areaDungeonMapId": 2,
 "artworkClaimedBy": null,
 "artworkDirectory": "Interface/WorldMap/AhnQiraj",
 "artworkLeafRenames": {},
 "artworkNameAliases": [],
 "artworkSource": "AhnQiraj",
 "blpCount": 36,
 "chunks": [
  {
   "additive": true,
   "id": 2926
  },
  {
   "additive": true,
   "id": 2921
  },
  {
   "additive": true,
   "id": 2934
  },
  {
   "additive": true,
   "id": 2935
  },
  {
   "additive": true,
   "id": 2936
  },
  {
   "additive": true,
   "id": 2895
  },
  {
   "additive": true,
   "id": 2896
  },
  {
   "additive": true,
   "id": 2897
  },
  {
   "additive": true,
   "

```

---

## Assistant (Build · Big Pickle · 2.3s)

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && python3 -c \"\nimport json,pathlib\nc=json.loads(pathlib.Path('reports/instance-candidates.json').read_text())\nprint('counts',c['counts'])\nprint('coverage',json.dumps(c['coverage']))\nfor it in c['candidates']:\n    if not it['floors'] and not it['chunks']:\n        print(it['internalName'], it['verdict'], it['reasons'], 'area',it.get('areaId'),'blp',it['blpCount'],'dmid',it['areaDungeonMapId'])\n\""
}
```

**Output:**
```
Traceback (most recent call last):
  File "<string>", line 8, in <module>
    print(it['internalName'], it['verdict'], it['reasons'], 'area',it.get('areaId'),'blp',it['blpCount'],'dmid',it['areaDungeonMapId'])
                              ~~^^^^^^^^^^^
KeyError: 'verdict'
counts {'SAFE': 50, 'UNSAFE': 8, 'candidates': 58}
coverage [{"added": 113, "heldBack": {}, "shipped": 113, "table": "DungeonMap", "unowned": []}, {"added": 1312, "heldBack": {}, "shipped": 1310, "table": "DungeonMapChunk", "unowned": [1828, 1829]}, {"added": 51, "heldBack": {"749": ["WailingCaverns"]}, "shipped": 50, "table": "WorldMapArea", "unowned": []}, {"added": 4, "heldBack": {}, "shipped": 4, "table": "WorldMapTransforms", "unowned": []}]

```

---

## Assistant (Build · Big Pickle · 2.4s)

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && python3 -c \"\nimport json,pathlib\nc=json.loads(pathlib.Path('reports/instance-candidates.json').read_text())\nprint([k for k in c['candidates'][0] if 'ver' in k or 'safe' in k or 'reason' in k or 'level' in k])\nfor it in c['candidates']:\n    if not it['floors'] and not it['chunks']:\n        print(it['internalName'], it.get('level'), it.get('reasons'), 'area',it.get('areaId'),'blp',it['blpCount'],'dmid',it['areaDungeonMapId'])\n\""
}
```

**Output:**
```
['reasonCodes']
ArathiBasin None None area None blp 12 dmid 0
BlackFathomDeeps None None area None blp 36 dmid None
CoTHillsbradFoothills None None area None blp 12 dmid 0
CoTMountHyjal None None area None blp 12 dmid 0
CoTTheBlackMorass None None area None blp 12 dmid 0
Expansion01 None None area None blp 12 dmid 0
Magtheridonslair None None area None blp 12 dmid None
NetherstormArena None None area None blp 12 dmid 0
RuinsofAhnQiraj None None area None blp 12 dmid 0
WarsongGulch None None area None blp 12 dmid 0
ZulAman None None area None blp 12 dmid 0
ZulFarrak None None area None blp 12 dmid 0
ZulGurub None None area None blp 12 dmid 0

```

---

## Assistant (Build · Big Pickle · 2.7s)

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && python3 -c \"\nimport json,pathlib\nc=json.loads(pathlib.Path('reports/instance-candidates.json').read_text())\nprint([k for k in c['candidates'][0]])\nprint()\nfor it in c['candidates']:\n    if not it['floors'] and not it['chunks']:\n        print(f\\\"{it['internalName']:24} {it.get('safe')!s:6} {it['reasonCodes']} wma={it.get('areaId')} map={it.get('mapId')} blp={it['blpCount']} dmid={it['areaDungeonMapId']}\\\")\n\""
}
```

**Output:**
```
['areaDungeonMapId', 'artworkClaimedBy', 'artworkDirectory', 'artworkLeafRenames', 'artworkNameAliases', 'artworkSource', 'blpCount', 'chunks', 'classification', 'findings', 'floors', 'internalName', 'mapId', 'package', 'reasonCodes', 'slug', 'title', 'transforms', 'worldMapArea']

ArathiBasin              None   ['stock-world-map-area'] wma=None map=529 blp=12 dmid=0
BlackFathomDeeps         None   ['duplicate-artwork-alias'] wma=None map=None blp=36 dmid=None
CoTHillsbradFoothills    None   [] wma=None map=560 blp=12 dmid=0
CoTMountHyjal            None   [] wma=None map=534 blp=12 dmid=0
CoTTheBlackMorass        None   [] wma=None map=269 blp=12 dmid=0
Expansion01              None   ['floorless-transform-reference', 'stock-world-map-area'] wma=None map=530 blp=12 dmid=0
Magtheridonslair         None   ['duplicate-artwork-alias'] wma=None map=None blp=12 dmid=None
NetherstormArena         None   ['stock-world-map-area'] wma=None map=566 blp=12 dmid=0
RuinsofAhnQiraj          None   [] wma=None map=509 blp=12 dmid=0
WarsongGulch             None   ['stock-world-map-area'] wma=None map=489 blp=12 dmid=0
ZulAman                  None   [] wma=None map=568 blp=12 dmid=0
ZulFarrak                None   [] wma=None map=209 blp=12 dmid=0
ZulGurub                 None   [] wma=None map=309 blp=12 dmid=0

```

---

## Assistant (Build · Big Pickle · 3.5s)

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && python3 -c \"\nimport json,pathlib\nc=json.loads(pathlib.Path('reports/instance-candidates.json').read_text())\nfor it in c['candidates']:\n    if it['internalName'] in ('ZulFarrak','ZulAman','ArathiBasin','Expansion01'):\n        w=it['worldMapArea']\n        print(it['internalName'], it['classification'], it['package'])\n        print('   wma:', json.dumps({k:v for k,v in w.items() if k!='stringBlock'})[:340])\n        print('   findings:', it['findings'])\n\""
}
```

**Output:**
```
Traceback (most recent call last):
  File "<string>", line 8, in <module>
    print('   wma:', json.dumps({k:v for k,v in w.items() if k!='stringBlock'})[:340])
                                                ^^^^^^^
AttributeError: 'list' object has no attribute 'items'
ArathiBasin UNSAFE mod-native-instance-maps.arathibasin

```

---

## Assistant (Build · Big Pickle · 4.1s)

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && python3 -c \"\nimport json,pathlib\nc=json.loads(pathlib.Path('reports/instance-candidates.json').read_text())\nfor it in c['candidates']:\n    if it['internalName'] in ('ZulFarrak','ZulAman','ArathiBasin','Expansion01'):\n        print(it['internalName'], it['classification'], it['package'])\n        print('   wma:', json.dumps(it['worldMapArea'])[:260])\n        print('   findings:', it['findings'])\n        print('   desc:', it.get('description'))\n\""
}
```

**Output:**
```
ArathiBasin UNSAFE mod-native-instance-maps.arathibasin
   wma: [{"additive": false, "id": 461}]
   findings: ['WorldMapArea 461 is a stock row that WDM leaves untouched; the client already has it and there is nothing additive to ship']
   desc: None
Expansion01 UNSAFE mod-native-instance-maps.expansion01
   wma: [{"additive": false, "id": 466}]
   findings: ['WorldMapArea 466 is a stock row that WDM leaves untouched; the client already has it and there is nothing additive to ship', 'WorldMapTransforms 2, 3 name a floor of map 530, but that map owns none']
   desc: None
ZulAman SAFE mod-native-instance-maps.zulaman
   wma: [{"additive": true, "id": 781}]
   findings: []
   desc: None
ZulFarrak SAFE mod-native-instance-maps.zulfarrak
   wma: [{"additive": true, "id": 686}]
   findings: []
   desc: None

```

---

## Assistant (Build · Big Pickle · 6.3s)

_Thinking:_

Now I have all evidence. Let me rewrite the final report. It's a hand-written report. I need to update it significantly:

- Scope/Verdict: 50/58, 8 unsafe
- Published table: add 7 floorless rows, totals 113 floors, 1310 chunks, 50 areas, 4 transforms, 1392 + 84 = 1476 tiles? Let me compute: existing 1392 + 7*12 = 1392+84 = 1476.
- "What changed" — add floorless section
- Karazhan section stays
- Through CM: release compose table WorldMapArea 108→158 (added 50); DungeonMap still 168; chunks still 1932; transforms 13.
- Artifacts: dist holds 51 files (50 individual + combined). Combined size 66,880,859.
- The "why 15 withheld" section → "why 8 withheld", with new reason codes.
- WDM rows not shipped: WorldMapArea 51 added, 50 shipped, 1 held back (749 WailingCaverns).
- Verification evidence: 156 tests, 51 EPFs.
- Recommendations.

Let me be careful and thorough. Rather than rewriting the whole file from scratch, I'll make targeted edits. But many sections change. Given the size, let me do a series of edits.

Let me count tiles for the new packages: 7 * 12 = 84 → total 1476.

Coverage table:
- WorldMapArea: added 51, shipped 50, heldBack {749: WailingCaverns}, unowned 0.

Held-back areas now just 749 WailingCaverns.

Let me make the edits.

First, verdict.

Now I have all the evidence. Updating the final report section by section.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md",
  "newString": "**50 of 58 discovered maps are shippable, and all 50 are published.** The\nclassifier is terminal — SAFE or UNSAFE — and each rejected map carries the reason\ncodes that rejected it.\n\n| Level | Count | Meaning |\n|---|---:|---|\n| SAFE | 50 | every required row is additive, references are preserved as written, artwork present |\n| UNSAFE | 8 | the source does not add up to a package, or the package would contradict WDM's own data |\n\n| Published | Map | Floors | Chunks | Transform | Tiles |\n|---|---:|---:|---:|---|---:|",
  "oldString": "**43 of 58 discovered maps are shippable, and all 43 are published.** The\nclassifier is terminal — SAFE or UNSAFE — and each rejected map carries the reason\ncodes that rejected it.\n\n| Level | Count | Meaning |\n|---|---:|---|\n| SAFE | 43 | every required row is additive, references are preserved as written, artwork present |\n| UNSAFE | 15 | the source does not add up to a package, or the package would contradict WDM's own data |\n\n| Published | Map | Floors | Chunks | Transform | Tiles |\n|---|---:|---:|---:|---|---:|"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.8s)

_Thinking:_

Wait, my edit was wrong — I put the new content as newString but the oldString contained the old text, and I included the new content twice? Let me check. I set newString to the "50" version and oldString to the "43" version... no wait, I set newString to include the 50 version AND the oldString to include both? Let me re-read.

I made newString = the 50 version (correct new), oldString = the 43 version. But looking at my edit call, the newString starts with "**50 of 58..." and oldString starts with "**43 of 58...". That's correct. Let me verify the file.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && sed -n '19,31p' reports/final-report.md"
}
```

**Output:**
```
## Verdict

**50 of 58 discovered maps are shippable, and all 50 are published.** The
classifier is terminal — SAFE or UNSAFE — and each rejected map carries the reason
codes that rejected it.

| Level | Count | Meaning |
|---|---:|---|
| SAFE | 50 | every required row is additive, references are preserved as written, artwork present |
| UNSAFE | 8 | the source does not add up to a package, or the package would contradict WDM's own data |

| Published | Map | Floors | Chunks | Transform | Tiles |
|---|---:|---:|---:|---|---:|

```

---

## Assistant (Build · Big Pickle · 4.7s)

_Thinking:_

Good, the edit is correct.

Now add the 7 floorless rows to the published table after uldaman, and update totals.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md",
  "newString": "| `mod-native-instance-maps.uldaman` | 70 | 2 | 52 | none | 24 |\n| `mod-native-instance-maps.hillsbrad-foothills` | 560 | 0 | 0 | none | 12 |\n| `mod-native-instance-maps.mount-hyjal` | 534 | 0 | 0 | none | 12 |\n| `mod-native-instance-maps.ruins-of-ahnqiraj` | 509 | 0 | 0 | none | 12 |\n| `mod-native-instance-maps.the-black-morass` | 269 | 0 | 0 | none | 12 |\n| `mod-native-instance-maps.zulaman` | 568 | 0 | 0 | none | 12 |\n| `mod-native-instance-maps.zulfarrak` | 209 | 0 | 0 | none | 12 |\n| `mod-native-instance-maps.zulgurub` | 309 | 0 | 0 | none | 12 |\n\nThe last seven rows are **floorless** maps: real, addressable world maps that own\nno `DungeonMap` row. They are described in\n[Floorless maps](#floorless-maps) below.\n\nTotals: **113 floors, 1310 chunks, 50 areas, 4 transforms, 1476 tiles.** Each is a\n`mod-content-manager` manifest in `content/<slug>/manifest.json` plus a\ndeterministic EPF in `dist/`, and all 50 compose into one release EPF. No DBC is\nshipped; composition is `mod-content-manager`'s.",
  "oldString": "| `mod-native-instance-maps.uldaman` | 70 | 2 | 52 | none | 24 |\n\nTotals: **113 floors, 1310 chunks, 43 areas, 4 transforms, 1392 tiles.** Each is a\n`mod-content-manager` manifest in `content/<slug>/manifest.json` plus a\ndeterministic EPF in `dist/`, and all 43 compose into one release EPF. No DBC is\nshipped; composition is `mod-content-manager`'s."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.9s)

_Thinking:_

Wait, I wrote "**113 floors, 1310 chunks, 50 areas, 4 transforms, 1476 tiles.**" — good.

Now I need to add a "Floorless maps" section. And update the "What changed" section, Karazhan, through CM, artifacts, why withheld, coverage, verification, recommendations.

Let me add a Floorless maps section. Good place: after the "What changed, and why" intro or as section 4/5. Actually the "What changed" has subsections 1-4. Let me add a section after "### What was *not* changed". Actually the floorless change is a real new capability, so it belongs in "What changed" as item 5. But it's substantial; maybe a top-level section "## Floorless maps" before "## Karazhan".

Let me look at the transition region around line 140-150.

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md",
  "limit": 30,
  "offset": 146
}
```

**Output:**
```
<path>/home/smithkt/git/mod-native-instance-maps/reports/final-report.md</path>
<type>file</type>
<content>
146: 
147: `SAFE / REVIEW / UNSAFE` became `SAFE / UNSAFE`, with a closed
148: `UNSAFE_REASONS` set. A third level that nothing could leave was a backlog, not a
149: classification: a map is either publishable from the vendored source, or it is
150: blocked with the reason codes that blocked it.
151: 
152: ### What was *not* changed
153: 
154: No transform is derived, allocated or synthesized. The refutation in
155: [transform-analysis.md](transform-analysis.md) still stands: for a multi-floor map
156: the default floor is not recoverable from these tables, because Deadmines and
157: Deeprun Tram are indistinguishable here yet WDM chose different floors for each.
158: That analysis is now a statement about what this project will not do, rather than
159: about what it may ship.
160: 
161: ## Karazhan
162: 
163: Map 532, the multi-floor stress case the old rule excluded, and still the
164: largest single package in the release.
165: 
166: | Property | Value | Source |
167: |---|---|---|
168: | `WorldMapArea` rows | 1 (id 799, `areaId` 3457, `virtualMapId` -1, `dungeonMapId` 0) | WDM |
169: | `DungeonMap` floors | 17 (383, 385–391, 393, 398, 399, 401–406) | WDM |
170: | `DungeonMapChunk` rows | 86 | WDM |
171: | `WorldMapTransforms` rows | **0** | WDM |
172: | Artwork | 204 BLP files | WDM |
173: 
174: The declaration is compared field-for-field against the raw WDM rows, not against
175: the importer's own intermediate state, so a renumbered row, a reordered chunk

(Showing lines 146-175 of 420. Use offset=176 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 10.6s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md",
  "newString": "### What was *not* changed\n\nNo transform is derived, allocated or synthesized. The refutation in\n[transform-analysis.md](transform-analysis.md) still stands: for a multi-floor map\nthe default floor is not recoverable from these tables, because Deadmines and\nDeeprun Tram are indistinguishable here yet WDM chose different floors for each.\nThat analysis is now a statement about what this project will not do, rather than\nabout what it may ship.\n\n## Floorless maps\n\nA `no-floors` reason code used to reject eleven maps on the assumption that a\nworld map without a `DungeonMap` row was incomplete. It was the wrong assumption.\nSome zones are a single continuous world map rather than a stack of floors, so WDM\ngives them a `WorldMapArea` and artwork but no `DungeonMap` at all. Having no floor\nis not a defect; it is the map's actual shape. The defect was on this side, and it\nwas fixed in two places:\n\n- `mod-content-manager` now accepts `\"floors\": []` and `\"chunks\": []` and validates\n  the resulting *floorless* area: `dungeonMapId` `0`, no chunks, no `floorNames`,\n  and no map transform (a `WorldMapTransforms` row redirects to a floor that does\n  not exist). See the upstream guide, `docs/WORLD_MAP_DBC.md#floors-may-be-empty`.\n- `tools/instances.py` no longer emits `no-floors` at all. A floorless map is\n  judged on the same terms as any other: is its area additive, is the artwork\n  present, does it collide with stock?\n\nSeven of the eleven are additive and ship. The evidence is direct:\n\n| Map | MapID | WMA | LibMapData type | Verdict |\n|---|---:|---:|---|---|\n| `CoTHillsbradFoothills` | 560 | 734 | party (1) | SAFE |\n| `CoTMountHyjal` | 534 | 775 | raid (2) | SAFE |\n| `CoTTheBlackMorass` | 269 | 733 | party (1) | SAFE |\n| `RuinsofAhnQiraj` | 509 | 717 | raid (2) | SAFE |\n| `ZulAman` | 568 | 781 | raid (2) | SAFE |\n| `ZulFarrak` | 209 | 686 | party (1) | SAFE |\n| `ZulGurub` | 309 | 697 | raid (2) | SAFE |\n\nEach declares `\"floors\": []`, `\"chunks\": []`, `dungeonMapId` `0`, and no\n`transform`. Composing one leaves `DungeonMap.dbc`, `DungeonMapChunk.dbc` and\n`WorldMapTransforms.dbc` byte-identical to the verified stock files, and the\npackage's only lease is its `WorldMapArea` row. Because a floorless map has no\nfloor dropdown row to rename, it declares no `floorNames` and requests no\n`protected-framexml` capability at all — `mod-content-manager` records that\ncapability as a consequence of the labels, so its absence is automatic.\n\nThe other four floorless maps are UNSAFE, and not because they lack floors:\n\n| Map | Reason codes |\n|---|---|\n| `ArathiBasin` | `stock-world-map-area` |\n| `NetherstormArena` | `stock-world-map-area` |\n| `WarsongGulch` | `stock-world-map-area` |\n| `Expansion01` | `floorless-transform-reference`, `stock-world-map-area` |\n\nThe first three are PvP maps whose `WorldMapArea` rows WDM leaves untouched, so\nthere is no additive area to ship. `Expansion01` is the same stock row *and* has\n`WorldMapTransforms` rows 2 and 3 naming a floor of map 530, which owns none — the\n`floorless-transform-reference` code this work introduced to name that condition\nprecisely, replacing the old catch-all `ambiguous-transform`.\n\nScope is corroborated independently of WDM. `LibMapData` labels the seven SAFE\nmaps `party` or `raid`, and labels the four rejected ones `PvP` or `world`; the\nclassifier itself does not read `LibMapData`, so this is a check on the result, not\nan input to it. Mapster's instance list also contains nine of the eleven.\n\n## Karazhan",
  "oldString": "### What was *not* changed\n\nNo transform is derived, allocated or synthesized. The refutation in\n[transform-analysis.md](transform-analysis.md) still stands: for a multi-floor map\nthe default floor is not recoverable from these tables, because Deadmines and\nDeeprun Tram are indistinguishable here yet WDM chose different floors for each.\nThat analysis is now a statement about what this project will not do, rather than\nabout what it may ship.\n\n## Karazhan"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.0s)

_Thinking:_

Wait I ended with a sentence "Mapster's instance list also contains nine of the eleven." — I need to verify that claim. Earlier summary said "Mapster coverage 42/43 SAFE (only Deeprun absent)". So for floorless candidates, Mapster likely contains 9 of 11. But I should verify rather than assert. Let me check Mapster's InstanceMaps.lua for these names. Actually, the earlier summary bullet said "Mapster coverage 42/43 SAFE (only Deeprun absent)". That doesn't directly give floorless coverage. Let me verify before leaving the claim.

Let me grep Mapster for the 11 names.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/WDM-addons/Mapster 2>/dev/null && ls; grep -rn \"ZulFarrak\\|Zul'Farrak\\|Hyjal\\|Hillsbrad\\|BlackMorass\\|AhnQiraj\\|ZulAman\\|ZulGurub\\|ArathiBasin\\|WarsongGulch\\|Netherstorm\\|Expansion01\" InstanceMaps.lua 2>/dev/null | head -30"
}
```

**Output:**
```
Artwork
BattleMap.lua
Changelog-Mapster-1.3.9.txt
Config.lua
Coords.lua
FogClear.lua
GroupIcons.lua
InstanceMaps.lua
Libs
Locale
Mapster.lua
Mapster.toc
Scaling.lua
20:		["Zul'Farrak"] = 686,
53:		["Old Hillsbrad Foothills"] = 734,
85:		["Hyjal Summit"] = 775,

```

---

## Assistant (Build · Big Pickle · 2.4s)

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/WDM-addons/Mapster && grep -n \"686\\|734\\|775\\|733\\|717\\|781\\|697\\|529\\|489\\|566\\|530\" InstanceMaps.lua"
}
```

**Output:**
```
20:		["Zul'Farrak"] = 686,
52:		["The Black Morass"] = 733,
53:		["Old Hillsbrad Foothills"] = 734,
66:		["Gundrak"] = 530,
80:		["Ruins of Ahn'Qiraj"] = 717,
82:		["Zul'Gurub"] = 697,
85:		["Hyjal Summit"] = 775,
96:		["Ulduar"] = 529,

```

---

## Assistant (Build · Big Pickle · 4.1s)

_Thinking:_

Mapster has these WMA IDs:
- Zul'Farrak 686 ✓
- The Black Morass 733 ✓
- Old Hillsbrad Foothills 734 ✓
- Ruins of Ahn'Qiraj 717 ✓
- Zul'Gurub 697 ✓
- Hyjal Summit 775 ✓
- Zul'Aman? grep for 781 didn't show. Let me search for Zul'Aman.

The grep for 781 returned nothing, so Zul'Aman absent. And map IDs 529/489/566/530 lines shown are coincidental (Gundrak=530, Ulduar=529). So Mapster covers 6 of the 7 SAFE floorless maps and 0 of the 4 rejected (their 529/530 matches are different maps' WMA IDs).

So my claim "nine of the eleven" is wrong. Let me correct to "six of the seven SAFE floorless maps". Let me verify Zul'Aman specifically.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/WDM-addons/Mapster && grep -in \"zul'aman\\|zulaman\\|zul aman\\|warsong\\|arathi\\|netherstorm\\|expansion\" InstanceMaps.lua"
}
```

**Output:**
```
107:		["Warsong Gulch"] = 443,
108:		["Arathi Basin"] = 461,

```

---

## Assistant (Build · Big Pickle · 5.5s)

_Thinking:_

Mapster:
- SAFE floorless covered: Zul'Farrak 686, Black Morass 733, Old Hillsbrad 734, Ahn'Qiraj 717, Zul'Gurub 697, Hyjal Summit 775 = 6 of 7. Zul'Aman 781 absent.
- Rejected: Warsong Gulch 443 and Arathi Basin 461 are listed in Mapster — but those are their PvP WMA IDs, and Mapster is an addon that maps instance names to WMA IDs generically, not a scope authority. Netherstorm and Expansion01 absent.

So my claim should be corrected. Actually, the Mapster evidence is weak/noisy here (it includes the PvP maps too). Let me just state accurately: Mapster lists 6 of the 7 SAFE floorless maps (all but Zul'Aman 781), and also lists Arathi Basin and Warsong Gulch under their PvP area IDs, which is why Mapster is corroboration only, not the classifier. Hmm, that's a lot of nuance. 

Simpler: Drop the Mapster sentence or make it precise. Let me replace with the accurate LibMapData statement only, since that's the clean independent evidence I already have. I'll remove the Mapster claim to avoid overclaiming.

Actually, better to state it accurately as additional corroboration but note its limit. Let me just say: "Mapster lists six of the seven SAFE floorless maps (all but `ZulAman`)." That's accurate and modest.

Let me fix.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md",
  "newString": "Scope is corroborated independently of WDM. `LibMapData` labels the seven SAFE\nmaps `party` or `raid`, and labels the four rejected ones `PvP` or `world`; the\nclassifier itself does not read `LibMapData`, so this is a check on the result, not\nan input to it. Mapster independently lists six of the seven SAFE floorless maps\n(all but `ZulAman`).",
  "oldString": "Scope is corroborated independently of WDM. `LibMapData` labels the seven SAFE\nmaps `party` or `raid`, and labels the four rejected ones `PvP` or `world`; the\nclassifier itself does not read `LibMapData`, so this is a check on the result, not\nan input to it. Mapster's instance list also contains nine of the eleven."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.3s)

Now the "Through mod-content-manager" compose table and surrounding text.

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md",
  "limit": 55,
  "offset": 253
}
```

**Output:**
```
<path>/home/smithkt/git/mod-native-instance-maps/reports/final-report.md</path>
<type>file</type>
<content>
253: | `WorldMapArea` | 108 | 151 | 43 |
254: | `WorldMapTransforms` | 9 | 13 | 4 |
255: 
256: Verified for every package, Karazhan included:
257: 
258: - no `WorldMapTransforms` request, no lease, no composed row, for the 39 maps WDM
259:   does not transform — so the composed table gains exactly WDM's 4 rows;
260: - every stock row and every stock string byte survives composition in place, so
261:   no verified row was edited;
262: - every appended row is leased at its declared WDM ID, and none collides with a
263:   stock ID;
264: - every authored row reads back out of the staged `DBFilesClient` file identical
265:   to the composed bytes;
266: - the parity artifact verifies, with a `WorldMapTransforms` hash recorded for
267:   the 4 transformed maps and none for the other 39 — because upstream refuses a
268:   hash for a table with no lease;
269: - a counterfactual confirms that supplying a transform *would* have produced one
270:   request, one lease and one row, so the zeroes are measured, not unchecked.
271: 
272: ## Artifacts
273: 
274: Deterministic EPFs, stored uncompressed with `manifest.json` first and a fixed
275: 1980 timestamp. `dist/` holds 44 files: 43 individual packages plus the combined
276: `dist/mod-native-instance-maps.epf` (63,086,428 bytes).
277: 
278: The four packages that shipped before the expansion are byte-pinned in
279: `tests/run_tests.py`, so a change to the description builder or the semantic
280: projection cannot silently rewrite a released manifest:
281: 
282: | Package | SHA-256 | Bytes |
283: |---|---|---:|
284: | `mod-native-instance-maps.karazhan.epf` | `612feb7ecf66d52e297a667c785fc751f44fa18348c6c23b77fa60be82836e5a` | 9,220,306 |
285: | `mod-native-instance-maps.deeprun-tram.epf` | `20dc20ae161184d360bbd55f4c91046d8622fffa2832562da82a245832237154` | 1,085,559 |
286: | `mod-native-instance-maps.the-deadmines.epf` | `9f15c23875838f4d819b292c67e1b42a3036ab80cc6343ab05b3409d9001fb59` | 1,088,281 |
287: | `mod-native-instance-maps.temple-of-atal-hakkar.epf` | `512db08dcb246ca23b50e25540738470facb604c73bd13b4edf09ebd2c45ea27` | 1,637,085 |
288: 
289: Nothing was deployed. `dist/` is gitignored; the committed artifacts are the
290: manifests.
291: 
292: ## Provenance and integrity
293: 
294: - WDM-patch revision `5e7e9d1957211f40c9636a9f417901d153b40d4d`, vendored
295:   read-only under `upstream/WDM-patch/` and recorded in
296:   `upstream/WDM-patch/SOURCE.json` as `modified: false`.
297: - `sha256sum -c ../SHA256SUMS`, run from `upstream/WDM-patch/Stable`:
298:   **17,072 OK, 0 FAILED.**
299: - `git status --porcelain upstream/` reports **0 changes**.
300: - All WDM locales ship byte-identical `DBFilesClient` tables; `enUS` is the
301:   representative tree.
302: 
303: ## Forensics
304: 
305: Full detail in [wdm-stable-audit.md](wdm-stable-audit.md). Summary:
306: 
307: | Table | Stock | WDM | Added IDs | Removed | Modified | Byte-identical |

(Showing lines 253-307 of 478. Use offset=308 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 2.2s)

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md",
  "limit": 14,
  "offset": 244
}
```

**Output:**
```
<path>/home/smithkt/git/mod-native-instance-maps/reports/final-report.md</path>
<type>file</type>
<content>
244: ```
245: 
246: The 43 individual packages and the combined release all pass. The release composes
247: as:
248: 
249: | Table | Stock rows | Composed rows | Added |
250: |---|---:|---:|---:|
251: | `DungeonMap` | 55 | 168 | 113 |
252: | `DungeonMapChunk` | 622 | 1932 | 1310 |
253: | `WorldMapArea` | 108 | 151 | 43 |
254: | `WorldMapTransforms` | 9 | 13 | 4 |
255: 
256: Verified for every package, Karazhan included:
257: 

(Showing lines 244-257 of 478. Use offset=258 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 7.2s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md",
  "newString": "The 50 individual packages and the combined release all pass. The release composes\nas:\n\n| Table | Stock rows | Composed rows | Added |\n|---|---:|---:|---:|\n| `DungeonMap` | 55 | 168 | 113 |\n| `DungeonMapChunk` | 622 | 1932 | 1310 |\n| `WorldMapArea` | 108 | 158 | 50 |\n| `WorldMapTransforms` | 9 | 13 | 4 |\n\nThe floorless maps add only `WorldMapArea` rows: the other three tables gain\nnothing from them, and each composed file is the verified stock file byte for\nbyte. A floorless package's sole lease is its `WorldMapArea` row.\n\nVerified for every package, Karazhan included:\n\n- no `WorldMapTransforms` request, no lease, no composed row, for the 46 maps WDM\n  does not transform — so the composed table gains exactly WDM's 4 rows;\n- every stock row and every stock string byte survives composition in place, so\n  no verified row was edited;\n- every appended row is leased at its declared WDM ID, and none collides with a\n  stock ID;\n- every authored row reads back out of the staged `DBFilesClient` file identical\n  to the composed bytes;\n- the parity artifact verifies, with a `WorldMapTransforms` hash recorded for\n  the 4 transformed maps and none for the other 46 — because upstream refuses a\n  hash for a table with no lease;\n- a counterfactual confirms that supplying a transform *would* have produced one\n  request, one lease and one row, so the zeroes are measured, not unchecked.\n\n## Artifacts\n\nDeterministic EPFs, stored uncompressed with `manifest.json` first and a fixed\n1980 timestamp. `dist/` holds 51 files: 50 individual packages plus the combined\n`dist/mod-native-instance-maps.epf` (66,880,859 bytes). All 51 are byte-reproducible\nacross two builds, and the 43 packages that predate the floorless work are\nbyte-identical to their pre-change hashes; only the combined release changed,\nbecause it now contains seven more maps.",
  "oldString": "The 43 individual packages and the combined release all pass. The release composes\nas:\n\n| Table | Stock rows | Composed rows | Added |\n|---|---:|---:|---:|\n| `DungeonMap` | 55 | 168 | 113 |\n| `DungeonMapChunk` | 622 | 1932 | 1310 |\n| `WorldMapArea` | 108 | 151 | 43 |\n| `WorldMapTransforms` | 9 | 13 | 4 |\n\nVerified for every package, Karazhan included:\n\n- no `WorldMapTransforms` request, no lease, no composed row, for the 39 maps WDM\n  does not transform — so the composed table gains exactly WDM's 4 rows;\n- every stock row and every stock string byte survives composition in place, so\n  no verified row was edited;\n- every appended row is leased at its declared WDM ID, and none collides with a\n  stock ID;\n- every authored row reads back out of the staged `DBFilesClient` file identical\n  to the composed bytes;\n- the parity artifact verifies, with a `WorldMapTransforms` hash recorded for\n  the 4 transformed maps and none for the other 39 — because upstream refuses a\n  hash for a table with no lease;\n- a counterfactual confirms that supplying a transform *would* have produced one\n  request, one lease and one row, so the zeroes are measured, not unchecked.\n\n## Artifacts\n\nDeterministic EPFs, stored uncompressed with `manifest.json` first and a fixed\n1980 timestamp. `dist/` holds 44 files: 43 individual packages plus the combined\n`dist/mod-native-instance-maps.epf` (63,086,428 bytes)."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.8s)

_Thinking:_

Now the "Why 15 maps are withheld" section and downstream. Let me read it now (line numbers shifted).

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && grep -n \"Why 15\\|Why 8\\|no-floors\\|no-chunks\\|held-back\\|Held-back\\|The dominant cause\\|All 43\\|43 individual\\|149 test\\|43 published\\|1392\\|44 files\\|43 maps\\|43 compose\\|other 39\\|39 of the 43\\|43 of the 43\" reports/final-report.md"
}
```

**Output:**
```
109:`NewDungeonMapID` is never guessed from a floor. 39 of the 43 published maps carry
163:A `no-floors` reason code used to reject eleven maps on the assumption that a
174:- `tools/instances.py` no longer emits `no-floors` at all. A floorless map is
339:## Why 15 maps are withheld
345:| `ArathiBasin` | `no-chunks`, `no-floors`, `stock-world-map-area` |
346:| `CoTHillsbradFoothills` | `no-chunks`, `no-floors` |
347:| `CoTMountHyjal` | `no-chunks`, `no-floors` |
348:| `CoTTheBlackMorass` | `no-chunks`, `no-floors` |
349:| `Expansion01` | `ambiguous-transform`, `no-chunks`, `no-floors`, `stock-world-map-area` |
350:| `NetherstormArena` | `no-chunks`, `no-floors`, `stock-world-map-area` |
351:| `RuinsofAhnQiraj` | `no-chunks`, `no-floors` |
352:| `WarsongGulch` | `no-chunks`, `no-floors`, `stock-world-map-area` |
353:| `ZulAman` | `no-chunks`, `no-floors` |
354:| `ZulFarrak` | `no-chunks`, `no-floors` |
355:| `ZulGurub` | `no-chunks`, `no-floors` |
361:The dominant cause is `no-floors` plus `no-chunks` on 11 maps: WDM gives them an
397:- **Held-back areas 686, 697, 717, 733, 734, 749, 775, 781** (`ZulFarrak`,
407:| `python3 tests/run_tests.py` | **149 tests, OK, 0 skipped** |
412:| All 43 published EPF payloads vs WDM artwork | byte-for-byte, including the 48 re-cased alias tiles |
415:| No two published maps share a target or a row | 0 collisions, 1392 targets |
460:  43 published maps have no transform, and that is the correct outcome.

```

---

## Assistant (Build · Big Pickle · 2.6s)

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md",
  "limit": 55,
  "offset": 339
}
```

**Output:**
```
<path>/home/smithkt/git/mod-native-instance-maps/reports/final-report.md</path>
<type>file</type>
<content>
339: ## Why 15 maps are withheld
340: 
341: Every rejection, with its reason codes:
342: 
343: | Map | Reason codes |
344: |---|---|
345: | `ArathiBasin` | `no-chunks`, `no-floors`, `stock-world-map-area` |
346: | `CoTHillsbradFoothills` | `no-chunks`, `no-floors` |
347: | `CoTMountHyjal` | `no-chunks`, `no-floors` |
348: | `CoTTheBlackMorass` | `no-chunks`, `no-floors` |
349: | `Expansion01` | `ambiguous-transform`, `no-chunks`, `no-floors`, `stock-world-map-area` |
350: | `NetherstormArena` | `no-chunks`, `no-floors`, `stock-world-map-area` |
351: | `RuinsofAhnQiraj` | `no-chunks`, `no-floors` |
352: | `WarsongGulch` | `no-chunks`, `no-floors`, `stock-world-map-area` |
353: | `ZulAman` | `no-chunks`, `no-floors` |
354: | `ZulFarrak` | `no-chunks`, `no-floors` |
355: | `ZulGurub` | `no-chunks`, `no-floors` |
356: | `Northrend` | `stock-chunk`, `stock-floor`, `stock-world-map-area` |
357: | `WailingCaverns` | `stock-chunk`, `stock-mutation-required` |
358: | `BlackFathomDeeps` | `duplicate-artwork-alias` |
359: | `Magtheridonslair` | `duplicate-artwork-alias` |
360: 
361: The dominant cause is `no-floors` plus `no-chunks` on 11 maps: WDM gives them an
362: area and artwork but no `DungeonMap` row, so there is nothing to enter and
363: publishing them would mean inventing a floor. `Expansion01` additionally has two
364: transforms (2 and 3) for map 530, so no default floor is derivable even if the
365: floors existed.
366: 
367: `Northrend` and `WailingCaverns` are the two maps whose rows are stock IDs WDM
368: mutates or deletes. The composer's append-only contract means neither can ship.
369: 
370: `BlackFathomDeeps` and `Magtheridonslair` name no map of their own — they are
371: artwork-only directories whose tiles ship inside the `BlackfathomDeeps` and
372: `MagtheridonsLair` packages. Publishing them separately would install the same
373: artwork twice under two names.
374: 
375: Additionally, 22 maps have `DungeonMap` floor geometry but no `WorldMapArea`
376: row at all (the stock raid floors — map 631 alone contributes eight). They have
377: no map identity to build a `worldMaps[]` entry around, so they are not
378: candidates; the full table with the stock/WDM-only split is in the audit report.
379: 
380: ## WDM rows the release does not ship
381: 
382: The classifier accounts for every row WDM adds, and the release is not all of
383: them. `Discovery.coverage()` reports each table as
384: `shipped + held back + unowned = added`, and a test asserts that identity.
385: 
386: | Table | WDM added | Shipped | Held back | Unowned |
387: |---|---:|---:|---:|---:|
388: | `DungeonMap` | 113 | 113 | 0 | 0 |
389: | `DungeonMapChunk` | 1312 | 1310 | 0 | 2 |
390: | `WorldMapArea` | 51 | 43 | 8 | 0 |
391: | `WorldMapTransforms` | 4 | 4 | 0 | 0 |
392: 
393: - **Unowned chunks 1828, 1829** belong to map 631 (*Icecrown Citadel*), which has

(Showing lines 339-393 of 485. Use offset=394 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 9.4s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md",
  "newString": "## Why 8 maps are withheld\n\nEvery rejection, with its reason codes:\n\n| Map | Reason codes |\n|---|---|\n| `ArathiBasin` | `stock-world-map-area` |\n| `Expansion01` | `floorless-transform-reference`, `stock-world-map-area` |\n| `NetherstormArena` | `stock-world-map-area` |\n| `WarsongGulch` | `stock-world-map-area` |\n| `Northrend` | `stock-chunk`, `stock-floor`, `stock-world-map-area` |\n| `WailingCaverns` | `stock-chunk`, `stock-mutation-required` |\n| `BlackFathomDeeps` | `duplicate-artwork-alias` |\n| `Magtheridonslair` | `duplicate-artwork-alias` |\n\nThe four floorless maps are rejected on their own merits, not for lacking floors.\n`ArathiBasin`, `NetherstormArena` and `WarsongGulch` are PvP maps whose\n`WorldMapArea` rows WDM leaves untouched, so there is no additive area to ship.\n`Expansion01` is the same stock row *and* has `WorldMapTransforms` rows 2 and 3\nnaming a floor of map 530, which owns none — `floorless-transform-reference`\nnames that condition, and replaced the old catch-all `ambiguous-transform`.\n\n`Northrend` and `WailingCaverns` are the two maps whose rows are stock IDs WDM\nmutates or deletes. The composer's append-only contract means neither can ship.\n\n`BlackFathomDeeps` and `Magtheridonslair` name no map of their own — they are\nartwork-only directories whose tiles ship inside the `BlackfathomDeeps` and\n`MagtheridonsLair` packages. Publishing them separately would install the same\nartwork twice under two names.\n\nAdditionally, 22 maps have `DungeonMap` floor geometry but no `WorldMapArea`\nrow at all (the stock raid floors — map 631 alone contributes eight). They have\nno map identity to build a `worldMaps[]` entry around, so they are not\ncandidates; the full table with the stock/WDM-only split is in the audit report.\n\n## WDM rows the release does not ship\n\nThe classifier accounts for every row WDM adds, and the release is not all of\nthem. `Discovery.coverage()` reports each table as\n`shipped + held back + unowned = added`, and a test asserts that identity.\n\n| Table | WDM added | Shipped | Held back | Unowned |\n|---|---:|---:|---:|---:|\n| `DungeonMap` | 113 | 113 | 0 | 0 |\n| `DungeonMapChunk` | 1312 | 1310 | 0 | 2 |\n| `WorldMapArea` | 51 | 50 | 1 | 0 |\n| `WorldMapTransforms` | 4 | 4 | 0 | 0 |",
  "oldString": "## Why 15 maps are withheld\n\nEvery rejection, with its reason codes:\n\n| Map | Reason codes |\n|---|---|\n| `ArathiBasin` | `no-chunks`, `no-floors`, `stock-world-map-area` |\n| `CoTHillsbradFoothills` | `no-chunks`, `no-floors` |\n| `CoTMountHyjal` | `no-chunks`, `no-floors` |\n| `CoTTheBlackMorass` | `no-chunks`, `no-floors` |\n| `Expansion01` | `ambiguous-transform`, `no-chunks`, `no-floors`, `stock-world-map-area` |\n| `NetherstormArena` | `no-chunks`, `no-floors`, `stock-world-map-area` |\n| `RuinsofAhnQiraj` | `no-chunks`, `no-floors` |\n| `WarsongGulch` | `no-chunks`, `no-floors`, `stock-world-map-area` |\n| `ZulAman` | `no-chunks`, `no-floors` |\n| `ZulFarrak` | `no-chunks`, `no-floors` |\n| `ZulGurub` | `no-chunks`, `no-floors` |\n| `Northrend` | `stock-chunk`, `stock-floor`, `stock-world-map-area` |\n| `WailingCaverns` | `stock-chunk`, `stock-mutation-required` |\n| `BlackFathomDeeps` | `duplicate-artwork-alias` |\n| `Magtheridonslair` | `duplicate-artwork-alias` |\n\nThe dominant cause is `no-floors` plus `no-chunks` on 11 maps: WDM gives them an\narea and artwork but no `DungeonMap` row, so there is nothing to enter and\npublishing them would mean inventing a floor. `Expansion01` additionally has two\ntransforms (2 and 3) for map 530, so no default floor is derivable even if the\nfloors existed.\n\n`Northrend` and `WailingCaverns` are the two maps whose rows are stock IDs WDM\nmutates or deletes. The composer's append-only contract means neither can ship.\n\n`BlackFathomDeeps` and `Magtheridonslair` name no map of their own — they are\nartwork-only directories whose tiles ship inside the `BlackfathomDeeps` and\n`MagtheridonsLair` packages. Publishing them separately would install the same\nartwork twice under two names.\n\nAdditionally, 22 maps have `DungeonMap` floor geometry but no `WorldMapArea`\nrow at all (the stock raid floors — map 631 alone contributes eight). They have\nno map identity to build a `worldMaps[]` entry around, so they are not\ncandidates; the full table with the stock/WDM-only split is in the audit report.\n\n## WDM rows the release does not ship\n\nThe classifier accounts for every row WDM adds, and the release is not all of\nthem. `Discovery.coverage()` reports each table as\n`shipped + held back + unowned = added`, and a test asserts that identity.\n\n| Table | WDM added | Shipped | Held back | Unowned |\n|---|---:|---:|---:|---:|\n| `DungeonMap` | 113 | 113 | 0 | 0 |\n| `DungeonMapChunk` | 1312 | 1310 | 0 | 2 |\n| `WorldMapArea` | 51 | 43 | 8 | 0 |\n| `WorldMapTransforms` | 4 | 4 | 0 | 0 |"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 4.0s)

_Thinking:_

Now the held-back areas bullet. Let me read lines around 397.

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md",
  "limit": 60,
  "offset": 391
}
```

**Output:**
```
<path>/home/smithkt/git/mod-native-instance-maps/reports/final-report.md</path>
<type>file</type>
<content>
391: - **Held-back areas 686, 697, 717, 733, 734, 749, 775, 781** (`ZulFarrak`,
392:   `ZulGurub`, `RuinsofAhnQiraj`, `CoTTheBlackMorass`, `CoTHillsbradFoothills`,
393:   `WailingCaverns`, `CoTMountHyjal`, `ZulAman`) belong to the withheld maps above.
394: 
395: ## Verification evidence
396: 
397: | Check | Result |
398: |---|---|
399: | `upstream/WDM-patch/SHA256SUMS` | 17,072 OK, 0 FAILED |
400: | `git status --porcelain upstream/` | 0 changes |
401: | `python3 tests/run_tests.py` | **149 tests, OK, 0 skipped** |
402: | Deadmines vs `mod-content-manager` golden fixture | exact match on `worldMaps` and `content` |
403: | Deadmines chunk order vs WDM's shipped DBC | exact match |
404: | Karazhan declaration vs raw WDM rows | field-for-field match, 17/86/1/0/204 |
405: | Karazhan artwork vs WDM payloads | 204/204 SHA-256 match |
406: | All 43 published EPF payloads vs WDM artwork | byte-for-byte, including the 48 re-cased alias tiles |
407: | Every WDM added row accounted for | `shipped + held back + unowned = added`, all four tables |
408: | No SAFE map claims a stock ID | 0 collisions across all four tables |
409: | No two published maps share a target or a row | 0 collisions, 1392 targets |
410: | Publication set == SAFE set | 43 == 43; no UNSAFE map has a `content/` directory |
411: | The four pre-existing manifests regenerated | byte-identical, no diff |
412: | `tests/validate_epfs.py` — all 44 EPFs through the full CM pipeline | valid, staged, composed, parity verified |
413: | `WorldMapTransforms` composition | +4 rows, all WDM's; stock rows untouched |
414: | `make check` | exit 0 |
415: 
416: The golden-fixture comparison remains the load-bearing one for Deadmines: its
417: manifest is derived *only* from WDM and then compared field-for-field, in order,
418: against a manifest authored independently. It matches exactly, on both the
419: semantic block and the artwork content block.
420: 
421: ## Constraints honoured
422: 
423: 1. **Append-only** — no package replaces, removes, or renumbers a stock row.
424:    The four WDM stock mutations are reported, never shipped.
425: 2. **Fixed IDs** — manifests carry WDM's IDs verbatim.
426: 3. **Order preserved** — `DungeonMapChunk` order is WDM's declaration order.
427:    Deadmines interleaves floors 166/167 and is not ID-sorted; grouping by floor
428:    produces a different DBC. This was a real bug caught during development and
429:    is now pinned by two tests.
430: 4. **References are references** — `dungeonMapId` is carried through signed and
431:    exact, and never becomes a row of its own.
432: 5. **No invented transforms** — a transform is WDM's or absent; `NewDungeonMapID`
433:    is never guessed and no transform ID is ever allocated.
434: 6. **No DBCs in packages** — a package ships artwork plus a manifest.
435: 7. **Deterministic** — canonical JSON manifests; uncompressed EPFs with a fixed
436:    1980 timestamp, verified byte-reproducible.
437: 8. **Upstream immutable** — vendored, checksummed, never edited.
438: 9. **Prohibited repos untouched** — `mod-content-manager`, `WDM-patch`,
439:    `wdm-stock-dbc/` and `upstream/` are all read-only inputs. Nothing was
440:    committed or pushed.
441: 
442: ## Recommendations
443: 
444: - **Verify the re-cased artwork on a live client.** `BlackfathomDeeps` and
445:   `MagtheridonsLair` are the only packages whose tile *paths* differ from WDM's
446:   layout. The reasoning is that `internal_name` is the client-baked identity and
447:   the DBC spelling is the only one the client can ask for, and the bytes are
448:   WDM's unchanged. That is a static argument; it is the one claim in this release
449:   most worth confirming in game.
450: - **Do not synthesise transforms.** A hand-written transform for, say,

(Showing lines 391-450 of 479. Use offset=451 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 8.5s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md",
  "newString": "- **Held-back area 749** (`WailingCaverns`) is the single additive `WorldMapArea`\n  row not shipped, belonging to the withheld map above. The seven floorless areas\n  that used to be held back (686, 697, 717, 733, 734, 775, 781) now ship.\n\n## Verification evidence\n\n| Check | Result |\n|---|---|\n| `upstream/WDM-patch/SHA256SUMS` | 17,072 OK, 0 FAILED |\n| `git status --porcelain upstream/` | 0 changes |\n| `python3 tests/run_tests.py` | **156 tests, OK, 0 failures** |\n| `mod-content-manager` Phase 4 world-map suite | PASS, including floorless area and floorless composition |\n| Deadmines vs `mod-content-manager` golden fixture | exact match on `worldMaps` and `content` |\n| Deadmines chunk order vs WDM's shipped DBC | exact match |\n| Karazhan declaration vs raw WDM rows | field-for-field match, 17/86/1/0/204 |\n| Karazhan artwork vs WDM payloads | 204/204 SHA-256 match |\n| All 50 published EPF payloads vs WDM artwork | byte-for-byte, including the 48 re-cased alias tiles |\n| Floorless composition | `DungeonMap`/`DungeonMapChunk`/`WorldMapTransforms` byte-identical to stock; one `WorldMapArea` lease |\n| Floorless package client requirements | no `protected-framexml`, no `floorNames` |\n| Every WDM added row accounted for | `shipped + held back + unowned = added`, all four tables |\n| No SAFE map claims a stock ID | 0 collisions across all four tables |\n| No two published maps share a target or a row | 0 collisions, 1476 targets |\n| Publication set == SAFE set | 50 == 50; no UNSAFE map has a `content/` directory |\n| The 43 pre-existing EPFs regenerated | byte-identical to their pre-change hashes |\n| `tests/validate_epfs.py` — all 51 EPFs through the full CM pipeline | valid, staged, composed, parity verified |\n| Release lifecycle (build A → B → C) on the 50-map release | PASS |\n| Two consecutive full builds | all 51 EPFs byte-identical |\n| `WorldMapTransforms` composition | +4 rows, all WDM's; stock rows untouched |\n| `make check` / `make verify` | exit 0 / exit 0 |",
  "oldString": "- **Held-back areas 686, 697, 717, 733, 734, 749, 775, 781** (`ZulFarrak`,\n  `ZulGurub`, `RuinsofAhnQiraj`, `CoTTheBlackMorass`, `CoTHillsbradFoothills`,\n  `WailingCaverns`, `CoTMountHyjal`, `ZulAman`) belong to the withheld maps above.\n\n## Verification evidence\n\n| Check | Result |\n|---|---|\n| `upstream/WDM-patch/SHA256SUMS` | 17,072 OK, 0 FAILED |\n| `git status --porcelain upstream/` | 0 changes |\n| `python3 tests/run_tests.py` | **149 tests, OK, 0 skipped** |\n| Deadmines vs `mod-content-manager` golden fixture | exact match on `worldMaps` and `content` |\n| Deadmines chunk order vs WDM's shipped DBC | exact match |\n| Karazhan declaration vs raw WDM rows | field-for-field match, 17/86/1/0/204 |\n| Karazhan artwork vs WDM payloads | 204/204 SHA-256 match |\n| All 43 published EPF payloads vs WDM artwork | byte-for-byte, including the 48 re-cased alias tiles |\n| Every WDM added row accounted for | `shipped + held back + unowned = added`, all four tables |\n| No SAFE map claims a stock ID | 0 collisions across all four tables |\n| No two published maps share a target or a row | 0 collisions, 1392 targets |\n| Publication set == SAFE set | 43 == 43; no UNSAFE map has a `content/` directory |\n| The four pre-existing manifests regenerated | byte-identical, no diff |\n| `tests/validate_epfs.py` — all 44 EPFs through the full CM pipeline | valid, staged, composed, parity verified |\n| `WorldMapTransforms` composition | +4 rows, all WDM's; stock rows untouched |\n| `make check` | exit 0 |"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.9s)

_Thinking:_

Now the "149" references in recommendations and reproducing section, and "39 of the 43 published maps", and "43 of the 43" etc. Let me grep again.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && grep -n \"149\\|1392\\|43 published\\|39 of the 43\\|44 files\\|All 43\\|43 compose\\|43 individual\\|Other 42\\|other 42\\|the other 42\\|43 of 58\\|63,086,428\" reports/final-report.md"
}
```

**Output:**
```
109:`NewDungeonMapID` is never guessed from a floor. 39 of the 43 published maps carry
459:  43 published maps have no transform, and that is the correct outcome.
467:- **Only Karazhan is runtime-proven.** The other 42 are byte-for-byte WDM's data
482:the 149-test suite, and drives every EPF through the `mod-content-manager`

```

---

## Assistant (Build · Big Pickle · 2.2s)

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md",
  "limit": 40,
  "offset": 452
}
```

**Output:**
```
<path>/home/smithkt/git/mod-native-instance-maps/reports/final-report.md</path>
<type>file</type>
<content>
452:   the DBC spelling is the only one the client can ask for, and the bytes are
453:   WDM's unchanged. That is a static argument; it is the one claim in this release
454:   most worth confirming in game.
455: - **Do not synthesise transforms.** A hand-written transform for, say,
456:   *Blackrock Spire* would be a guess about client-baked behaviour wearing WDM's
457:   fixed ID, and it would be indistinguishable, in the composed DBC, from real
458:   WDM data. A missing transform is a complete row set, not a gap to fill. 39 of the
459:   43 published maps have no transform, and that is the correct outcome.
460: - **Leave WDM's within-directory casing alone.** `TheTempleOfAtalHakkar` is
461:   spelled three different ways across its three floors in one directory. It works,
462:   because the client is case-insensitive. Re-casing it would rewrite a released
463:   package to fix a non-bug, so it is recorded by a test instead.
464: - **The `-1` sentinel was a `mod-content-manager` validator bug**, now fixed
465:   upstream: treating every non-zero `dungeonMapId` as an unresolvable reference
466:   made a legitimate client value unloadable.
467: - **Only Karazhan is runtime-proven.** The other 42 are byte-for-byte WDM's data
468:   composed by the same append-only path, which is the strongest claim the
469:   evidence supports. Whether the client renders each of them as WDM intends is a
470:   question only a live client can answer, and no such claim is made here.
471: - **Re-run `make check` after any upstream refresh.** The reports are generated,
472:   so `--check` turns a stale classification into a build failure rather than a
473:   silent drift.
474: 
475: ## Reproducing
476: 
477: ```bash
478: make check
479: ```
480: 
481: Regenerates `reports/`, `content/` and `dist/` from the vendored WDM tree, runs
482: the 149-test suite, and drives every EPF through the `mod-content-manager`
483: checkout. `make verify` is the CI gate: it writes nothing and fails if any
484: committed artifact is out of date.

(End of file - total 484 lines)
</content>
```

---

## Assistant (Build · Big Pickle · 3.7s)

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && python3 - <<'PY'\nimport pathlib\np=pathlib.Path('reports/final-report.md'); s=p.read_text()\ns=s.replace(\"\"\"`NewDungeonMapID` is never guessed from a floor. 39 of the 43 published maps carry\"\"\",\n\"\"\"`NewDungeonMapID` is never guessed from a floor. 46 of the 50 published maps carry\"\"\")\ns=s.replace(\"\"\"  43 published maps have no transform, and that is the correct outcome.\"\"\",\n\"\"\"  50 published maps have no transform, and that is the correct outcome.\"\"\")\ns=s.replace(\"\"\"- **Only Karazhan is runtime-proven.** The other 42 are byte-for-byte WDM's data\"\"\",\n\"\"\"- **Only Karazhan is runtime-proven.** The other 49 are byte-for-byte WDM's data\"\"\")\ns=s.replace(\"\"\"the 149-test suite, and drives every EPF through the `mod-content-manager`\"\"\",\n\"\"\"the 156-test suite, and drives every EPF through the `mod-content-manager`\"\"\")\np.write_text(s)\nPY\ngrep -n \"46 of the 50\\|156-test\\|other 49\\|50 published maps have no transform\" reports/final-report.md"
}
```

**Output:**
```
109:`NewDungeonMapID` is never guessed from a floor. 46 of the 50 published maps carry
459:  50 published maps have no transform, and that is the correct outcome.
467:- **Only Karazhan is runtime-proven.** The other 49 are byte-for-byte WDM's data
482:the 156-test suite, and drives every EPF through the `mod-content-manager`

```

---

## Assistant (Build · Big Pickle · 3.0s)

_Thinking:_

Now I need to add a recommendation about floorless maps. Actually, let me focus on what the task requires. But first, let me update the "What changed" intro to mention floorless as a fifth change? The section says "Three rules ... and a fourth change narrowed the classifier". Now there's a fifth (or rather the no-floors change and floorless support). Let me update that intro paragraph.

Line 86-87 area. Let me read.

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md",
  "limit": 10,
  "offset": 84
}
```

**Output:**
```
<path>/home/smithkt/git/mod-native-instance-maps/reports/final-report.md</path>
<type>file</type>
<content>
84: no `DungeonMap` row. They are described in
85: [Floorless maps](#floorless-maps) below.
86: 
87: Totals: **113 floors, 1310 chunks, 50 areas, 4 transforms, 1476 tiles.** Each is a
88: `mod-content-manager` manifest in `content/<slug>/manifest.json` plus a
89: deterministic EPF in `dist/`, and all 50 compose into one release EPF. No DBC is
90: shipped; composition is `mod-content-manager`'s.
91: 
92: Per-map verdicts and reasons: [instance-candidates.md](instance-candidates.md).
93: Machine-readable form: [instance-candidates.json](instance-candidates.json).

(Showing lines 84-93 of 484. Use offset=94 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 2.2s)

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md",
  "limit": 14,
  "offset": 94
}
```

**Output:**
```
<path>/home/smithkt/git/mod-native-instance-maps/reports/final-report.md</path>
<type>file</type>
<content>
94: 
95: ## What changed, and why
96: 
97: Three rules in `tools/instances.py` blocked maps that are in fact complete, and a
98: fourth change narrowed the classifier to a terminal two-level verdict.
99: 
100: ### 1. `no-transform` is no longer a reason code
101: 
102: A missing `WorldMapTransforms` row used to fail every map WDM does not transform.
103: `mod-content-manager` supports the opposite contract: a `worldMaps[]` entry may
104: omit `transform` entirely, in which case `AppendRequests` emits no
105: `WorldMapTransforms` request, `PlanFixed` issues no lease, and `Compose` leaves
106: the verified stock file byte for byte unchanged.
107: 

(Showing lines 94-107 of 484. Use offset=108 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 3.1s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md",
  "newString": "Three rules in `tools/instances.py` blocked maps that are in fact complete, a\nfourth change narrowed the classifier to a terminal two-level verdict, and a\nfifth added first-class floorless-map support on both sides.",
  "oldString": "Three rules in `tools/instances.py` blocked maps that are in fact complete, and a\nfourth change narrowed the classifier to a terminal two-level verdict."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 5.5s)

_Thinking:_

Now let me add a recommendation for floorless maps, and check the "### 4. The verdict is terminal" then "### What was not changed". I placed the floorless section after "What was not changed". That's fine.

Let me add a recommendation bullet about floorless maps. Insert before the "Re-run make check" bullet.

Actually, the recommendations currently: re-cased artwork, do not synthesise transforms, leave casing, -1 sentinel, only Karazhan runtime-proven, re-run make check. A floorless note would be good: "Verify a floorless map on a live client" — these are the newest class. Let me add one.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md",
  "newString": "- **Verify a floorless map on a live client.** The seven floorless packages are\n  the first in this project with no `DungeonMap` row and no transform, and their\n  composed `DungeonMap.dbc`, `DungeonMapChunk.dbc` and `WorldMapTransforms.dbc`\n  are the stock files untouched. The client-side claim — that a world map with no\n  floor dropdown behaves correctly when selected — is a static argument until\n  confirmed in game.\n- **Re-run `make check` after any upstream refresh.** The reports are generated,",
  "oldString": "- **Re-run `make check` after any upstream refresh.** The reports are generated,"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 7.0s)

_Thinking:_

Now let me update the "Constraints honoured" section item 9 which says mod-content-manager is read-only. That's now false — we modified mod-content-manager. Wait, the task was to add floorless support in mod-content-manager. The original constraint said "mod-content-manager is used strictly read-only" in validate_epfs.py. Hmm, but the objective explicitly includes modifying mod-content-manager. Let me re-read the prior summary: "Add first-class floorless WorldMapArea support in mod-content-manager". So we DID modify mod-content-manager. The "prohibited repos untouched" constraint must have been about something else, or the constraint changed.

Actually the prior summary says: "no commit/push; no PTR modification; no fabricated rows... retain protections." And Phase 2 is "allow empty floors array in ContentPackage.cpp". So mod-content-manager WAS modified as part of this task. So the final report's constraint #9 "Prohibited repos untouched — mod-content-manager ... read-only" is now outdated.

But wait — the final report is a document about the mod-native-instance-maps project, whose normal contract is that it consumes mod-content-manager read-only. This task expanded scope to add upstream support. I should update that constraint to reflect that the upstream change was made deliberately as part of this work.

Hmm, but I should be careful. Let me check the validate_epf.cpp header comment which says "mod-content-manager itself is never modified." That comment is now false too since we modified mod-content-manager. But that comment refers to the harness behavior (the harness links sources read-only and doesn't modify them at runtime) — which is still true. The comment means the test tool doesn't modify CM, not that the project never changes CM. So that's fine.

For the final report constraint #9: it says "Prohibited repos untouched — mod-content-manager, WDM-patch, wdm-stock-dbc/ and upstream/ are all read-only inputs. Nothing was committed or pushed." This describes the normal boundary. But this task did modify mod-content-manager (the source for the upstream support). I should update it to be accurate: the floorless validation/parse change was made in mod-content-manager as part of this work; WDM-patch/stock/upstream remain read-only; nothing committed or pushed.

Let me update constraint 9.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md",
  "newString": "9. **Vendored inputs untouched** — `WDM-patch`, `wdm-stock-dbc/` and `upstream/`\n   are read-only inputs and were never edited. `mod-content-manager` was modified\n   deliberately: accepting and validating floorless areas is upstream work this\n   task required, and the change is confined to `ContentPackage.{h,cpp}`,\n   `tests/world_map_tests.cpp` and the world-map guide. Nothing was committed or\n   pushed.",
  "oldString": "9. **Prohibited repos untouched** — `mod-content-manager`, `WDM-patch`,\n   `wdm-stock-dbc/` and `upstream/` are all read-only inputs. Nothing was\n   committed or pushed."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.5s)

_Thinking:_

Now check whether final-report mentions the "149" test suite anywhere else, and whether there are other stale facts. Let me re-grep for key stale numbers and the "44 files"/"43" remnants.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && grep -n \"\\b43\\b\\|\\b44\\b\\|\\b15\\b\\|1392\\|149\\|63,086,428\\|thirty-nine\\|39 \" reports/final-report.md"
}
```

**Output:**
```
49:| `mod-native-instance-maps.maraudon` | 349 | 2 | 43 | none | 24 |
68:| `mod-native-instance-maps.the-mechanar` | 554 | 2 | 15 | none | 24 |
282:across two builds, and the 43 packages that predate the floorless work are
329:1. **`DungeonMap 28`** (map 43, *Wailing Caverns*) — geometry rewritten
333:2. **`DungeonMapChunk 1237`** — deleted (`MapID 43`, `DungeonMapID 28`).
334:3. **`DungeonMapChunk 1238`** — deleted (`MapID 43`, `DungeonMapID 28`).
415:| The 43 pre-existing EPFs regenerated | byte-identical to their pre-change hashes |
462:  WDM data. A missing transform is a complete row set, not a gap to fill. 39 of the

```

---

## Assistant (Build · Big Pickle · 2.7s)

_Thinking:_

Line 462 still says "39 of the". Wait, I replaced "39 of the 43 published maps have no transform" with "50 published maps have no transform". Let me check line 462.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && sed -n '458,464p' reports/final-report.md"
}
```

**Output:**
```
  most worth confirming in game.
- **Do not synthesise transforms.** A hand-written transform for, say,
  *Blackrock Spire* would be a guess about client-baked behaviour wearing WDM's
  fixed ID, and it would be indistinguishable, in the composed DBC, from real
  WDM data. A missing transform is a complete row set, not a gap to fill. 39 of the
  50 published maps have no transform, and that is the correct outcome.
- **Leave WDM's within-directory casing alone.** `TheTempleOfAtalHakkar` is

```

---

## Assistant (Build · Big Pickle · 3.3s)

_Thinking:_

My replace produced "39 of the 50 published maps" because I only replaced the substring "43 published maps have no transform" → "50 published maps have no transform", leaving "39 of the " prefix. Need to fix "39 of the 50" → "50 published maps have no transform" or "46 of the 50". Since 46 of 50 have no transform (4 declare transforms), correct is "46 of the 50". Let me fix.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/reports/final-report.md",
  "newString": "  WDM data. A missing transform is a complete row set, not a gap to fill. 46 of\n  the 50 published maps have no transform, and that is the correct outcome.",
  "oldString": "  WDM data. A missing transform is a complete row set, not a gap to fill. 39 of the\n  50 published maps have no transform, and that is the correct outcome."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 6.5s)

_Thinking:_

Now let me verify the report is internally consistent and run make verify again (which checks reports are current). Wait — `make verify` runs the generated report check. The final-report.md is hand-written, so report.py doesn't regenerate it. But actual report.py generated files (instance-candidates.md/json, wdm-stable-audit.md) need to be regenerated to match. We already regenerated them earlier per summary. But since I've now changed nothing in tools, they should be current. `make verify` passed earlier. But wait, did I change tools after the last `make verify`? No. I only changed docs and the hand-written final report, plus test files. `make verify` shouldn't care about final-report.md unless a test checks it.

Actually, one thing: the earlier test run (which I reran and passed 156) includes `test_report_on_disk_is_current`, and it passed. But I ran the native tests before editing the README and final-report. Does any test check README.md or final-report.md content? The `test_report_on_disk_is_current` checks generated reports, not the hand-written final report. Let me check if tests assert on final-report.md content (e.g. test_report_does_not_overclaim_runtime_semantics). Earlier grep showed `test_report_on_disk_is_current` in TestTransformForensics, which likely checks generated reports. But there might be tests checking README final report.

Let me just rerun the full native test suite and make verify now to be safe after doc edits.

Also I should regenerate reports to be safe, then run make verify.

But hold on: does `make check` regenerate the generated reports and then compare? Let me just run `make check` then `make verify`.

Actually a concern: I edited final-report.md by hand, which is correct per its header. But some tests might parse final-report.md. Let me check.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && grep -rn \"final-report\\|final_report\" tests/*.py tools/*.py | head"
}
```

**Output:**
```
(no output)
```

---

## Assistant (Build · Big Pickle · 12.3s)

_Thinking:_

Good, no tests reference the final report. Now let me regenerate reports via make check and verify. Actually make check regenerates reports and content. Let me run make check then make verify. But make check will also re-run validate_epfs (slow-ish) — fine.

Actually wait: I edited tools? No. So generated reports unchanged. But let me run make verify (the CI gate) to confirm nothing is stale after my doc edits.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && timeout 2000 make verify 2>&1 | tail -6; echo \"=== make verify exit: ${PIPESTATUS[0]} ===\"",
  "timeout": 2000000
}
```

**Output:**
```
test_wdm_supplied_transforms_are_marked_as_wdm_supplied (__main__.TestTransformForensics.test_wdm_supplied_transforms_are_marked_as_wdm_supplied) ... ok

----------------------------------------------------------------------
Ran 156 tests in 7.431s

OK
=== make verify exit: 0 ===

```

---

## Assistant (Build · Big Pickle · 351.8s)

_Thinking:_

Good. Now let me also verify the CM tests still pass after my edits (I changed world_map_tests.cpp after the last CM run — I changed the 43→50 counts and the comments). I ran the full phase4 after that change and it passed. But I should rerun the plain suite to make sure the default (no args) still passes.

Let me run the plain CM suite once more quickly.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-content-manager && timeout 1200 python3 tests/run_phase4.py 2>&1 | grep -E \"world_map|frame_xml|FAIL|PASS\" | tail -8; echo \"=== exit: ${PIPESTATUS[0]} ===\"",
  "timeout": 1200000
}
```

**Output:**
```
  world-map first-build planning: PASS
  world-map activation parity: PASS
  world-map dungeonMapId reference: PASS
  world-map floorless area: PASS
  world-map EPF validation: PASS
world_map: PASS
frame_xml checks passed
frame_xml: PASS
=== exit: 0 ===

```

---

## Assistant (Build · Big Pickle · 3.9s)

_Thinking:_

Now let me do a final review of the full final report for any remaining inconsistencies, and check git status of both repos.

Let me also verify the README's coverage claims and the generator reports are consistent. Let me do a final grep of README for stale numbers.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && grep -n \"\\b43\\b\\|43 \\|forty\\|39 \\|15 \\|1392\\|149\" README.md | grep -v \"MapID\\|map 43\\|43 |\" | head -20"
}
```

**Output:**
```
49:is the only name the client can ask for. Nothing else about the 1392 tiles changes.
429:- **15 maps are withheld**, each with the reason codes that rejected it. Eleven

```

---

## Assistant (Build · Big Pickle · 2.2s)

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && sed -n '420,440p' README.md"
}
```

**Output:**
```
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

```

---

## Assistant (Build · Big Pickle · 4.1s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/README.md",
  "newString": "- **8 maps are withheld**, each with the reason codes that rejected it. Four are\n  floorless maps rejected on their own merits rather than for lacking floors:\n  `ArathiBasin`, `NetherstormArena` and `WarsongGulch` are stock `WorldMapArea`\n  rows, and `Expansion01` is a stock area that also has two transforms for one\n  map. `Northrend` and `WailingCaverns` need stock rows WDM mutates or deletes,\n  which an append-only package cannot claim. `BlackFathomDeeps` and\n  `Magtheridonslair` are artwork directories that name no map of their own; their\n  tiles ship inside the two packages that do. These are source-data gaps, not\n  schema limits.",
  "oldString": "- **15 maps are withheld**, each with the reason codes that rejected it. Eleven\n  have no `DungeonMap` floor rows and no chunk rows in WDM at all, so there is\n  nothing to enter; `Expansion01` additionally has two transforms for one map.\n  `Northrend` and `WailingCaverns` need stock rows WDM mutates or deletes, which\n  an append-only package cannot claim. `BlackFathomDeeps` and `Magtheridonslair`\n  are artwork directories that name no map of their own; their tiles ship inside\n  the two packages that do. These are source-data gaps, not schema limits."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.1s)

_Thinking:_

Wait, I made a mistake. The oldString included the trailing parts that I didn't include in newString properly. Let me re-read. My newString ends with "...schema limits." and oldString ends with "...schema limits." too. But my newString dropped nothing? Let me check the file. Actually my newString included the full rewritten bullet ending in "schema limits." and oldString included the full old bullet ending in "schema limits." — that's fine. But wait, I wrote oldString as:

```
- **15 maps are withheld**, ... 
  ... 
  the two packages that do. These are source-data gaps, not schema limits.
```

and newString as the 8-maps version. That should be correct. Let me verify the file.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && sed -n '427,442p' README.md"
}
```

**Output:**
```
## Known limitations

- **8 maps are withheld**, each with the reason codes that rejected it. Four are
  floorless maps rejected on their own merits rather than for lacking floors:
  `ArathiBasin`, `NetherstormArena` and `WarsongGulch` are stock `WorldMapArea`
  rows, and `Expansion01` is a stock area that also has two transforms for one
  map. `Northrend` and `WailingCaverns` need stock rows WDM mutates or deletes,
  which an append-only package cannot claim. `BlackFathomDeeps` and
  `Magtheridonslair` are artwork directories that name no map of their own; their
  tiles ship inside the two packages that do. These are source-data gaps, not
  schema limits.
- **`dungeonMapId = -1`** is WDM's "not an instance" sentinel, used by
  `BlackTemple` and `SunwellPlateau`. It is a reference like any other, so it is
  preserved verbatim and requests nothing. `mod-content-manager` accepts it.
- **`AhnQiraj`** (map 531) points `WorldMapArea 766` at `DungeonMap 2`, a stock
  row belonging to map 574. That reference cannot resolve and the ID is not

```

---

## Assistant (Build · Big Pickle · 5.0s)

_Thinking:_

Wait — I see a bug! Line 432 now reads "map. `Northrend` and `WailingCaverns` need stock rows..." but the preceding text about BlackFathomDeeps got mangled? Let me look: 

```
  rows, and `Expansion01` is a stock area that also has two transforms for one
  map. `Northrend` and `WailingCaverns` need stock rows WDM mutates or deletes,
  which an append-only package cannot claim. `BlackFathomDeeps` and
  `Magtheridonslair` are artwork directories that name no map of their own; their
  tiles ship inside the two packages that do. These are source-data gaps, not
  schema limits.
```

That's actually coherent. Good, I was mistaken. Everything reads properly.

Wait, but did the edit accidentally remove a sentence? The original had:
```
  `Northrend` and `WailingCaverns` need stock rows WDM mutates or deletes, which
  an append-only package cannot claim. `BlackFathomDeeps` and `Magtheridonslair`
  are artwork directories that name no map of their own; their tiles ship inside
  the two packages that do. These are source-data gaps, not schema limits.
```
The new has the same. Good.

Now line 49 "1392 tiles changes" — that's about the two re-cased packages' 1392 tiles? Actually 1392 was the total tiles of the 43 packages. The sentence: "Nothing else about the 1392 tiles changes." Hmm, this refers to the two re-cased packages? Let me read context around line 44-50.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && sed -n '41,52p' README.md"
}
```

**Output:**
```
declare the transform WDM supplies, and the composed `WorldMapTransforms.dbc`
gains exactly those 4 rows over the verified stock file.

Two packages install their artwork under a name WDM does not use on disk. The
client derives the artwork directory from the `WorldMapArea.internal_name` in the
DBC row, and for these two maps WDM's directory is spelled with different
capitals — `BlackFathomDeeps` for `BlackfathomDeeps`, `Magtheridonslair` for
`MagtheridonsLair`. The package installs WDM's bytes at the DBC spelling, which
is the only name the client can ask for. Nothing else about the 1392 tiles changes.

Of the 50, seven are **floorless** maps: `hillsbrad-foothills`, `mount-hyjal`,
`ruins-of-ahnqiraj`, `the-black-morass`, `zulaman`, `zulfarrak` and `zulgurub`.

```

---

## Assistant (Build · Big Pickle · 3.1s)

_Thinking:_

Line 49 "Nothing else about the 1392 tiles changes." This now should be 1476 (total tiles across 50 packages) if it refers to all tiles. Reading it: it's in the paragraph about the two re-cased packages. The phrase "the 1392 tiles" seems to refer to all the artwork across the release. With 50 packages, it's 1476. Let me update to 1476.

Actually, wait: the paragraph is about two packages with re-cased directories. "Nothing else about the 1392 tiles changes." The 1392 is the total artwork count from before. Now total is 1476. Update.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/README.md",
  "newString": "is the only name the client can ask for. Nothing else about the 1476 tiles changes.",
  "oldString": "is the only name the client can ask for. Nothing else about the 1392 tiles changes."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.9s)

_Thinking:_

Now let me check the "1. **Append-only**... four WDM stock mutations" is still accurate — yes, WDM diverges in 4 places.

Let me also check the README's verification section for test counts / claims. Let me grep README for "tests" and "verify".

Actually, let me check the README around the "make check" / verification area for stale counts.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && grep -n \"test\\|verify\\|check\\|EPF\\|package\" README.md | grep -in \"43\\|1392\\|149\\|44\\|fifteen\\|15 \" | head"
}
```

**Output:**
```
5:44:Two packages install their artwork under a name WDM does not use on disk. The
61:434:  which an append-only package cannot claim. `BlackFathomDeeps` and
62:436:  tiles ship inside the two packages that do. These are source-data gaps, not
63:443:  re-leasable, but it is not this package's to resolve: the value is preserved
64:448:  packages install WDM's bytes at the DBC spelling. Inside

```

---

## Assistant (Build · Big Pickle · 2.8s)

_Thinking:_

That grep output is confusing due to matching. Let me just grep for specific stale phrases in README.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && grep -n \"43\\|forty\\|1392\\|149 test\\|15 maps\\|fifteen\" README.md"
}
```

**Output:**
```
(no output)
```

---

## Assistant (Build · Big Pickle · 4.1s)

_Thinking:_

Good, no stale numbers in README except the ones I updated (MapID 43 etc were excluded because grep now finds none? Actually "map 43" would match "43". Let me re-run without filters — it returned nothing, which is odd since Honorable mention "MapID 43" might not exist. Fine.)

Wait, earlier grep found line 49 with 1392, and I changed it. Now grep for "43" returns nothing? There must have been "43" somewhere like map IDs. Let me double check with a broader search. Actually grep -n "43" README.md should match any '43'. It returned no output. That's surprising because table rows have numbers like 543, 349, etc. Oh — grep "43" would match "543" and "43". Hmm, it returned nothing? That can't be right.

Oh wait, I ran `grep -n "43\|forty\|..."` and got no output. But the table has "| 543 |" which contains 43. Unless... the bash tool's grep is being weird. Let me re-run.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && grep -c \"43\" README.md; grep -n \"543\" README.md | head -3"
}
```

**Output:**
```
0

```

---

## Assistant (Build · Big Pickle · 3.3s)

_Thinking:_

Interesting! `grep -c "43" README.md` returns 0 and `grep -n "543"` returns nothing. But the table earlier showed hellfire-ramparts map 543. Let me check — maybe the README was overwritten and lost content during one of my python edits? Let me check the file length and content around the table.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && wc -l README.md && sed -n '20,40p' README.md"
}
```

**Output:**
```
476 README.md

| Package | Map | Area | Floors | Chunks | Transform | Tiles | Floor labels |
|---|---:|---|---:|---:|---|---:|---|
| `mod-native-instance-maps.ahnqiraj` | 531 | `AhnQiraj` | 3 | 50 | WDM 13 | 36 | 11 locales |
| `mod-native-instance-maps.hillsbrad-foothills` | 560 | `CoTHillsbradFoothills` | 0 | 0 | none in WDM | 12 | none (no floors) |
| `mod-native-instance-maps.mount-hyjal` | 534 | `CoTMountHyjal` | 0 | 0 | none in WDM | 12 | none (no floors) |
| `mod-native-instance-maps.ruins-of-ahnqiraj` | 509 | `RuinsofAhnQiraj` | 0 | 0 | none in WDM | 12 | none (no floors) |
| `mod-native-instance-maps.the-black-morass` | 269 | `CoTTheBlackMorass` | 0 | 0 | none in WDM | 12 | none (no floors) |
| `mod-native-instance-maps.zulaman` | 568 | `ZulAman` | 0 | 0 | none in WDM | 12 | none (no floors) |
| `mod-native-instance-maps.zulfarrak` | 209 | `ZulFarrak` | 0 | 0 | none in WDM | 12 | none (no floors) |
| `mod-native-instance-maps.zulgurub` | 309 | `ZulGurub` | 0 | 0 | none in WDM | 12 | none (no floors) |

Every map's floors are named in all eleven locales WDM publishes, taken verbatim
from WDM-addons' own `DUNGEON_FLOOR_<INSTANCE><n>` strings. Karazhan's seventeen
read `Servant's Quarters`, `Upper Livery Stables`, `The Banquet Hall` and so on
instead of the stock `Floor 1`…`Floor 17`. See
[Dungeon floor names](#dungeon-floor-names).

Karazhan carries no `WorldMapTransforms` row because WDM has none for it. The
manifest omits the key entirely, so `mod-content-manager` requests no row, leases
no ID, and composes nothing. 46 of the 50 packages take this path; the other four

```

---

## Assistant (Build · Big Pickle · 5.8s)

_Thinking:_

This is a problem! The README table got mangled. My python script that inserted the 7 new rows replaced everything between the ahnqiraj row and the uldaman row with the 7 floorless rows, deleting all the other 42 rows!

Look at my earlier python:
```python
first=next(i for i,l in enumerate(lines) if l.startswith('| `mod-native-instance-maps.ahnqiraj`'))
last=next(i for i,l in enumerate(lines) if l.startswith('| `mod-native-instance-maps.uldaman`'))
out=lines[:first+1]
for r in sorted(new,key=...): out.append(r)
out+=lines[last+1:]
```

Yes! That deleted all rows between ahnqiraj and uldaman, replacing them with just the 7 new rows. I lost 42 package rows. That's a serious regression. Also `next()` for uldaman found the last uldaman? There's only one. So indeed lines between got wiped.

But wait, `wc -l` is 476 and the file still has content. The table now only has ahnqiraj + 7 floorless = 8 rows, then "Every map's floors...". So the published package table is destroyed.

I need to restore the README from git and reapply all my edits properly. Since it's tracked and unmodified before, I can use git checkout to restore, then reapply carefully. Let me check git diff to confirm.

Actually, this is a good catch. Let me restore README.md from HEAD and re-apply the edits cleanly. But I've made several edits: 50 packages, 50 validated, 46 of 50, floorless paragraph, table rows, backlog, known limitations, 1476 tiles.

Better approach: restore from git, then reapply each edit using the edit tool (which is precise) rather than the buggy python line-slicing.

Let me first check git status/diff stat.

I introduced a serious regression: my Python insertion deleted the 42 package rows between `ahnqiraj` and `uldaman`. Restoring README from git and re-applying carefully.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && git status --short README.md && git show HEAD:README.md | wc -l && git checkout -- README.md && wc -l README.md && grep -c \"^| \\`mod-native-instance-maps\" README.md"
}
```

**Output:**
```
 M README.md
496
496 README.md
43

```

---

## Assistant (Build · Big Pickle · 10.5s)

_Thinking:_

Good, restored to 43 rows. Now reapply my README edits carefully with the edit tool.

Edits needed:
1. Line 14: "**43 packages, all validated..." → 50
2. Line 18: "All 43 also compose" → 50
3. Table: insert 7 floorless rows (26 in sorted order after ahnqiraj, 29, etc.). Better: insert each row in correct alphabetical position, or just append after uldaman as before but without deleting. The original I did appended the 7 rows after uldaman? No, the original python inserted them after ahnqiraj (sorted). Either is fine. Simplest: add them after the uldaman row at the end of the table, in a fixed order. But table is sorted alphabetically by slug currently. The inserted rows in the earlier (broken) output were right after ahnqiraj. For readability, insert each in its alphabetical slot. Let me just do 7 separate edits using unique anchors.

Actually the table is alphabetical: ahnqiraj, auchenai-crypts, black-temple, blackfathom-deeps, blackrock-depths, blackrock-spire, blackwing-lair, coilfang-reservoir, cothillsbrad? No. Let's see the order: it's sorted by internal name? ahnqiraj, auchenai-crypts, black-temple, blackfathom-deeps, blackrock-depths, blackrock-spire, blackwing-lair, coilfang-reservoir, deeprun-tram, dire-maul, gnomeregan, gruuls-lair, hellfire-ramparts, karazhan, magisters-terrace, magtheridons-lair, mana-tombs, maraudon, molten-core, onyxias-lair, ragefire-chasm, razorfen-downs, razorfen-kraul, scarlet-monastery, scholomance, sethekk-halls, shadow-labyrinth, shadowfang-keep, stratholme, sunwell-plateau, tempest-keep, temple-of-atal-hakkar, the-arcatraz, the-blood-furnace, the-botanica, the-deadmines, the-mechanar, the-shattered-halls, the-slave-pens, the-steamvault, the-stockade, the-underbog, uldaman.

So sorted by package slug. New slugs:
- hillsbrad-foothills → after hellfire-ramparts, before karazhan
- mount-hyjal → after maraudon, before molten-core? Alphabetical: magisters-terrace, magtheridons-lair, mana-tombs, maraudon, moltern-core... "mount-hyjal" vs "molten-core": m-o-l vs m-o-u, "molten" < "mount". And "mount" vs "onyxias": m < o. So mount-hyjal after molten-core, before onyxias-lair.
- ruins-of-ahnqiraj → r: ragefire-chasm, razorfen-downs, razorfen-kraul, ruins-of-ahnqiraj, scarlet-monastery. "ruins" vs "scarlet": r < s. vs "razorfen": "ra" < "ru". So after razorfen-kraul, before scarlet-monastery.
- the-black-morass → the-arcatraz, the-blood-furnace, the-botanica, the-black... "the-black" vs "the-blood": bla < blo, so after the-arcatraz, before the-blood-furnace.
- zulaman, zulfarrak, zulgurub → after uldaman at end: zulaman < zulfarrak < zulgurub.

This is getting complex. Simpler and equally valid: append all 7 after uldaman (the file's table end). But then table isn't perfectly sorted. Given the original had them sorted, but correctness matters more than sort. However, README may have a test checking table order? Native tests didn't reference README. So sorting isn't functionally required.

But to keep it clean, I'll insert in alphabetical slots. Actually, simpler: place them all at the end after uldaman, since the table ends there and a note says "The last seven rows are floorless". Hmm, but that breaks the alphabetical sort that a reader expects. Let me just do the 4 insertion points (one group for the 3 zul* at end). That's 4 edits:
- after hellfire-ramparts: hillsbrad-foothills
- after molten-core: mount-hyjal
- after razorfen-kraul: ruins-of-ahnqiraj
- after the-arcatraz: the-black-morass
- after uldaman: zulaman, zulfarrak, zulgurub

Actually wait, "the-black-morass" internal name is CoTTheBlackMorass and slug is "the-black-morass". Sorted by slug yes after the-arcatraz.

Let me verify the exact lines. Let me read the table rows I need as anchors.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && git diff --stat README.md; grep -n \"^| \\`mod-native-instance-maps.hellfire-ramparts\\`\\|^| \\`mod-native-instance-maps.molten-core\\`\\|^| \\`mod-native-instance-maps.razorfen-kraul\\`\\|^| \\`mod-native-instance-maps.the-arcatraz\\`\\|^| \\`mod-native-instance-maps.uldaman\\`\\|^\\*\\*43 packages\\|All 43 also\\|39 of the 43\\|The current backlog is 43\\|MAP=all\\` creates the 43\\|All 43 SAFE\\|the other 15\\|15 maps are withheld\\|1392 tiles\" README.md"
}
```

**Output:**
```
14:**43 packages, all validated against `mod-content-manager`'s real pipeline** —
18:`ContentServerBundle::VerifyParity()`. All 43 also compose together into one
35:| `mod-native-instance-maps.hellfire-ramparts` | 543 | `HellfireRamparts` | 1 | 3 | none in WDM | 12 | 11 locales |
41:| `mod-native-instance-maps.molten-core` | 409 | `MoltenCore` | 1 | 12 | none in WDM | 12 | 11 locales |
45:| `mod-native-instance-maps.razorfen-kraul` | 47 | `RazorfenKraul` | 1 | 25 | none in WDM | 12 | 11 locales |
55:| `mod-native-instance-maps.the-arcatraz` | 552 | `TheArcatraz` | 3 | 21 | none in WDM | 36 | 11 locales |
65:| `mod-native-instance-maps.uldaman` | 70 | `Uldaman` | 2 | 52 | none in WDM | 24 | 11 locales |
75:no ID, and composes nothing. 39 of the 43 packages take this path; the other four
84:is the only name the client can ask for. Nothing else about the 1392 tiles changes.
86:**The backlog is closed.** All 43 SAFE maps are published, listed explicitly in
87:`content/publish.json`; the other 15 discovered maps are UNSAFE and each carries
112:`MAP=all` creates the 43 approved EPFs separately. `make release` instead
202:The current backlog is 43 SAFE and 15 UNSAFE:
451:- **15 maps are withheld**, each with the reason codes that rejected it. Eleven

```

---

## Assistant (Build · Big Pickle · 3.0s)

_Thinking:_

Good. Now let me reapply each edit precisely. I'll do them one at a time.

1. Line 14 and 18.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/README.md",
  "newString": "**50 packages, all validated against `mod-content-manager`'s real pipeline** —",
  "oldString": "**43 packages, all validated against `mod-content-manager`'s real pipeline** —"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.5s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/README.md",
  "newString": "`ContentServerBundle::VerifyParity()`. All 50 also compose together into one",
  "oldString": "`ContentServerBundle::VerifyParity()`. All 43 also compose together into one"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.8s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/README.md",
  "newString": "| `mod-native-instance-maps.hellfire-ramparts` | 543 | `HellfireRamparts` | 1 | 3 | none in WDM | 12 | 11 locales |\n| `mod-native-instance-maps.hillsbrad-foothills` | 560 | `CoTHillsbradFoothills` | 0 | 0 | none in WDM | 12 | none (no floors) |",
  "oldString": "| `mod-native-instance-maps.hellfire-ramparts` | 543 | `HellfireRamparts` | 1 | 3 | none in WDM | 12 | 11 locales |"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.7s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/README.md",
  "newString": "| `mod-native-instance-maps.molten-core` | 409 | `MoltenCore` | 1 | 12 | none in WDM | 12 | 11 locales |\n| `mod-native-instance-maps.mount-hyjal` | 534 | `CoTMountHyjal` | 0 | 0 | none in WDM | 12 | none (no floors) |",
  "oldString": "| `mod-native-instance-maps.molten-core` | 409 | `MoltenCore` | 1 | 12 | none in WDM | 12 | 11 locales |"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.4s)

_Thinking:_

Wait, I need to check whether the mount-hyjal row should come before or after molten-core. Alphabetical: "molten-core" vs "mount-hyjal": m-o-l vs m-o-u → 'l'(108) < 'u'(117), so molten-core < mount-hyjal. So mount-hyjal comes after molten-core. But what comes after molten-core? Line 42 is onyxias-lair. Let me verify the edit put it between molten-core and onyxias-lair. Yes, it inserted immediately after molten-core. Good.

Now razorfen-kraul → ruins-of-ahnqiraj. "razorfen-kraul" then "ruins-of-ahnqiraj" then "scarlet-monastery". Good.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/README.md",
  "newString": "| `mod-native-instance-maps.razorfen-kraul` | 47 | `RazorfenKraul` | 1 | 25 | none in WDM | 12 | 11 locales |\n| `mod-native-instance-maps.ruins-of-ahnqiraj` | 509 | `RuinsofAhnQiraj` | 0 | 0 | none in WDM | 12 | none (no floors) |",
  "oldString": "| `mod-native-instance-maps.razorfen-kraul` | 47 | `RazorfenKraul` | 1 | 25 | none in WDM | 12 | 11 locales |"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.9s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/README.md",
  "newString": "| `mod-native-instance-maps.the-arcatraz` | 552 | `TheArcatraz` | 3 | 21 | none in WDM | 36 | 11 locales |\n| `mod-native-instance-maps.the-black-morass` | 269 | `CoTTheBlackMorass` | 0 | 0 | none in WDM | 12 | none (no floors) |",
  "oldString": "| `mod-native-instance-maps.the-arcatraz` | 552 | `TheArcatraz` | 3 | 21 | none in WDM | 36 | 11 locales |"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 6.3s)

_Thinking:_

Careful: I just made a typo in the newString! I wrote `none (no floors) |` but the actual text I intended was `none (no floors)`. Let me check — I wrote "none (no floors) |"? Looking at the tool call: `... | 12 | none (no floors) |` wait no, I wrote `none (no floors) |`. Let me look precisely:

newString ended with: `| 12 | none (no floors) |`? The text I typed: "| 12 | none (no floors) |" — hmm actually I typed "none (no floors) |"? Let me re-read my call:

```
| `mod-native-instance-maps.the-black-morass` | 269 | `CoTTheBlackMorass` | 0 | 0 | none in WDM | 12 | none (no floors) |
```

Hmm, the displayed text shows "none (no floors)"? No — it shows `none (no floors)`. Wait, I actually wrote "none (no floors)" in the call? The call shows: `| 12 | none (no floors) |`. Let me just read the file to see what's there. I'm worried I wrote "none (no floors)" vs "none (no floors)". Both look same. There's no typo visible. Let me read the file.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && grep -n \"black-morass\\|the-blood-furnace\" README.md | head"
}
```

**Output:**
```
59:| `mod-native-instance-maps.the-black-morass` | 269 | `CoTTheBlackMorass` | 0 | 0 | none in WDM | 12 | none (no floors) |
60:| `mod-native-instance-maps.the-blood-furnace` | 542 | `TheBloodFurnace` | 1 | 7 | none in WDM | 12 | 11 locales |

```

---

## Assistant (Build · Big Pickle · 4.5s)

_Thinking:_

Wait, the grep output line 59 shows `none (no floors)`? It shows "none (no floors)"? The output literally is:

`| `mod-native-instance-maps.the-black-morass` | 269 | `CoTTheBlackMorass` | 0 | 0 | none in WDM | 12 | none (no floors) |`

Hmm the terminal rendering. Let me hexdump or use read to be sure. Actually the concern: I may have typed "no floors" vs "no floors" — identical. But in my tool call I wrote `none (no floors)` — wait, I need to look at the actual characters. Let me just Read the line. The Read tool will show exact.

Actually, I realize I might have written "none (no floors)" but I intended to write it consistently. Let me compare with the other floorless rows: earlier successful ones (hillsbrad, mount-hyjal, ruins) — let me grep all and see if they match.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && grep -n \"none (no floors)\" README.md"
}
```

**Output:**
```
36:| `mod-native-instance-maps.hillsbrad-foothills` | 560 | `CoTHillsbradFoothills` | 0 | 0 | none in WDM | 12 | none (no floors) |
43:| `mod-native-instance-maps.mount-hyjal` | 534 | `CoTMountHyjal` | 0 | 0 | none in WDM | 12 | none (no floors) |
48:| `mod-native-instance-maps.ruins-of-ahnqiraj` | 509 | `RuinsofAhnQiraj` | 0 | 0 | none in WDM | 12 | none (no floors) |
59:| `mod-native-instance-maps.the-black-morass` | 269 | `CoTTheBlackMorass` | 0 | 0 | none in WDM | 12 | none (no floors) |

```

---

## Assistant (Build · Big Pickle · 4.1s)

_Thinking:_

Wait, the grep pattern "none (no floors)" matched, which means the text is "none (no floors)". But in my edit call I wrote... hmm. Let me look at the actual bytes. The displayed grep result shows "none (no floors)". But wait, I think I actually typed "none (no floors)" with a typo "no floors" vs "no floors". The grep pattern is literally "none (no floors)" and it matched all four, so all four are consistent. 

Hold on — is the text "no floors" or "no floors"? They're the same string! I'm confusing myself. "no floors" = n-o-space-f-l-o-o-r-s. Yes. Fine. There's no typo. Good.

Hmm, but actually I did write in the the-black-morass edit: `none (no floors)` — wait, I wrote "no floors)?" OK it's fine. Moving on.

Now add the three zul rows after uldaman.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/README.md",
  "newString": "| `mod-native-instance-maps.uldaman` | 70 | `Uldaman` | 2 | 52 | none in WDM | 24 | 11 locales |\n| `mod-native-instance-maps.zulaman` | 568 | `ZulAman` | 0 | 0 | none in WDM | 12 | none (no floors) |\n| `mod-native-instance-maps.zulfarrak` | 209 | `ZulFarrak` | 0 | 0 | none in WDM | 12 | none (no floors) |\n| `mod-native-instance-maps.zulgurub` | 309 | `ZulGurub` | 0 | 0 | none in WDM | 12 | none (no floors) |",
  "oldString": "| `mod-native-instance-maps.uldaman` | 70 | `Uldaman` | 2 | 52 | none in WDM | 24 | 11 locales |"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 4.1s)

_Thinking:_

Now verify the table has 50 rows and is sorted.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && grep -c \"^| \\`mod-native-instance-maps\" README.md && python3 -c \"\nimport re,pathlib\nrows=[l.split('\\`')[1].strip() for l in pathlib.Path('README.md').read_text().split('\\n') if l.startswith('| \\`mod-native-instance-maps')]\nprint('n',len(rows),'sorted',rows==sorted(rows))\nfor a,b in zip(rows,rows[1:]):\n    if a>b: print('OUT OF ORDER',a,b)\n\""
}
```

**Output:**
```
50
n 50 sorted True

```

---

## Assistant (Build · Big Pickle · 3.9s)

_Thinking:_

The table now has 50 rows and is sorted. Now reapply the remaining text edits:
- line ~75: "39 of the 43 packages" → "46 of the 50 packages"
- line ~84: 1392 → 1476
- line ~86: backlog closed 43→50, 15→8
- line ~112: MAP=all 43 → 50
- line 202: "current backlog is 43 SAFE and 15 UNSAFE" and the bullet list
- line 451: "15 maps are withheld" → 8
- Also the floorless paragraph after "is the only name the client can ask for."
- The "UNSAFE — the package would either contradict..." addition and removing `no-floors` reason table row.

Let me get current line numbers after insertion (shifted by +7).

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && grep -n \"39 of the 43\\|1392 tiles\\|The backlog is closed\\|other 15 discovered\\|MAP=all\\` creates the 43\\|current backlog is 43\\|15 maps are withheld\\|is a defect. A \\`WorldMapTransforms\\`\\|no-floors\\`\" README.md"
}
```

**Output:**
```
82:no ID, and composes nothing. 39 of the 43 packages take this path; the other four
91:is the only name the client can ask for. Nothing else about the 1392 tiles changes.
93:**The backlog is closed.** All 43 SAFE maps are published, listed explicitly in
94:`content/publish.json`; the other 15 discovered maps are UNSAFE and each carries
119:`MAP=all` creates the 43 approved EPFs separately. `make release` instead
198:| `no-floors` | WDM adds no `DungeonMap` row, so there is no floor to enter. |
209:The current backlog is 43 SAFE and 15 UNSAFE:
211:- 11 blocked on `no-floors` — WDM gives them an area and artwork but no
458:- **15 maps are withheld**, each with the reason codes that rejected it. Eleven

```

---

## Assistant (Build · Big Pickle · 2.5s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/README.md",
  "newString": "no ID, and composes nothing. 46 of the 50 packages take this path; the other four",
  "oldString": "no ID, and composes nothing. 39 of the 43 packages take this path; the other four"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 4.0s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/README.md",
  "newString": "is the only name the client can ask for. Nothing else about the 1476 tiles changes.\n\nOf the 50, seven are **floorless** maps: `hillsbrad-foothills`, `mount-hyjal`,\n`ruins-of-ahnqiraj`, `the-black-morass`, `zulaman`, `zulfarrak` and `zulgurub`.\nWDM gives them an area and artwork but no `DungeonMap` row, because the zone is\na single continuous world map rather than a set of floors. They declare\n`\"floors\": []` and `\"chunks\": []`, `dungeonMapId` `0`, and no `transform`; the\ncomposed `DungeonMap.dbc`, `DungeonMapChunk.dbc` and `WorldMapTransforms.dbc` are\nthe verified stock files byte for byte, and each package's only lease is its\n`WorldMapArea` row. They ship no floor labels because there is no floor dropdown\nrow to rename, so they do not request the `protected-framexml` capability at all.\n\n**The backlog is closed.** All 50 SAFE maps are published, listed explicitly in\n`content/publish.json`; the other 8 discovered maps are UNSAFE and each carries",
  "oldString": "is the only name the client can ask for. Nothing else about the 1392 tiles changes.\n\n**The backlog is closed.** All 43 SAFE maps are published, listed explicitly in\n`content/publish.json`; the other 15 discovered maps are UNSAFE and each carries"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 5.3s)

_Thinking:_

Oops, I introduced corruption again: "does not request the `protected-framexml` capability at all." — I wrote "does not request the `protected-framexml` capability" but inserted a backtick issue? Let me look: I wrote ``they do not request the `protected-framexml` capability at all.`` That's fine actually — "protected-framexml" in backticks.

Wait, but I wrote "do not request the `protected-framexml` capability at all." Hmm that's correct. Let me re-read my newString:

```
... They ship no floor labels because there is no floor dropdown
row to rename, so they do not request the `protected-framexml` capability at all.
```

That's fine. But earlier I had written "do not request the `protected-framexml` capability at all" — hmm wait in the previous README edit (that got wiped) I had used the same. OK.

Actually, I notice the text says "does not request the `protected-framexml`" — no, it says "do not request". Fine.

Let me verify this region.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && sed -n '88,106p' README.md"
}
```

**Output:**
```
DBC row, and for these two maps WDM's directory is spelled with different
capitals — `BlackFathomDeeps` for `BlackfathomDeeps`, `Magtheridonslair` for
`MagtheridonsLair`. The package installs WDM's bytes at the DBC spelling, which
is the only name the client can ask for. Nothing else about the 1476 tiles changes.

Of the 50, seven are **floorless** maps: `hillsbrad-foothills`, `mount-hyjal`,
`ruins-of-ahnqiraj`, `the-black-morass`, `zulaman`, `zulfarrak` and `zulgurub`.
WDM gives them an area and artwork but no `DungeonMap` row, because the zone is
a single continuous world map rather than a set of floors. They declare
`"floors": []` and `"chunks": []`, `dungeonMapId` `0`, and no `transform`; the
composed `DungeonMap.dbc`, `DungeonMapChunk.dbc` and `WorldMapTransforms.dbc` are
the verified stock files byte for byte, and each package's only lease is its
`WorldMapArea` row. They ship no floor labels because there is no floor dropdown
row to rename, so they do not request the `protected-framexml` capability at all.

**The backlog is closed.** All 50 SAFE maps are published, listed explicitly in
`content/publish.json`; the other 8 discovered maps are UNSAFE and each carries
the reason codes that rejected it. See
[reports/instance-candidates.md](reports/instance-candidates.md) for the per-map

```

---

## Assistant (Build · Big Pickle · 3.6s)

_Thinking:_

Good. Now the remaining edits: MAP=all line 119 (now shifted), the UNSAFE description addition, the no-floors reason row removal, the backlog section, and the known limitations.

Let me re-grep.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && grep -n \"MAP=all\\` creates the 43\\|no-floors\\`\\|current backlog is 43\\|15 maps are withheld\" README.md"
}
```

**Output:**
```
129:`MAP=all` creates the 43 approved EPFs separately. `make release` instead
208:| `no-floors` | WDM adds no `DungeonMap` row, so there is no floor to enter. |
219:The current backlog is 43 SAFE and 15 UNSAFE:
221:- 11 blocked on `no-floors` — WDM gives them an area and artwork but no
468:- **15 maps are withheld**, each with the reason codes that rejected it. Eleven

```

---

## Assistant (Build · Big Pickle · 2.5s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/README.md",
  "newString": "`MAP=all` creates the 50 approved EPFs separately. `make release` instead",
  "oldString": "`MAP=all` creates the 43 approved EPFs separately. `make release` instead"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.0s)

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/README.md",
  "limit": 40,
  "offset": 196
}
```

**Output:**
```
<path>/home/smithkt/git/mod-native-instance-maps/README.md</path>
<type>file</type>
<content>
196: 
197: - **SAFE** — WDM supplies every row the map needs, all of them are additive
198:   against the verified stock baseline, every reference is preserved as WDM
199:   wrote it, and the artwork directory the client derives from `internalName`
200:   exists. A `WorldMapTransforms` row is optional; its absence is not a defect.
201: - **UNSAFE** — the package would either contradict WDM's own data (it depends on
202:   a stock row that WDM mutates or deletes) or be built from source that does not
203:   add up to one. Every rejection names its causes:
204: 
205: | Reason | Meaning |
206: | --- | --- |
207: | `no-area` | WDM adds no `WorldMapArea` row, so the map is not addressable. |
208: | `no-floors` | WDM adds no `DungeonMap` row, so there is no floor to enter. |
209: | `no-chunks` | WDM adds no `DungeonMapChunk` row, so the floor has no geometry. |
210: | `stock-world-map-area` | The area is a stock row WDM mutates or deletes. |
211: | `stock-floor` | A floor is a stock `DungeonMap` row WDM mutates or deletes. |
212: | `stock-chunk` | A chunk is a stock row WDM mutates or deletes. |
213: | `stock-transform` | The transform is a stock row WDM mutates. |
214: | `ambiguous-transform` | The transform names more than one floor choice. |
215: | `duplicate-artwork-alias` | The artwork directory names a map some other candidate already owns. |
216: | `no-artwork` | The client would look for artwork WDM does not ship. |
217: | `stock-mutation-required` | A composite of the `stock-*` causes above. |
218: 
219: The current backlog is 43 SAFE and 15 UNSAFE:
220: 
221: - 11 blocked on `no-floors` — WDM gives them an area and artwork but no
222:   `DungeonMap` row, so there is nothing to enter. Publishing them would mean
223:   inventing a floor.
224: - `Northrend` — every row it needs is a stock row WDM mutates.
225: - `WailingCaverns` — needs WDM's rewritten `DungeonMap 28` and its two deleted
226:   chunk rows.
227: - `BlackFathomDeeps` and `Magtheridonslair` — artwork directories that name a map
228:   the `BlackfathomDeeps` and `MagtheridonsLair` rows already own. They ship
229:   inside those two packages instead of as packages of their own.
230: 
231: ## Dungeon floor names
232: 
233: The stock client's floor dropdown numbers a map's floors `Floor 1`…`Floor N`.
234: The client has the names; they are just not where the dropdown looks. WDM-addons
235: publishes them as ordinary Lua globals, and this project ships them:

(Showing lines 196-235 of 513. Use offset=236 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 3.2s)

_Thinking:_

Line 224-226: Wait, there's something odd at line 224-229. Let me look:
```
- `Northrend` — every row it needs is a stock row WDM mutates.
- `WailingCaverns` — needs WDM's rewritten `DungeonMap 28` and its two deleted
  chunk rows.
- `BlackFathomDeeps` and `Magtheridonslair` — artwork directories that name a map
```

That's the restored original. Now let me make the edits:
1. Line 197-200: add floorless SAFE sentence.
2. Remove `no-floors` reason row (line 208).
3. Replace line 219-229 backlog.

Also add a reason for `floorless-transform-reference` (new code). Let me check what reason codes currently exist in tools/instances.py to list accurately.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && grep -n \"UNSAFE_REASONS\\|ReasonCode\\|floorless-dungeon-map-id\\|floorless-chunk-reference\\|floorless-transform-reference\\|ambiguous-transform\" tools/instances.py | head -20"
}
```

**Output:**
```
680:UNSAFE_REASONS = frozenset(
690:        "floorless-dungeon-map-id",
691:        "floorless-chunk-reference",
692:        "floorless-transform-reference",
696:        "ambiguous-transform",
842:                "floorless-chunk-reference",
849:                "floorless-transform-reference",
856:                "floorless-dungeon-map-id",
958:            "ambiguous-transform",
998:    unknown = check.codes - UNSAFE_REASONS
1002:            f"{sorted(unknown)}; UNSAFE_REASONS is the closed set"

```

---

## Assistant (Build · Big Pickle · 2.3s)

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/tools/instances.py",
  "limit": 28,
  "offset": 680
}
```

**Output:**
```
<path>/home/smithkt/git/mod-native-instance-maps/tools/instances.py</path>
<type>file</type>
<content>
680: UNSAFE_REASONS = frozenset(
681:     {
682:         "stock-mutation-required",
683:         "artwork-not-blp",
684:         "artwork-name-ambiguous",
685:         "duplicate-artwork-alias",
686:         "no-world-map-area",
687:         "ambiguous-world-map-area",
688:         "no-artwork",
689:         "no-chunks",
690:         "floorless-dungeon-map-id",
691:         "floorless-chunk-reference",
692:         "floorless-transform-reference",
693:         "floor-zero",
694:         "chunk-field2-zero",
695:         "chunk-floor-reference-unresolvable",
696:         "ambiguous-transform",
697:         "stock-transform",
698:         "stock-world-map-area",
699:         "stock-floor",
700:         "stock-chunk",
701:         "transform-new-map-zero",
702:         "transform-target-not-a-floor",
703:         "virtual-map-pinned",
704:     }
705: )
706: 
707: 

(Showing lines 680-707 of 1009. Use offset=708 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 8.2s)

_Thinking:_

There are many reason codes. The README table lists a subset. I should update it to reflect the new codes and remove `no-floors`. But the README table is a curated list, not exhaustive (e.g. `no-area` vs `no-world-map-area`; README says `no-area` but code has `no-world-map-area`). So the README table is illustrative. I'll remove `no-floors`, update `ambiguous-transform` context, and add the three `floorless-*` codes.

Let me edit:
- SAFE bullet: add floorless sentence.
- Remove `no-floors` row.
- Add `floorless-dungeon-map-id`, `floorless-chunk-reference`, `floorless-transform-reference` rows.
- Replace backlog.

Let me do it.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/README.md",
  "newString": "  exists. A `WorldMapTransforms` row is optional; its absence is not a defect. A\n  map that owns no `DungeonMap` row is **floorless**: it is a real, addressable\n  world map with no dungeon floors, and having no floors is not itself a defect.\n- **UNSAFE** — the package would either contradict WDM's own data (it depends on\n  a stock row that WDM mutates or deletes) or be built from source that does not\n  add up to one. Every rejection names its causes:\n\n| Reason | Meaning |\n| --- | --- |\n| `no-area` | WDM adds no `WorldMapArea` row, so the map is not addressable. |\n| `no-chunks` | WDM adds no `DungeonMapChunk` row, so the floor has no geometry. |\n| `floorless-dungeon-map-id` | A floorless area names a `DungeonMap` floor it owns none of. |\n| `floorless-chunk-reference` | A floorless area owns `DungeonMapChunk` rows, which belong to a floor. |\n| `floorless-transform-reference` | A floorless map declares a transform that redirects to a floor it does not own. |\n| `stock-world-map-area` | The area is a stock row WDM mutates or deletes. |\n| `stock-floor` | A floor is a stock `DungeonMap` row WDM mutates or deletes. |\n| `stock-chunk` | A chunk is a stock row WDM mutates or deletes. |\n| `stock-transform` | The transform is a stock row WDM mutates. |\n| `ambiguous-transform` | The transform names more than one floor choice. |\n| `duplicate-artwork-alias` | The artwork directory names a map some other candidate already owns. |\n| `no-artwork` | The client would look for artwork WDM does not ship. |\n| `stock-mutation-required` | A composite of the `stock-*` causes above. |\n\nThe current backlog is 50 SAFE and 8 UNSAFE:\n\n- Four floorless maps are rejected on their own merits, not for lacking floors:\n  `ArathiBasin`, `NetherstormArena` and `WarsongGulch` are PvP maps whose\n  `WorldMapArea` rows WDM leaves untouched, and `Expansion01` is a stock area\n  that also has two transforms for map 530.\n- `Northrend` — every row it needs is a stock row WDM mutates.\n- `WailingCaverns` — needs WDM's rewritten `DungeonMap 28` and its two deleted\n  chunk rows.\n- `BlackFathomDeeps` and `Magtheridonslair` — artwork directories that name a map\n  the `BlackfathomDeeps` and `MagtheridonsLair` rows already own. They ship\n  inside those two packages instead of as packages of their own.",
  "oldString": "  exists. A `WorldMapTransforms` row is optional; its absence is not a defect.\n- **UNSAFE** — the package would either contradict WDM's own data (it depends on\n  a stock row that WDM mutates or deletes) or be built from source that does not\n  add up to one. Every rejection names its causes:\n\n| Reason | Meaning |\n| --- | --- |\n| `no-area` | WDM adds no `WorldMapArea` row, so the map is not addressable. |\n| `no-floors` | WDM adds no `DungeonMap` row, so there is no floor to enter. |\n| `no-chunks` | WDM adds no `DungeonMapChunk` row, so the floor has no geometry. |\n| `stock-world-map-area` | The area is a stock row WDM mutates or deletes. |\n| `stock-floor` | A floor is a stock `DungeonMap` row WDM mutates or deletes. |\n| `stock-chunk` | A chunk is a stock row WDM mutates or deletes. |\n| `stock-transform` | The transform is a stock row WDM mutates. |\n| `ambiguous-transform` | The transform names more than one floor choice. |\n| `duplicate-artwork-alias` | The artwork directory names a map some other candidate already owns. |\n| `no-artwork` | The client would look for artwork WDM does not ship. |\n| `stock-mutation-required` | A composite of the `stock-*` causes above. |\n\nThe current backlog is 43 SAFE and 15 UNSAFE:\n\n- 11 blocked on `no-floors` — WDM gives them an area and artwork but no\n  `DungeonMap` row, so there is nothing to enter. Publishing them would mean\n  inventing a floor.\n- `Northrend` — every row it needs is a stock row WDM mutates.\n- `WailingCaverns` — needs WDM's rewritten `DungeonMap 28` and its two deleted\n  chunk rows.\n- `BlackFathomDeeps` and `Magtheridonslair` — artwork directories that name a map\n  the `BlackfathomDeeps` and `MagtheridonsLair` rows already own. They ship\n  inside those two packages instead of as packages of their own."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 4.7s)

_Thinking:_

Now the known limitations bullet. Let me update it.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/README.md",
  "newString": "- **8 maps are withheld**, each with the reason codes that rejected it. Four are\n  floorless maps rejected on their own merits rather than for lacking floors:\n  `ArathiBasin`, `NetherstormArena` and `WarsongGulch` are stock `WorldMapArea`\n  rows, and `Expansion01` is a stock area that also has two transforms for one\n  map. `Northrend` and `WailingCaverns` need stock rows WDM mutates or deletes,\n  which an append-only package cannot claim. `BlackFathomDeeps` and\n  `Magtheridonslair` are artwork directories that name no map of their own; their\n  tiles ship inside the two packages that do. These are source-data gaps, not\n  schema limits.",
  "oldString": "- **15 maps are withheld**, each with the reason codes that rejected it. Eleven\n  have no `DungeonMap` floor rows and no chunk rows in WDM at all, so there is\n  nothing to enter; `Expansion01` additionally has two transforms for one map.\n  `Northrend` and `WailingCaverns` need stock rows WDM mutates or deletes, which\n  an append-only package cannot claim. `BlackFathomDeeps` and `Magtheridonslair`\n  are artwork directories that name no map of their own; their tiles ship inside\n  the two packages that do. These are source-data gaps, not schema limits."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.0s)

_Thinking:_

Wait, I again mangled the ending. My newString ends with "schema limits." but I wrote "These are source-data gaps, not\n  schema limits." — that's fine. But I dropped the two packages sentence? Let me compare:

Original ending: "...their tiles ship inside\n  the two packages that do. These are source-data gaps, not schema limits."

My newString: "...their\n  tiles ship inside the two packages that do. These are source-data gaps, not\n  schema limits."

Wait, in my newString I wrote "tiles ship inside the two packages that do. These are source-data gaps, not schema limits." Yes that's complete. Good. Let me verify.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && sed -n '470,486p' README.md"
}
```

**Output:**
```

## Known limitations

- **8 maps are withheld**, each with the reason codes that rejected it. Four are
  floorless maps rejected on their own merits rather than for lacking floors:
  `ArathiBasin`, `NetherstormArena` and `WarsongGulch` are stock `WorldMapArea`
  rows, and `Expansion01` is a stock area that also has two transforms for one
  map. `Northrend` and `WailingCaverns` need stock rows WDM mutates or deletes,
  which an append-only package cannot claim. `BlackFathomDeeps` and
  `Magtheridonslair` are artwork directories that name no map of their own; their
  tiles ship inside the two packages that do. These are source-data gaps, not
  schema limits.
- **`dungeonMapId = -1`** is WDM's "not an instance" sentinel, used by
  `BlackTemple` and `SunwellPlateau`. It is a reference like any other, so it is
  preserved verbatim and requests nothing. `mod-content-manager` accepts it.
- **`AhnQiraj`** (map 531) points `WorldMapArea 766` at `DungeonMap 2`, a stock
  row belonging to map 574. That reference cannot resolve and the ID is not

```

---

## Assistant (Build · Big Pickle · 6.8s)

_Thinking:_

Hmm, line 476 reads: "map. `Northrend` and `WailingCaverns` need stock rows WDM mutates or deletes," but wait — there's a missing referent. Let me read carefully:

```
- **8 maps are withheld**, each with the reason codes that rejected it. Four are
  floorless maps rejected on their own merits rather than for lacking floors:
  `ArathiBasin`, `NetherstormArena` and `WarsongGulch` are stock `WorldMapArea`
  rows, and `Expansion01` is a stock area that also has two transforms for one
  map. `Northrend` and `WailingCaverns` need stock rows WDM mutates or deletes,
  which an append-only package cannot claim. `BlackFathomDeeps` and
  `Magtheridonslair` are artwork directories that name no map of their own; their
  tiles ship inside the two packages that do. These are source-data gaps, not
  schema limits.
```

This is coherent. Good. The rendering "map. `Northrend`" — fine.

Now I realize I should double check that I didn't leave a duplicate or lose content. The README is 513-ish lines. The original was 496. We added: 7 table rows + 9 lines floorless paragraph + 4 lines of new reason rows + net changes. 496 + 7 + 9 + 4 - 2 (backlog bullet reduction) ≈ 514. OK.

Let me verify the README table still has 50 rows, sorted, and the whole file has no obvious corruption. Also check for any double-inserted blocks.

Let me run a broad consistency grep.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && python3 -c \"\nimport pathlib\ns=pathlib.Path('README.md').read_text()\nprint('lines',len(s.split(chr(10))))\nfor k in ['50 packages','All 50 also','46 of the 50','All 50 SAFE','other 8','current backlog is 50','8 maps are withheld','1476 tiles']:\n    print(repr(k), s.count(k))\nfor bad in ['43 packages','39 of the 43','All 43 SAFE','other 15','15 UNSAFE','1392','no-floors']:\n    c=s.count(bad); print('BAD' if c else 'ok ', repr(bad), c)\n\""
}
```

**Output:**
```
lines 521
'50 packages' 2
'All 50 also' 1
'46 of the 50' 1
'All 50 SAFE' 1
'other 8' 1
'current backlog is 50' 1
'8 maps are withheld' 1
'1476 tiles' 1
ok  '43 packages' 0
ok  '39 of the 43' 0
ok  'All 43 SAFE' 0
ok  'other 15' 0
ok  '15 UNSAFE' 0
ok  '1392' 0
ok  'no-floors' 0

```

---

## Assistant (Build · Big Pickle · 5.7s)

_Thinking:_

Wait, '50 packages' count is 2. Let me check where both are. Line 14 "50 packages, all validated" and line 40 "46 of the 50 packages take this path" — that's "50 packages" as substring of "46 of the 50 packages". OK, count 2 is fine.

Now, one concern: does the README table now correctly list the 7 floorless rows with the right total and is the table sorted? Already verified 50 rows sorted.

Let me also double-check I removed the old `no-floors` row and the reason table is coherent. And check no duplicate floorless paragraph.

Let me look at the whole changed README diff stat. Also, I should rerun make verify to ensure no generated artifact check fails (README isn't generated, so should be fine) and confirm no test reads README. Already confirmed no test references README/final-report.

Now, let me also check the generated reports (instance-candidates.md) still reference 50/8 correctly — regenerated earlier. `make verify` passed, and `test_report_on_disk_is_current` passed, so generated reports are current.

Now, I earlier edited final-report.md with a floorless section and counted tiles 1476. But I should double check the final report had no other mangling from my edits. Let me scan the final report table for the 7 rows and totals, and ensure no content lost. Let me count published rows in final-report.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && python3 -c \"\nimport pathlib\nlines=pathlib.Path('reports/final-report.md').read_text().split(chr(10))\nrows=[l for l in lines if l.startswith('| \\`mod-native-instance-maps.') and l.endswith('|')]\nprint('published rows in final report:', len(rows))\n\" && grep -n \"Totals: \\*\\*\" reports/final-report.md"
}
```

**Output:**
```
published rows in final report: 54
87:Totals: **113 floors, 1310 chunks, 50 areas, 4 transforms, 1476 tiles.** Each is a

```

---

## Assistant (Build · Big Pickle · 3.1s)

_Thinking:_

54 rows because the "Package | SHA-256 | Bytes" table also has 4 rows starting with `| \`mod-native-instance-maps.` and the reason tables don't. 50 + 4 = 54. Good.

Now, let me do a final git diff review of both repos and check statuses. Then produce the final 29-item report and summary.

Actually, I need to also double check I haven't broken the "Every map's floors are named in all eleven locales" claim for floorless. That paragraph says "Every map's floors are named in all eleven locales" — but floorless maps have no floors. Let me read that paragraph and qualify.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && sed -n '32,40p' README.md"
}
```

**Output:**
```
| `mod-native-instance-maps.dire-maul` | 429 | `DireMaul` | 6 | 73 | none in WDM | 84 | 11 locales |
| `mod-native-instance-maps.gnomeregan` | 90 | `Gnomeregan` | 4 | 79 | none in WDM | 48 | 11 locales |
| `mod-native-instance-maps.gruuls-lair` | 565 | `GruulsLair` | 1 | 4 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.hellfire-ramparts` | 543 | `HellfireRamparts` | 1 | 3 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.hillsbrad-foothills` | 560 | `CoTHillsbradFoothills` | 0 | 0 | none in WDM | 12 | none (no floors) |
| `mod-native-instance-maps.karazhan` | 532 | `Karazhan` | 17 | 86 | none in WDM | 204 | 11 locales |
| `mod-native-instance-maps.magisters-terrace` | 585 | `MagistersTerrace` | 2 | 19 | none in WDM | 24 | 11 locales |
| `mod-native-instance-maps.magtheridons-lair` | 544 | `MagtheridonsLair`<br>(artwork `Magtheridonslair`) | 1 | 7 | none in WDM | 12 | 11 locales |
| `mod-native-instance-maps.mana-tombs` | 557 | `ManaTombs` | 1 | 14 | none in WDM | 12 | 11 locales |

```

---

## Assistant (Build · Big Pickle · 4.2s)

_Thinking:_

Wait! Line 39 shows `\`Magtheridonslair\`` with backslashes: `(artwork `Magtheridonslair`)`. But this is the restored original. Let me check — is that backslash in the original? Let me look with git diff. Actually the terminal output may be rendering backticks oddly. Let me check the raw byte with grep.

Actually, the sed output shows: `| \`mod-native-instance-maps.magtheridons-lair\` | ... | \`MagtheridonsLair\`<br>(artwork \`Magtheridonslair\`) |`. The backslashes before backticks are likely an artifact of the tool escaping? No, sed doesn't escape. Hmm, but the grep earlier also showed backticks without backslashes. This might be the Read/sed tool's rendering. Let me not worry; it's from the restored original so it's unchanged.

Wait, actually I'm now worried the table row insertion for hillsbrad put it in the wrong place. Line 35 is hellfire-ramparts, line 36 hillsbrad, line 37 karazhan. Alphabetically hellfire < hillsbrad < karazhan? "hellfire" vs "hillsbrad": h-e vs h-i → e < i, so hellfire < hillsbrad. And "hillsbrad" < "karazhan". Correct!

But wait, line numbering: earlier grep said hillsbrad at line 36. Good.

Now the "Every map's floors are named in all eleven locales" paragraph. Let me read it and qualify for floorless.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && sed -n '74,80p' README.md"
}
```

**Output:**
```
Every map's floors are named in all eleven locales WDM publishes, taken verbatim
from WDM-addons' own `DUNGEON_FLOOR_<INSTANCE><n>` strings. Karazhan's seventeen
read `Servant's Quarters`, `Upper Livery Stables`, `The Banquet Hall` and so on
instead of the stock `Floor 1`…`Floor 17`. See
[Dungeon floor names](#dungeon-floor-names).

Karazhan carries no `WorldMapTransforms` row because WDM has none for it. The

```

---

## Assistant (Build · Big Pickle · 3.1s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/smithkt/git/mod-native-instance-maps/README.md",
  "newString": "Every map that has floors has them named in all eleven locales WDM publishes,\ntaken verbatim from WDM-addons' own `DUNGEON_FLOOR_<INSTANCE><n>` strings. The\nseven floorless maps declare none, because there is no floor row to rename.\nKarazhan's seventeen read `Servant's Quarters`, `Upper Livery Stables`,\n`The Banquet Hall` and so on instead of the stock `Floor 1`…`Floor 17`. See\n[Dungeon floor names](#dungeon-floor-names).",
  "oldString": "Every map's floors are named in all eleven locales WDM publishes, taken verbatim\nfrom WDM-addons' own `DUNGEON_FLOOR_<INSTANCE><n>` strings. Karazhan's seventeen\nread `Servant's Quarters`, `Upper Livery Stables`, `The Banquet Hall` and so on\ninstead of the stock `Floor 1`…`Floor 17`. See\n[Dungeon floor names](#dungeon-floor-names)."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 5.9s)

_Thinking:_

Now let me verify the diff of README against HEAD is sane (only intended additions). Let me look at git diff stat and a summary. Since README is large, let me count added/removed lines.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && git diff --numstat README.md reports/final-report.md content/publish.json 2>/dev/null; echo \"---\"; git diff --numstat | tail -30"
}
```

**Output:**
```
51	26	README.md
8	1	content/publish.json
135	50	reports/final-report.md
---
51	26	README.md
8	1	content/publish.json
28	0	content/titles.json
135	50	reports/final-report.md
44	123	reports/instance-candidates.json
64	79	reports/instance-candidates.md
1	8	reports/wdm-stable-audit.md
254	12	tests/run_tests.py
28	6	tests/validate_epf.cpp
52	11	tools/instances.py
14	0	tools/package.py
8	4	tools/semantic.py

```

---

## Assistant (Build · Big Pickle · 2.4s)

_Thinking:_

README has 51 added, 26 removed — reasonable for the changes. But wait, the 26 removed seems high for what I did. Let me review the README diff to ensure no accidental deletion. Let me view it.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && git diff README.md"
}
```

**Output:**
```
diff --git a/README.md b/README.md
index ae44e1e..57f6d10 100644
--- a/README.md
+++ b/README.md
@@ -11,11 +11,11 @@ world-map DBCs is `mod-content-manager`'s job, not this repository's.
 
 ## What ships today
 
-**43 packages, all validated against `mod-content-manager`'s real pipeline** —
+**50 packages, all validated against `mod-content-manager`'s real pipeline** —
 `ContentPackage::Validate()`, `StageInto()`, `WorldMapDbcComposer`
 `AppendRequests`/`Compose`/`Stage` against the verified stock baseline,
 `ContentFrameXml::ComposeLua`/`ComposeToc`/`Stage`, and
-`ContentServerBundle::VerifyParity()`. All 43 also compose together into one
+`ContentServerBundle::VerifyParity()`. All 50 also compose together into one
 `dist/mod-native-instance-maps.epf`.
 
 | Package | Map | Area | Floors | Chunks | Transform | Tiles | Floor labels |
@@ -33,16 +33,19 @@ world-map DBCs is `mod-content-manager`'s job, not this repository's.
 | `mod-native-instance-maps.gnomeregan` | 90 | `Gnomeregan` | 4 | 79 | none in WDM | 48 | 11 locales |
 | `mod-native-instance-maps.gruuls-lair` | 565 | `GruulsLair` | 1 | 4 | none in WDM | 12 | 11 locales |
 | `mod-native-instance-maps.hellfire-ramparts` | 543 | `HellfireRamparts` | 1 | 3 | none in WDM | 12 | 11 locales |
+| `mod-native-instance-maps.hillsbrad-foothills` | 560 | `CoTHillsbradFoothills` | 0 | 0 | none in WDM | 12 | none (no floors) |
 | `mod-native-instance-maps.karazhan` | 532 | `Karazhan` | 17 | 86 | none in WDM | 204 | 11 locales |
 | `mod-native-instance-maps.magisters-terrace` | 585 | `MagistersTerrace` | 2 | 19 | none in WDM | 24 | 11 locales |
 | `mod-native-instance-maps.magtheridons-lair` | 544 | `MagtheridonsLair`<br>(artwork `Magtheridonslair`) | 1 | 7 | none in WDM | 12 | 11 locales |
 | `mod-native-instance-maps.mana-tombs` | 557 | `ManaTombs` | 1 | 14 | none in WDM | 12 | 11 locales |
 | `mod-native-instance-maps.maraudon` | 349 | `Maraudon` | 2 | 43 | none in WDM | 24 | 11 locales |
 | `mod-native-instance-maps.molten-core` | 409 | `MoltenCore` | 1 | 12 | none in WDM | 12 | 11 locales |
+| `mod-native-instance-maps.mount-hyjal` | 534 | `CoTMountHyjal` | 0 | 0 | none in WDM | 12 | none (no floors) |
 | `mod-native-instance-maps.onyxias-lair` | 249 | `OnyxiasLair` | 1 | 8 | none in WDM | 12 | 11 locales |
 | `mod-native-instance-maps.ragefire-chasm` | 389 | `Ragefire` | 1 | 6 | none in WDM | 12 | 11 locales |
 | `mod-native-instance-maps.razorfen-downs` | 129 | `RazorfenDowns` | 1 | 11 | none in WDM | 12 | 11 locales |
 | `mod-native-instance-maps.razorfen-kraul` | 47 | `RazorfenKraul` | 1 | 25 | none in WDM | 12 | 11 locales |
+| `mod-native-instance-maps.ruins-of-ahnqiraj` | 509 | `RuinsofAhnQiraj` | 0 | 0 | none in WDM | 12 | none (no floors) |
 | `mod-native-instance-maps.scarlet-monastery` | 189 | `ScarletMonastery` | 4 | 89 | none in WDM | 48 | 11 locales |
 | `mod-native-instance-maps.scholomance` | 289 | `Scholomance` | 4 | 26 | none in WDM | 48 | 11 locales |
 | `mod-native-instance-maps.sethekk-halls` | 556 | `SethekkHalls` | 2 | 19 | none in WDM | 24 | 11 locales |
@@ -53,6 +56,7 @@ world-map DBCs is `mod-content-manager`'s job, not this repository's.
 | `mod-native-instance-maps.tempest-keep` | 550 | `TempestKeep` | 1 | 16 | none in WDM | 12 | 11 locales |
 | `mod-native-instance-maps.temple-of-atal-hakkar` | 109 | `TheTempleOfAtalHakkar` | 3 | 75 | WDM 14 | 36 | 11 locales |
 | `mod-native-instance-maps.the-arcatraz` | 552 | `TheArcatraz` | 3 | 21 | none in WDM | 36 | 11 locales |
+| `mod-native-instance-maps.the-black-morass` | 269 | `CoTTheBlackMorass` | 0 | 0 | none in WDM | 12 | none (no floors) |
 | `mod-native-instance-maps.the-blood-furnace` | 542 | `TheBloodFurnace` | 1 | 7 | none in WDM | 12 | 11 locales |
 | `mod-native-instance-maps.the-botanica` | 553 | `TheBotanica` | 1 | 6 | none in WDM | 12 | 11 locales |
 | `mod-native-instance-maps.the-deadmines` | 36 | `TheDeadmines` | 2 | 29 | WDM 11 | 24 | 11 locales |
@@ -63,16 +67,20 @@ world-map DBCs is `mod-content-manager`'s job, not this repository's.
 | `mod-native-instance-maps.the-stockade` | 34 | `TheStockade` | 1 | 57 | none in WDM | 12 | 11 locales |
 | `mod-native-instance-maps.the-underbog` | 546 | `TheUnderbog` | 1 | 1 | none in WDM | 12 | 11 locales |
 | `mod-native-instance-maps.uldaman` | 70 | `Uldaman` | 2 | 52 | none in WDM | 24 | 11 locales |
-
-Every map's floors are named in all eleven locales WDM publishes, taken verbatim
-from WDM-addons' own `DUNGEON_FLOOR_<INSTANCE><n>` strings. Karazhan's seventeen
-read `Servant's Quarters`, `Upper Livery Stables`, `The Banquet Hall` and so on
-instead of the stock `Floor 1`…`Floor 17`. See
+| `mod-native-instance-maps.zulaman` | 568 | `ZulAman` | 0 | 0 | none in WDM | 12 | none (no floors) |
+| `mod-native-instance-maps.zulfarrak` | 209 | `ZulFarrak` | 0 | 0 | none in WDM | 12 | none (no floors) |
+| `mod-native-instance-maps.zulgurub` | 309 | `ZulGurub` | 0 | 0 | none in WDM | 12 | none (no floors) |
+
+Every map that has floors has them named in all eleven locales WDM publishes,
+taken verbatim from WDM-addons' own `DUNGEON_FLOOR_<INSTANCE><n>` strings. The
+seven floorless maps declare none, because there is no floor row to rename.
+Karazhan's seventeen read `Servant's Quarters`, `Upper Livery Stables`,
+`The Banquet Hall` and so on instead of the stock `Floor 1`…`Floor 17`. See
 [Dungeon floor names](#dungeon-floor-names).
 
 Karazhan carries no `WorldMapTransforms` row because WDM has none for it. The
 manifest omits the key entirely, so `mod-content-manager` requests no row, leases
-no ID, and composes nothing. 39 of the 43 packages take this path; the other four
+no ID, and composes nothing. 46 of the 50 packages take this path; the other four
 declare the transform WDM supplies, and the composed `WorldMapTransforms.dbc`
 gains exactly those 4 rows over the verified stock file.
 
@@ -81,10 +89,20 @@ client derives the artwork directory from the `WorldMapArea.internal_name` in th
 DBC row, and for these two maps WDM's directory is spelled with different
 capitals — `BlackFathomDeeps` for `BlackfathomDeeps`, `Magtheridonslair` for
 `MagtheridonsLair`. The package installs WDM's bytes at the DBC spelling, which
-is the only name the client can ask for. Nothing else about the 1392 tiles changes.
-
-**The backlog is closed.** All 43 SAFE maps are published, listed explicitly in
-`content/publish.json`; the other 15 discovered maps are UNSAFE and each carries
+is the only name the client can ask for. Nothing else about the 1476 tiles changes.
+
+Of the 50, seven are **floorless** maps: `hillsbrad-foothills`, `mount-hyjal`,
+`ruins-of-ahnqiraj`, `the-black-morass`, `zulaman`, `zulfarrak` and `zulgurub`.
+WDM gives them an area and artwork but no `DungeonMap` row, because the zone is
+a single continuous world map rather than a set of floors. They declare
+`"floors": []` and `"chunks": []`, `dungeonMapId` `0`, and no `transform`; the
+composed `DungeonMap.dbc`, `DungeonMapChunk.dbc` and `WorldMapTransforms.dbc` are
+the verified stock files byte for byte, and each package's only lease is its
+`WorldMapArea` row. They ship no floor labels because there is no floor dropdown
+row to rename, so they do not request the `protected-framexml` capability at all.
+
+**The backlog is closed.** All 50 SAFE maps are published, listed explicitly in
+`content/publish.json`; the other 8 discovered maps are UNSAFE and each carries
 the reason codes that rejected it. See
 [reports/instance-candidates.md](reports/instance-candidates.md) for the per-map
 verdict and reasoning; [reports/wdm-stable-audit.md](reports/wdm-stable-audit.md)
@@ -109,7 +127,7 @@ single-map selection and `MAP=all` are resolved through that allowlist;
 classification as SAFE alone never makes a map selectable. A bare `make epf`
 prints usage instead of choosing a publication scope.
 
-`MAP=all` creates the 43 approved EPFs separately. `make release` instead
+`MAP=all` creates the 50 approved EPFs separately. `make release` instead
 creates one ordinary Content Manager package containing those maps and their
 resources directly; it does not nest the individual ZIPs. The combined package
 is the canonical owner and explicitly migrates retained allocations from the
@@ -180,7 +198,9 @@ blocked, and each blocked map carries the reason codes that blocked it.
 - **SAFE** — WDM supplies every row the map needs, all of them are additive
   against the verified stock baseline, every reference is preserved as WDM
   wrote it, and the artwork directory the client derives from `internalName`
-  exists. A `WorldMapTransforms` row is optional; its absence is not a defect.
+  exists. A `WorldMapTransforms` row is optional; its absence is not a defect. A
+  map that owns no `DungeonMap` row is **floorless**: it is a real, addressable
+  world map with no dungeon floors, and having no floors is not itself a defect.
 - **UNSAFE** — the package would either contradict WDM's own data (it depends on
   a stock row that WDM mutates or deletes) or be built from source that does not
   add up to one. Every rejection names its causes:
@@ -188,8 +208,10 @@ blocked, and each blocked map carries the reason codes that blocked it.
 | Reason | Meaning |
 | --- | --- |
 | `no-area` | WDM adds no `WorldMapArea` row, so the map is not addressable. |
-| `no-floors` | WDM adds no `DungeonMap` row, so there is no floor to enter. |
 | `no-chunks` | WDM adds no `DungeonMapChunk` row, so the floor has no geometry. |
+| `floorless-dungeon-map-id` | A floorless area names a `DungeonMap` floor it owns none of. |
+| `floorless-chunk-reference` | A floorless area owns `DungeonMapChunk` rows, which belong to a floor. |
+| `floorless-transform-reference` | A floorless map declares a transform that redirects to a floor it does not own. |
 | `stock-world-map-area` | The area is a stock row WDM mutates or deletes. |
 | `stock-floor` | A floor is a stock `DungeonMap` row WDM mutates or deletes. |
 | `stock-chunk` | A chunk is a stock row WDM mutates or deletes. |
@@ -199,11 +221,12 @@ blocked, and each blocked map carries the reason codes that blocked it.
 | `no-artwork` | The client would look for artwork WDM does not ship. |
 | `stock-mutation-required` | A composite of the `stock-*` causes above. |
 
-The current backlog is 43 SAFE and 15 UNSAFE:
+The current backlog is 50 SAFE and 8 UNSAFE:
 
-- 11 blocked on `no-floors` — WDM gives them an area and artwork but no
-  `DungeonMap` row, so there is nothing to enter. Publishing them would mean
-  inventing a floor.
+- Four floorless maps are rejected on their own merits, not for lacking floors:
+  `ArathiBasin`, `NetherstormArena` and `WarsongGulch` are PvP maps whose
+  `WorldMapArea` rows WDM leaves untouched, and `Expansion01` is a stock area
+  that also has two transforms for map 530.
 - `Northrend` — every row it needs is a stock row WDM mutates.
 - `WailingCaverns` — needs WDM's rewritten `DungeonMap 28` and its two deleted
   chunk rows.
@@ -448,13 +471,15 @@ artifact.
 
 ## Known limitations
 
-- **15 maps are withheld**, each with the reason codes that rejected it. Eleven
-  have no `DungeonMap` floor rows and no chunk rows in WDM at all, so there is
-  nothing to enter; `Expansion01` additionally has two transforms for one map.
-  `Northrend` and `WailingCaverns` need stock rows WDM mutates or deletes, which
-  an append-only package cannot claim. `BlackFathomDeeps` and `Magtheridonslair`
-  are artwork directories that name no map of their own; their tiles ship inside
-  the two packages that do. These are source-data gaps, not schema limits.
+- **8 maps are withheld**, each with the reason codes that rejected it. Four are
+  floorless maps rejected on their own merits rather than for lacking floors:
+  `ArathiBasin`, `NetherstormArena` and `WarsongGulch` are stock `WorldMapArea`
+  rows, and `Expansion01` is a stock area that also has two transforms for one
+  map. `Northrend` and `WailingCaverns` need stock rows WDM mutates or deletes,
+  which an append-only package cannot claim. `BlackFathomDeeps` and
+  `Magtheridonslair` are artwork directories that name no map of their own; their
+  tiles ship inside the two packages that do. These are source-data gaps, not
+  schema limits.
 - **`dungeonMapId = -1`** is WDM's "not an instance" sentinel, used by
   `BlackTemple` and `SunwellPlateau`. It is a reference like any other, so it is
   preserved verbatim and requests nothing. `mod-content-manager` accepts it.

```

---

## Assistant (Build · Big Pickle · 3.6s)

_Thinking:_

The diff looks clean and correct. No corruption. 

Now let me reconsider the "no-floors" reason table row removal: I replaced it with the three floorless codes. Good.

One issue: the final report references `docs/WORLD_MAP_DBC.md#floors-may-be-empty` anchor. GitHub generates anchors from headings lowercased with hyphens; the heading "`floors` may be empty" → anchor `floors-may-be-empty`. Good.

Now let me also verify the CM docs edit didn't break the file and the CM tests still pass. I already ran CM phase4 after editing world_map_tests but before editing docs — docs don't affect tests. Fine.

Now, let me review the final report diff for correctness. It's 135 additions/50 removals. Let me skim the whole final report diff.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && git diff reports/final-report.md | head -200"
}
```

**Output:**
```
diff --git a/reports/final-report.md b/reports/final-report.md
index ab4052b..5e5cc1c 100644
--- a/reports/final-report.md
+++ b/reports/final-report.md
@@ -18,14 +18,14 @@ disagrees in letter case is a path to re-case, not a map to withhold.
 
 ## Verdict
 
-**43 of 58 discovered maps are shippable, and all 43 are published.** The
+**50 of 58 discovered maps are shippable, and all 50 are published.** The
 classifier is terminal — SAFE or UNSAFE — and each rejected map carries the reason
 codes that rejected it.
 
 | Level | Count | Meaning |
 |---|---:|---|
-| SAFE | 43 | every required row is additive, references are preserved as written, artwork present |
-| UNSAFE | 15 | the source does not add up to a package, or the package would contradict WDM's own data |
+| SAFE | 50 | every required row is additive, references are preserved as written, artwork present |
+| UNSAFE | 8 | the source does not add up to a package, or the package would contradict WDM's own data |
 
 | Published | Map | Floors | Chunks | Transform | Tiles |
 |---|---:|---:|---:|---|---:|
@@ -72,10 +72,21 @@ codes that rejected it.
 | `mod-native-instance-maps.the-stockade` | 34 | 1 | 57 | none | 12 |
 | `mod-native-instance-maps.the-underbog` | 546 | 1 | 1 | none | 12 |
 | `mod-native-instance-maps.uldaman` | 70 | 2 | 52 | none | 24 |
-
-Totals: **113 floors, 1310 chunks, 43 areas, 4 transforms, 1392 tiles.** Each is a
+| `mod-native-instance-maps.hillsbrad-foothills` | 560 | 0 | 0 | none | 12 |
+| `mod-native-instance-maps.mount-hyjal` | 534 | 0 | 0 | none | 12 |
+| `mod-native-instance-maps.ruins-of-ahnqiraj` | 509 | 0 | 0 | none | 12 |
+| `mod-native-instance-maps.the-black-morass` | 269 | 0 | 0 | none | 12 |
+| `mod-native-instance-maps.zulaman` | 568 | 0 | 0 | none | 12 |
+| `mod-native-instance-maps.zulfarrak` | 209 | 0 | 0 | none | 12 |
+| `mod-native-instance-maps.zulgurub` | 309 | 0 | 0 | none | 12 |
+
+The last seven rows are **floorless** maps: real, addressable world maps that own
+no `DungeonMap` row. They are described in
+[Floorless maps](#floorless-maps) below.
+
+Totals: **113 floors, 1310 chunks, 50 areas, 4 transforms, 1476 tiles.** Each is a
 `mod-content-manager` manifest in `content/<slug>/manifest.json` plus a
-deterministic EPF in `dist/`, and all 43 compose into one release EPF. No DBC is
+deterministic EPF in `dist/`, and all 50 compose into one release EPF. No DBC is
 shipped; composition is `mod-content-manager`'s.
 
 Per-map verdicts and reasons: [instance-candidates.md](instance-candidates.md).
@@ -83,8 +94,9 @@ Machine-readable form: [instance-candidates.json](instance-candidates.json).
 
 ## What changed, and why
 
-Three rules in `tools/instances.py` blocked maps that are in fact complete, and a
-fourth change narrowed the classifier to a terminal two-level verdict.
+Three rules in `tools/instances.py` blocked maps that are in fact complete, a
+fourth change narrowed the classifier to a terminal two-level verdict, and a
+fifth added first-class floorless-map support on both sides.
 
 ### 1. `no-transform` is no longer a reason code
 
@@ -95,7 +107,7 @@ omit `transform` entirely, in which case `AppendRequests` emits no
 the verified stock file byte for byte unchanged.
 
 The manifest now omits the key rather than writing `null`, and
-`NewDungeonMapID` is never guessed from a floor. 39 of the 43 published maps carry
+`NewDungeonMapID` is never guessed from a floor. 46 of the 50 published maps carry
 no transform because WDM supplies none.
 
 ### 2. `dungeonMapId` is a reference
@@ -147,6 +159,64 @@ Deeprun Tram are indistinguishable here yet WDM chose different floors for each.
 That analysis is now a statement about what this project will not do, rather than
 about what it may ship.
 
+## Floorless maps
+
+A `no-floors` reason code used to reject eleven maps on the assumption that a
+world map without a `DungeonMap` row was incomplete. It was the wrong assumption.
+Some zones are a single continuous world map rather than a stack of floors, so WDM
+gives them a `WorldMapArea` and artwork but no `DungeonMap` at all. Having no floor
+is not a defect; it is the map's actual shape. The defect was on this side, and it
+was fixed in two places:
+
+- `mod-content-manager` now accepts `"floors": []` and `"chunks": []` and validates
+  the resulting *floorless* area: `dungeonMapId` `0`, no chunks, no `floorNames`,
+  and no map transform (a `WorldMapTransforms` row redirects to a floor that does
+  not exist). See the upstream guide, `docs/WORLD_MAP_DBC.md#floors-may-be-empty`.
+- `tools/instances.py` no longer emits `no-floors` at all. A floorless map is
+  judged on the same terms as any other: is its area additive, is the artwork
+  present, does it collide with stock?
+
+Seven of the eleven are additive and ship. The evidence is direct:
+
+| Map | MapID | WMA | LibMapData type | Verdict |
+|---|---:|---:|---|---|
+| `CoTHillsbradFoothills` | 560 | 734 | party (1) | SAFE |
+| `CoTMountHyjal` | 534 | 775 | raid (2) | SAFE |
+| `CoTTheBlackMorass` | 269 | 733 | party (1) | SAFE |
+| `RuinsofAhnQiraj` | 509 | 717 | raid (2) | SAFE |
+| `ZulAman` | 568 | 781 | raid (2) | SAFE |
+| `ZulFarrak` | 209 | 686 | party (1) | SAFE |
+| `ZulGurub` | 309 | 697 | raid (2) | SAFE |
+
+Each declares `"floors": []`, `"chunks": []`, `dungeonMapId` `0`, and no
+`transform`. Composing one leaves `DungeonMap.dbc`, `DungeonMapChunk.dbc` and
+`WorldMapTransforms.dbc` byte-identical to the verified stock files, and the
+package's only lease is its `WorldMapArea` row. Because a floorless map has no
+floor dropdown row to rename, it declares no `floorNames` and requests no
+`protected-framexml` capability at all — `mod-content-manager` records that
+capability as a consequence of the labels, so its absence is automatic.
+
+The other four floorless maps are UNSAFE, and not because they lack floors:
+
+| Map | Reason codes |
+|---|---|
+| `ArathiBasin` | `stock-world-map-area` |
+| `NetherstormArena` | `stock-world-map-area` |
+| `WarsongGulch` | `stock-world-map-area` |
+| `Expansion01` | `floorless-transform-reference`, `stock-world-map-area` |
+
+The first three are PvP maps whose `WorldMapArea` rows WDM leaves untouched, so
+there is no additive area to ship. `Expansion01` is the same stock row *and* has
+`WorldMapTransforms` rows 2 and 3 naming a floor of map 530, which owns none — the
+`floorless-transform-reference` code this work introduced to name that condition
+precisely, replacing the old catch-all `ambiguous-transform`.
+
+Scope is corroborated independently of WDM. `LibMapData` labels the seven SAFE
+maps `party` or `raid`, and labels the four rejected ones `PvP` or `world`; the
+classifier itself does not read `LibMapData`, so this is a check on the result, not
+an input to it. Mapster independently lists six of the seven SAFE floorless maps
+(all but `ZulAman`).
+
 ## Karazhan
 
 Map 532, the multi-floor stress case the old rule excluded, and still the
@@ -174,19 +244,23 @@ list, a normalized signed field or an invented transform fails the suite. All
 Validate -> StageInto -> AppendRequests -> PlanFixed -> Compose -> Stage -> VerifyParity
 ```
 
-The 43 individual packages and the combined release all pass. The release composes
+The 50 individual packages and the combined release all pass. The release composes
 as:
 
 | Table | Stock rows | Composed rows | Added |
 |---|---:|---:|---:|
 | `DungeonMap` | 55 | 168 | 113 |
 | `DungeonMapChunk` | 622 | 1932 | 1310 |
-| `WorldMapArea` | 108 | 151 | 43 |
+| `WorldMapArea` | 108 | 158 | 50 |
 | `WorldMapTransforms` | 9 | 13 | 4 |
 
+The floorless maps add only `WorldMapArea` rows: the other three tables gain
+nothing from them, and each composed file is the verified stock file byte for
+byte. A floorless package's sole lease is its `WorldMapArea` row.
+
 Verified for every package, Karazhan included:
 
-- no `WorldMapTransforms` request, no lease, no composed row, for the 39 maps WDM
+- no `WorldMapTransforms` request, no lease, no composed row, for the 46 maps WDM
   does not transform — so the composed table gains exactly WDM's 4 rows;
 - every stock row and every stock string byte survives composition in place, so
   no verified row was edited;
@@ -195,7 +269,7 @@ Verified for every package, Karazhan included:
 - every authored row reads back out of the staged `DBFilesClient` file identical
   to the composed bytes;
 - the parity artifact verifies, with a `WorldMapTransforms` hash recorded for
-  the 4 transformed maps and none for the other 39 — because upstream refuses a
+  the 4 transformed maps and none for the other 46 — because upstream refuses a
   hash for a table with no lease;
 - a counterfactual confirms that supplying a transform *would* have produced one
   request, one lease and one row, so the zeroes are measured, not unchecked.
@@ -203,8 +277,11 @@ Verified for every package, Karazhan included:
 ## Artifacts
 
 Deterministic EPFs, stored uncompressed with `manifest.json` first and a fixed
-1980 timestamp. `dist/` holds 44 files: 43 individual packages plus the combined
-`dist/mod-native-instance-maps.epf` (63,086,428 bytes).
+1980 timestamp. `dist/` holds 51 files: 50 individual packages plus the combined
+`dist/mod-native-instance-maps.epf` (66,880,859 bytes). All 51 are byte-reproducible
+across two builds, and the 43 packages that predate the floorless work are
+byte-identical to their pre-change hashes; only the combined release changed,
+because it now contains seven more maps.
 
 The four packages that shipped before the expansion are byte-pinned in
 `tests/run_tests.py`, so a change to the description builder or the semantic
@@ -260,33 +337,27 @@ reportable but not shippable.
 Consequence: *Wailing Caverns* is UNSAFE, because its instance only works with
 WDM's rewritten floor and its deleted chunk rows.
 
-## Why 15 maps are withheld
+## Why 8 maps are withheld
 
 Every rejection, with its reason codes:
 
 | Map | Reason codes |
 |---|---|
-| `ArathiBasin` | `no-chunks`, `no-floors`, `stock-world-map-area` |
-| `CoTHillsbradFoothills` | `no-chunks`, `no-floors` |
-| `CoTMountHyjal` | `no-chunks`, `no-floors` |
-| `CoTTheBlackMorass` | `no-chunks`, `no-floors` |
-| `Expansion01` | `ambiguous-transform`, `no-chunks`, `no-floors`, `stock-world-map-area` |
-| `NetherstormArena` | `no-chunks`, `no-floors`, `stock-world-map-area` |

```

---

## Assistant (Build · Big Pickle · 1.6s)

_Thinking:_

The diff looks good so far. Let me see the rest of the final report diff.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && git diff reports/final-report.md | sed -n '200,340p'"
}
```

**Output:**
```
-| `NetherstormArena` | `no-chunks`, `no-floors`, `stock-world-map-area` |
-| `RuinsofAhnQiraj` | `no-chunks`, `no-floors` |
-| `WarsongGulch` | `no-chunks`, `no-floors`, `stock-world-map-area` |
-| `ZulAman` | `no-chunks`, `no-floors` |
-| `ZulFarrak` | `no-chunks`, `no-floors` |
-| `ZulGurub` | `no-chunks`, `no-floors` |
+| `ArathiBasin` | `stock-world-map-area` |
+| `Expansion01` | `floorless-transform-reference`, `stock-world-map-area` |
+| `NetherstormArena` | `stock-world-map-area` |
+| `WarsongGulch` | `stock-world-map-area` |
 | `Northrend` | `stock-chunk`, `stock-floor`, `stock-world-map-area` |
 | `WailingCaverns` | `stock-chunk`, `stock-mutation-required` |
 | `BlackFathomDeeps` | `duplicate-artwork-alias` |
 | `Magtheridonslair` | `duplicate-artwork-alias` |
 
-The dominant cause is `no-floors` plus `no-chunks` on 11 maps: WDM gives them an
-area and artwork but no `DungeonMap` row, so there is nothing to enter and
-publishing them would mean inventing a floor. `Expansion01` additionally has two
-transforms (2 and 3) for map 530, so no default floor is derivable even if the
-floors existed.
+The four floorless maps are rejected on their own merits, not for lacking floors.
+`ArathiBasin`, `NetherstormArena` and `WarsongGulch` are PvP maps whose
+`WorldMapArea` rows WDM leaves untouched, so there is no additive area to ship.
+`Expansion01` is the same stock row *and* has `WorldMapTransforms` rows 2 and 3
+naming a floor of map 530, which owns none — `floorless-transform-reference`
+names that condition, and replaced the old catch-all `ambiguous-transform`.
 
 `Northrend` and `WailingCaverns` are the two maps whose rows are stock IDs WDM
 mutates or deletes. The composer's append-only contract means neither can ship.
@@ -311,16 +382,16 @@ them. `Discovery.coverage()` reports each table as
 |---|---:|---:|---:|---:|
 | `DungeonMap` | 113 | 113 | 0 | 0 |
 | `DungeonMapChunk` | 1312 | 1310 | 0 | 2 |
-| `WorldMapArea` | 51 | 43 | 8 | 0 |
+| `WorldMapArea` | 51 | 50 | 1 | 0 |
 | `WorldMapTransforms` | 4 | 4 | 0 | 0 |
 
 - **Unowned chunks 1828, 1829** belong to map 631 (*Icecrown Citadel*), which has
   a stock `WorldMapArea` (604), no WDM area, no WDM floors and no WDM artwork —
   so it is not a candidate and the chunks ship nowhere. This is the only
   unaccounted-for row set in the release.
-- **Held-back areas 686, 697, 717, 733, 734, 749, 775, 781** (`ZulFarrak`,
-  `ZulGurub`, `RuinsofAhnQiraj`, `CoTTheBlackMorass`, `CoTHillsbradFoothills`,
-  `WailingCaverns`, `CoTMountHyjal`, `ZulAman`) belong to the withheld maps above.
+- **Held-back area 749** (`WailingCaverns`) is the single additive `WorldMapArea`
+  row not shipped, belonging to the withheld map above. The seven floorless areas
+  that used to be held back (686, 697, 717, 733, 734, 775, 781) now ship.
 
 ## Verification evidence
 
@@ -328,20 +399,25 @@ them. `Discovery.coverage()` reports each table as
 |---|---|
 | `upstream/WDM-patch/SHA256SUMS` | 17,072 OK, 0 FAILED |
 | `git status --porcelain upstream/` | 0 changes |
-| `python3 tests/run_tests.py` | **149 tests, OK, 0 skipped** |
+| `python3 tests/run_tests.py` | **156 tests, OK, 0 failures** |
+| `mod-content-manager` Phase 4 world-map suite | PASS, including floorless area and floorless composition |
 | Deadmines vs `mod-content-manager` golden fixture | exact match on `worldMaps` and `content` |
 | Deadmines chunk order vs WDM's shipped DBC | exact match |
 | Karazhan declaration vs raw WDM rows | field-for-field match, 17/86/1/0/204 |
 | Karazhan artwork vs WDM payloads | 204/204 SHA-256 match |
-| All 43 published EPF payloads vs WDM artwork | byte-for-byte, including the 48 re-cased alias tiles |
+| All 50 published EPF payloads vs WDM artwork | byte-for-byte, including the 48 re-cased alias tiles |
+| Floorless composition | `DungeonMap`/`DungeonMapChunk`/`WorldMapTransforms` byte-identical to stock; one `WorldMapArea` lease |
+| Floorless package client requirements | no `protected-framexml`, no `floorNames` |
 | Every WDM added row accounted for | `shipped + held back + unowned = added`, all four tables |
 | No SAFE map claims a stock ID | 0 collisions across all four tables |
-| No two published maps share a target or a row | 0 collisions, 1392 targets |
-| Publication set == SAFE set | 43 == 43; no UNSAFE map has a `content/` directory |
-| The four pre-existing manifests regenerated | byte-identical, no diff |
-| `tests/validate_epfs.py` — all 44 EPFs through the full CM pipeline | valid, staged, composed, parity verified |
+| No two published maps share a target or a row | 0 collisions, 1476 targets |
+| Publication set == SAFE set | 50 == 50; no UNSAFE map has a `content/` directory |
+| The 43 pre-existing EPFs regenerated | byte-identical to their pre-change hashes |
+| `tests/validate_epfs.py` — all 51 EPFs through the full CM pipeline | valid, staged, composed, parity verified |
+| Release lifecycle (build A → B → C) on the 50-map release | PASS |
+| Two consecutive full builds | all 51 EPFs byte-identical |
 | `WorldMapTransforms` composition | +4 rows, all WDM's; stock rows untouched |
-| `make check` | exit 0 |
+| `make check` / `make verify` | exit 0 / exit 0 |
 
 The golden-fixture comparison remains the load-bearing one for Deadmines: its
 manifest is derived *only* from WDM and then compared field-for-field, in order,
@@ -365,9 +441,12 @@ semantic block and the artwork content block.
 7. **Deterministic** — canonical JSON manifests; uncompressed EPFs with a fixed
    1980 timestamp, verified byte-reproducible.
 8. **Upstream immutable** — vendored, checksummed, never edited.
-9. **Prohibited repos untouched** — `mod-content-manager`, `WDM-patch`,
-   `wdm-stock-dbc/` and `upstream/` are all read-only inputs. Nothing was
-   committed or pushed.
+9. **Vendored inputs untouched** — `WDM-patch`, `wdm-stock-dbc/` and `upstream/`
+   are read-only inputs and were never edited. `mod-content-manager` was modified
+   deliberately: accepting and validating floorless areas is upstream work this
+   task required, and the change is confined to `ContentPackage.{h,cpp}`,
+   `tests/world_map_tests.cpp` and the world-map guide. Nothing was committed or
+   pushed.
 
 ## Recommendations
 
@@ -380,8 +459,8 @@ semantic block and the artwork content block.
 - **Do not synthesise transforms.** A hand-written transform for, say,
   *Blackrock Spire* would be a guess about client-baked behaviour wearing WDM's
   fixed ID, and it would be indistinguishable, in the composed DBC, from real
-  WDM data. A missing transform is a complete row set, not a gap to fill. 39 of the
-  43 published maps have no transform, and that is the correct outcome.
+  WDM data. A missing transform is a complete row set, not a gap to fill. 46 of
+  the 50 published maps have no transform, and that is the correct outcome.
 - **Leave WDM's within-directory casing alone.** `TheTempleOfAtalHakkar` is
   spelled three different ways across its three floors in one directory. It works,
   because the client is case-insensitive. Re-casing it would rewrite a released
@@ -389,10 +468,16 @@ semantic block and the artwork content block.
 - **The `-1` sentinel was a `mod-content-manager` validator bug**, now fixed
   upstream: treating every non-zero `dungeonMapId` as an unresolvable reference
   made a legitimate client value unloadable.
-- **Only Karazhan is runtime-proven.** The other 42 are byte-for-byte WDM's data
+- **Only Karazhan is runtime-proven.** The other 49 are byte-for-byte WDM's data
   composed by the same append-only path, which is the strongest claim the
   evidence supports. Whether the client renders each of them as WDM intends is a
   question only a live client can answer, and no such claim is made here.
+- **Verify a floorless map on a live client.** The seven floorless packages are
+  the first in this project with no `DungeonMap` row and no transform, and their
+  composed `DungeonMap.dbc`, `DungeonMapChunk.dbc` and `WorldMapTransforms.dbc`
+  are the stock files untouched. The client-side claim — that a world map with no
+  floor dropdown behaves correctly when selected — is a static argument until
+  confirmed in game.
 - **Re-run `make check` after any upstream refresh.** The reports are generated,
   so `--check` turns a stale classification into a build failure rather than a
   silent drift.
@@ -404,6 +489,6 @@ make check
 ```
 
 Regenerates `reports/`, `content/` and `dist/` from the vendored WDM tree, runs
-the 149-test suite, and drives every EPF through the `mod-content-manager`
+the 156-test suite, and drives every EPF through the `mod-content-manager`
 checkout. `make verify` is the CI gate: it writes nothing and fails if any
 committed artifact is out of date.
\ No newline at end of file

```

---

## Assistant (Build · Big Pickle · 10.7s)

_Thinking:_

Wait, the diff shows at the very bottom the "Verify a floorless map" recommendation includes text:
```
+  floor dropdown behaves correctly when selected — is a static argument until
+  confirmed in game.
```
but I had written "floor dropdown behaves correctly when selected — is a static argument..." Hmm the original text I wrote was "a world map with no floor dropdown behaves correctly when selected". Let me check the actual file to ensure no corruption. The diff shows it's fine.

Everything looks good. One small thing: the final report's "Verdict" now says "SAFE | 50 ... UNSAFE | 8". Good.

Now, the generated reports: instance-candidates.md/json and wdm-stable-audit.md were regenerated by report.py, with 44/123 and 64/79 changes. Those were generated by tools, and `make verify` passed, so they're consistent.

Now I should run the full native tests one final time and CM suite to confirm everything still passes after all doc edits (docs don't affect tests, but the world_map_tests.cpp change does — already verified). Let me run `make check` once more to be fully certain everything is green end-to-end, then `make verify`.

Actually I already ran make check (exit 0) and make verify (exit 0) and the release lifecycle with the arg. The only thing changed since the last make check is documentation (README, final-report, WORLD_MAP_DBC.md, ContentPackage comments? no). Documentation doesn't affect tests. But `make check` regenerates content/dist and runs tests. Since README/final-report aren't generated, make verify won't care.

However, to be safe and to produce final evidence, let me run `make check` one final time. It's the authoritative gate.

Actually, I realize I should double-check: does `make check` verify the README table against publish.json? There's no test referencing README, confirmed. Good.

Let me run make check and make verify one final time, then finalize.

Actually, I already have strong evidence. But the doc edits including the CM docs and test file were done before the last make verify, which passed. The README and final-report edits after that don't affect `make verify` (not generated/referenced). So we're fine.

But wait — I edited `world_map_tests.cpp` (43→50 counts) and then ran the CM phase4 suite which passed. And the native make verify passed after. Good.

Let me do one final combined run to be certain, then write the final report.

Let me run `make check` and capture exit, plus CM phase4 with release arg, in parallel? They both build. They're independent repos. But CM phase4 compiles CM sources. Fine to run sequentially to avoid confusion. Let me just run make check final.

Actually, I've already verified all of this. The remaining work is to produce the requested "29-item report". Let me think about what that is.

The prior summary said: "Final docs and reports pending: ... requested 29-item report." and "Phase 10: update docs and reports, final 29-item report". This refers to the original user request which presumably listed 29 items to verify/report. Since I don't have the original prompt with the 29 items, I need to infer or reconstruct. Hmm.

Wait, the user's very first message in this conversation was "What did we do so far?" and then I summarized. Then the user said "Continue if you have next steps, or stop and ask for clarification if you are unsure how to proceed." So I'm continuing the work.

The "29-item report" is referenced in my own prior summary as a deliverable. I don't know the exact 29 items. This is a case where I should probably ask for clarification, OR produce a comprehensive final report covering the work.

Hmm. Let me reconsider. The prior summary text was itself generated (by me) summarizing the task. The "29-item report" likely refers to a specific deliverable listed in the original task description that isn't in my context now. Since I can't recover the original 29 items, and the user said "stop and ask for clarification if you are unsure how to proceed", the right move might be to ask.

But actually, I've completed all the substantive verification. The docs are updated. The final report exists (reports/final-report.md), which is the natural "report" deliverable. The "29-item" might have been a checklist the task asked to produce.

Let me search the repo for any file mentioning 29 items, or a task/plan doc. Maybe there's a plan file from the original conversation. Let me search.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && grep -rln \"29\\b\" *.md docs tools tests reports 2>/dev/null | head; echo \"=== git log recent ===\"; git log --oneline -5"
}
```

**Output:**
```
README.md
session-ses_f065.md
tests/__pycache__/run_tests.cpython-314.pyc
tests/run_tests.py
reports/transform-analysis.md
reports/final-report.md
reports/wdm-stable-audit.md
reports/instance-candidates.md
reports/instance-candidates.json
=== git log recent ===
7db5798 Added more certified maps
d62939a Declare legacy package replacements
d0e52b8 Fixed path problem
8b84462 Add deterministic EPF build workflow
a303958 FrameXML fix

```

---

## Assistant (Build · Big Pickle · 2.6s)

_Thinking:_

There's a `session-ses_f065.md` file in the repo root! That's the untracked session file mentioned in the prior summary. It might contain the original task with the 29 items. Let me read it.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && wc -l session-ses_f065.md && grep -n \"29\" session-ses_f065.md | head"
}
```

**Output:**
```
9898 session-ses_f065.md
29:Now — a critical hint: WorldMapArea 686's area_id=1176, parentMapID=161, virtual_map_id=-1, dungeonMapId=0. Compare to how a stock map without dungeonMap works. Let's look at stock WMA rows for dungeon maps, e.g. map 47 (Razorfen Kraul), 129 (Razorfen Downs) — are those in stock WMA? Stock WMA 108 rows; let me list all stock WMA rows and all WDM-added ones with their fields, to understand.
46:WDM-only maps (in wdm not stock): [33, 34, 36, 47, 48, 70, 90, 109, 129, 189, 229, 230, 249, 289, 329, 349, 369, 389, 409, 429, 469, 531, 532, 540, 542, 543, 544, 545, 546, 547, 548, 550, 552, 553, 554, 555, 556, 557, 558, 564, 565, 580, 585]
73:So how does the client know which tile set? Let's check the stock WMA rows for map 209... none. Hmm! So how does stock 3.3.5a show Zul'Farrak? Maybe via Map.dbc? No — the world map is driven by WorldMapArea. Let me dump all stock WMA rows to see whether dungeon maps like Blackfathom (48), Razorfen Downs (129) are present in stock WMA. Let me check.
104:   29     0    46 BurningSteppes                  -1     0     0   same
137:  461   529  3358 ArathiBasin                     -1     0     0   same
165:  502   609  4298 ScarletEnclave                  -1     0     0   same
178:  529   603  4273 Ulduar                          -1    -1     0   same
206:  699   429  2557 DireMaul                        -1     0     0
209:  717   509  3429 RuinsofAhnQiraj                 -1     0   261
211:  721   229  1583 BlackrockSpire                  -1     0     0

```

---

## Assistant (Build · Big Pickle · 3.3s)

_Thinking:_

The session file is a transcript of the original session (9898 lines). Let me search it for the task specification with 29 items. Search for "29-item", "29 item", "checklist", or a numbered list of requirements.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && grep -ni \"29-item\\|29 item\\|29 deliverables\\|twenty-nine\\|final report with\\|produce a report\\|report covering\" session-ses_f065.md | head"
}
```

**Output:**
```
(no output)
```

---

## Assistant (Build · Big Pickle · 2.2s)

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && sed -n '1,40p' session-ses_f065.md"
}
```

**Output:**
```
# Zul'Farrak WDM forensic investigation

**Session ID:** ses_f06528860fferflkupaEdOJnrc
**Created:** 10/1/2026, 6:54:50 PM
**Updated:** 10/1/2026, 7:23:57 PM

---

## Assistant (Build · Big Pickle · 8.9s)

_Thinking:_

So map 209 has no DungeonMap rows in stock or WDM. But WDM 686's dungeonMapId = 0. Let me check how other WDM zero-floor candidates look, and how a SAFE map looks. Also check: are there DungeonMap rows in WDM with MapID 0? Let me look at what map IDs WDM DungeonMap rows cover.

Also important: DungeonMap 28 modified relates to map 43 (WailingCaverns). Let's check map 43's stock rows.

Now the key question: how does the client render Zul'Farrak? In 3.3.5a, GetCurrentMapAreaID, WorldMapArea row with map_id=209 and dungeonMapId=0. Hmm. Actually for instance maps, the client's WorldMapFrame uses the map's DungeonMap floor via... Let me think.

Actually in 3.3.5a, the dungeon floor handling: `WorldMapFrame:GetMapFloorInfo` / `GetCurrentMapFloor` reads DungeonMap.dbc by MapID and Floor index, where floor index comes from... `GetCurrentMapAreaID` returns the WMA id; then `WorldMapArea.dungeonMapId` gives the DungeonMap ID... Actually let me check the real 3.3.5a code. Hmm, in vanilla 3.3.5a, DungeonMap.dbc: ID, MapID, Floor, field3..7 (x,y,w,h?), field7. Hmm, actually field3-6 are coordinates and field7... let me look at stock DungeonMap rows.

Actually, I recall in 3.x, the dungeon map image is drawn as a single "floor" — the DungeonMap.dbc row for MapID=map, Floor=0? Hmm, DungeonMap 28 for map 43 has field7 0->11.

Let me look at stock DungeonMap rows for a map that works natively, e.g., map 90 (Gnomeregan) is added by WDM. Which maps have stock DungeonMap rows? Let's list stock DungeonMap by MapID.

Also, key: for a map like Shadowfang Keep (33) — that's SAFE with 7 floors from WDM. Which maps are stock-complete? e.g., 48 Blackfathom is SAFE with 3 floors.

The really interesting question: which stock rows exist for map 209? None. And WDM added none. So WDM added only WMA 686. So does the map function?

Now — a critical hint: WorldMapArea 686's area_id=1176, parentMapID=161, virtual_map_id=-1, dungeonMapId=0. Compare to how a stock map without dungeonMap works. Let's look at stock WMA rows for dungeon maps, e.g. map 47 (Razorfen Kraul), 129 (Razorfen Downs) — are those in stock WMA? Stock WMA 108 rows; let me list all stock WMA rows and all WDM-added ones with their fields, to understand.

Let me do a full dump of stock WMA and WDM-added WMA.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && python3 - <<'EOF'\nimport sys\nsys.path.insert(0,'tools')\nfrom wdbc import parse_file\nfrom pathlib import Path\nstock=Path('upstream/wow-3.3.5a-build-12340/DBFilesClient')\nwdm=Path('upstream/WDM-patch/Stable/enUS/DBFilesClient')\ns=parse_file(stock/'DungeonMap.dbc','DungeonMap'); w=parse_file(wdm/'DungeonMap.dbc','DungeonMap')\nfrom collections import defaultdict\nsm=defaultdict(list); wm=defaultdict(list)\nfor r in s.records: sm[r.map_id()].append(r)\nfor r in w.records: wm[r.map_id()].append(r)\nprint(\"stock DungeonMap maps:\", dict((k,[x.id for x in v]) for k,v in sorted(sm.items())))\nprint()\nprint(\"WDM-only maps (in wdm not stock):\", sorted(set(wm)-set(sm)))\nprint(\"maps in both where count differs or ids differ:\")\nfor k in sorted(set(sm)&set(wm)):\n    a=[x.id for x in sm[k]]; b=[x.id for x in wm[k]]\n    if a!=b: print(\"  \",k,\"stock\",a,\"wdm\",b)\nEOF"
}
```

```

---

## Assistant (Build · Big Pickle · 3.7s)

_Thinking:_

This session file is the prior session transcript. It's not the original task spec with 29 items — it starts mid-investigation. The "29-item report" in my summary may have been a mischaracterization or refer to something in the full transcript. Let me search for a numbered list near the end or for "report" with 29 entries.

Let me search for phrases like "29" combined with a list, or "checklist". Actually, maybe the original task had 29 verification requirements. Let me grep the session for a list of numbered items.

Let me search for "1." through "29." patterns or "items".

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && grep -ni \"checklist\\|29\\b\\|twenty.nine\\|test.*A\\b\\|requirement\" session-ses_f065.md | grep -vi \"dungeon\\|map 29\\|129\\|229\\|329\\|429\\|529\\|29 |\" | head -30"
}
```

**Output:**
```
104:   29     0    46 BurningSteppes                  -1     0     0   same
219:  729   553  3847 TheBotanica                     -1     0     0
339:drwxrwxr-x 34 smithkt smithkt 4096 Sep 30 22:29 ..
350:drwxrwxr-x  9 smithkt smithkt 4096 Sep 30 22:29 .
351:drwxrwxr-x 34 smithkt smithkt 4096 Sep 30 22:29 ..
552:### Requirements
584:drwxrwxr-x 9 smithkt smithkt  4096 Sep 30 22:29 ..
1430:29 0x8 8
1500:But wait — words 21-29 are 0x8000, 0x2000, 0x800, 0x200, 0x80, 0x20, 0x8, 0x8, 0x8. These are exactly mip sizes for 256x256 DXT1 (mip0 = 32768 = 256*256/2 for DXT1, yes!). So mipSizes array ends at word 29. So mipSizes[16] spans words 14..29. And mipOffsets[16] spans words -2..13? i.e. offsets array words 6..21? no.
1513:Hmm words 21-29 being mip sizes doesn't align.
1515:Alternative: this is the layout where mipSizes are at the end? Let's check: word 21..29 = 9 values of powers of 2 descending from 0x8000. 9 values. For a 256x256 DXT1 texture with full mip chain: 32768, 8192, 2048, 512, 128, 32, 8, 8, 8, 0,0,0,0,0,0,0 = 16 entries starting at word 21 → words 21..36. Words 30..36 are 0. Yes! That works: mipSizes[16] = words 21..36, with entries 21-29 nonzero.
1588:Look at words 21..29: 0x8000,0x2000,0x800,0x200,0x80,0x20,0x8,0x8,0x8 → that's mip sizes for a 256x256 texture. 9 nonzero. If mipSizes[16] occupies bytes ... hmm we need 16 entries; nonzero 9 then 7 zeros. Words 21..36 = 0x8000,0x2000,0x800,0x200,0x80,0x20,0x8,0x8,0x8,0,0,0,0,0,0,0. That's exactly 16 entries with 9 nonzero! And bytes 84..147. So mipSizes ends at byte 147, so it starts at byte 84 = word 21. So the header before mipSizes is 84 bytes: magic(4)+type(4)+encoding(4)+alphaDepth(4)+alphaEncoding(4)+hasMips(4) = 24, then 60 bytes more = 15 words of offsets (w[6..20])... 24+60 = 84. Yes! So mipOffsets[15]? Unlikely. Hmm, but if offsets array is 16 entries: w[6..21] would be offsets and then mipSizes would start at w[22]. But we determined mipSizes starts at w[21].
1684:Given w[21]=0x8000, w[22]=0x2000, w[23]=0x800, w[24]=0x200, w[25]=0x80, w[26]=0x20, w[27]=0x8, w[28]=0x8, w[29]=0x8 — these are mip sizes for a 256x256 DXT1 image (32768, 8192, 2048, 512, 128, 32, 8, 8, 8). So the actual header is: magic(0), then something at 1..5, then mipSizes[16] occupying words 6..21? No, mipSizes appear to be at words 21..29 = 0x8000,0x2000,0x800,0x200,0x80,0x20,0x8,0x8,0x8 then zeros. That's 16 entries starting at word 21? words 21..36 = 0x8000,0x2000,0x800,0x200,0x80,0x20,0x8,0x8,0x8,0,0,0,0,0,0,0 → that's exactly 16 mipSizes! And words 6..20 would be mipOffsets[16]? But mipOffsets should be increasing: 0x8494, 0xa494, 0xac94, 0xae94, 0xaf14, 0xaf34, 0xaf3c, 0xaf44, then zeros. Hmm those are the first 8 non-zero. And word 5 = 0x494 = 1172, which would be... hmm mipOffsets[0] should be right after header.
1742:Let me verify mip table is at words 21..36 as I derived, meaning header is 4+4*5 = 24 bytes then mipOffsets[16] at 24..87 (words 6..21) and mipSizes[16] at words 22..37? But we found sizes at 21..29. Hmm, offsets at words 6..20 (15 values) then sizes start at 21. So header could be 20 bytes (magic + 4 words: type, encoding, alphaDepth, alphaEncoding), then mipOffsets[15]? Nonstandard.
1913:            {   "alliance",    -5424.0,    -2929.0,      L["taxinode_thelsamar"]               },
2914:        ["Burning Steppes"] = 29,
2987:    ["TiragardeKeep11_"] = {"Durotar", 11, 1029},
3928:name a floor declared in the same map. Relaxing the *presence* requirement does not relax any
4094:transform 11, area 756/1581, floors 166 and 167, 29 chunks, and the 24 client BLP tiles. Composing it
4186:Let's check the width: In the client, map coordinate span → tile grid. Let's test with a known stock map to derive the tile-grid rule. Elwynn: word4=-7249.9995? no. Let's take Elwynn (ID 30, map 0, area 12): y1=-7249.9995, y2=-9209.3740? Let me actually get it.
4375:    29 BurningSteppes             dy=  2929.167 dx=  1952.083 ratio=1.5005
4404:   381 Darnassis                  dy=  1058.333 dx=   705.729 ratio=1.4996
4482:   798 MagistersTerrace           dy=   547.917 dx=   364.583 ratio=1.5029
4548:AreaTable in Beta has 36 fields — that's a later-client layout (Cataclysm+). The stock 3.3.5a AreaTable is 29 fields with a different layout: ID, ContinentID, Parent, ... Actually in 3.3.5a AreaTable field order: ID(0), ContinentID(1), Parent(2), ... Let me not over-claim. But the Beta AreaTable shows id 1176 -> w1=209 (map), which is consistent with AreaTable 1176 being Zul'Farrak in map 209. Let me check which field is the name in Beta's 36-field layout, and try to find a Zul'Farrak name string.
4592:  id=717 w29=0 ''
4629:  id=1176 w29=0 ''
4763:Actually BLP2 layout in newer clients: magic, type, encoding, alphaDepth, alphaEncoding, hasMips, mipOffsets[16]... Let me reconsider: w5=0x494=1172, w6=0x8494=33940, w7=0xa494=42132 ... these are increasing offsets — those look like mipOffsets. And w21=0x8000=32768, w22=0x2000=8192, w23=0x800, w24=0x200, w25=0x80, w26=0x20, w27=0x8, w28=0x8, w29=0x8 — these are mip sizes! 32768, 8192, 2048, 512, 128, 32, 8, 8, 8. For a 256x256 DXT1 image: 256*256/2 = 32768. Yes! So width=256, height=256.
4765:So header: magic(4), type(4)=1, encoding(4)=0x01000002, alphaDepth(4)=0x100, alphaEncoding(4)=0x100, then mipOffsets[16]? but w5..w13 are offsets (9 nonzero), then... hmm w14..w20 = 0, w21..w29 = sizes. Let's count: if mipOffsets is 16 entries w5..w20, then mipSizes w21..w36: 32768,8192,2048,512,128,32,8,8,8,0,...0. That's 9 nonzero sizes, consistent. Then w37..w40 = 0. Hmm but width/height should follow. w37=0,w38=0 — that can't be width/height=256.
4838:ContentClientRequirement.h
5142:Let me also check the mod-content-manager tests/fixtures and reference dir for any later client data.

```

---

## Assistant (Build · Big Pickle · 5.6s)

_Thinking:_

The session file has line 552 "### Requirements". Let me read around line 552. That might be the original task requirements (possibly 29 items).

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && sed -n '545,640p' session-ses_f065.md"
}
```

**Output:**
```
![GitHub Latest Pre-Release)](https://img.shields.io/github/v/release/Trimitor/WDM-patch?include_prereleases&label=pre-release&logo=github) 

This is additional, optional patch that expands the available maps in Wrath of the Lich King. It includes various extra locations such as caves, mines, dungeon entrances, starting zones, and hidden areas like GM Island and Hyjal.

> [!IMPORTANT]
> This patch is for 3.3.5a, not 3.4.3.

### Requirements

To use this patch, you **must** install:

-   The **main patch** ([Releases](https://github.com/Trimitor/WDM-patch/releases/latest))
-   The **WDM addon** and **Astrolabe** ([WDM-addons](https://github.com/Trimitor/WDM-addons/releases/latest))

### Installation

1.  Download the patch from [Releases](https://github.com/Trimitor/WDM-patch/releases) (marked as _pre-release_) or from the table below, based on language of your game client.
2.  Place the downloaded file into `[Game Folder]\Data\<yourLang>`, replacing `<yourLang>` with the language code of your game client (e.g., `enUS`, `frFR`, `deDE`).
3.  Ensure that both the **main patch** and **addons** are installed and active.

|Language  |Link  | 
|--|--|
|English (enUS)  |[patch-enUS-N.MPQ](https://github.com/Trimitor/WDM-patch/releases/download/2.4.5-beta/patch-enUS-N.MPQ)  | 
|English (enGB)  |[patch-enGB-N.MPQ](https://github.com/Trimitor/WDM-patch/releases/download/2.4.5-beta/patch-enGB-N.MPQ)  | 
|Deutsch (deDE)  |[patch-deDE-N.MPQ](https://github.com/Trimitor/WDM-patch/releases/download/2.4.5-beta/patch-deDE-N.MPQ)  | 
|Français (frFR)  |[patch-frFR-N.MPQ](https://github.com/Trimitor/WDM-patch/releases/download/2.4.5-beta/patch-frFR-N.MPQ)  | 
|Español (esES) |[patch-esES-N.MPQ](https://github.com/Trimitor/WDM-patch/releases/download/2.4.5-beta/patch-esES-N.MPQ) | 
|Mexicano (esMX) |[patch-esMX-N.MPQ](https://github.com/Trimitor/WDM-patch/releases/download/2.4.5-beta/patch-esMX-N.MPQ)  | 
|한국인 (koKR)  |[patch-koKR-N.MPQ](https://github.com/Trimitor/WDM-patch/releases/download/2.4.5-beta/patch-koKR-N.MPQ)  | 
|Русский (ruRU)  |[patch-ruRU-N.MPQ](https://github.com/Trimitor/WDM-patch/releases/download/2.4.5-beta/patch-ruRU-N.MPQ)  | 
|中国人 (zhCN)  |[patch-zhCN-N.MPQ](https://github.com/Trimitor/WDM-patch/releases/download/2.4.5-beta/patch-zhCN-N.MPQ) | 
|中国人 english voice (enCN)  |[patch-enCN-N.MPQ](https://github.com/Trimitor/WDM-patch/releases/download/2.4.5-beta/patch-enCN-N.MPQ)  | 
|台灣語 (zhTW)  |[patch-zhTW-N.MPQ](https://github.com/Trimitor/WDM-patch/releases/download/2.4.5-beta/patch-zhTW-N.MPQ) | 

## Contact me
If you have any questions, feel free to reach out to me on Discord: **p.trimitor**.
=== wdm-stock-dbc ===
total 40
drwxrwxr-x 2 smithkt smithkt  4096 Sep 28 17:52 .
drwxrwxr-x 9 smithkt smithkt  4096 Sep 30 22:29 ..
-rwxr-xr-x 1 smithkt smithkt  1781 Sep 28 17:52 DungeonMap.dbc
-rwxr-xr-x 1 smithkt smithkt 12461 Sep 28 17:52 DungeonMapChunk.dbc
-rwxr-xr-x 1 smithkt smithkt  6075 Sep 28 17:52 WorldMapArea.dbc
-rwxr-xr-x 1 smithkt smithkt   381 Sep 28 17:52 WorldMapTransforms.dbc
=== minimal-deadmines ===
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines1_7.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines1_9.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines1_1.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines2_5.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines2_6.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines2_2.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines2_9.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines2_12.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines2_10.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines2_8.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines2_3.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines2_7.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines1_12.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines2_4.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines1_5.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines1_3.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines2_1.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines1_10.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines2_11.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines1_6.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines1_8.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines1_4.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines1_2.blp
minimal-deadmines/Interface/WorldMap/TheDeadmines/TheDeadmines1_11.blp
minimal-deadmines/DBFilesClient/WorldMapTransforms.dbc
minimal-deadmines/DBFilesClient/DungeonMapChunk.dbc
minimal-deadmines/DBFilesClient/DungeonMap.dbc
minimal-deadmines/DBFilesClient/WorldMapArea.dbc

```

---

## Assistant (Build · Big Pickle · 3.1s)

_Thinking:_

Key: "The patch adds 56 maps from retail World of Warcraft, including dungeons, continents, and battlegrounds. All maps are fully compatible with Wrath of the Lich King." — the main patch (Stable) is intended to work alone; the Caverns and Mines patch requires the addon.

Now let's look at the WDM addon for Zul'Farrak / 209 / 686.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/WDM-addons/WDM && find . -type f -name '*.lua' -not -path './libs/*' | sort && echo \"=== toc ===\" && find . -name '*.toc' -not -path './libs/*' -exec sh -c 'echo \"--- $1\"; cat \"$1\"' _ {} \\;"
}
```

**Output:**

```

---

## Assistant (Build · Big Pickle · 3.8s)

_Thinking:_

That "Requirements" is the WDM-patch README, not the task. The session transcript is the original investigation. The "29-item report" reference in my summary is unclear.

Let me search the transcript for the actual user task prompt. It might be at the very beginning or somewhere. The transcript starts with assistant thinking, so maybe the user prompt is embedded later. Let me search for "Your task" or "Objective" or a long user message.

Actually, the transcript format seems to start mid-session (Created 6:54, but the session file itself might be an export that starts at some point). Let me search for "user" role markers.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && grep -n \"^## User\\|^## Assistant\\|^# \" session-ses_f065.md | head -40"
}
```

**Output:**
```
1:# Zul'Farrak WDM forensic investigation
9:## Assistant (Build · Big Pickle · 8.9s)
53:## Assistant (Build · Big Pickle · 13.4s)
253:## Assistant (Build · Big Pickle · 452.3s)
305:## Assistant (Build · Big Pickle · 3.7s)
370:## Assistant (Build · Big Pickle · 3.4s)
444:# WDM Addons
512:# Dungeon Maps for WotLK
623:## Assistant (Build · Big Pickle · 3.1s)
699:# Libs
704:# Languages
707:# Core
710:# Modules
721:## Assistant (Build · Big Pickle · 3.6s)
767:## Assistant (Build · Big Pickle · 4.1s)
895:## Assistant (Build · Big Pickle · 9.4s)
1015:## Assistant (Build · Big Pickle · 3.0s)
1053:## Assistant (Build · Big Pickle · 13.2s)
1119:## Assistant (Build · Big Pickle · 7.4s)
1159:## Assistant (Build · Big Pickle · 9.7s)
1196:## Assistant (Build · Big Pickle · 3.4s)
1227:## Assistant (Build · Big Pickle · 4.7s)
1253:## Assistant (Build · Big Pickle · 8.3s)
1324:## Assistant (Build · Big Pickle · 17.9s)
1451:## Assistant (Build · Big Pickle · 40.2s)
1674:## Assistant (Build · Big Pickle · 34.2s)
1943:## Assistant (Build · Big Pickle · 2.6s)
2005:## Assistant (Build · Big Pickle · 21.2s)
2067:## Assistant (Build · Big Pickle · 4.7s)
2141:## Assistant (Build · Big Pickle · 136.7s)
2199:## Assistant (Build · Big Pickle · 4.0s)
2243:## Assistant (Build · Big Pickle · 3.9s)
2305:## Assistant (Build · Big Pickle · 2.8s)
2373:## Assistant (Build · Big Pickle · 6.0s)
2402:## Assistant (Build · Big Pickle · 8.2s)
2445:## Assistant (Build · Big Pickle · 31.8s)
2711:## Assistant (Build · Big Pickle · 3.6s)
2735:## Assistant (Build · Big Pickle · 2.3s)
2845:## Assistant (Build · Big Pickle · 2.7s)
3113:## Assistant (Build · Big Pickle · 4.9s)

```

---

## Assistant (Build · Big Pickle · 2.7s)

_Thinking:_

The transcript only has Assistant sections in the beginning? Let me search for "User" case-insensitively.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && grep -ni \"^## user\\|^## .*user\\|user (build\" session-ses_f065.md | head"
}
```

**Output:**
```
5554:## User
5893:## User

```

---

## Assistant (Build · Big Pickle · 2.6s)

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && sed -n '5554,5720p' session-ses_f065.md"
}
```

**Output:**
```
## User

---

## Assistant (Compaction · Big Pickle · 61.7s)

_Thinking:_

We need output structured summary exact template, terse bullets, same language conversation (English). Need summarize detailed progress. Need not continue. Need capture objective, constraints, completed findings, active state, blockers, next moves, relevant files exact paths. Need ensure no unsupported overclaims? We should summarize what assistant found, distinguish verified vs inferred. Include key facts and commands/error. Let's formulate.

Objective: forensic investigation of Zul'Farrak WDM Stable vs stock 3.3.5a to determine minimum delta/how map functions, classify, propose solution, only then optional fixture, no guessing/modifications/commit/push.

Important details:
- repos paths and sources.
- authoritative baseline stock files descriptors; don't invent; no publish.json; append-only strict ownership.
- map target MapID 209, WMA 686.
- no modifications made yet (as far history; only /tmp script created maybe /tmp/opencode/zf/dump.py? Actually assistant created mkdir and cat heredoc to /tmp/opencode/zf/dump.py, outside repos. Mention no repo changes).
- tool rg missing; grep/find used.
- find / command timed out, targeted find found only listed DBC dirs, no WorldMapFrame.lua.
- BLP parser initially wrong but inferred dimensions.

Completed:
- explored repos, tools, reports, classifier.
- vendored stock baseline at path with 4 DBC, WDM Stable enUS DBC and art, WDM addons separate repos.
- candidates JSON: 58 candidates 43 SAFE 15 UNSAFE; ZulFarrak entry UNSAFE reasons no-chunks/no-floors, WMA 686 additive, no floors/chunks, 12 BLPs, map 209.
- report audit counts table:
DungeonMap stock 55 WDM 168 added 113 removed 0 modified 1 (DungeonMap ID 28 MapID43 field3...field7)
DungeonMapChunk stock 622 WDM 1932 added 1312 removed 1237,1238, no modified
WorldMapArea stock108 WDM159 added51 removed0 modified ID609
WorldMapTransforms stock9 WDM13 added4 no mods.
- actual keyed comparison; no map209 rows in stock/WDM in DungeonMap, DungeonMapChunk, WorldMapTransforms; stock no WMA map209; WDM only WMA 686.
- WMA 686 decoded fields exact:
ID686 map_id209 area_id1176
internal_name ZulFarrak
y1 1624.9998779296875
y2 241.66665649414062
x1 2052.083251953125
x2 1129.1666259765625
virtual_map_id -1
dungeonMap_id 0
parentMapID161 (Tanaris inferred? Actually parent map 161 likely Tanaris; do not say authoritative unless source. WDM LibMapData has Tanaris? WDM WMA row.)
record index 109, stock 686 absent.
- refs: dungeonMap_id 0 resolves no DungeonMap row; no chunks map209; no transforms; parentMapID 161 stock? Need say not yet fully followed; stock WMA parent likely row 161 Tanaris, perhaps should verify. AreaTable 1176: Beta/enUS AreaTable 36-field row ID1176 w1=209, w11 string Zul'Farrak (layout interpretation not fully verified); not stock baseline.
- artwork path `.../ZulFarrak/`, exact lowercase `zulfarrak1.blp`..`zulfarrak12.blp`, 12 files, each 44876 bytes, distinct md5; header analysis indicates BLP2 DXT1 256x256, 4x3 grid inferred/standard zone convention. No recasing.
- Compare art patterns: dungeon `<Name><Floor>_<Tile>.blp` for floors; zone `<Name><N>.blp` 12 tiles; ZulFarrak zone pattern. Other zero-floor WDM dirs similarly zone. DireMaul/BlackTemple/SunwellPlateau ship both, with floor and plain.
- stock baseline evidence: outdoor stock WMA rows (Durotar, etc) have dungeonMap_id0 and no DungeonMap rows (map 1 no rows), proving zero-floor WMA is valid stock zone map shape. WarsongGulch etc stock WMA rows and no map rows; WDM ships corresponding art. Need be careful: "proves" maybe assistant asserted. Summary can state evidence.
- Ratio WMA coordinate extents `(y1-y2)/(x1-x2)=1.5` for stock zones; ZulFarrak dy 1383.333 dx922.917 ratio1.5. BLP dimensions perhaps parsing was messy but agent concluded 256x256 DXT1. Mention as provisional/forensic result.
- LibMapData WDM-addons `LibMapData-1.0.lua` mapData[686] floors=0, name ZulFarrak, rzti 209, map_type1, link2, transform0, coordinate tuple. Note repeated entries.
- WDM addon:
  - `WDM.lua`, `_data.lua`, `microdungeons.lua`, `zonelevel.lua`, `minimap.lua`, `atlaspoi.lua`, no explicit 209/686 or ZulFarrak special case except locale strings/POI. grep `farrak` finds locale `DUNGEON_FLOOR_ZULFARRAK` and `_data.lua` POI `BZ["Zul'Farrak"]` with coords; no `\b(686|209)\b` match (except unrelated 2818.209).
  - `DUNGEON_FLOOR_ZULFARRAK` used only `microdungeons.lua:280` to label microdungeon floor; likely optional Caverns/Mines. Need note uncertain whether addon required. `mdlevels` likely Beta-only.
- WDM package layout:
  - Stable/enUS includes DBFilesClient 4 DBC + Interface/WorldMap/56 dirs, including ZulFarrak.
  - Beta has AreaTable/WMOAreaTable/WorldMapArea and art (639 enUS files), no DungeonMap/Chunk; likely Caverns/Mines.
  - Beta WMA 686 same ZulFarrak row; beta only modifies stock WMA 609.
  - Stable README says patch adds 56 maps, fully compatible WotLK; install patch MPQ; addon optional for Caverns/Mines (need inspect exact README maybe says).
- Content Manager:
  - `src/ContentPackage.cpp:327-328` rejects `worldMaps area requires a nonempty floors array`; line127 floors entries must objects. `src/ContentFrameXml.cpp:199` floors.empty() also.
  - `tools/semantic.py` projection semantics: transform optional; areas[].dungeonMapId signed reference pass-through; no floor ID inference. Need mention.
- Classification preliminary: likely NEW-SEMANTIC-CASE (category 6), not importer bug/stock mutation/addon-dependent. But assistant had not finalized; user asks final report. Need mark active/inference. Also maybe alternative 7 due inability inspect client FrameXML. Need note.

Active:
- Need complete keyed diff/report, field-by-field stock/WDM relevant rows, follow all references incl parentMapID 161 and area 1176; compare with known SAFE TheStockade map (already partly done: map34, WMA area717, floor 165, 12 dungeon-style BLPs, map 34; WMA dungeonMapId0? TheStockade WDM WMA row? We saw manifest area dungeonMapId0, parent0, virtual -1, x/y 0, one floor; chunks IDs 4065 etc. Need include.
- Need inspect source exact ContentPackage validation, WDM README full relevant lines, addon source details.
- Need investigate later Blizzard data locally: find found only stock and WDM paths plus `WDM-patch/minimal-deadmines` and `wdm-stock-dbc`; no later client data. Need parse Beta? done.
- Need determine if no later data and report.
- Need formulate minimum solution: add explicit semantic support for zone-style world map area with no floors/chunks? Existing Content Manager requires nonempty floors, so architecture likely change needed. Proposal likely semantic construct e.g. `zoneTiles`/`artwork` or allow `areas[]` with empty floors while preserving append-only, and package WMA row + artwork; no DBC floor rows; maybe model `areas[].floors` optional/empty and explicit `mapKind: zone` / `tileLayout`. Need not invent exact design; active proposal.
- Optional fixture only after forensic complete and if no new architecture; here architecture likely required, so no fixture. Need not change code.

Blocked:
- No stock `WorldMapFrame.lua` locally; only `FrameXML.toc`, so client tile-selection implementation cannot be directly cited. Must label inference.
- No stock AreaTable DBC locally; Beta AreaTable is later 36-field layout; area ID evidence not from stock.
- No `rg` command; find root timed out.
- Need perhaps verify MPQ case-insensitive and tile layout; not proven locally.
- `git status`/diff not yet run? Need final report requires. Active.
- The exact WDM README statement addon optional / Caverns Mines maybe truncated; need verify.
- Need check whether `mod-content-manager` schema already has possible `artwork`/`tile` construct not found.

Relevant Files exact paths:
- `/home/smithkt/git/mod-native-instance-maps/reports/instance-candidates.json`
- reports/instance-candidates.md, wdm-stable-audit.md, final-report.md, transform-analysis.md
- tools/instances.py, semantic.py, wdbc.py, floornames.py, paths.py, report.py, transform.py, package.py
- content/publish.json, content/the-stockade/manifest.json
- upstream stock DBFilesClient files, SOURCE.json/SHA256SUMS
- upstream WDM Stable enUS DBFilesClient and Interface/WorldMap/ZulFarrak files, SOURCE
- `/home/smithkt/git/WDM-addons/WDM/...` files and LibMapData
- `/home/smithkt/git/WDM-patch/README.md`, Stable/Beta dirs, wdm-stock-dbc, minimal-deadmines
- `/home/smithkt/git/mod-content-manager/src/ContentPackage.cpp` lines 127,327-328; `src/ContentFrameXml.cpp:199`; `src/WorldMapDbcComposer.*`; `docs/WORLD_MAP_DBC.md`; README.
- `/tmp/opencode/zf/dump.py` scratch (outside repo), perhaps not relevant but exact.

Need follow exact output structure, no extra headers. Desired terse. Need include enough context. The user prompt asked "Create a new anchored summary..." We must only output summary. Ensure all sections. Could make bullets detailed but terse.

Let's ensure exact facts:
- WDM `DungeonMap` modification ID28: field3 -410.946 → -375.946, field4 595.529 → 560.529, field5 -483.479 → -410.146, field6 187.504 → 214.17, field7 0→11. Need preserve.
- chunk removals 1237/1238 stock rows MapID43, DungeonMapID28, field2 3338/3339, field4 -10000. Could mention.
- WMA modified 609 details not yet decoded. Need state active.
- WMA 686 row index 109.
- stock baseline row counts. Good.
- WDM Stable source revision `5e7e9d...`, stable 56 map dirs; SHA manifest 17072 entries all OK. Maybe relevant.
- MapID authoritative? MapID 209 from WMA row; Map.dbc absent locally. User asked instance Map.dbc MapID. We need state Map.dbc not available? Assistant found no Map.dbc. `AreaTable` Beta row shows 209. Need summary say MapID 209 is evidenced by WDM WMA map_id and LibMapData rzti; Map.dbc not locally available, so authoritative Map.dbc cross-check pending. This is important blocker.
- AreaTable 1176 from Beta only, later layout; stock AreaTable not present. Also `AreaTable` IDs if relevant. `area_id=1176`.
- parentMapID161: WMA row; map 161 likely Tanaris from WDM addon data. Did assistant verify stock WMA row 161? Not shown. Mark pending.
- `WorldMapArea` descriptor fields per docs: y1,y2,x1,x2, virtual_map_id, dungeonMap_id, parentMapID.
- WDM row `parentMapID=161`; no exact stock row decoded in history. Mention pending.
- WDM 686 references no dungeon row because 0.
- The four DBC diff actual comparison: WDM WMA common 108 identical except 609; WDM DungeonMap stock row 28 mutation; chunk removals; transforms no changes.
- Existing SAFE map compare TheStockade: map34, WMA area 717 internal TheStockade, one floor DungeonMap 165, 12 dungeon-style artwork. WMA x1/x2/y1/y2 zeros (in manifest; source row likely). It has `dungeonMapId=0` but has floor row; note WMA dungeonMapId=0 doesn't mean no floors necessarily? TheStockade WMA dungeonMapId=0 yet floor 165. Important nuance: WMA 686 dungeonMapId=0 and no floors; TheStockade has dungeonMapId=0 and one floor. Need not say WMA 0 always means no dungeon; semantics per map/DungeonMap rows.
- Actually WMA 686 `dungeonMap_id=0`; TheStockade `dungeonMapId=0`, yet floor 165. So classification based on presence of DungeonMap rows, not only field. Mention.
- The Stockade map WMA maybe area ID 717 (from manifest) and map 34, floor 165; artwork `TheStockade1_1..12`. Good.
- There are 43 SAFE maps all have floors, no WDM addon trickery per prior user background; assistant did not fully verify all but report says.

Artwork exact count, dimensions:
BLP file sizes all 44876. The assistant's BLP parsing ended with "header is 1172 bytes ... DXT1 256x256". We can state "header analysis indicates..." not absolute if parser uncertain.
- Lowercase filenames differ from internalName. User instructed do not recase. Need preserve.
- 12 tile convention likely 4x3; label as inferred, not client source-confirmed.
- WDM art has all 12 distinct md5, so no duplicates/placeholder identical.

Addon:
- Search used `grep`; `rg` missing error `/bin/bash: line 1: rg: command not found`.
- WDM addon has no explicit `209` or `686` numeric map case. Search `\b(686|209)\b` found only unrelated coordinate `2818.209`.
- `_data.lua:255` POI with BZ["Zul'Farrak"] coords -6793,-2892; not map display.
- locale strings in `WDM/locales/global/*.lua`, e.g. enus `DUNGEON_FLOOR_ZULFARRAK = "Zul' Farrak"`; `microdungeons.lua:280` uses DUNGEON_FLOOR for optional microdungeon UI.
- WDM `WDM.lua` config and generic behavior; no map rendering.
- `Beta`/`Beta-Blizzard` likely Caverns/Mines; need maybe README confirms. State preliminary.

Potential issue: summary should not overly state final classification because active. We can say "Working hypothesis: category 6 NEW-SEMANTIC-CASE; not finalized pending client-source/architecture verification." This is useful.

Need mention no code/manifests modified, no commits/push. `git status` not yet checked. No proof fixture.

Let's construct exact markdown structure. Use bullets. "Blocked" with `(none)`? There are blockers, list.

Objective one or two sentences.

Important Details could be many bullets.

Work State Completed bullets perhaps long. Need maintain terse. Desired oververbosity 3, but task complex; include all key evidence. We need not include every tool call but important.

Let's make exact headings.

Potential concern: User said output exactly Markdown structure shown; bullets can be nested? Keep simple.

Let's ensure no mention "conversation compacted".

Let's draft:

## Objective
- Forensically determine exact stock 3.3.5a vs WDM Stable delta for Zul'Farrak, explain native rendering/addon dependence, classify and propose minimum safe fix; only then optional unpublished fixture; no guessing/commits/push.

## Important Details
- Repos etc.
- constraints.
- descriptors.
- known findings/interpretive caveat.

## Work State
### Completed
- baseline etc.
- row inventory.
- Zul row.
- artwork.
- classifier/content manager.
- WDM package/addon.
- preliminary hypothesis.

### Active
- complete final report...
- follow references, exact Map.dbc and AreaTable, client FrameXML etc.

```

---

## Assistant (Build · Big Pickle · 4.6s)

_Thinking:_

This is a previous compaction summary from within the original session. So the "29-item report" isn't in the transcript either (or it's a later requirement). The user's continuation is likely a much larger task with a numbered verification plan. But since I don't have it, and I've completed the substantive work, let me search the transcript for a detailed task list that might be the "29 items". Search for phrases like "SPEC", "Task:", "Do the following", or "1)" with many items.

Actually, the original user request probably appears in the part of the transcript after line 5893 (the second User section) or as the final user message. But the transcript only has 2 User markers and both seem to be compaction requests. That means the session file is an export that only captured the assistant side + compaction prompts. The actual task might be in a system/parent context not exported.

Given this, the "29-item report" in my prior summary may have been my own invention/paraphrase of a deliverable. Wait — my prior summary explicitly listed: "Final docs and reports pending: ... Final eleven-candidate evidence table and requested 29-item report." Hmm "29-item report" — maybe the user asked for a report with 29 specific questions answered. 

Let me search the transcript for a numbered list of many questions, perhaps near line 5893 or after.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && sed -n '5893,5990p' session-ses_f065.md"
}
```

**Output:**
```
## User

---

## Assistant (Build · Big Pickle · 16.0s)

_Thinking:_

Let me continue the investigation. I have concrete next steps:

1. Verify AreaTable 1176 layout in the Beta AreaTable.dbc — DONE. col1 = MapID (ContinentID), col11 = AreaName. Confirmed: AreaTable 1176 = "Zul'Farrak" on map 209.
2. Check Mapster InstanceMaps.lua — found `["Zul'Farrak"] = 686` in iclassic table, data "mostly from SetMapByID". This is important: Mapster maps zone name → WorldMapArea ID for the map list. Let me look at how Mapster uses this — does it iterate the table to build a dropdown of maps? If yes, then Zul'Farrak appears in Mapster's map list at WMA 686. But is Mapster optional? Mapster is a third-party addon, definitely not required.

Actually more important: does Mapster's presence in the WDM addon bundle matter? The WDM addon folder (/home/smithkt/git/WDM-addons/WDM) is the WDM addon proper. Let me confirm Mapster is separate. Mapster is at /home/smithkt/git/WDM-addons/Mapster — separate addon, bundled in the WDM-addons repo. So optional.

3. Next: verify the zone-tile claim more. Let me check the other zero-floor maps that ARE stock-world-map-area (ArathiBasin, WarsongGulch, NetherstormArena, Expansion01) — for those, stock has WorldMapArea rows. Do stock clients have artwork? No, stock 3.3.5a MPQ has no Interface\WorldMap\ArathiBasin. So WDM adds artwork for maps that exist in stock DBC but lack stock art. Hmm, wait: in stock 3.3.5a, do Arathi Basin / Warsong Gulch / Netherstorm Arena zone maps exist in the MPQ? Actually the 3.x clients DID ship Interface\WorldMap\ArathiBasin\ArathiBasin1-12.blp? Hmm. Let me think.

In vanilla/TBC 3.x, outdoor zone maps are in the MPQ: Interface\WorldMap\Elwynn\Elwynn1.blp etc. Battleground maps (Arathi Basin, Warsong Gulch, Alterac Valley) — in 3.x these were only accessible via map UI, and they DO have art. Actually I recall ArathiBasin art in Interface\WorldMap\ArathiBasin\ArathiBasin1.blp..12.blp shipping in TBC. Yes, I'm fairly confident.

Hmm, this matters: if stock ships ArathiBasin art and stock WMA row, then those maps work in stock 3.3.5a with zero DungeonMap rows → decisive local evidence (DBC + reasoning) that zero-floor zone-tiled maps are stock-supported.

But even better: stock outdoor zones Durotar/Elwynn (map 1) have zero DungeonMap rows and definitely work.

So my classification holds. Let me now check:
- Whether `content/` has any existing package that ships only artwork without a WorldMapArea row — i.e., is there precedent for "artwork-only" maps? That would tell whether the mod has a concept of art-only additions. Let me check the mod's README and any manifests.

4. Check mod-content-manager README worldMaps section (line 641) and the docs for `worldMaps` schema, plus check for any existing "artwork only" or "zone" concept in package.json schema/FrameXML module.

5. Check WorldMapDbcComposer for floors-empty handling and FrameXML module requirements.

6. Verify the classifier reason codes + whether instances.py's `no-floors` gate is the only blocker for Zul'Farrak. Let me actually run the classifier and see what happens if I remove the no-floors gate — no, don't modify. Instead, let me determine the minimal set of validation changes needed.

Let me batch these investigations.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-content-manager && grep -n -i \"worldMaps\" README.md | head -40 && echo \"=== schema/artwork refs ===\" && grep -rn \"artwork\\|Artwork\" --include=*.hpp --include=*.cpp --include=*.md . | head -30"
}
```

**Output:**
```
641:Schema 2 and 3 packages may declare `worldMaps[]`, which lets a mod define an instance's
651:`worldmap/transform/<transformId>`. A map's position inside `worldMaps[]` is never part of its
=== schema/artwork refs ===
./tests/world_map_tests.cpp:128:// DungeonMap floors, its DungeonMapChunk rows and the artwork, and no
./tests/world_map_tests.cpp:1802:	// World-map artwork must live under a declared area directory. Reusing an
./tests/world_map_tests.cpp:1805:	auto withArtwork = manifest;
./tests/world_map_tests.cpp:1806:	withArtwork["content"] = json::array({json{{"type", "file"},
./tests/world_map_tests.cpp:1809:	auto artPath = scratch / "artwork.epf";
./tests/world_map_tests.cpp:1811:	Save(artPath, withArtwork);
./tests/world_map_tests.cpp:1814:	auto stray = withArtwork;
./tests/world_map_tests.cpp:1824:	auto unrelated = withArtwork;
./tests/world_map_tests.cpp:1831:	auto traversal = withArtwork;
./tests/world_map_tests.cpp:1838:	// Staging installs the declared artwork and never writes a world-map DBC:
./tests/world_map_tests.cpp:1852:	auto duplicateTarget = withArtwork;
./tests/world_map_tests.cpp:2159:	fs::path const &artworkDirectory)
./tests/world_map_tests.cpp:2164:	// through a synthesized EPF. Client artwork is stock data and is not
./tests/world_map_tests.cpp:2165:	// committed, so the artwork list is checked rather than extracted.
./tests/world_map_tests.cpp:2191:	// The declared artwork is exactly the 24 Deadmines tiles under the client
./tests/world_map_tests.cpp:2204:	// When the caller supplies the artwork, every declared tile must be present
./tests/world_map_tests.cpp:2207:	if (!artworkDirectory.empty() && fs::is_directory(artworkDirectory)) {
./tests/world_map_tests.cpp:2220:				// The caller supplies the area's artwork directory, so resolve each
./tests/world_map_tests.cpp:2223:				auto const payload = ReadAll(artworkDirectory /
./tests/world_map_tests.cpp:2358:		auto const artwork = fs::path(argc > 3 && argv[3][0] ? argv[3] : "");
./tests/world_map_tests.cpp:2360:			GoldenTests(stockDirectory, golden, artwork);
./docs/WORLD_MAP_DBC.md:193:- Artwork declared for a world-map area must live under
./docs/WORLD_MAP_DBC.md:334:committed, `build_epf.py` assembles the EPF from the manifest plus an artwork directory:
./docs/WORLD_MAP_DBC.md:339:  --artwork /path/to/Interface/WorldMap/TheDeadmines \
./docs/WORLD_MAP_DBC.md:349:skipped unless the stock, golden, and artwork directories are supplied:
./docs/WORLD_MAP_DBC.md:355:  --world-map-artwork        /home/smithkt/git/WDM-patch/minimal-deadmines/Interface/WorldMap/TheDeadmines
./docs/WORLD_MAP_DBC.md:362:duplicate IDs, missing keys, dangling floor references, artwork in the wrong directory, path
./src/ContentPackage.cpp:456:			// be WorldMapArea + DungeonMap + DungeonMapChunk + artwork only, so
./src/ContentPackage.cpp:540:	// Client artwork for a contributed map must use the exact area directory the

```

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && ls content/ && echo \"=== manifests ===\" && for f in content/*/manifest.json; do echo \"--- $f\"; python3 -c \"\nimport json,sys\nm=json.load(open('$f'))\nfor w in m.get('worldMaps',[]):\n    print(' map',w.get('id'),w.get('internalName'),'areas',len(w.get('areas',[])))\n\"; done"
}
```

**Output:**
```
ahnqiraj
auchenai-crypts
black-temple
blackfathom-deeps
blackrock-depths
blackrock-spire
blackwing-lair

```

---

## Assistant (Build · Big Pickle · 64.0s)

_Thinking:_

The session file is the original exploration, not containing a 29-item task. The original user task isn't fully in view, but the deliverable is clearly the updated `reports/final-report.md` and README/docs. 

I think the "29-item report" in my summary was likely a mis-transcription; but to be safe, I should ask the user for clarification about what "29-item report" refers to, OR just present the completed work.

Actually, re-reading the user's current instruction: "Continue if you have next steps, or stop and ask for clarification if you are unsure how to proceed." I have next steps that are clearly defined (finish docs/reports, final verification), and I've done them. The only ambiguous item is the "29-item report". 

Given I've robustly completed all substantive work, the best action is:
1. Do a final full verification run (make check) to have clean evidence.
2. Present a concise final report/summary covering everything.
3. Note that I couldn't find the specific "29-item" deliverable and ask if they want it in a particular form.

But asking a question at the end might be appropriate. Actually the instruction says stop and ask if unsure. I'm only unsure about one specific deliverable. Let me check the transcript one more time for the number 29 in a task/list context — search for a list with items 1..29, maybe in an assistant message giving a plan.

Let me search for "1\." near a list that goes to "29." Actually let me grep for a series of numbered lines. Search for lines matching `^[0-9]+\.` and containing keywords.

Actually, I already grepped "29\b" and the only hits were data. There's no 29-item list. So the "29-item report" was likely hallucinated in my own compaction summary. I'll not chase it. I'll produce a thorough final report and mention the full verification.

Let me do the final `make check` to lock in evidence, then write the summary.

Actually, I want to be thorough: let me run `make check` one final time and capture the key lines. And run the CM phase4 with the release arg once more? Already done. `make check` includes native tests + validate_epfs. It does NOT include the CM phase4 suite. I already ran that separately and it passed.

Let me run make check final.

The substantive work is complete. Let me do a final end-to-end gate and review the complete change set.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && timeout 4000 make check > /tmp/opencode/zf/final-check.log 2>&1; echo \"make check exit: $?\"; grep -E \"Ran [0-9]+ tests|^OK|all packages valid|validating [0-9]+ package|wrote dist/mod-native-instance-maps.epf\" /tmp/opencode/zf/final-check.log",
  "timeout": 4000000
}
```

**Output:**
```
make check exit: 0
Ran 156 tests in 7.029s
OK
wrote dist/mod-native-instance-maps.epf (66880859 bytes)
all packages valid, staged, composed and verified
validating 51 package(s) against /home/smithkt/git/mod-content-manager

```

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-native-instance-maps && git status --short && echo \"=== content untracked dirs ===\" && git status --short content/ | head -20"
}
```

**Output:**
```
 M README.md
 M content/publish.json
 M content/titles.json
 M reports/final-report.md
 M reports/instance-candidates.json
 M reports/instance-candidates.md
 M reports/wdm-stable-audit.md
 M tests/run_tests.py
 M tests/validate_epf.cpp
 M tools/instances.py
 M tools/package.py
 M tools/semantic.py
?? content/hillsbrad-foothills/
?? content/mount-hyjal/
?? content/ruins-of-ahnqiraj/
?? content/the-black-morass/
?? content/zulaman/
?? content/zulfarrak/
?? content/zulgurub/
?? session-ses_f065.md
=== content untracked dirs ===
 M content/publish.json
 M content/titles.json
?? content/hillsbrad-foothills/
?? content/mount-hyjal/
?? content/ruins-of-ahnqiraj/
?? content/the-black-morass/
?? content/zulaman/
?? content/zulfarrak/
?? content/zulgurub/

```

---

## Assistant (Build · Big Pickle · 353.4s)

_Thinking:_

The output got a bit jumbled: "?? session-ses_f065.md" appeared, and 8 content dirs. Good. Note there are 8 untracked content dirs listed:
hillsbrad-foothills, mount-hyjal, ruins-of-ahnqiraj, the-black-morass, zulaman, zulfarrak, zulgurub = 7. Plus session file. Good, 7 new content dirs.

Now let me capture the CM repo status.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-content-manager && git status --short"
}
```

**Output:**
```
 M README.md
 M docs/WORLD_MAP_DBC.md
 M src/ContentPackage.cpp
 M src/ContentPackage.h
 M tests/world_map_tests.cpp

```

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/smithkt/git/mod-content-manager && timeout 3000 python3 tests/run_phase4.py --world-map-baseline-dir /home/smithkt/git/mod-native-instance-maps/upstream/wow-3.3.5a-build-12340/DBFilesClient --world-map-golden-dir /nonexistent --world-map-artwork /home/smithkt/git/mod-native-instance-maps/upstream/WDM-patch/Stable/enUS/Interface/WorldMap --world-map-release-epf /home/smithkt/git/mod-native-instance-maps/dist/mod-native-instance-maps.epf 2>&1 | grep -E \"world_map:|FAIL\" | tail -3; echo \"exit ${PIPESTATUS[0]}\"",
  "timeout": 3000000
}
```

**Output:**
```
world_map: PASS
exit 0

```

---

## Assistant (Build · Big Pickle · 5.8s)

_Thinking:_

Everything is green.

Now let me produce the final report to the user. I've completed:
- Phase 9 verification: all done
- Phase 10 docs/reports: done (README, WORLD_MAP_DBC.md, final-report.md; generated reports regenerated)

Let me mark the todo complete.

Then write a concise final summary of what was done, the verification evidence, and git status. Also note the "29-item report" ambiguity — actually, I'll just deliver the comprehensive report. I think the best is to present the final report content.

But wait — should I be concerned that I haven't run `git status` on the mod-native repo for the session file? It was pre-existing untracked, leave it.

Let me update the todo and give final summary.

**Tool: todowrite**

**Input:**
```json
{
  "todos": [
    {
      "content": "Phase 1: capture baseline 43-map release state (hashes, counts, manifests)",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Phase 2: allow empty floors array in ContentPackage.cpp + floorless invariants",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Phase 3: add world_map_tests.cpp floorless tests",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Phase 4: build and run mod-content-manager Phase 4 suite",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Phase 5: update tools/instances.py classifier for floorless candidates",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Phase 6: update tests/validate_epf.cpp assertions + mod-native tests",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Phase 7: reclassify all 11 zero-floor candidates with evidence table",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Phase 8: publish Zul'Farrak and the six other approved packages",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Phase 9: full verification (tests, make check/verify, EPF pipeline, determinism, release lifecycle, regression)",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Phase 10: update docs and reports",
      "priority": "medium",
      "status": "completed"
    }
  ]
}
```

**Output:**
```
[
  {
    "content": "Phase 1: capture baseline 43-map release state (hashes, counts, manifests)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 2: allow empty floors array in ContentPackage.cpp + floorless invariants",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 3: add world_map_tests.cpp floorless tests",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 4: build and run mod-content-manager Phase 4 suite",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 5: update tools/instances.py classifier for floorless candidates",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 6: update tests/validate_epf.cpp assertions + mod-native tests",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 7: reclassify all 11 zero-floor candidates with evidence table",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 8: publish Zul'Farrak and the six other approved packages",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 9: full verification (tests, make check/verify, EPF pipeline, determinism, release lifecycle, regression)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 10: update docs and reports",
    "status": "completed",
    "priority": "medium"
  }
]
```

---

## Assistant (Build · Big Pickle · 7.5s)

All work is complete and green. Here is the final result.

## What changed

**`mod-content-manager`** (floorless support upstream)
- `src/ContentPackage.cpp`: accepts `"floors": []` / `"chunks": []`; new `CheckFloorlessArea()` enforces `dungeonMapId == 0`, empty chunks, no floor names. The existing transform check rejects a transform on a floorless map.
- `src/ContentPackage.h`, `docs/WORLD_MAP_DBC.md`, `README.md`: documented the `floors` may be empty contract.
- `tests/world_map_tests.cpp`: floorless fixtures + composition tests; release-lifecycle row counts updated for 50 maps.

**`mod-native-instance-maps`**
- `tools/instances.py`: removed `no-floors`; added `floorless-dungeon-map-id`, `floorless-chunk-reference`, `floorless-transform-reference`. Result: **50 SAFE / 8 UNSAFE**.
- `tools/semantic.py`: emits `floorNames` only when there are floors.
- `tools/package.py`, `content/titles.json`, `content/publish.json`: 7 new packages.
- `tests/validate_epf.cpp`: fixed a latent assertion that contradicted Content Manager's contract (a label-less package must **not** request `protected-framexml`).
- `tests/run_tests.py`, generated reports, `README.md`, `reports/final-report.md`.

## Outcome
- Seven floorless maps published: `hillsbrad-foothills`, `mount-hyjal`, `ruins-of-ahnqiraj`, `the-black-morass`, `zulaman`, `zulfarrak`, `zulgurub`. Each composes `DungeonMap`/`DungeonMapChunk`/`WorldMapTransforms` byte-identical to stock with a single `WorldMapArea` lease.
- Four floorless rejects are on their own merits: `ArathiBasin`, `NetherstormArena`, `WarsongGulch` (stock areas), `Expansion01` (stock area + transform reference).

## Verification
- `mod-native-instance-maps`: 156 tests OK; `make check` exit 0; `make verify` exit 0.
- `mod-content-manager` Phase 4 suite: `world_map: PASS` incl. floorless area/composition; release lifecycle A→B→C PASS.
- `validate_epfs.py`: all 51 EPFs valid/staged/composed/parity-verified.
- Determinism: all 51 EPFs byte-identical across rebuilds.
- Regression: the 43 pre-existing individual EPFs byte-identical to baseline; only the combined release changed.
- `git status`: both repos modified, **nothing committed/pushed**. Untracked `session-ses_f065.md` left untouched.

One note: I could not find any "29-item report" specification in the repo or the prior transcript, so `reports/final-report.md` is the complete final report. If you had a specific 29-item checklist in mind, point me at it and I'll format the evidence to match.

---

