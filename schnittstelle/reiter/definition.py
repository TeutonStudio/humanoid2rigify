from ...operatoren.__operator__ import Operatoren
from ...__eigenschaften__ import TORSO, WIRBEL, ARME, BEINE, FINGER, WURZEL
from ..__panel__ import Panel, Panele
from .__methoden__ import draw_bone_prop_with_status_per_side, draw_finger_bone_props_grouped, draw_bone_prop_group, draw_single_bone_prop


class DEFINITION_panel(Panel):
    bl_idname = Panele.DEFINITION
    bl_label = "Definition"
    # bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        # Wurzel
        header, body = layout.panel(
            "definition_root",
            default_closed=False,
        )
        header.label(text="Wurzel", icon="BONE_DATA")

        if body:
            draw_single_bone_prop(
                body,
                context,
                WURZEL,
            )

        # Torso
        header, body = layout.panel(
            "definition_upper_body",
            default_closed=False,
        )
        header.label(text="Torso", icon="BONE_DATA")

        if body:
            draw_bone_prop_group(
                body,
                context,
                TORSO,
            )

        # Wirbelsäule
        header, body = layout.panel(
            "definition_spines",
            default_closed=False,
        )
        header.label(text="Wirbelsäule", icon="BONE_DATA")

        if body:
            draw_bone_prop_group(
                body,
                context,
                WIRBEL,
            )

        # Arme
        header, body = layout.panel(
            "definition_arms",
            default_closed=True,
        )
        header.label(text="Arme", icon="BONE_DATA")

        if body:
            draw_bone_prop_with_status_per_side(
                body,
                context,
                ARME,
            )

        # Beine
        header, body = layout.panel(
            "definition_legs",
            default_closed=True,
        )
        header.label(text="Beine", icon="BONE_DATA")

        if body:
            draw_bone_prop_with_status_per_side(
                body,
                context,
                BEINE,
            )

        # Finger
        header, body = layout.panel(
            "definition_fingers",
            default_closed=True,
        )
        header.label(text="Finger", icon="BONE_DATA")

        if body:
            draw_finger_bone_props_grouped(
                body,
                context,
                FINGER,
                prop_button=True,
            )
