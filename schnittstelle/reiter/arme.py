import bpy

from ...__eigenschaften__ import ARME
from ..__panel__ import Panel, Panele
from .__methoden__ import draw_bone_prop_with_status, draw_bone_prop_with_status_per_side

class ARMS_panel(Panel):
    bl_idname = Panele.ARME
    bl_label = "Arms"
    # bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context): draw_bone_prop_with_status_per_side(self.layout,context,ARME)
