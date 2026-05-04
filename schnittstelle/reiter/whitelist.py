import bpy

from ...operatoren.__operator__ import Operatoren
from ...__methoden__ import get_current_armature, schedule_merge_whitelist_initialization
from ..__panel__ import Panel, Panele


class MERGE_WHITELIST_panel(Panel):
    bl_idname = Panele.VERSCHMELZUNG
    bl_label = "Merge Whitelist"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        armature = get_current_armature(context)

        box = layout.box()
        box.label(text="Knochen-Übernahme")

        schedule_merge_whitelist_initialization(scn)
        box.label(text="Standardmuster und Bones des aktuellen Rigs")

        if len(scn.merge_extra_bone_whitelist) == 0:
            box.label(text="Keine Einträge vorhanden")

        row = box.row()
        col = row.column()
        for index, item in enumerate(scn.merge_extra_bone_whitelist):
            item_row = col.row(align=True)
            item_row.prop(item, "value", text=f"{index + 1}")
            pick_button = item_row.row(align=True)
            pick_button.enabled = armature is not None
            pick_op = pick_button.operator(Operatoren.AUSWÄHLEN, text="", icon="BONE_DATA")
            pick_op.item_index = index
            remove_op = item_row.operator(Operatoren.VERBIETEN, text="", icon="X")
            remove_op.item_index = index

        button_row = box.row(align=True)
        button_row.operator(Operatoren.ADDIEREN, icon="ADD")
        box.operator(Operatoren.STANDARDISIEREN, icon="FILE_REFRESH")
