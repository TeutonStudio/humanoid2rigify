import bpy

from . import auswählen, erweitern, verbieten, standardisieren
from ..__operator__ import Operator
from typing import Type

_OPERATOREN: list[Type[Operator]] = [
    auswählen.OPR_pick_merge_whitelist_bone,
    erweitern.OPR_add_merge_whitelist_item,
    erweitern.OPR_add_merge_whitelist_group,
    verbieten.OPR_remove_merge_whitelist_item,
    verbieten.OPR_remove_merge_whitelist_group,
    #   standardisieren.OPR_reset_merge_whitelist,
]

def register():
    for op in _OPERATOREN: bpy.utils.register_class(op)

def unregister():
    for op in reversed(_OPERATOREN): bpy.utils.unregister_class(op)
