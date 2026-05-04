import bpy

from ...__eigenschaften__ import FINGER
from ..__panel__ import Panel, Panele
from .__methoden__ import draw_bone_prop_with_status, draw_bone_prop_with_status_per_side

class FINGERS_panel(Panel):
    bl_idname = Panele.FINGER
    bl_label = "Fingers"
    # bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context): draw_bone_prop_with_status_per_side(self.layout,context,FINGER,True)
