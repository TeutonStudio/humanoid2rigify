import bpy

from bpy.types import Armature, Context, Scene, UILayout

from ...operatoren.__operator__ import Operatoren
from ...__eigenschaften__ import SEITE


def get_selected_armature(context: Context) -> Armature | None:
    active_object = context.active_object

    if active_object is not None and active_object.type == "ARMATURE":
        return active_object

    for obj in context.selected_objects:
        if obj.type == "ARMATURE":
            return obj

    return None

def get_bone_status(context: Context, bone_name: str | None) -> str:
    armature = get_selected_armature(context)

    if armature is None:
        return "missing_armature"

    if bone_name and bone_name in armature.data.bones:
        return "found"

    return "missing_bone"

def draw_bone_status(layout: UILayout, context: Context, bone_name: str | None) -> None:
    status = get_bone_status(context, bone_name)
    status_row = layout.row()

    if status == "missing_armature":
        status_row.enabled = False
        status_row.label(text="Kein Skelett ausgewählt", icon="INFO")
        return

    if status == "found":
        status_row.label(text="Knochen gefunden", icon="CHECKMARK")
        return

    status_row.alert = True
    status_row.label(
        text="Knochen existiert im aktuellen Skelett nicht",
        icon="ERROR",
    )

def _get_prop_label(scene: Scene, prop_name: str) -> str:
    prop_meta = scene.bl_rna.properties.get(prop_name)

    if prop_meta is None:
        return prop_name

    return prop_meta.name

def _scene_has_prop(scene: Scene, prop_name: str) -> bool:
    return scene.bl_rna.properties.get(prop_name) is not None

def draw_missing_scene_prop(layout: UILayout, prop_name: str) -> None:
    row = layout.row(align=True)
    row.alert = True
    row.label(
        text=f"Property fehlt: {prop_name}",
        icon="ERROR",
    )

def draw_bone_prop_with_status(layout: UILayout, context: Context, scene: Scene, prop_name: str) -> None:
    if not _scene_has_prop(scene, prop_name):
        draw_missing_scene_prop(layout, prop_name)
        return

    armature = get_selected_armature(context)
    prop_label = _get_prop_label(scene, prop_name)
    bone_name = getattr(scene, prop_name, "")

    row = layout.row(align=True)

    status = get_bone_status(context, bone_name)

    if status == "found":
        row.label(text="", icon="CHECKMARK")
    elif status == "missing_bone":
        row.alert = True
        row.label(text="", icon="ERROR")
    else:
        row.enabled = False
        row.label(text="", icon="INFO")

    row.prop(scene, prop_name, text=prop_label)

    pick_button = row.row(align=True)
    pick_button.enabled = armature is not None

    pick_op = pick_button.operator(
        Operatoren.KNOCHEN,
        text="",
        icon="BONE_DATA",
    )
    pick_op.prop_name = prop_name

def draw_bone_prop_group(layout: UILayout, context: Context, prop_names: list[str]) -> None:
    scene = context.scene
    box = layout.box()

    for prop_name in prop_names:
        draw_bone_prop_with_status(
            box,
            context,
            scene,
            prop_name,
        )

def draw_single_bone_prop(layout: UILayout, context: Context, prop_name: str) -> None:
    scene = context.scene
    box = layout.box()

    draw_bone_prop_with_status(
        box,
        context,
        scene,
        prop_name,
    )

def draw_bone_prop_with_status_per_side(
    layout: UILayout,
    context: Context,
    liste: list[str],
    prop_button: bool = False,
) -> None:
    scene = context.scene
    box = layout.box()

    for seite in SEITE:
        side_box = box.box()
        side_box.label(
            text=_side_label(seite),
            icon="ARROW_LEFTRIGHT",
        )

        if prop_button:
            bool_prop = "fingers_bool_" + seite

            if _scene_has_prop(scene, bool_prop):
                side_box.prop(scene, bool_prop)

                if not getattr(scene, bool_prop):
                    continue
            else:
                draw_missing_scene_prop(side_box, bool_prop)
                continue

        _draw_bone_iteration(
            side_box,
            context,
            scene,
            liste,
            seite,
        )

def draw_finger_bone_props_grouped(
    layout: UILayout,
    context: Context,
    finger_liste: list[str],
    prop_button: bool = True,
) -> None:
    scene = context.scene
    box = layout.box()

    finger_groups = _build_finger_groups(finger_liste)

    for seite in SEITE:
        side_box = box.box()
        side_box.label(
            text=_side_label(seite),
            icon="ARROW_LEFTRIGHT",
        )

        if prop_button:
            bool_prop = "fingers_bool_" + seite

            if _scene_has_prop(scene, bool_prop):
                side_box.prop(scene, bool_prop)

                if not getattr(scene, bool_prop):
                    continue
            else:
                draw_missing_scene_prop(side_box, bool_prop)
                continue

        for group_label, prop_parts in finger_groups:
            finger_box = side_box.box()
            finger_box.label(
                text=group_label,
                icon="BONE_DATA",
            )

            for prop_part in prop_parts:
                prop_name = prop_part + seite
                draw_bone_prop_with_status(
                    finger_box,
                    context,
                    scene,
                    prop_name,
                )

def _draw_bone_iteration(
    layout: UILayout,
    context: Context,
    scene: Scene,
    liste: list[str],
    seite: str,
) -> None:
    for prop_part in liste:
        prop_name = prop_part + seite

        draw_bone_prop_with_status(
            layout,
            context,
            scene,
            prop_name,
        )

def _side_label(seite: str) -> str:
    if seite == "r":
        return "Rechts"

    if seite == "l":
        return "Links"

    return seite

def _build_finger_groups(finger_liste: list[str]) -> list[tuple[str, list[str]]]:
    known_groups = [
        (
            "Daumen",
            (
                "thumb_",
            ),
        ),
        (
            "Zeigefinger",
            (
                "palm_index_",
                "index_",
            ),
        ),
        (
            "Mittelfinger",
            (
                "palm_middle_",
                "middle_",
            ),
        ),
        (
            "Ringfinger",
            (
                "palm_ring_",
                "ring_",
            ),
        ),
        (
            "Kleiner Finger",
            (
                "palm_pinky_",
                "pinky_",
            ),
        ),
    ]

    groups: list[tuple[str, list[str]]] = []

    for group_label, prefixes in known_groups:
        prop_parts = [
            prop_part
            for prop_part in finger_liste
            if prop_part.startswith(prefixes)
        ]

        if prop_parts:
            groups.append((group_label, prop_parts))

    used = {
        prop_part
        for _, prop_parts in groups
        for prop_part in prop_parts
    }

    unknown = [
        prop_part
        for prop_part in finger_liste
        if prop_part not in used
    ]

    if unknown:
        groups.append(("Sonstige Fingerknochen", unknown))

    return groups