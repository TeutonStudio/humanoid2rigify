import bpy

from ...operatoren.__operator__ import Operatoren
from ..__panel__ import Panel, Panele


class MAPPING_panel(Panel):
    bl_idname = Panele.ZUORDNUNG
    bl_label = "Mapping"
    # bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        # row = layout.row()
        # icon = 'TRIA_DOWN' if scn.subpanel_status_upper else 'TRIA_RIGHT'
        # row.prop(scn, 'subpanel_status_mapping', icon=icon, icon_only=True)
        # row.label(text='Mapping')
        # if scn.subpanel_status_mapping:

        box = layout.box()
        box.label(text="save mapping")

        box.prop(scn, "json_file_name")
        box.operator(Operatoren.SPEICHERN, text="save mapping")

        box = layout.box()
        box.label(text="import presets")
        box.prop(scn, "presets")
        box.operator(Operatoren.IMPORTIEREN, text="import mapping")

        box = layout.box()
        box.label(text="delete active preset")
        box.operator(Operatoren.VERNICHTEN, text=f"delete {scn.presets}")

        box = layout.box()
        box.label(text="rename active reset")
        box.prop(scn, "rename_preset")
        box.operator(Operatoren.UMBENNENEN, text="rename preset")
