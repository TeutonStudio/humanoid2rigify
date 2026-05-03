from typing import Type

import bpy

from . import übernahme, übernahme, zuordnung, vorlagen
from .__operator__ import Operator

_MODULES: list = [
    übernahme,
    zuordnung,
    vorlagen,
]

def register():
    for m in _MODULES: bpy.utils.register_class(m)

def unregister():
    for m in reversed(_MODULES): bpy.utils.unregister_class(m)
