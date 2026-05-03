from typing import Type

import bpy

from . import arme, beine, erzeuger, finger, torso, wirbel, zuordnung, whitelist
from ..__panel__ import Panel

_PANELE: list[Type[Panel]] = [
    erzeuger.GENERATE_panel,
    whitelist.MERGE_WHITELIST_panel,
    zuordnung.MAPPING_panel,
    torso.UPPER_BODY_panel,
    wirbel.SPINES_panel,
    arme.ARMS_panel,
    finger.FINGERS_panel,
    beine.LEGS_panel,
]

def register():
    for p in _PANELE: bpy.utils.register_class(p)


def unregister():
    for p in reversed(_PANELE): bpy.utils.unregister_class(p)
