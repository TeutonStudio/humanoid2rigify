from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bpy.types import Context, Object, Scene, UILayout

from .__methoden__ import draw_grouped_merge_whitelist
from ..operatoren.__operator__ import Operatoren
from ..__methoden__ import (
    #   DEFAULT_MERGE_EXTRA_BONE_WHITELIST,
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
        box.label(text="Standardmuster und Bones des aktuellen Rigs")

        if len(scene.merge_extra_bone_whitelist) == 0:
            box.label(text="Keine Einträge vorhanden")

        draw_grouped_merge_whitelist(
            box,
            context,
            scene,
            armature,
        )

        button_row = box.row(align=True)
        button_row.operator(Operatoren.ADDIEREN, icon="ADD")
        box.operator(Operatoren.STANDARDISIEREN, icon="FILE_REFRESH")

