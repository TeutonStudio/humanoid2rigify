import bpy

bl_info = {
    "name": "Any Rig to Rigify",
    "author": "demania",
    "description": "Convert arbitrary armatures to Rigify with Blender 4.x/5.x compatibility.",
    "blender": (4, 0, 0),
    "version": (0, 1, 0),
    "location": "View3D",
    "warning": "",
    "category": "Object",
}

from . import schnittstelle, operatoren


_MODULES = [
    schnittstelle,
    operatoren,
]


def register():
    for m in _MODULES: m.register()

def unregister():
    for m in _MODULES: m.unregister()
