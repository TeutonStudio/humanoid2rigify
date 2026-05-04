import bpy

#   from ...__methoden__ import ensure_merge_whitelist
from ..__operator__ import Operator, Operatoren


class OPR_remove_merge_whitelist_item(Operator):
    bl_idname = Operatoren.WHITELIST_EINTRAG_LOESCHEN.value
    bl_label = "Whitelist-Eintrag löschen"
    bl_options = {"UNDO"}

    group_index: bpy.props.IntProperty(default=-1)
    item_index: bpy.props.IntProperty(default=-1)

    def execute(self, context):
        groups = context.scene.merge_extra_bone_groups

        if self.group_index < 0 or self.group_index >= len(groups):
            return {"CANCELLED"}

        group = groups[self.group_index]

        if self.item_index < 0 or self.item_index >= len(group.entries):
            return {"CANCELLED"}

        group.entries.remove(self.item_index)
        group.active_index = min(self.item_index, len(group.entries) - 1)

        return {"FINISHED"}
