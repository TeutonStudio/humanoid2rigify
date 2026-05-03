import bpy

from __eigenschaften__ import KNOCHEN
from __methoden__ import ensure_merge_whitelist
from operatoren.__methoden__ import generate_rig
from operatoren.__operator__ import Operator


class ObjectOperator(Operator):
    bl_idname = "opr.object_operator"
    bl_label = "Any Rig to Rigify"
    bl_options = {"UNDO"}

    def execute(self, context):
        ensure_merge_whitelist(context.scene)
        params = [(str(wert), getattr(context.scene,wert)) for wert in KNOCHEN]

        objects = bpy.context.selected_objects
        generate_rig(self, objects, params)

        return {"FINISHED"}
