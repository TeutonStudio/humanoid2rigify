import bpy

from .__methoden__ import build_params
from ...__methoden__ import ensure_merge_whitelist
from ..__methoden__ import generate_rig
from ..__operator__ import Operator, Operatoren


class ObjectOperator(Operator):
    bl_idname = Operatoren.ERZEUGUNG
    bl_label = "Any Rig to Rigify"
    bl_options = {"UNDO"}

    def execute(self, context):
        ensure_merge_whitelist(context.scene)
        params = build_params(context.scene)

        objects = bpy.context.selected_objects
        generate_rig(self, objects, params)

        return {"FINISHED"}
