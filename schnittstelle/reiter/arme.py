import bpy

from __eigenschaften__ import ARME
from .__methoden__ import draw_bone_prop_with_status, draw_bone_prop_with_status_per_side
from ..__panel__ import Panel

class ARMS_panel(Panel):
    bl_idname = "ARMS_PT_panel"
    bl_label = "Arms"
    # bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context): draw_bone_prop_with_status_per_side(self.layout,context,ARME)
