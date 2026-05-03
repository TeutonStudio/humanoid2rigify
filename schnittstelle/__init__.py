import bpy

from . import reiter
from .eigenschaften import PROPS

_MODULES = [
    reiter
]

def register():
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)

    for m in _MODULES: m.register()


def unregister():
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)

    for m in reversed(_MODULES): m.unregister()
