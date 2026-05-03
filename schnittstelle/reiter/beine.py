import bpy

from .__methoden__ import draw_bone_prop_with_status


class LEGS_panel(bpy.types.Panel):
    bl_idname = "LEGS_PT_panel"
    bl_label = "Legs"
    bl_category = "Any Rig to Rigify"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    # bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        box = layout.box()

        for prop_name in [
            "thigh_r",
            "calf_r",
            "foot_r",
            "toe_r",
            "heel_r",
            "thigh_l",
            "calf_l",
            "foot_l",
            "toe_l",
            "heel_l",
        ]:
            draw_bone_prop_with_status(box, context, scn, prop_name)
