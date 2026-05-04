import bpy

from ..operatoren.__operator__ import Operatoren
from .__methoden__ import operatorlabel
from .__panel__ import Panel, Panele


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

        operatorlabel(layout,scn,"save mapping",
                                 "json_file_name", Operatoren.ZUORDNUNG_SPEICHERN,
                                 "save mapping")
        operatorlabel(layout,scn,"import presets",
                                 "presets", Operatoren.ZUORDNUNG_IMPORTIEREN,
                                 "import mapping")
        operatorlabel(layout,scn,"delete active preset",
                                 "delete active preset", Operatoren.ZUORDNUNG_VERNICHTEN,
                                 f"delete {scn.presets}")
        operatorlabel(layout,scn,"rename active reset",
                                 "rename_preset", Operatoren.ZUORDNUNG_UMBENNENEN,
                                 "rename preset")
        #   box = layout.box()
        #   box.label(text="save mapping")
        #   box.prop(scn, "json_file_name")
        #   box.operator(Operatoren.ZUORDNUNG_SPEICHERN, text="save mapping")
#
        #   box = layout.box()
        #   box.label(text="import presets")
        #   box.prop(scn, "presets")
        #   box.operator(Operatoren.ZUORDNUNG_IMPORTIEREN, text="import mapping")
#
        #   box = layout.box()
        #   box.label(text="delete active preset")
        #   box.operator(Operatoren.ZUORDNUNG_VERNICHTEN, text=f"delete {scn.presets}")
#
        #   box = layout.box()
        #   box.label(text="rename active reset")
        #   box.prop(scn, "rename_preset")
        #   box.operator(Operatoren.ZUORDNUNG_UMBENNENEN, text="rename preset")
