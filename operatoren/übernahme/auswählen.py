import bpy

from ...__methoden__ import get_cached_bone_items, get_current_armature, is_bone_name_cache_valid, rebuild_bone_name_cache
from ..__operator__ import Operator


class OPR_pick_merge_whitelist_bone(Operator):
    bl_idname = "opr.pick_merge_whitelist_bone"
    bl_label = "Whitelist-Knochen waehlen"
    bl_property = "selected_bone"

    item_index: bpy.props.IntProperty(default=-1)
    selected_bone: bpy.props.EnumProperty(
        name="Bone",
        items=lambda self, context: get_cached_bone_items(context),
    )

    def invoke(self, context, _event):
        if self.item_index < 0:
            return {"CANCELLED"}

        armature = get_current_armature(context)
        if armature is None:
            self.report({"WARNING"}, "Keine Armature aktiv")
            return {"CANCELLED"}

        if not is_bone_name_cache_valid(context.scene, armature):
            rebuild_bone_name_cache(context.scene, armature)

        whitelist = context.scene.merge_extra_bone_whitelist
        if self.item_index >= len(whitelist):
            return {"CANCELLED"}

        current_value = whitelist[self.item_index].value
        bone_items = get_cached_bone_items(context)
        if bone_items:
            valid_values = {item[0] for item in bone_items}
            self.selected_bone = (
                current_value if current_value in valid_values else bone_items[0][0]
            )

        context.window_manager.invoke_search_popup(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        whitelist = context.scene.merge_extra_bone_whitelist
        if 0 <= self.item_index < len(whitelist):
            whitelist[self.item_index].value = self.selected_bone
            return {"FINISHED"}

        return {"CANCELLED"}
