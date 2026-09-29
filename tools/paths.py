#!/usr/bin/env python3
"""Repository layout and default locations shared by every tool in ``tools/``.

Everything is resolved relative to this file so a checkout can be moved or
copied without editing anything.  External reference trees (the stock 3.3.5a
DBC baseline and the mod-content-manager golden fixture) are *not* required to
regenerate content; they are only needed by the validation commands and the
test suite, which skip or fail loudly when they are absent.
"""

from __future__ import annotations

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
    """Stock 3.3.5a build-12340 baseline used by mod-content-manager.

    Overridable with ``MOD_NATIVE_INSTANCE_MAPS_STOCK_DBC``; the directory is
    read-only reference data and is never written to.
    """
    override = os.environ.get("MOD_NATIVE_INSTANCE_MAPS_STOCK_DBC")
    if override:
        return Path(override).expanduser()
    return Path("/home/smithkt/git/WDM-patch/wdm-stock-dbc")


def content_manager_dir() -> Path:
    """mod-content-manager checkout, used only for cross-validation."""
    override = os.environ.get("MOD_CONTENT_MANAGER_DIR")
    if override:
        return Path(override).expanduser()
    return Path("/home/smithkt/git/mod-content-manager")


def deadmines_golden_fixture() -> Path:
    """Known-good Content Manager Deadmines manifest."""
    return content_manager_dir() / "tests" / "fixtures" / "deadmines" / "manifest.json"


def wdm_deadmines_golden_dbc_dir() -> Path:
    """WDM project's own minimal Deadmines composition, a byte-level oracle."""
    override = os.environ.get("WDM_PATCH_DIR")
    root = Path(override).expanduser() if override else Path("/home/smithkt/git/WDM-patch")
    return root / "minimal-deadmines" / "DBFilesClient"


def package_key(slug: str) -> str:
    return f"mod-native-instance-maps.{slug}"


def slugify(name: str) -> str:
    """Deterministic package slug from a WorldMapArea internal name."""
    return "".join(
        char.lower() if char.isalnum() and char.isascii() else "-"
        for char in name
    ).strip("-")
