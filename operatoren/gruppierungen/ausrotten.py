import bpy

from ..__operator__ import Operatoren, Operator


class OPR_remove_merge_whitelist_group(Operator):
    bl_idname = Operatoren.WHITELIST_GRUPPE_LOESCHEN.value
    bl_label = "Whitelist-Gruppe löschen"
    bl_options = {"UNDO"}

    group_index: bpy.props.IntProperty(default=-1)

    def execute(self, context):
        groups = context.scene.merge_extra_bone_groups

        if self.group_index < 0 or self.group_index >= len(groups):
            return {"CANCELLED"}

        groups.remove(self.group_index)

        context.scene.merge_extra_bone_group_active_index = min(
            self.group_index,
            len(groups) - 1,
        )

        return {"FINISHED"}