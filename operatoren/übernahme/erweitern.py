import bpy

from ...__methoden__ import ensure_merge_whitelist, get_next_merge_whitelist_value
from ..__operator__ import Operator, Operatoren


class OPR_add_merge_whitelist_item(Operator):
    bl_idname = Operatoren.ADDIEREN
    bl_label = "Whitelist-Eintrag hinzufügen"

    def execute(self, context):
        ensure_merge_whitelist(context.scene)
        item = context.scene.merge_extra_bone_whitelist.add()
        item.value = get_next_merge_whitelist_value(context.scene, context)
        return {"FINISHED"}
