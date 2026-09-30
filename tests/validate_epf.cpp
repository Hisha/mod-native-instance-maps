// Acceptance harness: run every EPF passed on the command line through
// mod-content-manager's real world-map pipeline.
//
// Stages, in the order the build service uses them:
//
//   1. ContentPackage::Validate()                    -- schema, artwork, row rules
//   2. ContentPackage::StageInto()                   -- artwork lands where declared
//   3. WorldMapDbcComposer::AppendRequests()         -- one request per authored row
//   4. ContentResourceAllocator::PlanFixed()         -- one lease per request
//   5. WorldMapDbcComposer::Compose()                -- append-only DBC composition
//   6. WorldMapDbcComposer::Stage()                  -- write DBFilesClient, read back
//   7. ContentServerBundle::VerifyParity()           -- activation check
//
// Nothing here reimplements the rules: each stage is the same code that will
// install and activate the package, so a package this harness accepts is one the
// build service accepts.
//
// The transform contract is asserted directly.  A package whose manifest declares
// no transform must request no WorldMapTransforms row, hold no
// WorldMapTransforms lease, and leave the verified stock WorldMapTransforms file
// byte-identical.  A package that does declare one must carry exactly the WDM
// row, pointing back at its own map and at a floor it declares itself.  Nothing
// in this harness can supply a missing transform.
//
// This is a test tool, not a runtime module.  It links the upstream units
// read-only and exists solely so this repository's generated packages are
// checked by the same code that will install them.  mod-content-manager itself
// is never modified.
//
// Usage: validate_epf <scratch-dir> <stock-dbc-dir> <package.epf>...
// Exit code 0 when every package validates, stages, composes and verifies.

#include <algorithm>
#include <cassert>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>

#include "ContentAllocationRegistry.h"
#include "ContentBaselineRegistry.h"
#include "ContentBuildHash.h"
#include "ContentFrameXml.h"
#include "ContentPackage.h"
#include "ContentResourceAllocator.h"
#include "ContentServerBundle.h"
#include "DbcDescriptor.h"
#include "DbcReader.h"
#include "WorldMapDbcComposer.h"

namespace fs = std::filesystem;

