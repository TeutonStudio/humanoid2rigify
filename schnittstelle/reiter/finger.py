import bpy

from schnittstelle.reiter.__methoden__ import draw_bone_prop_with_status


class FINGERS_panel(bpy.types.Panel):
    bl_idname = "FINGERS_PT_panel"
    bl_label = "Fingers"
    bl_category = "Any Rig to Rigify"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    # bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        # right fingers
        box = layout.box()
        box.prop(scn, "fingers_bool_r")
        if scn.fingers_bool_r == True:
            for prop_name in [
                "thumb_01_r",
                "thumb_02_r",
                "thumb_03_r",
                "palm_index_r",
                "index_01_r",
                "index_02_r",
                "index_03_r",
                "palm_middle_r",
                "middle_01_r",
                "middle_02_r",
                "middle_03_r",
                "palm_ring_r",
                "ring_01_r",
                "ring_02_r",
                "ring_03_r",
                "palm_pinky_r",
                "pinky_01_r",
                "pinky_02_r",
                "pinky_03_r",
            ]:
                draw_bone_prop_with_status(box, context, scn, prop_name)


        # left fingers
        box.prop(scn, "fingers_bool_l")
        if scn.fingers_bool_l == True:
            for prop_name in [
                "thumb_01_l",
                "thumb_02_l",
                "thumb_03_l",
                "palm_index_l",
                "index_01_l",
                "index_02_l",
                "index_03_l",
                "palm_middle_l",
                "middle_01_l",
                "middle_02_l",
                "middle_03_l",
                "palm_ring_l",
                "ring_01_l",
                "ring_02_l",
                "ring_03_l",
                "palm_pinky_l",
                "pinky_01_l",
                "pinky_02_l",
                "pinky_03_l",
            ]:
                draw_bone_prop_with_status(box, context, scn, prop_name)
