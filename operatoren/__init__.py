import bpy

from . import importieren, objekt, speichern, umbennen, vernichten

_CLASSES = [
    objekt.ObjectOperator,
    speichern.MappingSaveOperator,
    importieren.MappingImportOperator,
    vernichten.MappingDeleteOperator,
    umbennen.MappingRenameOperator,
]

def register():
    for c in _CLASSES: bpy.utils.register_class(c)

def unregister():
    for c in reversed(_CLASSES): bpy.utils.unregister_class(c)
