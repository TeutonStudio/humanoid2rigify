import bpy

from . import knochen, objekt
from ..__operator__ import Operator
from typing import Type

_OPERATOREN: list[Type[Operator]] = [
    knochen.OPR_pick_scene_bone_prop,
    objekt.ObjectOperator,
]

def register():
    for op in _OPERATOREN: bpy.utils.register_class(op)

def unregister():
    for op in reversed(_OPERATOREN): bpy.utils.unregister_class(op)
