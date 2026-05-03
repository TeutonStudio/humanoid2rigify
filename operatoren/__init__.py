import bpy

from operatoren.objekt import ObjectOperator
from operatoren.speichern import MappingSaveOperator
from operatoren.importieren import MappingImportOperator
from operatoren.vernichten import MappingDeleteOperator
from operatoren.umbennen import MappingRenameOperator

_CLASSES = [
    ObjectOperator,
    MappingSaveOperator,
    MappingImportOperator,
    MappingDeleteOperator,
    MappingRenameOperator,
]

def register():
    for c in _CLASSES: bpy.utils.register_class(c)


def unregister():
    for c in reversed(_CLASSES): bpy.utils.unregister_class(c)