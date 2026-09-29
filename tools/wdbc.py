#!/usr/bin/env python3
"""Strict WDBC reader for the four build-12340 native world-map tables.

The reader is intentionally paranoid.  Every structural assumption it makes is
verified, because a silently mis-parsed header turns the 20 header bytes into
"record zero" and then produces billion-sized IDs that look like real data.

Physical layout (little endian)::

    offset 0   char[4]  magic, always b"WDBC"
    offset 4   uint32   record_count
    offset 8   uint32   field_count
    offset 12  uint32   record_size   (field_count * 4 for every table we use)
    offset 16  uint32   string_block_size
    offset 20  record_count * record_size bytes of record data
    ...        string_block_size bytes of string data

Only the Python standard library is used, and the reader is byte oriented:
records are never reformatted before they are compared, so "modified" always
means "the raw record bytes differ".
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

__all__ = [
    "WdbcError",
    "Field",
    "TableSpec",
    "DbcRecord",
    "DbcFile",
    "HEADER_SIZE",
    "MAGIC",
    "TABLES",
    "TABLE_NAMES",
    "table_spec",
    "parse_bytes",
    "parse_file",
    "f32",
]

MAGIC = b"WDBC"
HEADER_FORMAT = "<4sIIII"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # 20
_U32 = struct.Struct("<I")
_F32 = struct.Struct("<f")
_I32 = struct.Struct("<i")


class WdbcError(ValueError):
    """Raised for any structural or semantic defect found while reading a WDBC."""


def f32(word: int) -> float:
    """Decode a raw 32-bit word as an IEEE-754 single, exactly."""
    return _F32.unpack(_U32.pack(word & 0xFFFFFFFF))[0]


def _bits_to_i32(word: int) -> int:
    return _I32.unpack(_U32.pack(word & 0xFFFFFFFF))[0]


# ---------------------------------------------------------------------------
# Field / table descriptors
# ---------------------------------------------------------------------------

UINT32 = "uint32"
INT32 = "int32"
FLOAT32 = "float32"
STROFF = "stroff"

# Manifest key for each descriptor word.  ``None`` means the word is not authored
# in a mod-content-manager worldMaps[] entry: it is either the ID (declared
# elsewhere in the JSON) or the MapID (written from ``worldMaps[].mapId``).
_DUNGEON_MAP = (
    ("ID", UINT32, "id"),
    ("MapID", UINT32, None),
    ("Floor", UINT32, "floor"),
    ("field3", FLOAT32, "field3"),
    ("field4", FLOAT32, "field4"),
    ("field5", FLOAT32, "field5"),
    ("field6", FLOAT32, "field6"),
    ("field7", UINT32, "field7"),
)

_DUNGEON_MAP_CHUNK = (
    ("ID", UINT32, "id"),
    ("MapID", UINT32, None),
    ("field2", UINT32, "field2"),
    ("DungeonMapID", UINT32, "dungeonMapId"),
    ("field4", FLOAT32, "field4"),
)

_WORLD_MAP_AREA = (
    ("ID", UINT32, "id"),
    ("map_id", UINT32, None),
    ("area_id", UINT32, "areaId"),
    ("internal_name", STROFF, "internalName"),
    ("y1", FLOAT32, "y1"),
    ("y2", FLOAT32, "y2"),
    ("x1", FLOAT32, "x1"),
    ("x2", FLOAT32, "x2"),
    ("virtual_map_id", INT32, "virtualMapId"),
    ("dungeonMap_id", INT32, "dungeonMapId"),
    ("parentMapID", UINT32, "parentMapId"),
)

_WORLD_MAP_TRANSFORMS = (
    ("ID", UINT32, "id"),
    ("MapID", UINT32, None),
    ("RegionBottom", FLOAT32, "regionBottom"),
    ("RegionRight", FLOAT32, "regionRight"),
    ("RegionTop", FLOAT32, "regionTop"),
    ("RegionLeft", FLOAT32, "regionLeft"),
    ("NewMapID", UINT32, "newMapId"),
    ("RegionOffset_X", FLOAT32, "regionOffsetX"),
    ("RegionOffset_Y", FLOAT32, "regionOffsetY"),
    ("NewDungeonMapID", UINT32, "newDungeonMapId"),
)


@dataclass(frozen=True)
class Field:
    name: str
    kind: str
    key: Optional[str] = None

    def decode(self, word: int) -> object:
        if self.kind == FLOAT32:
            return f32(word)
        if self.kind == INT32:
            return _bits_to_i32(word)
        return word


@dataclass(frozen=True)
class TableSpec:
    name: str
    fields: Tuple[Field, ...]

    @property
    def field_count(self) -> int:
        return len(self.fields)

    @property
    def record_size(self) -> int:
        return len(self.fields) * 4

    @property
    def id_index(self) -> int:
        return 0

    @property
    def map_index(self) -> int:
        for index, item in enumerate(self.fields):
            if item.name in ("MapID", "map_id"):
                return index
        raise WdbcError(f"{self.name} has no MapID/map_id field")

    def key_index(self, key: str) -> int:
        for index, item in enumerate(self.fields):
            if item.key == key:
                return index
        raise WdbcError(f"{self.name} has no manifest key {key!r}")


TABLES: Dict[str, TableSpec] = {
    "DungeonMap": TableSpec("DungeonMap", tuple(Field(*row) for row in _DUNGEON_MAP)),
    "DungeonMapChunk": TableSpec(
        "DungeonMapChunk", tuple(Field(*row) for row in _DUNGEON_MAP_CHUNK)
    ),
    "WorldMapArea": TableSpec(
        "WorldMapArea", tuple(Field(*row) for row in _WORLD_MAP_AREA)
    ),
    "WorldMapTransforms": TableSpec(
        "WorldMapTransforms", tuple(Field(*row) for row in _WORLD_MAP_TRANSFORMS)
    ),
}

# Declaration order of the four tables; also the order the composer owns them.
TABLE_NAMES: Tuple[str, ...] = (
    "DungeonMap",
    "DungeonMapChunk",
    "WorldMapArea",
    "WorldMapTransforms",
)


def table_spec(name: str) -> TableSpec:
    try:
        return TABLES[name]
    except KeyError:
        raise WdbcError(f"unsupported world-map table {name!r}") from None


# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DbcRecord:
    """One physical record, kept in both declaration order and ID-addressable form."""

    index: int
    spec: TableSpec
    words: Tuple[int, ...]
    raw: bytes
    strings: Tuple[str, ...] = ()

    @property
    def id(self) -> int:
        return self.words[0]

    def uint(self, name: str) -> int:
        return self.words[self._index(name)]

    def value(self, name: str) -> object:
        index = self._index(name)
        item = self.spec.fields[index]
        if item.kind == STROFF:
            return self.strings[index]
        return item.decode(self.words[index])

    def key(self, key: str) -> object:
        """Value of a mod-content-manager manifest key."""
        index = self.spec.key_index(key)
        item = self.spec.fields[index]
        if item.kind == STROFF:
            return self.strings[index]
        return item.decode(self.words[index])

    def map_id(self) -> int:
        return self.words[self.spec.map_index]

    def _index(self, name: str) -> int:
        for index, item in enumerate(self.spec.fields):
            if item.name == name:
                return index
        raise WdbcError(f"{self.spec.name} has no field {name!r}")


@dataclass
class DbcFile:
    path: Optional[Path]
    spec: TableSpec
    magic: bytes
    record_count: int
    field_count: int
    record_size: int
    string_block_size: int
    file_size: int
    expected_size: int
    trailing_bytes: int
    string_block: bytes
    records: List[DbcRecord] = field(default_factory=list)
    duplicate_ids: Dict[int, List[int]] = field(default_factory=dict)
    by_id: Dict[int, DbcRecord] = field(default_factory=dict)

    def __post_init__(self) -> None:
        index: Dict[int, int] = {}
        duplicates: Dict[int, List[int]] = {}
        for record in self.records:
            previous = index.get(record.id)
            if previous is None:
                index[record.id] = record.index
            else:
                duplicates.setdefault(record.id, [previous]).append(record.index)
        self.by_id = {record.id: record for record in self.records}
        self.duplicate_ids = duplicates

    def __iter__(self) -> Iterator[DbcRecord]:
        return iter(self.records)

    def __len__(self) -> int:
        return len(self.records)

    def get(self, record_id: int) -> DbcRecord:
        try:
            return self.by_id[record_id]
        except KeyError:
            raise WdbcError(f"{self.describe()}: no record with ID {record_id}") from None

    def ids(self) -> List[int]:
        return [record.id for record in self.records]

    def describe(self) -> str:
        return str(self.path) if self.path is not None else f"<memory:{self.spec.name}>"

    def rows_where(self, **conditions: int) -> List[DbcRecord]:
        """Records whose named field equals the given raw unsigned value."""
        out: List[DbcRecord] = []
        for record in self.records:
            for name, expected in conditions.items():
                if record.uint(name) != expected:
                    break
            else:
                out.append(record)
        return out

    def records_for_map(self, map_id: int) -> List[DbcRecord]:
        """Records whose MapID/map_id column equals ``map_id`` (declaration order)."""
        index = self.spec.map_index
        return [record for record in self.records if record.words[index] == map_id]


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def _read_string(block: bytes, offset: int, where: str) -> str:
    if offset < 0 or offset > len(block):
        raise WdbcError(f"{where}: string offset {offset} outside 0..{len(block)}")
    if offset == len(block):
        raise WdbcError(f"{where}: string offset {offset} addresses past the string block")
    end = block.find(b"\x00", offset)
    if end == -1:
        raise WdbcError(f"{where}: string at offset {offset} is not NUL terminated")
    try:
        return block[offset:end].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise WdbcError(f"{where}: string at offset {offset} is not valid UTF-8: {exc}") from None


def parse_bytes(
    data: bytes,
    spec: TableSpec,
    *,
    path: Optional[Path] = None,
    allow_trailing: bool = False,
    require_packed: bool = True,
    require_unique_ids: bool = True,
) -> DbcFile:
    """Parse and fully validate WDBC ``data`` against ``spec``."""
    where = str(path) if path is not None else f"<memory:{spec.name}>"
    if len(data) < HEADER_SIZE:
        raise WdbcError(
            f"{where}: truncated header ({len(data)} bytes, need {HEADER_SIZE}); "
            "the first record must start at offset 20"
        )
    magic, record_count, field_count, record_size, string_block_size = struct.unpack_from(
        HEADER_FORMAT, data, 0
    )
    if magic != MAGIC:
        raise WdbcError(f"{where}: bad magic {magic!r}, expected {MAGIC!r}")

    if field_count != spec.field_count:
        raise WdbcError(
            f"{where}: field_count {field_count} does not match {spec.name} "
            f"layout ({spec.field_count})"
        )
    if record_size != spec.record_size:
        raise WdbcError(
            f"{where}: record_size {record_size} does not match the {spec.name} "
            f"layout ({spec.field_count * 4})"
        )
    if require_packed and record_size != field_count * 4:
        raise WdbcError(
            f"{where}: record_size {record_size} is not field_count * 4 "
            f"({field_count} * 4 = {field_count * 4})"
        )

    expected_size = HEADER_SIZE + record_count * record_size + string_block_size
    if len(data) < expected_size:
        raise WdbcError(
            f"{where}: truncated body: header declares {expected_size} bytes "
            f"(20 + {record_count}*{record_size} + {string_block_size}) but the "
            f"file is {len(data)} bytes"
        )
    trailing = len(data) - expected_size
    if trailing and not allow_trailing:
        raise WdbcError(
            f"{where}: {trailing} unexplained trailing byte(s) after the string block"
        )

    record_start = HEADER_SIZE
    string_start = record_start + record_count * record_size
    string_block = data[string_start:string_start + string_block_size]

    records: List[DbcRecord] = []
    seen: Dict[int, int] = {}
    duplicates: Dict[int, List[int]] = {}
    for index in range(record_count):
        start = record_start + index * record_size
        raw = data[start:start + record_size]
        words = tuple(
            _U32.unpack_from(raw, offset)[0] for offset in range(0, record_size, 4)
        )
        strings: List[str] = [""] * spec.field_count
        for position, item in enumerate(spec.fields):
            if item.kind == STROFF:
                strings[position] = _read_string(
                    string_block,
                    words[position],
                    f"{where} record {index} (ID {words[0]}) field {item.name}",
                )
        record = DbcRecord(
            index=index,
            spec=spec,
            words=words,
            raw=raw,
            strings=tuple(strings),
        )
        if record.id == 0:
            raise WdbcError(f"{where}: record {index} has a zero ID")
        previous = seen.get(record.id)
        if previous is not None:
            duplicates.setdefault(record.id, [previous]).append(index)
        else:
            seen[record.id] = index
        records.append(record)

    if require_unique_ids and duplicates:
        raise WdbcError(
            f"{where}: duplicate record ID(s) "
            + ", ".join(
                f"{key} at records {[i + 1 for i in value]}"
                for key, value in sorted(duplicates.items())
            )
            + "; a DBC must address each row uniquely"
        )

    return DbcFile(
        path=path,
        spec=spec,
        magic=magic,
        record_count=record_count,
        field_count=field_count,
        record_size=record_size,
        string_block_size=string_block_size,
        file_size=len(data),
        expected_size=expected_size,
        trailing_bytes=trailing,
        string_block=string_block,
        records=records,
        duplicate_ids=duplicates,
    )


def parse_file(
    path: Path | str,
    table: str,
    *,
    allow_trailing: bool = False,
) -> DbcFile:
    """Read and validate ``path`` as the named world-map table."""
    spec = table_spec(table)
    resolved = Path(path)
    try:
        data = resolved.read_bytes()
    except OSError as exc:
        raise WdbcError(f"cannot read {resolved}: {exc}") from None
    return parse_bytes(data, spec, path=resolved, allow_trailing=allow_trailing)


def build_bytes(
    spec: TableSpec,
    records: Sequence[Sequence[int]],
    string_block: bytes = b"\x00",
) -> bytes:
    """Serialise records back to WDBC bytes.  Used by the round-trip tests."""
    out = bytearray()
    out += struct.pack(
        HEADER_FORMAT, MAGIC, len(records), spec.field_count, spec.record_size, len(string_block)
    )
    for row in records:
        if len(row) != spec.field_count:
            raise WdbcError(f"row width {len(row)} does not match {spec.name}")
        for word in row:
            out += _U32.pack(word & 0xFFFFFFFF)
    out += string_block
    return bytes(out)
