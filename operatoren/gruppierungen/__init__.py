import bpy

from . import ausrotten, definieren
from ..__operator__ import Operator
from typing import Type

_OPERATOR: list[Type[Operator]] = [
    ausrotten.OPR_remove_merge_whitelist_group,
    definieren.OPR_add_merge_whitelist_group,
]

def register():
    for op in _OPERATOR: bpy.utils.register_class(op)

def unregister():
    for op in reversed(_OPERATOR): bpy.utils.unregister_class(op)
