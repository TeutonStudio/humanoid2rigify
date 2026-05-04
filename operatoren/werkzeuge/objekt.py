from collections.abc import Sequence

import bpy

from bpy.types import Object

from .__methoden__ import build_params
from ..erzeugungsmodi import RigifyBauer

from ...__methoden__ import ensure_merge_whitelist
from ..__operator__ import Operator, Operatoren

class ObjectOperator(Operator):
    bl_idname = Operatoren.ERZEUGUNG
    bl_label = "Any Rig to Rigify"
    bl_options = {"UNDO"}

    def execute(self, context):
        ensure_merge_whitelist(context.scene)
        params = build_params(context.scene)

        return RigifyBauer(
            operator=self,
            selektion=bpy.context.selected_objects,
            params=params,
        ).erzeuge_rig()