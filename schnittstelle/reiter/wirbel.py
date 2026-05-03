import bpy

from __eigenschaften__ import WIRBEL
from .__methoden__ import draw_bone_prop_with_status
from ..__panel__ import Panel


class SPINES_panel(Panel):
    bl_idname = "SPINES_PT_panel"
    bl_label = "Spines"
    # bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        # Spines
        row = layout.row()
        row.label(text='Spines')

        box = layout.box()
        for prop_name in WIRBEL:
            draw_bone_prop_with_status(box, context, scn, prop_name)