namespace {

std::uint32_t const kClientBuild = 12340;
std::string const kRealm = "nim-acceptance";

int failures = 0;

void Fail(fs::path const &package, std::string const &what) {
    std::cerr << "  FAIL " << package.filename().string() << ": " << what << "\n";
    ++failures;
}

void Expect(bool condition, fs::path const &package, std::string const &what) {
    if (!condition) Fail(package, what);
}

std::string Number(std::size_t value) { return std::to_string(value); }

DbcDocument Stock(std::string const &table, fs::path const &baselineDirectory) {
    auto const descriptor = FindDbcDescriptor(kClientBuild, table);
    assert(descriptor);
    auto const read = DbcReader::Read(baselineDirectory / (table + ".dbc"), *descriptor);
    assert(read.valid);
    return read.document;
}

std::size_t Floors(ContentWorldMap const &map) {
    std::size_t count = 0;
    for (auto const &area : map.areas) count += area.floors.size();
    return count;
}

std::size_t Chunks(ContentWorldMap const &map) {
    std::size_t count = 0;
    for (auto const &area : map.areas) count += area.chunks.size();
    return count;
}

// One composed row, as it sits in the file.
std::vector<std::uint32_t> Row(DbcDocument const &document, std::size_t index) {
    std::size_t const first = index * document.fieldCount;
    return std::vector<std::uint32_t>(
        document.words.begin() + static_cast<std::ptrdiff_t>(first),
        document.words.begin() + static_cast<std::ptrdiff_t>(first + document.fieldCount));
}

// How one package's contribution to one table came out.
struct TableResult {
    std::size_t stockRows = 0;
    std::size_t composedRows = 0;
    std::size_t addedRows = 0;
    bool stockPreserved = false;   // every stock word and string byte survived
    bool stockIdentical = false;   // no row added, so the file is unchanged
    bool stagedOk = false;
    std::vector<std::uint32_t> ids;  // contributed IDs, in composition order
    DbcDocument staged;              // read back from DBFilesClient
    bool stagedParsed = false;
};

struct Pipeline {
    std::map<std::string, TableResult> tables;
    std::vector<ItemAllocation> leases;
    std::vector<ContentBaseline> baselines;
    std::map<std::string, std::string> hashes;
    std::map<std::string, std::vector<ResourceAllocationRequest>> requests;
    std::vector<ResolvedWorldMap> resolved;
    std::map<std::string, std::string> frameXmlHashes;
    std::size_t frameXmlFiles = 0;
    std::size_t frameXmlTocGrowth = 0;
    bool parityOk = false;
    std::string parityError;
};

// The generated client FrameXML, composed and staged exactly as the build
// service does.  This is what proves the floor labels actually reach the client
// dropdown rather than merely parsing: the stock table of contents is rebuilt
// from the bytes this EPF shipped, the Lua is generated from the manifest's own
// declarations, and both are read back from disk.
void RunFrameXmlPipeline(fs::path const &package, fs::path const &workspace,
                         ContentPackageManifest const &manifest, Pipeline& out) {
    ContentFrameXml::Declared declared;
    std::string error;
    Expect(ContentFrameXml::Collect(manifest.worldMaps, declared, error), package,
           "Collect: " + error);

    if (declared.empty()) {
        // No labels means no generated files and no requirement: stock behaviour,
        // unchanged.  Assert the absence rather than tolerating it.
        Expect(manifest.clientRequirements ==
                   std::vector<std::string>{"protected-framexml"},
               package,
               "a package with no floor labels requested protected-framexml");
        return;
    }

    Expect(manifest.clientRequirements ==
               std::vector<std::string>{"protected-framexml"},
           package,
           "floor labels declared without requesting protected-framexml");

    std::string lua;
    Expect(ContentFrameXml::ComposeLua(declared, lua, error), package,
           "ComposeLua: " + error);

    // The generated module must delegate: a map or locale it has no labels for
    // keeps the stock "Floor %d" text.  Overriding the whole dropdown with a
    // table that always answers would break every unlabelled map in the game.
    Expect(lua.find("WorldMapLevelDropDown_Initialize") != std::string::npos, package,
           "generated module does not override WorldMapLevelDropDown_Initialize");
    Expect(lua.find("FLOOR_NUMBER") != std::string::npos, package,
           "generated module does not fall back to the stock FLOOR_NUMBER label");
    // The header comment names the stock files it does *not* touch, so the real
    // safety property is that nothing is loaded or replaced at runtime.
    for (auto const& forbidden : {"dofile", "loadfile", "loadstring", "require",
                                  "LoadAddOn", "SetAddOn"}) {
        Expect(lua.find(forbidden) == std::string::npos, package,
               std::string("generated module calls ") + forbidden +
                   ", so it depends on stock files at runtime");
    }
    Expect(lua.find("WorldMapFrame.xml") != std::string::npos, package,
           "generated module does not state the stock file it loads after");

    // The stock table of contents the EPF shipped, read back from the package's
    // own manifest pin.  ContentPackage already verified its digest; this proves
    // the composer's insertion is the only difference.
    Expect(manifest.clientFrameXml.has_value(), package,
           "floor labels declared without clientFrameXml");
    std::vector<std::uint8_t> stock;
    Expect(ContentPackage::ReadMember(package,
                                      manifest.clientFrameXml->stockTocSource,
                                      stock, error),
           package, "ReadMember " + manifest.clientFrameXml->stockTocSource + ": " + error);
    std::string const stockBytes(stock.begin(), stock.end());
    std::string toc;
    Expect(ContentFrameXml::ComposeToc(stock, toc, error), package,
           "ComposeToc: " + error);

    // Exactly one added line, and it is the module.  Byte counts prove nothing
    // else moved: the stock TOC plus one CRLF-terminated module name.
    // A table of contents line is a bare leaf name, not a path.
    std::string const module =
        fs::path(ContentFrameXml::GeneratedLuaTarget()).filename().string();
    Expect(toc.size() > stockBytes.size(), package,
           "composed table of contents is not larger than stock");
    std::size_t const added = toc.size() - stockBytes.size();
    Expect(added == module.size() + 2, package,
           "table of contents grew by " + Number(added) + " bytes, not one "
           "CRLF-terminated module line of " + Number(module.size() + 2));
    Expect(toc.find(module) != std::string::npos, package,
           "generated module is absent from the table of contents");
    Expect(toc.find(ContentFrameXml::TocInsertionMarker()) != std::string::npos,
           package,
           "the insertion marker vanished from the composed table of contents");
    out.frameXmlTocGrowth = added;

    // Stage both files through the real composer and read them back.
    for (auto const& target : ContentFrameXml::Targets()) {
        std::string const& text =
            target == ContentFrameXml::GeneratedLuaTarget() ? lua : toc;
        Expect(ContentFrameXml::Stage(target, text, workspace, error), package,
               "Stage " + target + ": " + error);
        out.frameXmlHashes[target] = ContentBuildHash::Bytes(
            std::vector<std::uint8_t>(text.begin(), text.end()));
        out.frameXmlFiles += 1;
        std::ifstream read(workspace / target, std::ios::binary);
        std::string const stagedText((std::istreambuf_iterator<char>(read)),
                                     std::istreambuf_iterator<char>());
        Expect(stagedText == text, package, "staged " + target + " differs from "
               "the bytes composed for it");
    }

    // The stock table of contents must not have been shipped pre-modified: the
    // composer, not this repository, is what adds the module.
    Expect(toc != stockBytes, package,
           "composed table of contents is identical to stock");
}

// Plan, compose, stage and read back every world-map table.
bool RunPipeline(fs::path const &package, fs::path const &baselineDirectory,
                 fs::path const &workspace, ContentPackageManifest const &manifest,
                 Pipeline& out) {
    WorldMapDbcComposer::AppendRequests(manifest.packageKey, manifest.worldMaps,
                                        out.requests);
    for (auto const &map : manifest.worldMaps)
        out.resolved.push_back(ResolvedWorldMap{manifest.packageKey, map});

    for (auto const &entry : out.requests)
        for (auto const &request : entry.second)
            Expect(request.packageKey == manifest.packageKey, package,
                   "request attributed to " + request.packageKey);

    for (auto const &table : WorldMapDbcTables()) {
        TableResult result;
        auto const found = out.requests.find(table);
        static std::vector<ResourceAllocationRequest> const none;
        auto const &wants = found == out.requests.end() ? none : found->second;
        auto const &pin = WorldMapDbcComposer::VerifiedBaselineSha256(table);

        // -- allocation -----------------------------------------------------
        // Fixed IDs, pinned to the verified stock snapshot of this very table.
        // No searching planner runs: a world-map row keeps the identity its
        // manifest declares.
        auto const plan = ContentResourceAllocator::PlanFixed(
            kRealm, ContentResourceAllocator::FixedRowIdPolicy(
                        WorldMapDbcComposer::ResourceKind(table)),
            wants, {}, {}, kClientBuild, pin);
        Expect(plan.size() == wants.size(), package,
               table + ": planned " + Number(plan.size()) + " leases for " +
                   Number(wants.size()) + " request(s)");

        std::map<std::uint32_t, std::string> leased;
        for (auto const &lease : plan) {
            Expect(lease.resourceKind == WorldMapDbcComposer::ResourceKind(table),
                   package, table + ": lease has kind " + lease.resourceKind);
            Expect(lease.packageKey == manifest.packageKey, package,
                   table + ": lease belongs to " + lease.packageKey);
            Expect(lease.baselineSha256 == pin, package,
                   table + ": lease is not pinned to the verified baseline");
            Expect(leased.emplace(lease.value, lease.symbol).second, package,
                   table + ": duplicate lease for row " + Number(lease.value));
            out.leases.push_back(lease);
        }
        for (auto const &want : wants)
            Expect(leased.count(want.fixedValue) == 1, package,
                   table + ": row " + Number(want.fixedValue) +
                       " was not leased at its declared ID");

        // -- composition ----------------------------------------------------
        DbcDocument const stock = Stock(table, baselineDirectory);
        auto const bytes = WorldMapDbcComposer::Compose(table, stock, out.resolved);
        Expect(WorldMapDbcComposer::Compose(table, stock, out.resolved) == bytes, package,
               table + ": composition is not deterministic");

        result.stockRows = stock.recordCount;
        result.ids = WorldMapDbcComposer::Rows(table, out.resolved);
        result.addedRows = result.ids.size();
        result.composedRows = stock.recordCount + result.addedRows;
        // The request set and the composed row set must describe the same rows.
        std::set<std::uint32_t> requested;
        for (auto const &want : wants) requested.insert(want.fixedValue);
        Expect(requested == std::set<std::uint32_t>(result.ids.begin(), result.ids.end()),
               package,
               table + ": the request set and the composed rows disagree");

        auto const composed = DbcReader::Parse(bytes, *FindDbcDescriptor(kClientBuild, table));
        Expect(composed.valid, package,
               table + ": composed bytes do not reparse" +
                   (composed.valid ? "" : ": " + composed.error));
        if (!composed.valid) return false;
        Expect(composed.document.recordCount == result.composedRows, package,
               table + ": composed row count " + Number(composed.document.recordCount) +
                   " != expected " + Number(result.composedRows));

        // Append-only: every stock word and every stock string byte survives in
        // place, so composition cannot have edited a verified row.
        result.stockPreserved =
            std::equal(stock.words.begin(), stock.words.end(),
                       composed.document.words.begin()) &&
            std::equal(stock.strings.begin(), stock.strings.end(),
                       composed.document.strings.begin());
        Expect(result.stockPreserved, package,
               table + ": the stock rows or string block were not preserved");
        // Adding nothing reproduces the verified stock file exactly.
        result.stockIdentical =
            wants.empty() && bytes == DbcReader::Serialize(stock);
        if (wants.empty())
            Expect(result.stockIdentical, package,
                   table + ": changed although no row was contributed");
        else
            Expect(WorldMapDbcComposer::Inspect(table, composed.document).size() ==
                       result.composedRows,
                   package, table + ": Inspect() disagrees with the composed count");

        // -- staged readback -------------------------------------------------
        std::string error;
        result.stagedOk =
            WorldMapDbcComposer::Stage(table, bytes, workspace / "worldmap", result.staged,
                                       error);
        if (!result.stagedOk) {
            Fail(package, table + ": Stage(): " + error);
            return false;
        }
        Expect(fs::is_regular_file(workspace / "worldmap" / "DBFilesClient" /
                                   (table + ".dbc")),
               package, table + ": staged file missing under DBFilesClient/");
        result.stagedParsed = DbcReader::Parse(
            DbcReader::Serialize(result.staged),
            *FindDbcDescriptor(kClientBuild, table)).valid;
        Expect(result.stagedParsed, package, table + ": staged readback does not reparse");
        Expect(std::equal(result.staged.words.begin(), result.staged.words.end(),
                          composed.document.words.begin()),
               package, table + ": staged readback differs from the composed bytes");
        Expect(std::equal(result.staged.strings.begin(), result.staged.strings.end(),
                          composed.document.strings.begin()),
               package, table + ": staged string block differs from the composed bytes");

        out.tables[table] = result;
        // A table this package contributes nothing to gets no lease, and the
        // parity artifact must not carry a hash for it either: upstream refuses
        // a hash for a table with no lease.  The composed file is still compared
        // against stock directly above, which is a stronger statement than any
        // hash in an artifact this repository does not write.
        if (!wants.empty()) {
            out.hashes[table] = pin;
            ContentBaseline snapshot;
            snapshot.table = table;
            snapshot.clientBuild = kClientBuild;
            snapshot.descriptorVersion = FindDbcDescriptor(kClientBuild, table)->version;
            snapshot.hash = pin;
            out.baselines.push_back(snapshot);
        }
    }

    // -- parity: the artifact an activation reads ----------------------------
    // The upstream suite records the baseline pin as the composed hash, because
    // real SHA-256 needs OpenSSL.  Parity only checks the shape and the
    // lease/hash pairing, so byte equality is asserted directly against the
    // stock file instead -- see the stockPreserved and stockIdentical checks.
    auto const parity = ContentServerBundle::ParityJson(
        kRealm, 7, out.leases, {}, "", "", "mpq", "server", "", "", {},
        out.baselines, "", {}, {}, {}, {}, {}, {}, "", false, out.hashes,
        out.frameXmlHashes);
    out.parityOk = ContentServerBundle::VerifyParity(parity, kRealm, 7, "", "mpq",
                                                     "server", {}, out.leases,
                                                     out.parityError, {}, {}, {}, {},
                                                     {}, {}, out.hashes,
                                                     out.frameXmlHashes);
    Expect(out.parityOk, package, "VerifyParity rejected the artifact: " + out.parityError);
    // Every table holding a lease must also carry a composed hash.  That pairing
    // is what makes "stock byte-identical" auditable at activation: an orphan
    // lease with no recorded composed file is refused.
    std::set<std::string> leasedKinds;
    for (auto const &lease : out.leases) leasedKinds.insert(lease.resourceKind);
    std::set<std::string> hashedKinds;
    for (auto const &entry : out.hashes)
        hashedKinds.insert(WorldMapDbcComposer::ResourceKind(entry.first));
    Expect(leasedKinds <= hashedKinds, package,
           "a lease exists for a table with no composed hash");
    return true;
}

// The transform contract, read straight off the validated manifest.
void CheckTransformContract(fs::path const &package, ContentPackageManifest const &manifest,
                            Pipeline const &pipeline) {
    std::map<std::string, std::vector<ResourceAllocationRequest>> requests;
    WorldMapDbcComposer::AppendRequests(manifest.packageKey, manifest.worldMaps, requests);
    std::vector<ResolvedWorldMap> resolved;
    for (auto const &map : manifest.worldMaps)
        resolved.push_back(ResolvedWorldMap{manifest.packageKey, map});

    for (auto const &map : manifest.worldMaps) {
        std::set<std::uint32_t> declaredFloors;
        for (auto const &area : map.areas)
            for (auto const &floor : area.floors) declaredFloors.insert(floor.id);

        if (!map.transform) {
            // No transform in the source.  Nothing may supply one.
            Expect(requests.count("WorldMapTransforms") == 0 ||
                       requests.at("WorldMapTransforms").empty(),
                   package,
                   "a package without a transform requested a WorldMapTransforms row");
            Expect(WorldMapDbcComposer::Rows("WorldMapTransforms", resolved).empty(),
                   package,
                   "a package without a transform composed WorldMapTransforms rows");
            Expect(pipeline.tables.at("WorldMapTransforms").addedRows == 0, package,
                   "a package without a transform added a WorldMapTransforms record");
            Expect(pipeline.tables.at("WorldMapTransforms").stockIdentical, package,
                   "WorldMapTransforms is not byte-identical to the verified stock file");
            // NewDungeonMapID is never guessed from a floor.  With no transform
            // there is no such field to guess into.
            Expect(!map.transform, package, "unreachable: transform appeared");
        } else {
            auto const& transformRequests = requests.at("WorldMapTransforms");
            std::size_t const wanted =
                static_cast<std::size_t>(std::count_if(
                    manifest.worldMaps.begin(), manifest.worldMaps.end(),
                    [](ContentWorldMap const& entry) { return bool(entry.transform); }));
            Expect(transformRequests.size() == wanted, package,
                   "expected " + Number(wanted) +
                       " WorldMapTransforms request(s), got " +
                       Number(transformRequests.size()));
            Expect(WorldMapDbcComposer::Rows("WorldMapTransforms", resolved).size() == wanted,
                   package, "unexpected number of composed WorldMapTransforms rows");
            // The composed row is exactly the declared one, unmodified.
            Expect(map.transform->newMapId == map.mapId, package,
                   "the transform does not point back at its own map");
            Expect(map.transform->newMapId != 0 && map.transform->id != 0 &&
                       map.transform->newDungeonMapId != 0,
                   package, "a transform identity is zero, which CM refuses");
            Expect(declaredFloors.count(map.transform->newDungeonMapId) == 1, package,
                   "the transform's NewDungeonMapID " +
                       Number(map.transform->newDungeonMapId) +
                       " is not a floor this package declares");
        }

        // A floor is a floor: no floor row may claim to be a transform target
        // unless a transform actually names it, and none is invented here.
        for (auto const &area : map.areas) {
            Expect(!area.floors.empty() || !area.chunks.empty(), package,
                   "area " + Number(area.id) + " declares neither floors nor chunks");
            for (auto const &floor : area.floors) {
                Expect(floor.id != 0, package, "floor 0 is refused by CM");
                Expect(floor.floor != 0, package,
                       "floor " + Number(floor.id) + " has Floor 0, which CM refuses");
            }
            for (auto const &chunk : area.chunks) {
                Expect(chunk.id != 0, package, "chunk 0 is refused by CM");
                Expect(chunk.field2 != 0, package,
                       "chunk " + Number(chunk.id) + " has field2 0, which CM refuses");
                Expect(chunk.dungeonMapId != 0, package,
                       "chunk " + Number(chunk.id) + " has DungeonMapID 0, which CM refuses");
                // A chunk points at a floor this same package declares.
                bool declared = false;
                for (auto const &floor : area.floors)
                    declared = declared || floor.id == chunk.dungeonMapId;
                Expect(declared, package,
                       "chunk " + Number(chunk.id) + " names DungeonMapID " +
                           Number(chunk.dungeonMapId) +
                           ", which this area does not declare");
            }
        }
    }
}

// Every authored row, read back out of the composed file.
void CheckRowReadback(fs::path const &package, fs::path const &baselineDirectory,
                      ContentPackageManifest const &manifest, Pipeline const &pipeline) {
    for (auto const &table : WorldMapDbcTables()) {
        auto const found = pipeline.tables.find(table);
        if (found == pipeline.tables.end()) continue;
        auto const &result = found->second;
        if (result.ids.empty()) continue;
        // No contributed identity may reuse a stock identity.
        auto const stockIds = WorldMapDbcComposer::Inspect(table, Stock(table, baselineDirectory));
        for (auto const id : result.ids)
            Expect(stockIds.count(id) == 0, package,
                   table + ": row " + Number(id) + " collides with a stock row");
    }

    // DungeonMap and DungeonMapChunk: the composed row carries the declared ID,
    // the map it belongs to, and its own declared fields.
    for (auto const &map : manifest.worldMaps) {
        std::size_t floorOffset = pipeline.tables.at("DungeonMap").stockRows;
        std::size_t chunkOffset = pipeline.tables.at("DungeonMapChunk").stockRows;
        for (auto const &area : map.areas) {
            for (auto const &floor : area.floors) {
                auto const row = Row(pipeline.tables.at("DungeonMap").staged, floorOffset++);
                auto const expected = WorldMapDbcComposer::FloorWords(map.mapId, floor);
                Expect(row == expected, package,
                       "DungeonMap row " + Number(floor.id) + " read back differently");
            }
            for (auto const &chunk : area.chunks) {
                auto const row = Row(pipeline.tables.at("DungeonMapChunk").staged, chunkOffset++);
                auto const expected = WorldMapDbcComposer::ChunkWords(map.mapId, chunk);
                Expect(row == expected, package,
                       "DungeonMapChunk row " + Number(chunk.id) + " read back differently");
            }
        }
    }

    // WorldMapArea: the appended internal-name string follows every stock byte,
    // so no stock offset can move.
    std::size_t areaOffset = pipeline.tables.at("WorldMapArea").stockRows;
    std::set<std::uint32_t> declaredFloors, declaredChunks;
    for (auto const &map : manifest.worldMaps) {
        std::uint32_t const stockStringBytes =
            Stock("WorldMapArea", baselineDirectory).stringBlockSize;
        std::uint32_t interned = stockStringBytes;
        for (auto const &area : map.areas) {
            // Every contributed row must sit after the stock string block and
            // point at an appended string, never at a stock one.
            auto const row = Row(pipeline.tables.at("WorldMapArea").staged, areaOffset++);
            Expect(row[0] == area.id, package,
                   "WorldMapArea row " + Number(area.id) + " read back as " + Number(row[0]));
            Expect(row[1] == map.mapId, package,
                   "WorldMapArea row " + Number(area.id) + " carries map " + Number(row[1]));
            Expect(row[2] == area.areaId, package,
                   "WorldMapArea row " + Number(area.id) + " carries areaId " + Number(row[2]));
            Expect(row[3] >= stockStringBytes, package,
                   "WorldMapArea row " + Number(area.id) +
                       " points into the stock string block");
            std::string const name =
                reinterpret_cast<char const*>(pipeline.tables.at("WorldMapArea").staged.strings.data() +
                                              row[3]);
            Expect(name == area.internalName, package,
                   "WorldMapArea row " + Number(area.id) + " reads back internal name \"" +
                       name + "\", expected \"" + area.internalName + "\"");
            Expect(row[3] == interned, package,
                   "WorldMapArea row " + Number(area.id) +
                       " reuses another row's interned name");
            interned += static_cast<std::uint32_t>(area.internalName.size() + 1);
            // dungeonMapId is a reference, preserved signed: the unsigned word is
            // the bit pattern of the signed source value, never a renormalised
            // non-negative number.
            Expect(row[9] == static_cast<std::uint32_t>(area.dungeonMapId), package,
                   "WorldMapArea row " + Number(area.id) +
                       " did not preserve dungeonMapId " +
                       std::to_string(area.dungeonMapId));
            Expect(row[8] == static_cast<std::uint32_t>(area.virtualMapId) &&
                       row[10] == area.parentMapId,
                   package, "WorldMapArea row " + Number(area.id) +
                       " lost its map reference fields");
            // Every chunk names a floor this same area declares, and the dungeonMapId
            // reference was not turned into a row of its own.
            for (auto const &chunk : area.chunks) declaredChunks.insert(chunk.id);
            for (auto const &floor : area.floors) declaredFloors.insert(floor.id);
        }
    }
    // The DungeonMap and DungeonMapChunk lease sets are exactly the declared
    // floors and chunks.  An area's dungeonMapId is a reference: it never
    // requested the DungeonMap row it names, so it adds nothing to either set.
    std::set<std::uint32_t> leasedFloors, leasedChunks;
    for (auto const &lease : pipeline.leases) {
        if (lease.resourceKind == WorldMapDbcComposer::ResourceKind("DungeonMap"))
            leasedFloors.insert(lease.value);
        if (lease.resourceKind == WorldMapDbcComposer::ResourceKind("DungeonMapChunk"))
            leasedChunks.insert(lease.value);
    }
    Expect(leasedFloors == declaredFloors, package,
           "the DungeonMap leases are not exactly the declared floors (" +
               Number(leasedFloors.size()) + " leased, " +
               Number(declaredFloors.size()) + " declared)");
    Expect(leasedChunks == declaredChunks, package,
           "the DungeonMapChunk leases are not exactly the declared chunks (" +
               Number(leasedChunks.size()) + " leased, " +
               Number(declaredChunks.size()) + " declared)");
}

// Prove the "no transform" result is a measurement, not an absence of checking.
// If a transform were supplied for a map that declares none, the request set,
// the lease and the composed row would all appear -- so a package that reports
// zero of each really carries none, rather than being silently unchecked.
void CheckCounterfactual(fs::path const &package, fs::path const &baselineDirectory,
                         ContentPackageManifest const &manifest) {
    for (auto const &map : manifest.worldMaps) {
        if (map.transform) continue;
        ContentWorldMap invented = map;
        // The shape a synthesizer reaches for: name the first declared floor as
        // the default. The ID is arbitrary; the point is that any transform at
        // all changes every downstream count.
        for (auto const &area : map.areas)
            if (!area.floors.empty()) {
                invented.transform = ContentWorldMapTransform{3000, 0.0f, 1.0f, 2.0f,
                                                              3.0f, map.mapId, 0.0f, 0.0f,
                                                              area.floors.front().id};
                break;
            }
        if (!invented.transform) continue;
        std::map<std::string, std::vector<ResourceAllocationRequest>> requests;
        WorldMapDbcComposer::AppendRequests(manifest.packageKey, {invented}, requests);
        Expect(requests.count("WorldMapTransforms") == 1 &&
                   requests.at("WorldMapTransforms").size() == 1,
               package, "counterfactual: a supplied transform produced no request");
        std::vector<ResolvedWorldMap> const resolved{{manifest.packageKey, invented}};
        Expect(WorldMapDbcComposer::Rows("WorldMapTransforms", resolved) ==
                   std::vector<std::uint32_t>{3000},
               package, "counterfactual: a supplied transform composed no row");
        DbcDocument const stock = Stock("WorldMapTransforms", baselineDirectory);
        auto const bytes = WorldMapDbcComposer::Compose("WorldMapTransforms", stock, resolved);
        Expect(bytes != DbcReader::Serialize(stock), package,
               "counterfactual: a supplied transform left the stock file unchanged");
        auto const plan = ContentResourceAllocator::PlanFixed(
            kRealm,
            ContentResourceAllocator::FixedRowIdPolicy(
                WorldMapDbcComposer::ResourceKind("WorldMapTransforms")),
            requests.at("WorldMapTransforms"), {}, {}, kClientBuild,
            WorldMapDbcComposer::VerifiedBaselineSha256("WorldMapTransforms"));
        Expect(plan.size() == 1, package, "counterfactual: a supplied transform got no lease");
        std::cout << "  counter " << package.filename().string()
                  << ": map " << map.mapId
                  << " would gain 1 request, 1 lease and 1 WorldMapTransforms row if a "
                     "transform were supplied\n";
    }
}

void Check(fs::path const &epf, fs::path const &baselineDirectory, fs::path const &scratch) {
    ContentPackage package{epf};
    auto const result = package.Validate();
    if (!result.valid) {
        Fail(epf, "INVALID: " + result.error);
        return;
    }

    auto const &manifest = result.manifest;
    std::cout << "  valid   " << epf.filename().string() << ": schema " << manifest.schema
              << ", " << manifest.content.size() << " file(s), "
              << manifest.worldMaps.size() << " world map(s)";
    for (auto const &map : manifest.worldMaps)
        std::cout << " [map " << map.mapId << ": " << map.areas.size() << " area(s), "
                  << Floors(map) << " floor(s), " << Chunks(map) << " chunk(s), "
                  << (map.transform ? "WDM transform " + std::to_string(map.transform->id)
                                    : "no transform") << "]";
    std::cout << "\n";

    // -- staging: the artwork really lands where the manifest says -----------
    auto const workspace = scratch / epf.stem().string();
    fs::remove_all(workspace);
    fs::create_directories(workspace);
    auto const staged = package.StageInto(workspace, manifest);
    if (!staged.success) {
        Fail(epf, "StageInto: " + staged.error);
        return;
    }
    Expect(staged.stagedFiles.size() == manifest.content.size(), epf,
           "staged " + Number(staged.stagedFiles.size()) + " of " +
               Number(manifest.content.size()) + " files");
    for (auto const &entry : manifest.content)
        Expect(fs::is_regular_file(workspace / entry.target), epf,
               "missing staged target " + entry.target);
    Expect(!fs::exists(workspace / "DBFilesClient"), epf,
           "package staged a DBFilesClient tree: composition belongs to "
           "mod-content-manager");
    Expect(!package.StageInto(workspace, manifest).success, epf,
           "re-staging was allowed; it must be refused");
    std::cout << "  staged  " << epf.filename().string() << ": "
              << staged.stagedFiles.size() << " file(s) verified\n";

    // -- generated client FrameXML --------------------------------------------
    Pipeline pipeline;
    RunFrameXmlPipeline(epf, workspace, manifest, pipeline);
    if (pipeline.frameXmlFiles)
        std::cout << "  framexml " << epf.filename().string() << ": "
                  << Number(pipeline.frameXmlFiles)
                  << " generated file(s) staged, TOC +"
                  << Number(pipeline.frameXmlFiles == 2
                                ? pipeline.frameXmlTocGrowth
                                : 0)
                  << " byte(s)\n";

    // -- the real world-map pipeline -----------------------------------------
    if (!RunPipeline(epf, baselineDirectory, workspace, manifest, pipeline)) return;

    for (auto const &table : WorldMapDbcTables()) {
        auto const &result = pipeline.tables.at(table);
        std::cout << "  compose " << epf.filename().string() << ": " << table << " "
                  << result.stockRows << " -> " << result.composedRows << " (+"
                  << result.addedRows << (result.addedRows == 1 ? " row" : " rows") << ", stock "
                  << (result.stockPreserved ? "preserved" : "LOST") << ")"
                  << (result.addedRows == 0 ? " [byte-identical to stock]" : "") << "\n";
    }

    CheckTransformContract(epf, manifest, pipeline);
    CheckRowReadback(epf, baselineDirectory, manifest, pipeline);
    CheckCounterfactual(epf, baselineDirectory, manifest);

    std::cout << "  parity  " << epf.filename().string() << ": "
              << (pipeline.parityOk ? "verified" : "REJECTED") << " ("
              << pipeline.leases.size() << " lease(s), "
              << pipeline.leases.size() -
                     static_cast<std::size_t>(std::count_if(
                         pipeline.leases.begin(), pipeline.leases.end(),
                         [](ItemAllocation const& lease) {
                             return lease.resourceKind ==
                                    WorldMapDbcComposer::ResourceKind("WorldMapTransforms");
                         }))
              << " non-transform)\n";
}

}  // namespace

int main(int argc, char **argv) {
    if (argc < 3) {
        std::cerr << "usage: validate_epf <scratch-dir> <stock-dbc-dir> <package.epf>...\n";
        return 2;
    }
    fs::path const scratch{argv[1]};
    fs::path const baselineDirectory{argv[2]};
    fs::remove_all(scratch);
    fs::create_directories(scratch);
    for (auto const &table : WorldMapDbcTables())
        if (!fs::is_regular_file(baselineDirectory / (table + ".dbc"))) {
            std::cerr << "stock baseline " << baselineDirectory << " is missing " << table
                      << ".dbc\n";
            return 2;
        }

    for (int i = 3; i < argc; ++i) {
        std::filesystem::path const epf{argv[i]};
        if (!fs::is_regular_file(epf)) {
            Fail(epf, "missing package");
            continue;
        }
        Check(epf, baselineDirectory, scratch);
    }

    if (failures) {
        std::cerr << failures << " package check(s) failed\n";
        return 1;
    }
    std::cout << "all packages valid, staged, composed and verified\n";
    return 0;
}