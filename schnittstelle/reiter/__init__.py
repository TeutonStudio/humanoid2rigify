import bpy

from schnittstelle.reiter.erzeuger import GENERATE_panel
from schnittstelle.reiter.zuordnung import MAPPING_panel
from schnittstelle.reiter.torso import UPPER_BODY_panel
from schnittstelle.reiter.wirbel import SPINES_panel
from schnittstelle.reiter.arme import ARMS_panel
from schnittstelle.reiter.finger import FINGERS_panel
from schnittstelle.reiter.beine import LEGS_panel


_CLASSES = [
    GENERATE_panel,
    MAPPING_panel,
    UPPER_BODY_panel,
    SPINES_panel,
    ARMS_panel,
    FINGERS_panel,
    LEGS_panel,
]

def register():
    for c in _CLASSES: bpy.utils.register_class(c)


def unregister():
    for c in reversed(_CLASSES): bpy.utils.unregister_class(c)