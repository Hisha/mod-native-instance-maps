#!/usr/bin/env python3
"""Repository layout and default locations shared by every tool in ``tools/``.

Everything is resolved relative to this file so a checkout can be moved or
copied without editing anything. The WDM source material and stock build-12340
baselines are immutable, repository-owned inputs. Only the mod-content-manager
source integration is external, selected explicitly or from a sibling checkout.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / "tools"
CONTENT_DIR = REPO_ROOT / "content"
DIST_DIR = REPO_ROOT / "dist"
REPORTS_DIR = REPO_ROOT / "reports"
TESTS_DIR = REPO_ROOT / "tests"
UPSTREAM_PATCH_DIR = REPO_ROOT / "upstream" / "WDM-patch"
UPSTREAM_STABLE_DIR = UPSTREAM_PATCH_DIR / "Stable"
UPSTREAM_SHA256SUMS = UPSTREAM_PATCH_DIR / "SHA256SUMS"
UPSTREAM_SOURCE_JSON = UPSTREAM_PATCH_DIR / "SOURCE.json"
UPSTREAM_SOURCE_MD = UPSTREAM_PATCH_DIR / "SOURCE.md"

#: WDM-addons carries the author's own instance floor names as Lua globals.  The
#: vendored copies are the sole source for every floor label this project emits,
#: so regenerating a manifest never depends on an external WDM checkout.
UPSTREAM_ADDONS_DIR = REPO_ROOT / "upstream" / "WDM-addons"
WDM_LOCALE_DIR = UPSTREAM_ADDONS_DIR / "WDM" / "locales" / "global"
WDM_LOCALE_SHA256SUMS = UPSTREAM_ADDONS_DIR / "SHA256SUMS"

#: The stock build-12340 ``Interface/FrameXML/FrameXML.toc``.  mod-content-manager
#: never regenerates FrameXML; it inserts one module line into this exact,
#: digest-pinned file.  Vendoring it keeps the EPF self-contained and lets the
#: pinned digest be reviewed without the client installed.
STOCK_FRAMEXML_DIR = REPO_ROOT / "upstream" / "wow-3.3.5a-build-12340"
STOCK_FRAMEXML_TOC = (
    STOCK_FRAMEXML_DIR / "Interface" / "FrameXML" / "FrameXML.toc"
)
STOCK_FRAMEXML_SOURCE_JSON = STOCK_FRAMEXML_DIR / "SOURCE.json"
STOCK_FRAMEXML_SHA256SUMS = STOCK_FRAMEXML_DIR / "SHA256SUMS"
STOCK_DBC_DIR = STOCK_FRAMEXML_DIR / "DBFilesClient"
STOCK_DBC_SHA256SUMS = STOCK_DBC_DIR / "SHA256SUMS"
STOCK_DBC_SOURCE_JSON = STOCK_DBC_DIR / "SOURCE.json"

WORLD_MAP_TABLES = (
    "DungeonMap",
    "DungeonMapChunk",
    "WorldMapArea",
    "WorldMapTransforms",
)


def wdm_locale_dir() -> Path:
    """Vendored WDM-addons locale string tables, one file per client locale."""
    return WDM_LOCALE_DIR

#: WDM Stable ships identical DBFilesClient for every client locale.  enUS is the
#: representative tree; :func:`verify_locale_parity` proves that at run time.
DEFAULT_LOCALE = "enUS"


def wdm_root(locale: str = DEFAULT_LOCALE) -> Path:
    """Root of one vendored WDM Stable locale."""
    return UPSTREAM_STABLE_DIR / locale


def wdm_dbc_dir(locale: str = DEFAULT_LOCALE) -> Path:
    return wdm_root(locale) / "DBFilesClient"


def wdm_artwork_dir(locale: str = DEFAULT_LOCALE) -> Path:
    return wdm_root(locale) / "Interface" / "WorldMap"


def stock_dbc_dir() -> Path:
    """Return the hash-verified, vendored stock build-12340 baseline."""
    expected = {}
    if not STOCK_DBC_SHA256SUMS.is_file():
        raise RuntimeError(f"missing stock DBC checksum manifest: {STOCK_DBC_SHA256SUMS}")
    for line in STOCK_DBC_SHA256SUMS.read_text(encoding="ascii").splitlines():
        digest, name = line.split(None, 1)
        expected[name.strip()] = digest
    wanted = {f"{table}.dbc" for table in WORLD_MAP_TABLES}
    if set(expected) != wanted:
        raise RuntimeError("stock DBC checksum manifest must name exactly four world-map DBCs")
    for name, digest in expected.items():
        source = STOCK_DBC_DIR / name
        if not source.is_file():
            raise RuntimeError(f"missing vendored stock DBC: {source}")
        actual = hashlib.sha256(source.read_bytes()).hexdigest()
        if actual != digest:
            raise RuntimeError(
                f"vendored stock DBC hash mismatch for {name}: {actual}, expected {digest}"
            )
    return STOCK_DBC_DIR


def content_manager_dir() -> Path:
    """Declared or sibling mod-content-manager checkout for cross-validation."""
    override = os.environ.get("MOD_CONTENT_MANAGER_DIR")
    if override:
        return Path(override).expanduser()
    return REPO_ROOT.parent / "mod-content-manager"


def deadmines_golden_fixture() -> Path:
    """Known-good Content Manager Deadmines manifest."""
    return content_manager_dir() / "tests" / "fixtures" / "deadmines" / "manifest.json"


#: Explicit list of candidates this project has decided to package.  The
#: classifier answers "can this ship?"; this file is the separate, human decision
#: of which shippable maps are actually being published.  A SAFE candidate absent
#: from this list is reported but not generated, so a classifier correction can
#: never mass-publish a backlog on its own.
PUBLISH_FILE = CONTENT_DIR / "publish.json"


def package_key(slug: str) -> str:
    return f"mod-native-instance-maps.{slug}"


def slugify(name: str) -> str:
    """Deterministic package slug from a WorldMapArea internal name."""
    return "".join(
        char.lower() if char.isalnum() and char.isascii() else "-"
        for char in name
    ).strip("-")
