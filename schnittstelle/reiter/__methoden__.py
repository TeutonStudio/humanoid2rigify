import bpy

from bpy.types import Context, Object, Scene, UILayout

from typing import cast
from collections.abc import Iterable, Iterator

from ...operatoren.__operator__ import Operatoren
from ...__eigenschaften__ import (
    KEnum,
    KnochenEnum,
    LRKnochenEnum,
    Seite,
)


def get_selected_armature(context: Context) -> Object | None:
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


def draw_bone_status(
    layout: UILayout,
    context: Context,
    bone_name: str | None,
) -> None:
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


def draw_foldout(
    layout: UILayout,
    panel_id: str,
    label: str,
    icon: str = "BONE_DATA",
    default_closed: bool = True,
) -> UILayout | None:
    header, body = layout.panel(
        panel_id,
        default_closed=default_closed,
    )
    header.label(text=label, icon=icon, translate=False)
    return body


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


def _is_knochen_enum(source: object) -> bool:
    return isinstance(source, type) and issubclass(source, KnochenEnum)


def _is_lr_knochen_enum(source: object) -> bool:
    return isinstance(source, type) and issubclass(source, LRKnochenEnum)


def _iter_bone_props(
    source: KEnum | Iterable[str],
    seiten_suffix: str | None = None,
) -> Iterator[str]:
    """
    Erzeugt Property-Namen aus alter list[str]-Struktur oder neuer Enum-Struktur.

    Unterstützt:
    - Wirbelsäule              -> root, head, ...
    - Arme + Seite             -> clav_l, uparm_l, ...
    - Beine + Seite            -> thigh_l, calf_l, ...
    - Finger + Seite           -> thumb_01_l, palm_index_l, ...
    - alte Listen ohne Seite   -> root, head, ...
    - alte Listen mit Seite    -> thumb_01_ + l -> thumb_01_l
    """

    if _is_knochen_enum(source):
        enum_cls = cast(type[KnochenEnum], source)
        yield from enum_cls.knochen()
        return

    if _is_lr_knochen_enum(source):
        if seiten_suffix is None:
            raise ValueError(
                "LRKnochenEnum benötigt einen seiten_suffix, "
                "z. B. 'l' oder 'r'."
            )

        enum_cls = cast(type[LRKnochenEnum], source)
        yield from enum_cls.knochen(seiten_suffix)
        return

    for prop_name in source:
        if seiten_suffix is None:
            yield prop_name
        else:
            yield f"{prop_name}{seiten_suffix}"


def draw_bone_prop_with_status(
    layout: UILayout,
    context: Context,
    scene: Scene,
    prop_name: str,
) -> None:
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


def draw_single_bone_prop(
    layout: UILayout,
    context: Context,
    prop_name: str,
) -> None:
    scene = context.scene
    box = layout.box()

    draw_bone_prop_with_status(
        box,
        context,
        scene,
        prop_name,
    )


def draw_bone_prop_group(
    layout: UILayout,
    context: Context,
    prop_names: KEnum | Iterable[str],
) -> None:
    scene = context.scene
    box = layout.box()

    for prop_name in _iter_bone_props(prop_names):
        draw_bone_prop_with_status(
            box,
            context,
            scene,
            prop_name,
        )


def draw_bone_props_per_side_foldouts(
    layout: UILayout,
    context: Context,
    liste: KEnum | Iterable[str],
    panel_prefix: str,
    default_closed: bool = True,
) -> None:
    scene = context.scene
    box = layout.box()

    for seite in Seite:
        seiten_suffix = seite.value

        body = draw_foldout(
            box,
            f"{panel_prefix}_{seiten_suffix}",
            _side_label(seite),
            icon="ARROW_LEFTRIGHT",
            default_closed=default_closed,
        )

        if body is None:
            continue

        for prop_name in _iter_bone_props(liste, seiten_suffix):
            draw_bone_prop_with_status(
                body,
                context,
                scene,
                prop_name,
            )


def draw_finger_bone_props_grouped_foldouts(
    layout: UILayout,
    context: Context,
    finger_liste: KEnum | Iterable[str],
    panel_prefix: str,
    prop_button: bool = True,
    side_default_closed: bool = True,
    finger_default_closed: bool = True,
) -> None:
    scene = context.scene
    box = layout.box()

    for seite in Seite:
        seiten_suffix = seite.value

        side_header, side_body = box.panel(
            f"{panel_prefix}_side_{seiten_suffix}",
            default_closed=side_default_closed,
        )

        side_header.label(
            text=_side_label(seite),
            icon="ARROW_LEFTRIGHT",
            translate=False,
        )

        if prop_button:
            bool_prop = f"fingers_bool_{seiten_suffix}"

            if _scene_has_prop(scene, bool_prop):
                side_header.prop(
                    scene,
                    bool_prop,
                    text="",
                )
            elif side_body is not None:
                draw_missing_scene_prop(side_body, bool_prop)
                continue

        if side_body is None:
            continue

        if prop_button:
            bool_prop = f"fingers_bool_{seiten_suffix}"

            if _scene_has_prop(scene, bool_prop) and not getattr(scene, bool_prop):
                disabled_box = side_body.box()
                disabled_box.enabled = False
                disabled_box.label(
                    text="Finger dieser Seite sind deaktiviert",
                    icon="INFO",
                )
                continue

        finger_prop_names = list(
            _iter_bone_props(
                finger_liste,
                seiten_suffix,
            )
        )

        finger_groups = _build_finger_groups(finger_prop_names)

        for group_key, group_label, prop_names in finger_groups:
            finger_body = draw_foldout(
                side_body,
                f"{panel_prefix}_{seiten_suffix}_{group_key}",
                group_label,
                icon="BONE_DATA",
                default_closed=finger_default_closed,
            )

            if finger_body is None:
                continue

            for prop_name in prop_names:
                draw_bone_prop_with_status(
                    finger_body,
                    context,
                    scene,
                    prop_name,
                )


def _side_label(seite: Seite | str) -> str:
    if isinstance(seite, Seite):
        return seite.erhalte_label()

    if seite == "r":
        return "Rechts"

    if seite == "l":
        return "Links"

    return seite


def _build_finger_groups(
    finger_liste: Iterable[str],
) -> list[tuple[str, str, list[str]]]:
    known_groups = [
        (
            "thumb",
            "Daumen",
            (
                "thumb_",
            ),
        ),
        (
            "index",
            "Zeigefinger",
            (
                "palm_index_",
                "index_",
            ),
        ),
        (
            "middle",
            "Mittelfinger",
            (
                "palm_middle_",
                "middle_",
            ),
        ),
        (
            "ring",
            "Ringfinger",
            (
                "palm_ring_",
                "ring_",
            ),
        ),
        (
            "pinky",
            "Kleiner Finger",
            (
                "palm_pinky_",
                "pinky_",
            ),
        ),
    ]

    finger_liste = list(finger_liste)
    groups: list[tuple[str, str, list[str]]] = []

    for group_key, group_label, prefixes in known_groups:
        prop_parts = [
            prop_part
            for prop_part in finger_liste
            if prop_part.startswith(prefixes)
        ]

        if prop_parts:
            groups.append(
                (
                    group_key,
                    group_label,
                    prop_parts,
                )
            )

    used = {
        prop_part
        for _, _, prop_parts in groups
        for prop_part in prop_parts
    }

    unknown = [
        prop_part
        for prop_part in finger_liste
        if prop_part not in used
    ]

    if unknown:
        groups.append(
            (
                "unknown",
                "Sonstige Fingerknochen",
                unknown,
            )
        )

    return groups