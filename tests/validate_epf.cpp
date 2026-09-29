// Validation harness: run every EPF passed on the command line through
// mod-content-manager's real ContentPackage::Validate() and Stage().
//
// This is a test tool, not a runtime module.  It links the upstream units
// read-only and exists solely so this repository's generated packages are
// checked by the same code that will install them.  mod-content-manager itself
// is never modified.
//
// Exit code 0 when every package validates and stages, 1 otherwise.

#include <filesystem>
#include <iostream>
#include <string>
#include <vector>

#include "ContentBuildHash.h"
#include "ContentPackage.h"

namespace fs = std::filesystem;

// The real SHA-256 implementation pulls in OpenSSL. Nothing this harness does
// hashes anything -- it only links ContentServerBundle, which references the
// shape check -- so mirror the standalone suites' stub exactly.
bool ContentBuildHash::Valid(std::string const &hash) {
    return hash.size() == 64 &&
           hash.find_first_not_of("0123456789abcdef") == std::string::npos;
}

namespace {

int failures = 0;

void Check(std::filesystem::path const &epf, fs::path const &scratch) {
    ContentPackage package{epf};
    auto const result = package.Validate();
    if (!result.valid) {
        std::cerr << "  INVALID " << epf.filename().string() << ": " << result.error
                  << "\n";
        ++failures;
        return;
    }

    auto const &manifest = result.manifest;
    std::cout << "  valid   " << epf.filename().string() << ": schema "
              << manifest.schema << ", " << manifest.content.size() << " file(s), "
              << manifest.worldMaps.size() << " world map(s)";
    for (auto const &map : manifest.worldMaps) {
        std::size_t floors = 0, chunks = 0;
        for (auto const &area : map.areas) {
            floors += area.floors.size();
            chunks += area.chunks.size();
        }
        std::cout << " [map " << map.mapId << ": " << map.areas.size() << " area(s), "
                  << floors << " floor(s), " << chunks << " chunk(s), transform "
                  << map.transform.id << "]";
    }
    std::cout << "\n";

    // Staging proves the artwork really lands where the manifest says, and
    // that nothing extra (in particular no DBC) is written.
    auto const workspace = scratch / epf.stem().string();
    fs::remove_all(workspace);
    fs::create_directories(workspace);
    auto const staged = package.StageInto(workspace, manifest);
    if (!staged.success) {
        std::cerr << "  STAGE FAILED " << epf.filename().string() << ": "
                  << staged.error << "\n";
        ++failures;
        return;
    }
    if (staged.stagedFiles.size() != manifest.content.size()) {
        std::cerr << "  STAGED " << staged.stagedFiles.size() << " of "
                  << manifest.content.size() << " files for " << epf.filename().string()
                  << "\n";
        ++failures;
        return;
    }
    for (auto const &entry : manifest.content) {
        if (!fs::is_regular_file(workspace / entry.target)) {
            std::cerr << "  MISSING STAGED TARGET " << entry.target << " for "
                      << epf.filename().string() << "\n";
            ++failures;
            return;
        }
    }
    if (fs::exists(workspace / "DBFilesClient")) {
        std::cerr << "  package staged a DBFilesClient tree: composition belongs to "
                     "mod-content-manager\n";
        ++failures;
        return;
    }
    // Re-staging the same package must be refused rather than overwrite.
    if (package.StageInto(workspace, manifest).success) {
        std::cerr << "  re-staging " << epf.filename().string()
                  << " was allowed; it must be refused\n";
        ++failures;
        return;
    }
    std::cout << "  staged  " << epf.filename().string() << ": "
              << staged.stagedFiles.size() << " file(s) verified\n";
}

}  // namespace

int main(int argc, char **argv) {
    if (argc < 2) {
        std::cerr << "usage: validate_epf <scratch-dir> <package.epf>...\n";
        return 2;
    }
    fs::path const scratch{argv[1]};
    fs::remove_all(scratch);
    fs::create_directories(scratch);

    for (int i = 2; i < argc; ++i) {
        std::filesystem::path const epf{argv[i]};
        if (!fs::is_regular_file(epf)) {
            std::cerr << "  MISSING " << epf << "\n";
            ++failures;
            continue;
        }
        Check(epf, scratch);
    }

    if (failures) {
        std::cerr << failures << " package check(s) failed\n";
        return 1;
    }
    std::cout << "all packages valid and staged\n";
    return 0;
}
