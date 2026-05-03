import bpy

from . import umbennen, vernichten, importieren, speichern
from ..__operator__ import Operator
from typing import Type

_OPERATOR: list[Type[Operator]] = [
    speichern.MappingSaveOperator,
    importieren.MappingImportOperator,
    vernichten.MappingDeleteOperator,
    umbennen.MappingRenameOperator,
]

def register():
    for op in _OPERATOR: bpy.utils.register_class(op)

def unregister():
    for op in reversed(_OPERATOR): bpy.utils.unregister_class(op)
