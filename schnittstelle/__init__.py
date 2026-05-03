import bpy

from . import reiter, eigenschaften

_MODULES = [
    reiter,
    eigenschaften,
]

def register():
    for m in _MODULES: m.register()

def unregister():
    for m in reversed(_MODULES): m.unregister()
