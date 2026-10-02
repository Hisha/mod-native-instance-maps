#!/usr/bin/env python3
"""Generate ``content/`` manifests and deterministic ``dist/`` EPFs.

Three rules shape everything here.

**The manifest is the only authored artifact.**  It is bare JSON so it reviews
as a diff, and it declares the semantic ``worldMaps[]`` entry exactly as
``mod-content-manager`` will consume it.  Nothing here re-derives a value the
manifest already states.

**Publication is a separate decision from classification.**  The classifier in
``tools/instances.py`` answers whether a map *can* ship; ``content/publish.json``
is the hand-maintained list of maps that are actually being shipped.  Only their
intersection is generated, so fixing a classifier rule cannot silently publish a
backlog.

**The EPF is a build product.**  Artwork bytes are read from the vendored WDM
tree at build time rather than committed twice, and the archive is byte-stable:
``manifest.json`` first, then each tile in manifest order, stored
uncompressed, fixed 1980 timestamp.  Building twice over unchanged inputs
produces identical bytes.

Usage::

    python3 tools/package.py --map karazhan
    python3 tools/package.py --all-approved
    python3 tools/package.py --release
    python3 tools/package.py --manifests  # manifests only
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import paths
import semantic
from instances import SAFE, Candidate, Discovery, discover

#: Fixed DOS timestamp for every archive member.  1980-01-01 is the epoch of the
#: ZIP format, so this is the one value that cannot drift with the clock.
FIXED_TIME = (1980, 1, 1, 0, 0, 0)

SCHEMA = 3
VERSION = "1.0.0"

#: Where the vendored stock table of contents travels inside the EPF, and the
#: EPF-relative name mod-content-manager resolves ``clientFrameXml.stockTocSource``
#: against.  It must be the stock client's own path: the composer verifies the
#: digest, then writes it back to exactly this target.
STOCK_TOC_MEMBER = "Interface/FrameXML/FrameXML.toc"

#: The generated module the stock dropdown ends up loading.
STOCK_MODULE_NAME = "ContentManagerWorldMapFloorNames"

#: Tile targets are ``Interface/WorldMap/<internalName>/<leaf>``.  The client
#: derives that directory from ``internalName``, and mod-content-manager
#: rejects artwork that lands anywhere else, so the target is generated from
#: the same string the WorldMapArea row carries rather than typed in.
ARTWORK_PREFIX = "Interface/WorldMap/"
SOURCE_PREFIX = "artwork/"
RELEASE_PACKAGE = "mod-native-instance-maps"


def stock_toc_bytes() -> bytes:
    """The vendored stock ``FrameXML.toc``, read verbatim.

    A missing vendored copy is a hard error rather than a reason to regenerate or
    substitute one.  The composer refuses any TOC whose digest does not match the
    manifest, so shipping a locally rebuilt file would only fail later, further
    from the cause.
    """
    if not paths.STOCK_FRAMEXML_TOC.is_file():
        raise SystemExit(
            f"missing vendored stock FrameXML table of contents: "
            f"{paths.STOCK_FRAMEXML_TOC}"
        )
    return paths.STOCK_FRAMEXML_TOC.read_bytes()


def stock_toc_sha256() -> str:
    return hashlib.sha256(stock_toc_bytes()).hexdigest()


def floor_label_locales(world_map: Dict[str, object]) -> List[str]:
    """Client locales this one ``worldMaps[]`` entry labels, sorted.

    Counted per map, not per package, so the description states the truth for a
    map whose area WDM names only as an instance and therefore has no labels.
    """
    locales = set()
    for area in world_map.get("areas", []):
        locales.update(area.get("floorNames", {}))
    return sorted(locales)


def artwork_targets(candidate: Candidate) -> List[Dict[str, str]]:
    """One content entry per tile, in stable natural filename order.

    ``source`` names the file in the vendored WDM tree, ``target`` names the file
    the client reads.  The two differ only for a map whose WDM artwork directory
    is spelled with different capitals than its ``WorldMapArea.internal_name``;
    see :func:`instances.tile_target_name`.
    """
    return [
        {
            "type": "file",
            "source": SOURCE_PREFIX + source,
            "target": f"{ARTWORK_PREFIX}{candidate.internal_name}/{target}",
        }
        for source, target in zip(candidate.blps, candidate.tile_targets)
    ]


def published_candidates(discovery: Discovery) -> List[Candidate]:
    """The SAFE candidates this project has decided to publish, in natural name order.

    Classification and publication are separate decisions.  ``content/publish.json``
    is the hand-maintained list of candidates whose packages are approved; the
    classifier only says whether a map *can* ship.  Without this gate a classifier
    correction would mass-publish every newly packageable map, which is not a
    consequence anyone chose.
    """
    selection = publish_slugs()
    by_name = {item.internal_name: item for item in discovery.candidates}
    chosen: List[Candidate] = []
    for internal_name, slug in sorted(selection.items()):
        candidate = by_name.get(internal_name)
        if candidate is None:
            raise SystemExit(
                f"content/publish.json names {internal_name!r}, which WDM Stable does "
                "not ship as a candidate"
            )
        if candidate.classification != SAFE:
            raise SystemExit(
                f"content/publish.json names {internal_name!r}, which is "
                f"{candidate.classification}: {', '.join(candidate.findings)}"
            )
        if candidate.slug != slug:
            raise SystemExit(
                f"content/publish.json maps {internal_name!r} to slug {slug!r} but "
                f"content/titles.json says {candidate.slug!r}"
            )
        chosen.append(candidate)
    return chosen


def select_published(discovery: Discovery, slug: str) -> List[Candidate]:
    """Select one approved slug, never merely a classifier-SAFE candidate."""
    approved = published_candidates(discovery)
    by_slug = {candidate.slug: candidate for candidate in approved}
    candidate = by_slug.get(slug)
    if candidate is None:
        accepted = ", ".join(sorted(by_slug))
        raise SystemExit(
            f"unknown or unapproved map {slug!r}; approved map slugs: {accepted}"
        )
    return [candidate]


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
        # WDM's own transform ID when it supplies one, otherwise absent.  Never a
        # synthesised row: see semantic.world_map_declaration.
        candidate.transform_ids[0] if candidate.transform_ids else None,
    )
    tiles = artwork_targets(candidate)
    floors = len(candidate.floor_ids)
    # The description states only what the package actually contains, so a map
    # with no WDM transform does not advertise one.  A map that does carry WDM's
    # row keeps the wording it has always shipped with, so regenerating an
    # existing package produces byte-identical output.
    transform_clause = (
        "the instance WorldMapTransforms row"
        if candidate.transform_ids
        else "no WorldMapTransforms row (WDM supplies none for this map)"
    )
    manifest = {
        "schema": SCHEMA,
        "package": paths.package_key(candidate.slug),
        "name": candidate.title,
        "version": VERSION,
        "description": (
            f"Native pre-Cataclysm {candidate.title} instance map: {floors} DungeonMap "
            f"floor{'' if floors == 1 else 's'}, {len(candidate.chunk_ids)} "
            f"DungeonMapChunk entries, one WorldMapArea, {transform_clause} and "
            f"{len(tiles)} client BLP tiles."
        ),
        "content": tiles,
        "worldMaps": [declaration],
    }
    if not floors:
        # A reader who finds `"floors": []` cannot tell a deliberate native shape
        # from a package that forgot its geometry, so the description says which
        # it is.  The 3.3.5a client draws such a map from its WorldMapArea row and
        # its tiles alone: stock build 12340 already ships 48 such areas, WDM
        # Stable 55, and WDM declares no DungeonMap, DungeonMapChunk or
        # WorldMapTransforms row for this one, so nothing is missing.
        manifest["description"] += (
            " This map is floorless by design: the 3.3.5a client draws it from "
            "this WorldMapArea row and its tiles alone, WDM Stable declares no "
            "DungeonMap, DungeonMapChunk or WorldMapTransforms row for it, and the "
            "three remaining world-map DBCs are therefore left stock byte for "
            "byte."
        )
    if candidate.artwork_renames:
        # Stated in the package's own description because it is the one thing a
        # reader of this manifest cannot see: the bytes are WDM's, and only the
        # path the client reads was rebuilt from the area's own internal_name.
        manifest["description"] += (
            f" WDM Stable spells this map's artwork directory "
            f"{candidate.source_dir} in different capitals than the WorldMapArea "
            f"internal_name {candidate.internal_name}; the {len(tiles)} tiles are "
            "WDM's bytes installed at the names the client derives from "
            "internal_name."
        )
    locales = floor_label_locales(declaration)
    if locales:
        # Declaring floor labels obliges the package to name the exact stock
        # FrameXML table of contents mod-content-manager will extend.  The digest
        # is read from the vendored file, so a manifest can never claim a TOC the
        # composer would not accept.
        manifest["clientFrameXml"] = {
            "stockTocSource": STOCK_TOC_MEMBER,
            "stockTocSha256": stock_toc_sha256(),
        }
        manifest["description"] += (
            f" Dungeon floor labels for {len(locales)} client locales, added to "
            f"the stock FrameXML by one added module."
        )
    return manifest


def serialise(manifest: Dict[str, object]) -> bytes:
    """Stable manifest bytes: 1-space indent, LF, trailing newline.

    Matches the reviewed fixture style, and is deterministic so regenerating an
    unchanged manifest produces no diff.
    """
    return (
        json.dumps(manifest, indent=1, ensure_ascii=False, sort_keys=True).encode("utf-8")
        + b"\n"
    )


def publish_slugs() -> Dict[str, str]:
    """``internalName -> slug`` from ``content/publish.json``."""
    if not paths.PUBLISH_FILE.is_file():
        return {}
    data = json.loads(paths.PUBLISH_FILE.read_text(encoding="utf-8"))
    return {str(key): str(value) for key, value in data.items()}


def write_manifests(
    discovery: Discovery,
    write: bool = True,
    candidates: Sequence[Candidate] | None = None,
) -> List[Path]:
    written: List[Path] = []
    for candidate in candidates or published_candidates(discovery):
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

    The tile is looked up by leaf name beneath the candidate's WDM artwork
    directory, matching how ``mod-content-manager``'s own end-to-end test supplies
    artwork.  The directory is the one the vendored tree actually uses, which is
    the ``internal_name`` spelling except for the two maps WDM spells with
    different capitals than their own ``WorldMapArea`` row.
    """
    name = Path(entry["source"]).name
    source = artwork_root / candidate.source_dir / name
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
    root = artwork_root or paths.wdm_artwork_dir()
    payloads = [
        (item["source"], _artwork_source(candidate, item, root).read_bytes())
        for item in entries
    ]
    return _write_epf(manifest, manifest_bytes, payloads, output, str(manifest_path))


