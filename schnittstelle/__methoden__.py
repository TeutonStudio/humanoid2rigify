from dataclasses import dataclass
from typing import Iterable, Iterator, cast, Any

import bpy
import os

from bpy.types import Scene, Context, Object, UILayout

from ..__methoden__ import DEFAULT_MERGE_EXTRA_BONE_WHITELIST
from ..__eigenschaften__ import KnochenEnum, LRKnochenEnum, KEnum, Seite, Finger, Wirbelsäule, Arme, Beine
from ..operatoren.__operator__ import Operatoren


@dataclass(frozen=True)
class WhitelistEintrag:
    group_index: int
    item_index: int
    item: Any
    value: str


@dataclass(frozen=True)
class WhitelistGruppe:
    group_index: int
    key: str
    label: str
    group: Any
    einträge: list[WhitelistEintrag]


@dataclass(frozen=True)
class WhitelistGruppenSchema:
    key: str
    label: str
    prop_names: tuple[str, ...] = ()
    literal_values: tuple[str, ...] = ()



def operatorlabel(layout: UILayout,scene: Scene,lb_text: str,property: str,operator: Operatoren,op_text: str):
    box = layout.box()
    box.label(text=lb_text)
    box.prop(scene,property)
    box.operator(operator,text=op_text)

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

def draw_grouped_merge_whitelist(
    layout: UILayout,
    context: Context,
    scene: Scene,
    armature: Object | None,
) -> None:
    groups = getattr(scene, "merge_extra_bone_groups", None)

    if groups is None:
        draw_missing_scene_prop(layout, "merge_extra_bone_groups")
        return

    for group_index, group in enumerate(groups):
        _draw_merge_whitelist_data_group(
            layout,
            context,
            scene,
            armature,
            group_index,
            group,
            panel_prefix="merge_whitelist",
        )

def _draw_merge_whitelist_data_group(
    layout: UILayout,
    context: Context,
    scene: Scene,
    armature: Object | None,
    group_index: int,
    group: Any,
    panel_prefix: str,
) -> None:
    header, body = layout.panel(
        f"{panel_prefix}_group_{group_index}",
        default_closed=not bool(group.expanded),
    )

    header.prop(group, "name", text="", icon="GROUP_BONE")

    remove_group_op = header.operator(
        Operatoren.WHITELIST_GRUPPE_LOESCHEN.value,
        text="",
        icon="X",
    )
    remove_group_op.group_index = group_index

    if body is None:
        return

    if len(group.entries) == 0:
        body.label(text="Keine Einträge in dieser Gruppe", icon="INFO")

    categorized_entries = _baue_whitelist_kategorie_gruppen(
        scene,
        group_index,
        group,
    )

    for category in categorized_entries:
        _draw_whitelist_category_group(
            body,
            context,
            category,
            armature,
            panel_prefix=f"{panel_prefix}_group_{group_index}",
        )

    add_item_op = body.operator(
        Operatoren.WHITELIST_EINTRAG_HINZUFUEGEN.value,
        text="Eintrag hinzufügen",
        icon="ADD",
    )
    add_item_op.group_index = group_index

def _baue_whitelist_kategorie_gruppen(
    scene: Scene,
    group_index: int,
    group: Any,
) -> list[WhitelistGruppe]:
    schemas = _baue_whitelist_gruppen_schemas()
    sonstige_key = "sonstige"

    gruppen: dict[str, WhitelistGruppe] = {
        schema.key: WhitelistGruppe(
            group_index=group_index,
            key=schema.key,
            label=schema.label,
            group=group,
            einträge=[],
        )
        for schema in schemas
    }

    gruppen[sonstige_key] = WhitelistGruppe(
        group_index=group_index,
        key=sonstige_key,
        label="Sonstige",
        group=group,
        einträge=[],
    )

    for item_index, item in enumerate(group.entries):
        value = item.value

        schema = _finde_schema_für_wert(
            scene,
            schemas,
            value,
        )

        key = schema.key if schema is not None else sonstige_key

        gruppen[key].einträge.append(
            WhitelistEintrag(
                group_index=group_index,
                item_index=item_index,
                item=item,
                value=value,
            )
        )

    return [
        gruppe
        for gruppe in gruppen.values()
        if gruppe.einträge
    ]

def _draw_whitelist_category_group(
    layout: UILayout,
    context: Context,
    gruppe: WhitelistGruppe,
    armature: Object | None,
    panel_prefix: str,
) -> None:
    body = draw_foldout(
        layout,
        f"{panel_prefix}_{gruppe.key}",
        gruppe.label,
        icon="BONE_DATA",
        default_closed=True,
    )

    if body is None:
        return

    for eintrag in gruppe.einträge:
        _draw_whitelist_item_row(
            body,
            armature,
            eintrag.group_index,
            eintrag.item_index,
            eintrag.item,
        )

def _draw_whitelist_group(
    layout: UILayout,
    context: Context,
    gruppe: WhitelistGruppe,
    armature: Object | None,
    panel_prefix: str,
) -> None:
    body = draw_foldout(
        layout,
        f"{panel_prefix}_{gruppe.key}",
        gruppe.label,
        icon="BONE_DATA",
        default_closed=True,
    )

    if body is None:
        return

    for eintrag in gruppe.einträge:
        _draw_whitelist_item_row(
            body,
            armature,
            eintrag.index,
            eintrag.item,
        )


