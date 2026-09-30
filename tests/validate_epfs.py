#!/usr/bin/env python3
"""Run every EPF in ``dist/`` through mod-content-manager's real pipeline.

This is the only step in this repository that builds C++.  It exists so the
generated packages are checked by the same ``ContentPackage::Validate``,
``StageInto``, ``WorldMapDbcComposer`` and ``ContentServerBundle::VerifyParity``
that will install and activate them, rather than by a reimplementation of the
rules here.

Each package is checked against the verified stock 3.3.5a build-12340 DBC
baseline, so composition is exercised for real: rows are leased at their declared
IDs, composed, staged, read back, and the result is compared against the stock
file to prove every stock row survived byte for byte.

mod-content-manager is used strictly read-only: its sources are compiled into a
throwaway binary under a temporary directory and nothing in that checkout is
written to.

    python3 tests/validate_epfs.py
    python3 tests/validate_epfs.py --epf dist/mod-native-instance-maps.karazhan.epf
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import paths  # noqa: E402

HARNESS = Path(__file__).resolve().with_name("validate_epf.cpp")

# The same translation units mod-content-manager's own world_map unit links.
# Keeping the list identical means the harness exercises the real code paths.
UNITS = (
    "WorldMapDbcComposer",
    "ContentResourceAllocator",
    "ContentPackage",
    "ContentServerBundle",
    "ContentVendorRow",
    "ContentManagedServerDescriptor",
    "ServerTableDescriptor",
    "CurrencyCategoryDbcComposer",
    "CurrencyDbcComposer",
    "ItemExtendedCostDbc",
    "DbcReader",
    "DbcDescriptor",
    "SpellDbcComposer",
    "ContentFrameXml",
    # Real SHA-256 for the generated FrameXML files recorded in parity.  Parity
    # pins these at activation, so a placeholder would defeat the check.
    "ContentBuildHash",
)

# The four client tables a native instance map composes into.
WORLD_MAP_TABLES = ("DungeonMap", "DungeonMapChunk", "WorldMapArea", "WorldMapTransforms")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epf", type=Path, action="append", dest="epfs")
    parser.add_argument(
        "--stock-dbc",
        type=Path,
        help="stock 3.3.5a build-12340 DBC baseline "
        "(default: the one mod-content-manager verifies)",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="reuse an existing harness binary at --binary",
    )
    args = parser.parse_args(argv)

    root = paths.content_manager_dir()
    if not (root / "src" / "ContentPackage.h").is_file():
        print(
            f"mod-content-manager not found at {root}; set MOD_CONTENT_MANAGER_DIR",
            file=sys.stderr,
        )
        return 2

    stock = args.stock_dbc or paths.stock_dbc_dir()
    if not all((stock / f"{table}.dbc").is_file() for table in WORLD_MAP_TABLES):
        print(
            f"stock DBC baseline not found at {stock}; set --stock-dbc",
            file=sys.stderr,
        )
        return 2

    epfs = args.epfs or sorted(paths.DIST_DIR.glob("*.epf"))
    if not epfs:
        print(f"no EPFs in {paths.DIST_DIR}; run python3 tools/package.py", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="nim-validate-") as scratch:
        binary = Path(scratch) / "validate_epf"
        if not args.skip_build:
            command = [
                os.environ.get("CXX", "g++"),
                "-std=c++17",
                "-O0",
                "-g",
                f"-I{root / 'src'}",
                str(HARNESS),
            ]
            command += [str(root / "src" / f"{unit}.cpp") for unit in UNITS]
            command.append(str(root / "src" / "third_party" / "miniz" / "miniz.c"))
            if "ContentBuildHash" in UNITS:
                command.append("-lcrypto")
            command += ["-o", str(binary)]
            subprocess.run(command, check=True)

        command = [str(binary), str(Path(scratch) / "workspace"), str(stock)]
        command += [str(epf.resolve()) for epf in epfs]
        print(f"validating {len(epfs)} package(s) against {root}")
        print(f"stock DBC baseline: {stock}")
        return subprocess.run(command).returncode


if __name__ == "__main__":
    raise SystemExit(main())