def _write_epf(
    manifest: Dict[str, object],
    manifest_bytes: bytes,
    payloads: Sequence[Tuple[str, bytes]],
    output: Path,
    label: str,
) -> Path:
    """Write one normal Content Manager EPF from validated direct resources."""
    entries = manifest["content"]
    sources = [item["source"] for item in entries]
    targets = [item["target"] for item in entries]
    if not entries:
        raise SystemExit(f"{label}: no artwork declared")
    if len(sources) != len(set(sources)):
        raise SystemExit(f"{label}: duplicate package source")
    if len(targets) != len(set(targets)):
        raise SystemExit(f"{label}: duplicate install target")
    if [name for name, _ in payloads] != sources:
        raise SystemExit(f"{label}: payload order does not match manifest content")
    if any(not blob for _, blob in payloads):
        raise SystemExit(f"{label}: empty artwork payload")

    # ``clientFrameXml`` is declared, so the stock table of contents travels in the
    # EPF unchanged.  The digest is re-derived here and compared with the manifest,
    # so an EPF can never disagree with the pin mod-content-manager enforces.
    toc_bytes = b""
    declared = manifest.get("clientFrameXml")
    if declared is not None:
        if declared.get("stockTocSource") != STOCK_TOC_MEMBER:
            raise SystemExit(
                f"{label}: clientFrameXml.stockTocSource must be {STOCK_TOC_MEMBER}"
            )
        toc_bytes = stock_toc_bytes()
        digest = hashlib.sha256(toc_bytes).hexdigest()
        if digest != declared.get("stockTocSha256"):
            raise SystemExit(
                f"{label}: vendored FrameXML.toc digest {digest} does not match "
                f"declared {declared.get('stockTocSha256')}"
            )
        if STOCK_TOC_MEMBER in targets or STOCK_TOC_MEMBER in sources:
            raise SystemExit(f"{label}: stock FrameXML.toc declared twice")

    output.parent.mkdir(parents=True, exist_ok=True)
    # ZIP_STORED plus a fixed timestamp: no clock, no compressor version, no
    # filesystem ordering.  Same inputs, same bytes.
    with zipfile.ZipFile(output, "w", zipfile.ZIP_STORED) as archive:
        archive.writestr(zipfile.ZipInfo("manifest.json", FIXED_TIME), manifest_bytes)
        if toc_bytes:
            archive.writestr(zipfile.ZipInfo(STOCK_TOC_MEMBER, FIXED_TIME), toc_bytes)
        for name, blob in payloads:
            archive.writestr(zipfile.ZipInfo(name, FIXED_TIME), blob)
    return output


