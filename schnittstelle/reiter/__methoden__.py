import bpy
from bpy.types import Armature

from ...operatoren.__operator__ import Operatoren
from ...__eigenschaften__ import SEITE
#from ...__methoden__ import schedule_bone_name_cache_refresh, is_bone_name_cache_valid

def get_selected_armature(context) -> Armature | None:
    active_object = context.active_object
    if active_object is not None and active_object.type == "ARMATURE":
        return active_object

    for obj in context.selected_objects:
        if obj.type == "ARMATURE":
            return obj

    return None

def get_bone_status(context, bone_name) -> str:
    armature = get_selected_armature(context)
    if armature is None:
        return "missing_armature"

    if bone_name and bone_name in armature.data.bones:
        return "found"

    return "missing_bone"

def draw_bone_status(layout, context, bone_name):
    status = get_bone_status(context, bone_name)
    status_row = layout.row()

    if status == "missing_armature":
        status_row.enabled = False
        status_row.label(text="Kein Skelett ausgewählt", icon="INFO")
        return

    if status == "found":
        status_row.label(text="Knochen gefunden", icon="CHECKMARK")
        return

    status_row.alert = True
    status_row.label(text="Knochen existiert im aktuellen Skelett nicht",icon="ERROR")

def draw_bone_prop_with_status(layout, context, scene, prop_name):
    armature = get_selected_armature(context)
    prop_meta = scene.bl_rna.properties[prop_name]
    prop_label = prop_meta.name

    row = layout.row(align=True)
    row.prop(scene, prop_name, text=prop_label)
    pick_button = row.row(align=True)
    pick_button.enabled = armature is not None # and is_bone_name_cache_valid(scene, armature)
    pick_op = pick_button.operator(Operatoren.KNOCHEN, text="", icon="BONE_DATA")
    pick_op.prop_name = prop_name

def draw_bone_prop_with_status_per_side(layout, context, liste, prop_button=False):
    scene = context.scene
    box = layout.box()
    for seite in SEITE:
        prop = "fingers_bool_"+seite
        if prop_button:
            box.prop(scene,prop)
            if getattr(scene,prop) == True: _draw_bone_iteration(layout,context,scene,liste,seite)
        else: _draw_bone_iteration(layout,context,scene,liste,seite)

def _draw_bone_iteration(layout,context,scene,liste,seite):
    for prop_part in liste:
        prop_name = prop_part + seite
        draw_bone_prop_with_status(layout,context,scene,prop_name)
