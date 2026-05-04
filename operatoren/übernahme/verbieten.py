import bpy

from ...__methoden__ import ensure_merge_whitelist
from ..__operator__ import Operator, Operatoren


class OPR_remove_merge_whitelist_item(Operator):
    bl_idname = Operatoren.VERBIETEN
    bl_label = "Whitelist-Eintrag entfernen"

    item_index: bpy.props.IntProperty(default=-1)

    def execute(self, context):
        ensure_merge_whitelist(context.scene)
        whitelist = context.scene.merge_extra_bone_whitelist
        index = self.item_index
        if 0 <= index < len(whitelist):
            whitelist.remove(index)
        return {"FINISHED"}
