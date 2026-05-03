import bpy

from .__methoden__ import draw_bone_prop_with_status

FINGER = [
    "thumb_01_",
    "thumb_02_",
    "thumb_03_",
    "palm_index_",
    "index_01_",
    "index_02_",
    "index_03_",
    "palm_middle_",
    "middle_01_",
    "middle_02_",
    "middle_03_",
    "palm_ring_",
    "ring_01_",
    "ring_02_",
    "ring_03_",
    "palm_pinky_",
    "pinky_01_",
    "pinky_02_",
    "pinky_03_",
]

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
        for seite in ["l","r"]:
            prop = "fingers_bool_"+seite
            box.prop(scn,prop)
            if getattr(scn,prop) == True:
                for prop_name in FINGER:
                    draw_bone_prop_with_status(box, context, scn, prop_name+seite)
