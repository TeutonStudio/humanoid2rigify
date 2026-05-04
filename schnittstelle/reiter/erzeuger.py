import bpy

from ...operatoren.__operator__ import Operatoren
from ..__panel__ import Panel, Panele


class GENERATE_panel(Panel):
    bl_idname = Panele.ERZEUGUNG
    bl_label = "Generate"
    # bl_options = {"DEFAULT_OPENED"}


    def draw(self, context):
        layout = self.layout
        scn = context.scene
        box = self.layout.box()
        box.label(text="Generate")
        box.prop(scn, "generation_mode")
        box.operator(Operatoren.ERZEUGUNG, text="Generate Rigify")
        box.prop(scn, "copy_loc_constr")
