import bpy

from ..werkzeuge.__methoden__ import bone_item_list
from ...__methoden__ import get_current_armature, get_current_bone_names
from ..__operator__ import Operator, Operatoren


class OPR_pick_merge_whitelist_bone(Operator):
    bl_idname = Operatoren.WHITELIST_KNOCHEN_AUSWAEHLEN.value
    bl_label = "Whitelist-Knochen wählen"
    bl_property = "selected_bone"

    group_index: bpy.props.IntProperty(default=-1)
    item_index: bpy.props.IntProperty(default=-1)

    selected_bone: bpy.props.EnumProperty(
        name="Bone",
        items=bone_item_list,
    )

    def invoke(self, context, event):
        groups = context.scene.merge_extra_bone_groups

        if self.group_index < 0 or self.group_index >= len(groups):
            return {"CANCELLED"}

        group = groups[self.group_index]

        if self.item_index < 0 or self.item_index >= len(group.entries):
            return {"CANCELLED"}

        current_value = group.entries[self.item_index].value

        if current_value:
            self.selected_bone = current_value

        return context.window_manager.invoke_search_popup(self)

    def execute(self, context):
        groups = context.scene.merge_extra_bone_groups

        if self.group_index < 0 or self.group_index >= len(groups):
            return {"CANCELLED"}

        group = groups[self.group_index]

        if self.item_index < 0 or self.item_index >= len(group.entries):
            return {"CANCELLED"}

        group.entries[self.item_index].value = self.selected_bone

        return {"FINISHED"}