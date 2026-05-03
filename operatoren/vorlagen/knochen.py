import bpy

from __methoden__ import get_cached_bone_items, get_current_armature, is_bone_name_cache_valid, rebuild_bone_name_cache
from operatoren.__operator__ import Operator


class OPR_pick_scene_bone_prop(Operator):
    bl_idname = "opr.pick_scene_bone_prop"
    bl_label = "Knochen waehlen"
    bl_property = "selected_bone"

    prop_name: bpy.props.StringProperty(default="")
    selected_bone: bpy.props.EnumProperty(
        name="Bone",
        items=lambda self, context: get_cached_bone_items(context),
    )

    def invoke(self, context, _event):
        if not self.prop_name or not hasattr(context.scene, self.prop_name):
            return {"CANCELLED"}

        armature = get_current_armature(context)
        if armature is None:
            self.report({"WARNING"}, "Keine Armature aktiv")
            return {"CANCELLED"}

        if not is_bone_name_cache_valid(context.scene, armature):
            rebuild_bone_name_cache(context.scene, armature)

        current_value = getattr(context.scene, self.prop_name)
        bone_items = get_cached_bone_items(context)
        if bone_items:
            valid_values = {item[0] for item in bone_items}
            self.selected_bone = (
                current_value if current_value in valid_values else bone_items[0][0]
            )

        context.window_manager.invoke_search_popup(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        if hasattr(context.scene, self.prop_name):
            setattr(context.scene, self.prop_name, self.selected_bone)
            return {"FINISHED"}

        return {"CANCELLED"}
