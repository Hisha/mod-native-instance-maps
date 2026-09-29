#!/usr/bin/env python3
"""Generate ``content/`` manifests and deterministic ``dist/`` EPFs.

Two rules shape everything here.

**The manifest is the only authored artifact.**  It is bare JSON so it reviews
as a diff, and it declares the semantic ``worldMaps[]`` entry exactly as
``mod-content-manager`` will consume it.  Nothing here re-derives a value the
manifest already states.

**The EPF is a build product.**  Artwork bytes are read from the vendored WDM
tree at build time rather than committed twice, and the archive is byte-stable:
``manifest.json`` first, then each tile in manifest order, stored
uncompressed, fixed 1980 timestamp.  Building twice over unchanged inputs
produces identical bytes.

Usage::

    python3 tools/package.py              # manifests + EPFs
    python3 tools/package.py --manifests  # manifests only
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
from typing import Dict, List

import paths
import semantic
from instances import SAFE, Candidate, Discovery, discover, natural_key

#: Fixed DOS timestamp for every archive member.  1980-01-01 is the epoch of the
#: ZIP format, so this is the one value that cannot drift with the clock.
FIXED_TIME = (1980, 1, 1, 0, 0, 0)

SCHEMA = 3
VERSION = "1.0.0"

#: Tile targets are ``Interface/WorldMap/<internalName>/<leaf>``.  The client
#: derives that directory from ``internalName``, and mod-content-manager
#: rejects artwork that lands anywhere else, so the target is generated from
#: the same string the WorldMapArea row carries rather than typed in.
ARTWORK_PREFIX = "Interface/WorldMap/"
SOURCE_PREFIX = "artwork/"


def artwork_targets(candidate: Candidate) -> List[Dict[str, str]]:
    """One content entry per tile, in stable natural filename order."""
    leaves = sorted((candidate.blps or []), key=natural_key)
    return [
        {
            "type": "file",
            "source": SOURCE_PREFIX + Path(leaf).name,
            "target": f"{ARTWORK_PREFIX}{candidate.internal_name}/{Path(leaf).name}",
        }
        for leaf in leaves
    ]


def manifest_for(candidate: Candidate, discovery: Discovery) -> Dict[str, object]:
    """Build the full schema-3 manifest for one SAFE candidate."""
    if candidate.classification != SAFE:
        raise SystemExit(
            f"{candidate.internal_name} is {candidate.classification}, refusing to "
            f"package it: {', '.join(candidate.findings)}"
        )
    declaration = semantic.world_map_declaration(
        discovery.tables,
        candidate.map_id,
        candidate.world_map_area_ids,
        candidate.floor_ids,
        candidate.chunk_ids,
        candidate.transform_ids[0],
    )
    tiles = artwork_targets(candidate)
    floors = len(candidate.floor_ids)
    return {
        "schema": SCHEMA,
        "package": paths.package_key(candidate.slug),
        "name": candidate.title,
        "version": VERSION,
        "description": (
            f"Native pre-Cataclysm {candidate.title} instance map: {floors} DungeonMap "
            f"floor{'' if floors == 1 else 's'}, {len(candidate.chunk_ids)} "
            f"DungeonMapChunk entries, one WorldMapArea, the instance "
            f"WorldMapTransforms row and {len(tiles)} client BLP tiles."
        ),
        "content": tiles,
        "worldMaps": [declaration],
    }


def serialise(manifest: Dict[str, object]) -> bytes:
    """Stable manifest bytes: 1-space indent, LF, trailing newline.

    Matches the reviewed fixture style, and is deterministic so regenerating an
    unchanged manifest produces no diff.
    """
    return (
        json.dumps(manifest, indent=1, ensure_ascii=False, sort_keys=True).encode("utf-8")
        + b"\n"
    )


def write_manifests(discovery: Discovery, write: bool = True) -> List[Path]:
    written: List[Path] = []
    for candidate in discovery.by_classification(SAFE):
        target = paths.CONTENT_DIR / candidate.slug / "manifest.json"
        payload = serialise(manifest_for(candidate, discovery))
        if not write:
            current = target.read_bytes() if target.is_file() else None
            if current != payload:
                written.append(target)
            continue
        if target.is_file() and target.read_bytes() == payload:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        written.append(target)
    return written


def _artwork_source(
    candidate: Candidate, entry: Dict[str, str], artwork_root: Path
) -> Path:
    """Resolve a declared tile to its file under ``artwork_root``.

    The tile is looked up by leaf name beneath the area directory, matching how
    ``mod-content-manager``'s own end-to-end test supplies artwork.
    """
    name = Path(entry["source"]).name
    source = artwork_root / candidate.internal_name / name
    if not source.is_file():
        raise SystemExit(f"missing artwork for {candidate.internal_name}: {source}")
    return source


def build_epf(
    candidate: Candidate,
    manifest_path: Path,
    output: Path,
    artwork_root: Path | None = None,
) -> Path:
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    entries = manifest["content"]
    targets = [item["target"] for item in entries]
    if len(targets) != len(set(targets)):
        raise SystemExit(f"{manifest_path}: duplicate install target")
    if not entries:
        raise SystemExit(f"{manifest_path}: no artwork declared")

    root = artwork_root or paths.wdm_artwork_dir()
    payloads = [
        (item["source"], _artwork_source(candidate, item, root).read_bytes())
        for item in entries
    ]
    if any(not blob for _, blob in payloads):
        raise SystemExit(f"{manifest_path}: empty artwork payload")

    output.parent.mkdir(parents=True, exist_ok=True)
    # ZIP_STORED plus a fixed timestamp: no clock, no compressor version, no
    # filesystem ordering.  Same inputs, same bytes.
    with zipfile.ZipFile(output, "w", zipfile.ZIP_STORED) as archive:
        archive.writestr(zipfile.ZipInfo("manifest.json", FIXED_TIME), manifest_bytes)
        for name, blob in payloads:
            archive.writestr(zipfile.ZipInfo(name, FIXED_TIME), blob)
    return output


def build_all(discovery: Discovery) -> List[Path]:
    outputs: List[Path] = []
    for candidate in discovery.by_classification(SAFE):
        manifest_path = paths.CONTENT_DIR / candidate.slug / "manifest.json"
        if not manifest_path.is_file():
            raise SystemExit(f"missing manifest: {manifest_path}")
        output = paths.DIST_DIR / f"{paths.package_key(candidate.slug)}.epf"
        build_epf(candidate, manifest_path, output)
        outputs.append(output)
    return outputs


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifests", action="store_true", help="write manifests only")
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if manifests are out of date; never writes anything",
    )
    options = parser.parse_args(argv)

    discovery = discover(paths.wdm_dbc_dir(), paths.wdm_artwork_dir(), paths.stock_dbc_dir())

    if options.check:
        stale = write_manifests(discovery, write=False)
        for target in stale:
            print(f"out of date: {target.relative_to(paths.REPO_ROOT)}", file=sys.stderr)
        if stale:
            print("run: python3 tools/package.py", file=sys.stderr)
            return 1
        return 0

    paths.CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    for target in write_manifests(discovery, write=True):
        print(f"wrote: {target.relative_to(paths.REPO_ROOT)}")

    for output in build_all(discovery):
        size = output.stat().st_size
        print(f"wrote {output.relative_to(paths.REPO_ROOT)} ({size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
