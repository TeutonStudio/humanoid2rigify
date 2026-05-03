import bpy

from schnittstelle.reiter.__methoden__ import draw_bone_prop_with_status


class UPPER_BODY_panel(bpy.types.Panel):
    bl_idname = "UPPER_BODY_PT_panel"
    bl_label = "Upper body"
    bl_category = "Any Rig to Rigify"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    # bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        box = layout.box()
        for prop_name in ["head", "first_neck", "last_neck", "clav_r", "clav_l"]:
            draw_bone_prop_with_status(box, context, scn, prop_name)
