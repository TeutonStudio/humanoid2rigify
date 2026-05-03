import bpy

from . import arme, beine, erzeuger, finger, torso, wirbel, zuordnung

_CLASSES = [
    erzeuger.OPR_add_merge_whitelist_item,
    erzeuger.OPR_remove_merge_whitelist_item,
    erzeuger.OPR_reset_merge_whitelist,
    erzeuger.GENERATE_panel,
    erzeuger.MERGE_WHITELIST_panel,
    zuordnung.MAPPING_panel,
    torso.UPPER_BODY_panel,
    wirbel.SPINES_panel,
    arme.ARMS_panel,
    finger.FINGERS_panel,
    beine.LEGS_panel,
]

def register():
    for c in _CLASSES: bpy.utils.register_class(c)


def unregister():
    for c in reversed(_CLASSES): bpy.utils.unregister_class(c)
