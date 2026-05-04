import bpy
import uuid

from ...__methoden__ import get_next_merge_whitelist_value
from ..__operator__ import Operator, Operatoren


class OPR_add_merge_whitelist_group(Operator):
    bl_idname = Operatoren.WHITELIST_GRUPPE_HINZUFUEGEN.value
    bl_label = "Whitelist-Gruppe hinzufügen"
    bl_options = {"UNDO"}

    def execute(self, context):
        groups = context.scene.merge_extra_bone_groups

        group = groups.add()
        group.uid = uuid.uuid4().hex
        group.name = "Neue Gruppe"
        group.expanded = True
        group.active_index = -1

        context.scene.merge_extra_bone_group_active_index = len(groups) - 1

        return {"FINISHED"}


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
        item.value = get_next_merge_whitelist_value(context.scene, context)

        group.active_index = len(group.entries) - 1
        context.scene.merge_extra_bone_group_active_index = self.group_index

        return {"FINISHED"}