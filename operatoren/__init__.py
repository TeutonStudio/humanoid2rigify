from typing import Type

import bpy

from . import übernahme, übernahme, zuordnung, werkzeuge, gruppierungen
from .__operator__ import Operator

_MODULES: list = [
    übernahme,
    zuordnung,
    werkzeuge,
    gruppierungen,
]

def register():
    for m in _MODULES: m.register()

def unregister():
    for m in reversed(_MODULES): m.unregister()
