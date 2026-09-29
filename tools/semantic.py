"""Project WDM's four tables into a mod-content-manager ``worldMaps[]`` entry.

This module is deliberately a *projection*, not a composer.  It reads rows out
of the WDM tables in WDM's own order and renames them into the keys
``ReadWorldMaps``/``ReadWorldMapArea``/``ReadWorldMapFloor``/
``ReadWorldMapChunk``/``ReadWorldMapTransform`` expect.  It never allocates IDs,
never renumbers, never sorts, and never drops a row: append-only composition
and the fixed-ID allocator are mod-content-manager's job.

Row order is load-bearing.  ``DungeonMapChunk`` order in particular is not
cosmetic, so records are emitted in the order WDM declares them rather than by
ID.
"""

from __future__ import annotations

import hashlib
from typing import Dict, List

from wdbc import DbcFile

# DBC field name -> manifest key, per manifest section.  Anything absent from
# these maps is a field the client derives from the map entry itself (MapID) or
# a field the manifest has no way to express; see docs/WORLD_MAP_DBC.md.
FLOOR_FIELDS = (
    ("Floor", "floor"),
    ("field3", "field3"),
    ("field4", "field4"),
    ("field5", "field5"),
    ("field6", "field6"),
    ("field7", "field7"),
)

CHUNK_FIELDS = (
    ("field2", "field2"),
    ("DungeonMapID", "dungeonMapId"),
    ("field4", "field4"),
)

AREA_FIELDS = (
    ("area_id", "areaId"),
    ("y1", "y1"),
    ("y2", "y2"),
    ("x1", "x1"),
    ("x2", "x2"),
    ("virtual_map_id", "virtualMapId"),
    ("dungeonMap_id", "dungeonMapId"),
    ("parentMapID", "parentMapId"),
)

TRANSFORM_FIELDS = (
    ("RegionBottom", "regionBottom"),
    ("RegionRight", "regionRight"),
    ("RegionTop", "regionTop"),
    ("RegionLeft", "regionLeft"),
    ("NewMapID", "newMapId"),
    ("RegionOffset_X", "regionOffsetX"),
    ("RegionOffset_Y", "regionOffsetY"),
    ("NewDungeonMapID", "newDungeonMapId"),
)


def _project(record, fields) -> Dict[str, object]:
    return {key: record.value(source) for source, key in fields}


def floor_declaration(floors: DbcFile, identifier: int) -> Dict[str, object]:
    declaration = {"id": identifier}
    declaration.update(_project(floors.get(identifier), FLOOR_FIELDS))
    return declaration


def chunk_declaration(chunks: DbcFile, identifier: int) -> Dict[str, object]:
    declaration = {"id": identifier}
    declaration.update(_project(chunks.get(identifier), CHUNK_FIELDS))
    return declaration


def area_declaration(
    areas: DbcFile,
    floors: DbcFile,
    chunks: DbcFile,
    identifier: int,
    floor_ids: List[int],
    chunk_ids: List[int],
) -> Dict[str, object]:
    record = areas.get(identifier)
    declaration = {"id": identifier, "internalName": record.value("internal_name")}
    declaration.update(_project(record, AREA_FIELDS))
    # Order follows WDM, not ID.  The client walks floors in declaration order.
    declaration["floors"] = [floor_declaration(floors, i) for i in floor_ids]
    declaration["chunks"] = [chunk_declaration(chunks, i) for i in chunk_ids]
    return declaration


def transform_declaration(transforms: DbcFile, identifier: int) -> Dict[str, object]:
    declaration = {"id": identifier}
    declaration.update(_project(transforms.get(identifier), TRANSFORM_FIELDS))
    return declaration


def world_map_declaration(
    tables: Dict[str, DbcFile],
    map_id: int,
    area_ids: List[int],
    floor_ids: List[int],
    chunk_ids: List[int],
    transform_id: int,
) -> Dict[str, object]:
    """Build the single ``worldMaps[]`` entry for one instance map."""
    areas: DbcFile = tables["WorldMapArea"]
    floors: DbcFile = tables["DungeonMap"]
    chunks: DbcFile = tables["DungeonMapChunk"]
    transforms: DbcFile = tables["WorldMapTransforms"]
    return {
        "mapId": map_id,
        "transform": transform_declaration(transforms, transform_id),
        "areas": [
            area_declaration(areas, floors, chunks, identifier, floor_ids, chunk_ids)
            for identifier in area_ids
        ],
    }


def canonical_json(value: object) -> bytes:
    """Stable bytes for hashing and diffing a declaration.

    Floats are the awkward part: ``-796.6220092773438`` must survive a
    round trip through JSON without being reformatted, or semantic equality
    stops being checkable.  ``repr`` gives shortest-round-trip in Python 3 and
    ``json`` uses it, so no special handling is needed beyond fixed separators.
    """
    import json

    return json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def semantic_digest(declaration: object) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(declaration)).hexdigest()
