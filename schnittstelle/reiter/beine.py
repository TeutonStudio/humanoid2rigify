import bpy

from __eigenschaften__ import BEINE
from .__methoden__ import draw_bone_prop_with_status, draw_bone_prop_with_status_per_side
from ..__panel__ import Panel

class LEGS_panel(Panel):
    bl_idname = "LEGS_PT_panel"
    bl_label = "Legs"
    # bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context): draw_bone_prop_with_status_per_side(self.layout,context,BEINE)
