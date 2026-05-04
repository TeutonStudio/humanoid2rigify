import bpy

#   from ...__methoden__ import ensure_merge_whitelist, get_next_merge_whitelist_value
from ..__operator__ import Operator, Operatoren


class OPR_add_merge_whitelist_item(Operator):
    bl_idname = Operatoren.WHITELIST_EINTRAG_HINZUFUEGEN.value
    bl_label = "Whitelist-Eintrag hinzufügen"
    bl_options = {"UNDO"}

    group_index: bpy.props.IntProperty(default=-1)

    def execute(self, context):
        groups = context.scene.merge_extra_bone_groups

        if self.group_index < 0 or self.group_index >= len(groups):
            return {"CANCELLED"}

        group = groups[self.group_index]
        item = group.entries.add()
        item.value = ""

        group.active_index = len(group.entries) - 1
        group.expanded = True

        return {"FINISHED"}
