#!/usr/bin/env python3
"""Stock-versus-WDM forensic comparison for the four world-map tables.

Two questions are kept strictly apart, because conflating them hides the only
findings that actually need human judgement:

*Membership*
    which record IDs exist in the WDM file and not in the stock file (and the
    reverse).  This is a property of the source datasets alone.

*Classification*
    of the IDs that exist in both: are the raw record bytes identical, or did
    WDM change a row the client already has?  Equality is decided on
    ``record.raw`` bytes, never on a formatted float or a decoded dictionary.

A WDM row whose ID already exists in the stock table can never be shipped as a
mod-content-manager ``worldMaps[]`` addition: the composer refuses any declared
ID that is occupied in the verified stock baseline, and it must refuse, because
appending a second row with a live ID is not an append.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from wdbc import DbcFile, DbcRecord, TABLE_NAMES, WdbcError, parse_file

__all__ = [
    "RecordDiff",
    "TableForensics",
    "compare_table",
    "forensics",
    "sha256",
    "sha256_file",
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass
class RecordDiff:
    id: int
    stock_index: Optional[int]
    wdm_index: Optional[int]
    stock_raw: Optional[bytes]
    wdm_raw: Optional[bytes]
    stock_record: Optional[DbcRecord]
    wdm_record: Optional[DbcRecord]

    @property
    def kind(self) -> str:
        if self.stock_record is None:
            return "added"
        if self.wdm_record is None:
            return "removed"
        return "modified" if self.stock_raw != self.wdm_raw else "identical"

    def word_deltas(self) -> List[Tuple[str, int, int]]:
        """Descriptor field names whose raw word changed (same-ID rows only)."""
        if self.stock_record is None or self.wdm_record is None:
            return []
        spec = self.stock_record.spec
        out = []
        for index, item in enumerate(spec.fields):
            before = self.stock_record.words[index]
            after = self.wdm_record.words[index]
            if before != after:
                out.append((item.name, before, after))
        return out

    def string_deltas(self) -> List[Tuple[str, str, str]]:
        if self.stock_record is None or self.wdm_record is None:
            return []
        spec = self.stock_record.spec
        out = []
        for index, item in enumerate(spec.fields):
            if item.kind != "stroff":
                continue
            before = self.stock_record.strings[index]
            after = self.wdm_record.strings[index]
            if before != after:
                out.append((item.name, before, after))
        return out


@dataclass
class TableForensics:
    table: str
    stock: DbcFile
    wdm: DbcFile
    stock_sha256: str
    wdm_sha256: str
    added: List[RecordDiff] = field(default_factory=list)
    removed: List[RecordDiff] = field(default_factory=list)
    modified: List[RecordDiff] = field(default_factory=list)
    identical: List[RecordDiff] = field(default_factory=list)

    @property
    def stock_count(self) -> int:
        return self.stock.record_count

    @property
    def wdm_count(self) -> int:
        return self.wdm.record_count

    @property
    def byte_identical_stock_count(self) -> int:
        return len(self.identical)

    @property
    def stock_preserved_count(self) -> int:
        """Stock IDs that survive in WDM with unchanged bytes (identical + modified)."""
        return len(self.identical) + len(self.modified)

    @property
    def wdm_only_count(self) -> int:
        return len(self.added)

    def added_ids(self) -> List[int]:
        return [entry.id for entry in self.added]

    def removed_ids(self) -> List[int]:
        return [entry.id for entry in self.removed]

    def modified_ids(self) -> List[int]:
        return [entry.id for entry in self.modified]

    def summary(self) -> Dict[str, int]:
        return {
            "stock_records": self.stock_count,
            "wdm_records": self.wdm_count,
            "added_ids": len(self.added),
            "removed_ids": len(self.removed),
            "modified_same_id": len(self.modified),
            "byte_identical": len(self.identical),
        }


def compare_table(
    table: str,
    stock_path: Path,
    wdm_path: Path,
    *,
    strict_ids: bool = True,
) -> TableForensics:
    stock = parse_file(stock_path, table)
    wdm = parse_file(wdm_path, table)
    if strict_ids:
        for label, document in (("stock", stock), ("WDM", wdm)):
            if document.duplicate_ids:
                raise WdbcError(
                    f"{label} {table} has duplicate record IDs: "
                    + ", ".join(
                        f"{key} at {[i + 1 for i in value]}"
                        for key, value in sorted(document.duplicate_ids.items())
                    )
                )
    if (stock.field_count, stock.record_size) != (wdm.field_count, wdm.record_size):
        raise WdbcError(
            f"{table}: layout mismatch between stock "
            f"({stock.field_count}x{stock.record_size}) and WDM "
            f"({wdm.field_count}x{wdm.record_size})"
        )

    result = TableForensics(
        table=table,
        stock=stock,
        wdm=wdm,
        stock_sha256=sha256_file(stock_path),
        wdm_sha256=sha256_file(wdm_path),
    )

    for record in wdm.records:
        existing = stock.by_id.get(record.id)
        if existing is None:
            result.added.append(
                RecordDiff(record.id, None, record.index, None, record.raw, None, record)
            )
        elif existing.raw == record.raw:
            result.identical.append(
                RecordDiff(
                    record.id,
                    existing.index,
                    record.index,
                    existing.raw,
                    record.raw,
                    existing,
                    record,
                )
            )
        else:
            result.modified.append(
                RecordDiff(
                    record.id,
                    existing.index,
                    record.index,
                    existing.raw,
                    record.raw,
                    existing,
                    record,
                )
            )
    for record in stock.records:
        if record.id not in wdm.by_id:
            result.removed.append(
                RecordDiff(
                    record.id, record.index, None, record.raw, None, record, None
                )
            )

    result.added.sort(key=lambda entry: entry.id)
    result.removed.sort(key=lambda entry: entry.id)
    result.modified.sort(key=lambda entry: entry.id)
    result.identical.sort(key=lambda entry: entry.id)
    return result


def forensics(
    stock_dir: Path,
    wdm_dir: Path,
    tables: Sequence[str] = TABLE_NAMES,
) -> "Dict[str, TableForensics]":
    out: Dict[str, TableForensics] = {}
    for table in tables:
        out[table] = compare_table(
            table, Path(stock_dir) / f"{table}.dbc", Path(wdm_dir) / f"{table}.dbc"
        )
    return out
