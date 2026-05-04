import bpy

from ...__eigenschaften__ import Finger, Beine, Arme, Wirbelsäule
from ..__panel__ import Panel, Panele
from .__methoden__ import draw_bone_prop_group, draw_single_bone_prop, draw_finger_bone_props_grouped_foldouts, draw_foldout, draw_bone_props_per_side_foldouts


class DEFINITION_panel(Panel):
    bl_idname = Panele.DEFINITION
    bl_label = "Definition"
    # bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

#        # Wurzel
#        body = draw_foldout(
#            layout,
#            "definition_root",
#            "Wurzel",
#            icon="BONE_DATA",
#            default_closed=False,
#        )
#
#        if body:
#            draw_single_bone_prop(
#                body,
#                context,
#                WURZEL,
#            )

#        # Torso
#        body = draw_foldout(
#            layout,
#            "definition_torso",
#            "Torso",
#            icon="BONE_DATA",
#            default_closed=False,
#        )
#
#        if body:
#            draw_bone_prop_group(
#                body,
#                context,
#                TORSO,
#            )

        # Wirbelsäule
        body = draw_foldout(
            layout,
            "definition_spines",
            "Wirbelsäule",
            icon="BONE_DATA",
            default_closed=False,
        )

        if body:
            draw_bone_prop_group(
                body,
                context,
                Wirbelsäule,
            )

        # Arme
        body = draw_foldout(
            layout,
            "definition_arms",
            "Arme",
            icon="BONE_DATA",
            default_closed=True,
        )

        if body:
            draw_bone_props_per_side_foldouts(
                body,
                context,
                Arme,
                panel_prefix="definition_arms",
                default_closed=True,
            )

        # Beine
        body = draw_foldout(
            layout,
            "definition_legs",
            "Beine",
            icon="BONE_DATA",
            default_closed=True,
        )

        if body:
            draw_bone_props_per_side_foldouts(
                body,
                context,
                Beine,
                panel_prefix="definition_legs",
                default_closed=True,
            )

        # Finger
        body = draw_foldout(
            layout,
            "definition_fingers",
            "Finger",
            icon="BONE_DATA",
            default_closed=True,
        )

        if body:
            draw_finger_bone_props_grouped_foldouts(
                body,
                context,
                Finger,
                panel_prefix="definition_fingers",
                prop_button=True,
                side_default_closed=True,
                finger_default_closed=True,
            )
