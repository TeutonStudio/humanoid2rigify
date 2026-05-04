from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bpy.types import Context, Object, Scene, UILayout

from ..operatoren.__operator__ import Operatoren
from ..__methoden__ import (
    DEFAULT_MERGE_EXTRA_BONE_WHITELIST,
    get_current_armature,
    schedule_merge_whitelist_initialization,
)
from ..__eigenschaften__ import (
    Arme,
    Beine,
    Finger,
    KnochenEnum,
    LRKnochenEnum,
    Seite,
    Wirbelsäule,
)
from .__panel__ import Panel, Panele
from .__methoden__ import draw_foldout


@dataclass(frozen=True)
class WhitelistEintrag:
    index: int
    item: Any
    value: str


@dataclass(frozen=True)
class WhitelistGruppe:
    key: str
    label: str
    einträge: list[WhitelistEintrag]


@dataclass(frozen=True)
class WhitelistGruppenSchema:
    key: str
    label: str
    prop_names: tuple[str, ...] = ()
    literal_values: tuple[str, ...] = ()


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


def draw_grouped_merge_whitelist(
    layout: UILayout,
    context: Context,
    scene: Scene,
    armature: Object | None,
) -> None:
    gruppen = _baue_whitelist_gruppen(scene)

    for gruppe in gruppen:
        _draw_whitelist_group(
            layout,
            context,
            gruppe,
            armature,
            panel_prefix="merge_whitelist",
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