def build_selected(
    discovery: Discovery,
    candidates: Sequence[Candidate],
    output_dir: Path = paths.DIST_DIR,
) -> List[Path]:
    outputs: List[Path] = []
    for candidate in candidates:
        manifest_path = paths.CONTENT_DIR / candidate.slug / "manifest.json"
        if not manifest_path.is_file():
            raise SystemExit(f"missing manifest: {manifest_path}")
        output = output_dir / f"{paths.package_key(candidate.slug)}.epf"
        build_epf(candidate, manifest_path, output)
        outputs.append(output)
    return outputs


def combined_manifest_for(
    candidates: Sequence[Candidate], discovery: Discovery
) -> Dict[str, object]:
    """One schema-3 package containing the approved manifests' direct content."""
    content: List[Dict[str, str]] = []
    world_maps: List[Dict[str, object]] = []
    frame_xml = None
    for candidate in candidates:
        component = manifest_for(candidate, discovery)
        content.extend(component["content"])
        world_maps.extend(component["worldMaps"])
        declared = component.get("clientFrameXml")
        if declared is not None:
            if frame_xml is not None and frame_xml != declared:
                raise SystemExit("approved maps disagree about the stock FrameXML baseline")
            frame_xml = declared

    manifest: Dict[str, object] = {
        "schema": SCHEMA,
        "package": RELEASE_PACKAGE,
        "name": "Native Instance Maps",
        "version": VERSION,
        "description": (
            f"Native pre-Cataclysm instance maps for {len(candidates)} approved maps, "
            "packaged directly from the reviewed individual map declarations."
        ),
        # These are the two historical owners of resources now shipped by the
        # canonical combined package.  Individual map packages intentionally
        # omit this declaration: migration is one-way into the canonical owner.
        "replaces": [
            "mod-deadmines-dungeon-map",
            "mod-native-instance-maps.karazhan",
        ],
        "content": content,
        "worldMaps": world_maps,
    }
    if frame_xml is not None:
        manifest["clientFrameXml"] = frame_xml
    return manifest


