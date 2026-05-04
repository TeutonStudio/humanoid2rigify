import bpy

from ...__methoden__ import ensure_merge_whitelist, DEFAULT_MERGE_EXTRA_BONE_WHITELIST
from ..__operator__ import Operator, Operatoren


class OPR_reset_merge_whitelist(Operator):
    bl_idname = Operatoren.STANDARDISIEREN
    bl_label = "Whitelist zurücksetzen"

    def execute(self, context):
        ensure_merge_whitelist(context.scene)
        whitelist = context.scene.merge_extra_bone_whitelist
        while len(whitelist) != 0:
            whitelist.remove(len(whitelist) - 1)

        for pattern in DEFAULT_MERGE_EXTRA_BONE_WHITELIST:
            item = whitelist.add()
            item.value = pattern

        return {"FINISHED"}
