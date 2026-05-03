import bpy

from . import eigenschaften, reiter

_MODULES = [
    eigenschaften,
    reiter,
]

def register():
    for m in _MODULES: m.register()

def unregister():
    for m in reversed(_MODULES): m.unregister()
