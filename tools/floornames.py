#!/usr/bin/env python3
"""Read dungeon floor labels out of WDM's own locale string tables.

WDM publishes instance floor names as ordinary Lua globals --
``DUNGEON_FLOOR_KARAZHAN7 = "Lower Broken Stair";`` -- in one file per locale
under ``WDM/locales/global``.  Those strings are the label the author wrote, so
this project copies them verbatim instead of retyping or translating them.

Only the vendored copies under ``upstream/WDM-addons`` are read.  Nothing here
reaches outside the repository, so regenerating a manifest needs no external
WDM checkout, and the vendored file hashes in ``SHA256SUMS`` are the provenance
for every string that ends up in a package.

Nothing is invented.  A map whose locale file is missing, or that omits a floor,
simply has no label for it and the stock ``Floor %d`` label stays.  WDM ships no
``itIT`` or ``ptBR`` table at all, so those two client locales keep stock labels
for every map -- which is stock behaviour, not a gap in this importer.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

from paths import wdm_locale_dir

#: ``DUNGEON_FLOOR_<TOKEN><LEVEL>``.  The token is the WorldMapArea internal
#: name ASCII-folded to upper case, matching mod-content-manager's generated
#: Lua lookup exactly; the level is the trailing decimal floor index.
_GLOBAL = re.compile(r"^DUNGEON_FLOOR_([A-Z0-9_]+?)([0-9]{1,4})\s*=\s*(.*)$")

#: WDM also publishes a handful of unnumbered globals (``DUNGEON_FLOOR_ZULFARRAK``)
#: that name the instance rather than a floor.  WDM's own dropdown code reads only
#: ``DUNGEON_FLOOR_<TOKEN><floorNum>`` and falls back to ``string.format(FLOOR_NUMBER,
#: floorNum)`` otherwise, so an unnumbered global is skipped here for the same
#: reason: promoting one to "floor 1" would be a mapping WDM never makes.
_INSTANCE_ONLY = re.compile(r"^DUNGEON_FLOOR_[A-Z0-9_]+\s*=\s*\".*\";?\s*$")

#: Matches mod-content-manager's floor-name rules, which it enforces again on
#: the manifest: 1..1023 and 1..255 UTF-8 bytes with no control characters.
MAX_LEVEL = 1023
MAX_LABEL_BYTES = 255

#: The locales a build-12340 client can actually select.  A vendored file
#: outside this set is ignored rather than emitted into a manifest the client
#: could never look up.
CLIENT_LOCALES = (
    "deDE", "enCN", "enGB", "enUS", "esES", "esMX",
    "frFR", "itIT", "koKR", "ptBR", "ruRU", "zhCN", "zhTW",
)


class FloorNameError(ValueError):
    """A vendored WDM locale table does not match its published shape."""


def floor_token(internal_name: str) -> str:
    """The token WDM uses in ``DUNGEON_FLOOR_<token><level>``.

    Same rule as mod-content-manager's ``ContentFrameXml::FloorNameToken``:
    printable ASCII, lower case folded up.  A non-ASCII internal name is refused
    rather than folded, because reproducing the client's own Latin-1 fold here
    would be a guess.
    """
    if not internal_name:
        raise FloorNameError("WorldMapArea internal name is empty")
    for char in internal_name:
        if not (32 <= ord(char) <= 126):
            raise FloorNameError(
                f"WorldMapArea internal name {internal_name!r} is outside the ASCII "
                "range the client floor lookup matches"
            )
    return "".join(
        char.upper() if "a" <= char <= "z" else char for char in internal_name
    )


def _lua_string(raw: str, path: Path) -> str:
    """Decode one quoted Lua string literal.

    Only the two-quote form WDM actually uses is supported.  Rejecting anything
    else loudly is the point: a silent misread would ship a floor label built
    from the wrong bytes.
    """
    value = raw.strip()
    if not value.endswith(";"):
        value = value + ";"
    body = value[:-1].rstrip()
    if len(body) < 2 or body[0] != '"' or body[-1] != '"':
        raise FloorNameError(f"{path}: floor name is not a double-quoted Lua string")
    inner = body[1:-1]
    for char in inner:
        code = ord(char)
        if code < 32 or code == 127:
            raise FloorNameError(f"{path}: floor name contains a control character")
        if code > 127:
            # The vendored tables are UTF-8.  Decode the escape-free remainder as
            # text, and let the byte-length check below enforce the manifest cap.
            continue
    if len(inner.encode("utf-8")) > MAX_LABEL_BYTES:
        raise FloorNameError(
            f"{path}: floor name exceeds {MAX_LABEL_BYTES} UTF-8 bytes"
        )
    if not inner:
        raise FloorNameError(f"{path}: floor name is empty")
    return inner


def read_locale_table(path: Path) -> Dict[str, str]:
    """Every ``DUNGEON_FLOOR_*`` global in one vendored WDM locale file."""
    table: Dict[str, str] = {}
    for number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.startswith("DUNGEON_FLOOR_"):
            continue
        match = _GLOBAL.match(line.strip())
        if match is None:
            if _INSTANCE_ONLY.match(line.strip()) is not None:
                # An instance name, not a floor label.  See _INSTANCE_ONLY.
                continue
            raise FloorNameError(f"{path}:{number}: unparsable DUNGEON_FLOOR_ line")
        table[f"{match.group(1)}{match.group(2)}"] = _lua_string(
            match.group(3), path
        )
    return table


def floor_labels(
    internal_name: str,
    locales: Tuple[str, ...] = CLIENT_LOCALES,
    root: Path | None = None,
) -> Dict[str, Dict[str, str]]:
    """``locale -> {floor level: label}`` for one map, from vendored WDM files.

    Locales WDM does not publish are absent from the result rather than filled
    in, so the client keeps its stock label for them.  Floors are keyed by the
    stock dropdown's own loop index, which is the trailing number in WDM's own
    global, so no renumbering happens here either.
    """
    token = floor_token(internal_name)
    directory = root or wdm_locale_dir()
    declaration: Dict[str, Dict[str, str]] = {}
    for locale in locales:
        path = directory / f"{locale.lower()}.lua"
        if not path.is_file():
            continue
        table = read_locale_table(path)
        labels: Dict[str, str] = {}
        for key, label in table.items():
            if not key.startswith(token):
                continue
            suffix = key[len(token):]
            if not suffix.isdigit():
                continue
            level = int(suffix)
            if level == 0:
                # WDM publishes a level-0 global for several maps (Black Temple,
                # Sunwell Plateau).  The stock dropdown numbers floors from 1, so
                # nothing can display index 0 and shipping it would put a label in
                # the generated Lua that no client state can reach.  Skipped, not
                # renamed to 1: that would shift every real floor by one.
                continue
            if not 1 <= level <= MAX_LEVEL:
                raise FloorNameError(
                    f"{path}: floor level {level} is outside 1..{MAX_LEVEL}"
                )
            if level in labels:
                raise FloorNameError(f"{path}: floor level {level} declared twice")
            labels[str(level)] = label
        if labels:
            declaration[locale] = labels
    return declaration


def missing_locales(internal_name: str) -> List[str]:
    """Client locales WDM publishes no table for.

    Reported, never emitted.  This exists so a reviewer can see *why* two
    locales keep stock labels instead of assuming they were forgotten.
    """
    token = floor_token(internal_name)
    directory = wdm_locale_dir()
    return [
        locale
        for locale in CLIENT_LOCALES
        if not (directory / f"{locale.lower()}.lua").is_file()
    ]