def _draw_whitelist_item_row(
    layout: UILayout,
    armature: Object | None,
    index: int,
    item: Any,
) -> None:
    item_row = layout.row(align=True)

    item_row.prop(
        item,
        "value",
        text=f"{index + 1}",
    )

    pick_button = item_row.row(align=True)
    pick_button.enabled = armature is not None

    pick_op = pick_button.operator(
        Operatoren.AUSWÄHLEN,
        text="",
        icon="BONE_DATA",
    )
    pick_op.item_index = index

    remove_op = item_row.operator(
        Operatoren.VERBIETEN,
        text="",
        icon="X",
    )
    remove_op.item_index = index


def _baue_whitelist_gruppen(scene: Scene) -> list[WhitelistGruppe]:
    schemas = _baue_whitelist_gruppen_schemas()
    sonstige_key = "sonstige"

    gruppen: dict[str, WhitelistGruppe] = {
        schema.key: WhitelistGruppe(
            key=schema.key,
            label=schema.label,
            einträge=[],
        )
        for schema in schemas
    }

    gruppen[sonstige_key] = WhitelistGruppe(
        key=sonstige_key,
        label="Sonstige",
        einträge=[],
    )

    for index, item in enumerate(scene.merge_extra_bone_whitelist):
        value = item.value

        schema = _finde_schema_für_wert(
            scene,
            schemas,
            value,
        )

        key = schema.key if schema is not None else sonstige_key

        gruppen[key].einträge.append(
            WhitelistEintrag(
                index=index,
                item=item,
                value=value,
            )
        )

    return [
        gruppe
        for gruppe in gruppen.values()
        if gruppe.einträge
    ]


def _finde_schema_für_wert(
    scene: Scene,
    schemas: list[WhitelistGruppenSchema],
    value: str,
) -> WhitelistGruppenSchema | None:
    for schema in schemas:
        if _schema_passt_zu_wert(scene, schema, value):
            return schema

    return None


def _schema_passt_zu_wert(
    scene: Scene,
    schema: WhitelistGruppenSchema,
    value: str,
) -> bool:
    if value in schema.literal_values:
        return True

    for prop_name in schema.prop_names:
        if _scene_prop_passt_zu_wert(scene, prop_name, value):
            return True

    return False


def _scene_prop_passt_zu_wert(
    scene: Scene,
    prop_name: str,
    value: str,
) -> bool:
    if value == prop_name:
        return True

    prop_meta = scene.bl_rna.properties.get(prop_name)
    if prop_meta is None:
        return False

    mapped_bone_name = getattr(scene, prop_name, "")

    return bool(mapped_bone_name) and mapped_bone_name == value


def _baue_whitelist_gruppen_schemas() -> list[WhitelistGruppenSchema]:
    schemas: list[WhitelistGruppenSchema] = [
        WhitelistGruppenSchema(
            key="standard",
            label="Standardmuster",
            literal_values=tuple(DEFAULT_MERGE_EXTRA_BONE_WHITELIST),
        ),
        WhitelistGruppenSchema(
            key="wirbelsaeule",
            label="Wirbelsäule",
            prop_names=_werte_von_knochen_enum(Wirbelsäule),
        ),
    ]

    for seite in Seite:
        suffix = seite.value
        side_label = _side_label(seite)

        schemas.append(
            WhitelistGruppenSchema(
                key=f"arme_{suffix}",
                label=f"Arme {side_label}",
                prop_names=_werte_von_lr_enum(Arme, seite),
            )
        )

        schemas.append(
            WhitelistGruppenSchema(
                key=f"beine_{suffix}",
                label=f"Beine {side_label}",
                prop_names=_werte_von_lr_enum(Beine, seite),
            )
        )

        for finger in Finger:
            schemas.append(
                WhitelistGruppenSchema(
                    key=f"finger_{finger.value}_{suffix}",
                    label=f"{_finger_label(finger)} {side_label}",
                    prop_names=_finger_werte(finger, seite),
                )
            )

    return schemas


def _werte_von_knochen_enum(
    enum_cls: type[KnochenEnum],
) -> tuple[str, ...]:
    return tuple(enum_cls.knochen())


def _werte_von_lr_enum(
    enum_cls: type[LRKnochenEnum],
    seite: Seite,
) -> tuple[str, ...]:
    return tuple(enum_cls.knochen(seite.value))


def _finger_werte(
    finger: Finger,
    seite: Seite,
) -> tuple[str, ...]:
    return tuple(finger.finger_knochen(seite.value))


def _side_label(seite: Seite) -> str:
    return seite.erhalte_label()


def _finger_label(finger: Finger) -> str:
    labels = {
        Finger.DAUMEN: "Daumen",
        Finger.ZEIGE: "Zeigefinger",
        Finger.MITTEL: "Mittelfinger",
        Finger.RING: "Ringfinger",
        Finger.KLEIN: "Kleiner Finger",
    }

    return labels.get(finger, finger.value)