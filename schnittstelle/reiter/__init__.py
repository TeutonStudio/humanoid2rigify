from typing import Type

import bpy

from ..__panel__ import Panel
from . import erzeuger, zuordnung, whitelist, definition

_PANELE: list[Type[Panel]] = [
    erzeuger.GENERATE_panel,
    zuordnung.MAPPING_panel,
    definition.DEFINITION_panel,
    whitelist.MERGE_WHITELIST_panel,
]

def register():
    for p in _PANELE: bpy.utils.register_class(p)


def unregister():
    for p in reversed(_PANELE): bpy.utils.unregister_class(p)
