from enum import Enum

import bpy

class Operatoren(str,Enum):
    # Werkzeuge
    ERZEUGUNG = "opr.object_operator"
    KNOCHEN = "opr.pick_scene_bone_prop"
    # Zuordnung
    IMPORTIEREN = "opr.mapping_import_operator"
    SPEICHERN = "opr.mapping_save_operator"
    UMBENNENEN = "opr.mapping_rename_operator"
    VERNICHTEN = "opr.mapping_delete_operator"
    # Übernahme
    AUSWÄHLEN = "opr.pick_merge_whitelist_bone"
    ADDIEREN = "opr.add_merge_whitelist_item"
    STANDARDISIEREN = "opr.reset_merge_whitelist"
    VERBIETEN = "opr.remove_merge_whitelist_item"

class Operator(bpy.types.Operator): pass
