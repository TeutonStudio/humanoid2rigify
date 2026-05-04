from __future__ import annotations
import bpy
from bpy.types import Object

from ...operatoren.erzeugungsmodi.backup import create_backups
from ...__eigenschaften__ import ErzeugungsModus


from .__methoden__ import get_generation_blocker_message, create_generation_context
from .deformieren import DeformRigErhalter
from .erhalten import OriginalErhalter
from .verschmelzen import RigVerschmelzer

from collections.abc import Sequence

class RigifyBauer:
    def __init__(
        self,
        operator,
        selektion: Sequence[Object],
        params: dict,
    ):
        self.operator = operator
        self.selektion = selektion
        self.params = params

    def erzeuge_rig(self) -> set[str]:
        armature_objects = self.armaturen_aus_selektion()

        if not self.selektion:
            self.operator.report({"ERROR"}, "Kein Objekt ausgewählt")
            return {"CANCELLED"}

        if not armature_objects:
            self.operator.report({"ERROR"}, "Keine Armature ausgewählt")
            return {"CANCELLED"}

        success = False

        for armature in armature_objects:
            self.aktiviere_armature(armature)

            if self.erzeuge_rig_fuer_armature(armature):
                success = True

        if success:
            return {"FINISHED"}

        return {"CANCELLED"}

    def armaturen_aus_selektion(self) -> list[Object]:
        return [
            obj
            for obj in self.selektion
            if obj.type == "ARMATURE"
        ]

    def aktiviere_armature(self, armature_obj: Object) -> None:
        if bpy.context.object is not None and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        bpy.ops.object.select_all(action="DESELECT")

        armature_obj.select_set(True)
        bpy.context.view_layer.objects.active = armature_obj

    def erzeuge_rig_fuer_armature(self, armature_obj: Object) -> bool:
        blocker_message = get_generation_blocker_message(armature_obj)
        if blocker_message is not None:
            self.operator.report({"INFO"}, blocker_message)
            return False

        context = create_generation_context(
            self.operator,
            armature_obj,
            self.params,
        )

        modus = ErzeugungsModus.from_blender(context.generation_mode)
        if modus is None:
            self.operator.report(
                {"ERROR"},
                f"Unbekannter Erzeugungsmodus: {context.generation_mode}",
            )
            return False

        modus_klasse = MODUS_KLASSEN.get(modus)
        if modus_klasse is None:
            self.operator.report(
                {"ERROR"},
                f"Keine Klasse für Erzeugungsmodus: {modus.value}",
            )
            return False

        if modus.needs_backup:
            create_backups(context)

        return modus_klasse(context).erzeuge()


MODUS_KLASSEN = {
    ErzeugungsModus.ORIGINAL_BEHALTEN: OriginalErhalter,
    ErzeugungsModus.DEFORM_RIG_BEHALTEN: DeformRigErhalter,
    ErzeugungsModus.ZU_RIGIFY_UMBAUEN: RigVerschmelzer,
}


__all__ = [
    "RigifyBauer",
    "OriginalErhalter",
    "DeformRigErhalter",
    "RigVerschmelzer",
]