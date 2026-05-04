import bpy

bl_info = {
    "name": "Humanoid 2 Rigify",
    "author": "TeutonStudio",
    "description": "Convert arbitrary armatures to Rigify with Blender 4.x/5.x compatibility.",
    "blender": (5, 1, 0),
    "version": (0, 5, 0),
    "location": "View3D",
    "warning": "",
    "category": "Object",
}

from . import operatoren, schnittstelle
_MODULES = [
    schnittstelle,
    operatoren,
]

def register():
    for m in _MODULES: m.register()

def unregister():
    for m in reversed(_MODULES): m.unregister()
