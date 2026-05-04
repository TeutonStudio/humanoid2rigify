import bpy

from ...__eigenschaften__ import TORSO
from ..__panel__ import Panel, Panele
from .__methoden__ import draw_bone_prop_with_status

class UPPER_BODY_panel(Panel):
    bl_idname = Panele.TORSO
    bl_label = "Upper body"
    # bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        box = layout.box()
        for prop_name in TORSO:
            draw_bone_prop_with_status(box, context, scn, prop_name)