def build_release(
    discovery: Discovery,
    output: Path = paths.DIST_DIR / f"{RELEASE_PACKAGE}.epf",
) -> Path:
    candidates = published_candidates(discovery)
    manifest = combined_manifest_for(candidates, discovery)
    payloads: List[Tuple[str, bytes]] = []
    root = paths.wdm_artwork_dir()
    for candidate in candidates:
        for entry in artwork_targets(candidate):
            payloads.append(
                (entry["source"], _artwork_source(candidate, entry, root).read_bytes())
            )
    manifest_bytes = serialise(manifest)
    return _write_epf(manifest, manifest_bytes, payloads, output, "combined release")


def clean_outputs(output_dir: Path = paths.DIST_DIR) -> List[Path]:
    """Remove generated EPFs only; source-controlled inputs are out of scope."""
    removed: List[Path] = []
    if not output_dir.is_dir():
        return removed
    for target in sorted(output_dir.glob("*.epf")):
        if target.is_file():
            target.unlink()
            removed.append(target)
    return removed


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--map", metavar="SLUG", help="build one approved map EPF")
    mode.add_argument(
        "--all-approved",
        action="store_true",
        help="build every map named by content/publish.json as an individual EPF",
    )
    mode.add_argument(
        "--release", action="store_true", help="build one combined approved release EPF"
    )
    mode.add_argument("--manifests", action="store_true", help="write manifests only")
    mode.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if manifests are out of date; never writes anything",
    )
    mode.add_argument(
        "--clean", action="store_true", help="remove generated dist/*.epf files only"
    )
    options = parser.parse_args(argv)

    if options.clean:
        for target in clean_outputs():
            print(f"removed {target.relative_to(paths.REPO_ROOT)}")
        return 0

    discovery = discover(paths.wdm_dbc_dir(), paths.wdm_artwork_dir(), paths.stock_dbc_dir())

    if options.check:
        stale = write_manifests(discovery, write=False)
        for target in stale:
            print(f"out of date: {target.relative_to(paths.REPO_ROOT)}", file=sys.stderr)
        if stale:
            print("run: python3 tools/package.py", file=sys.stderr)
            return 1
        return 0

    candidates = (
        select_published(discovery, options.map)
        if options.map
        else published_candidates(discovery)
    )
    paths.CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    for target in write_manifests(discovery, write=True, candidates=candidates):
        print(f"wrote: {target.relative_to(paths.REPO_ROOT)}")

    if options.manifests:
        return 0
    if options.release:
        output = build_release(discovery)
        print(f"wrote {output.relative_to(paths.REPO_ROOT)} ({output.stat().st_size} bytes)")
        return 0

    for output in build_selected(discovery, candidates):
        size = output.stat().st_size
        print(f"wrote {output.relative_to(paths.REPO_ROOT)} ({size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
