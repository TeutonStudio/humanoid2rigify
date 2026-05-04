from enum import Enum

import bpy

class Operatoren(str,Enum):
    # Werkzeuge
    ERZEUGUNG = "opr.object_operator"
    KNOCHEN = "opr.pick_scene_bone_prop"
    # Zuordnung
    ZUORDNUNG_IMPORTIEREN = "opr.mapping_import_operator"
    ZUORDNUNG_SPEICHERN = "opr.mapping_save_operator"
    ZUORDNUNG_UMBENNENEN = "opr.mapping_rename_operator"
    ZUORDNUNG_VERNICHTEN = "opr.mapping_delete_operator"

    # Whitelist Gruppen
    WHITELIST_GRUPPE_HINZUFUEGEN = "opr.add_merge_whitelist_group"
    WHITELIST_GRUPPE_LOESCHEN = "opr.remove_merge_whitelist_group"
    WHITELIST_GRUPPE_STANDARDISIEREN = "opr.reset_merge_whitelist_groups"

    # Whitelist Einträge
    WHITELIST_EINTRAG_HINZUFUEGEN = "opr.add_merge_whitelist_item"
    WHITELIST_EINTRAG_LOESCHEN = "opr.remove_merge_whitelist_item"
    WHITELIST_KNOCHEN_AUSWAEHLEN = "opr.pick_merge_whitelist_bone"

class Operator(bpy.types.Operator): pass
