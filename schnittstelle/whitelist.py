from __future__ import annotations

from bpy.types import Context

from .__methoden__ import draw_grouped_merge_whitelist
from ..operatoren.__operator__ import Operatoren
from ..__methoden__ import (
    get_current_armature,
    schedule_merge_whitelist_initialization,
)
from .__panel__ import Panel, Panele


class MERGE_WHITELIST_panel(Panel):
    bl_idname = Panele.VERSCHMELZUNG
    bl_label = "Merge Whitelist"

    def draw(self, context: Context) -> None:
        layout = self.layout
        scene = context.scene
        armature = get_current_armature(context)

        box = layout.box()
        box.label(text="Knochen-Übernahme")

        schedule_merge_whitelist_initialization(scene)

        groups = getattr(scene, "merge_extra_bone_groups", None)

        if groups is None:
            row = box.row()
            row.alert = True
            row.label(
                text="Property fehlt: merge_extra_bone_groups",
                icon="ERROR",
            )
            return

        if len(groups) == 0:
            box.label(text="Keine Gruppen vorhanden", icon="INFO")

        draw_grouped_merge_whitelist(
            box,
            context,
            scene,
            armature,
        )

        button_row = box.row(align=True)

        button_row.operator(
            Operatoren.WHITELIST_GRUPPE_HINZUFUEGEN.value,
            text="Gruppe hinzufügen",
            icon="ADD",
        )

        #   box.operator(
        #       Operatoren.WHITELIST_GRUPPE_STANDARDISIEREN.value,
        #       text="Standardgruppen wiederherstellen",
        #       icon="FILE_REFRESH",
        #   )