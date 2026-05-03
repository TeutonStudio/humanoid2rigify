import bpy

from ...__methoden__ import ensure_merge_whitelist, get_next_merge_whitelist_value
from ..__operator__ import Operator


class OPR_add_merge_whitelist_item(Operator):
    bl_idname = "opr.add_merge_whitelist_item"
    bl_label = "Whitelist-Eintrag hinzufügen"

    def execute(self, context):
        ensure_merge_whitelist(context.scene)
        item = context.scene.merge_extra_bone_whitelist.add()
        item.value = get_next_merge_whitelist_value(context.scene, context)
        return {"FINISHED"}
