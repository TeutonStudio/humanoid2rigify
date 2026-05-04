import bpy

from ...__methoden__ import get_current_armature, \
    get_current_bone_names  # is_bone_name_cache_valid, rebuild_bone_name_cache
from .__methoden__ import bone_item_list
from ..__operator__ import Operator, Operatoren


class OPR_pick_scene_bone_prop(Operator):
    bl_idname = Operatoren.KNOCHEN
    bl_label = "Knochen waehlen"
    bl_property = "selected_bone"

    prop_name: bpy.props.StringProperty(default="")
    selected_bone: bpy.props.EnumProperty(name="Bone",items=bone_item_list)

    def invoke(self, context, _event):
        if not self.prop_name or not hasattr(context.scene, self.prop_name):
            return {"CANCELLED"}

        armature = get_current_armature(context)
        if armature is None:
            self.report({"WARNING"}, "Keine Armature aktiv")
            return {"CANCELLED"}

        bone_names = get_current_bone_names(context)
        if not bone_names:
            self.report({"WARNING"}, "Die Armature hat keine Knochen")
            return {"CANCELLED"}

        current_value = getattr(context.scene, self.prop_name)

        if current_value in bone_names:
            self.selected_bone = current_value
        else:
            self.selected_bone = bone_names[0]

        context.window_manager.invoke_search_popup(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        if not hasattr(context.scene, self.prop_name):
            return {"CANCELLED"}

        bone_names = get_current_bone_names(context)

        if self.selected_bone not in bone_names:
            self.report({"WARNING"}, f"Knochen nicht gefunden: {self.selected_bone}")
            return {"CANCELLED"}

        setattr(context.scene, self.prop_name, self.selected_bone)
        return {"FINISHED"}
