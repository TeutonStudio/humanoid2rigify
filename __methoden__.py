import os
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any

import bpy
from bpy.types import Context, Object, Scene


_MERGE_WHITELIST_INIT_SCENE: str | None = None


DEFAULT_MERGE_EXTRA_BONE_GROUPS = [
    {
        "name": "Additional",
        "entries": [
            "rig",
            "properties",
            "clothes",
        ],
    },
]


# Kompatibilität für alten Code, der noch eine flache Whitelist erwartet.
DEFAULT_MERGE_EXTRA_BONE_WHITELIST = [
    value
    for group in DEFAULT_MERGE_EXTRA_BONE_GROUPS
    for value in group["entries"]
]


# ============================================================
# Aktuelle Armature / Bone-Namen
# ============================================================

def get_current_armature(context: Context | None) -> Object | None:
    if context is None:
        return None

    context_object: Object | None = getattr(context, "object", None)
    if context_object is not None and context_object.type == "ARMATURE":
        return context_object

    active_object: Object | None = getattr(context, "active_object", None)
    if active_object is not None and active_object.type == "ARMATURE":
        return active_object

    selected_objects: Sequence[Object] = getattr(context, "selected_objects", [])
    for obj in selected_objects:
        if obj.type == "ARMATURE":
            return obj

    return None


def get_current_bone_names(context: Context | None) -> list[str]:
    armature_obj = get_current_armature(context)

    if armature_obj is None:
        return []

    if armature_obj.type != "ARMATURE":
        return []

    return [bone.name for bone in armature_obj.data.bones]


def is_pose_armature_context(context: Context | None) -> bool:
    armature = get_current_armature(context)

    if armature is None:
        return False

    def ist_pose_modus(etwas: object) -> bool:
        return getattr(etwas, "mode", None) == "POSE"

    return ist_pose_modus(context) or ist_pose_modus(armature)


# ============================================================
# Mapping-Ordner / Preset-Liste
# ============================================================

def get_mapping_folder() -> str:
    mapping_folder = Path(__file__).resolve().parent / "mapping_templates"
    mapping_folder.mkdir(parents=True, exist_ok=True)
    return mapping_folder.as_posix()


def my_settings_callback(scene: Scene, context: Context) -> list[tuple[str, str, str]]:
    mapping_folder = get_mapping_folder()

    json_presets: list[str] = []

    for file_name in sorted(os.listdir(mapping_folder)):
        _, file_extension = os.path.splitext(file_name)

        if file_extension == ".json":
            json_presets.append(file_name)

    return [
        (
            preset_name,
            preset_name,
            "",
        )
        for preset_name in json_presets
    ]


# ============================================================
# Whitelist-Gruppen: Zugriff / Serialisierung
# ============================================================

def scene_has_merge_whitelist_groups(scene: Scene | None) -> bool:
    if scene is None:
        return False

    return hasattr(scene, "merge_extra_bone_groups")


def get_merge_whitelist_groups(scene: Scene | None):
    if scene is None:
        return None

    return getattr(scene, "merge_extra_bone_groups", None)


def iter_merge_whitelist_group_entries(scene: Scene | None) -> Iterator[str]:
    groups = get_merge_whitelist_groups(scene)

    if groups is None:
        return

    for group in groups:
        for item in group.entries:
            value = item.value.strip()

            if value:
                yield value


def build_flat_merge_whitelist_from_groups(scene: Scene | None) -> list[str]:
    return list(iter_merge_whitelist_group_entries(scene))


def build_merge_extra_bone_groups(scene: Scene | None) -> list[dict[str, Any]]:
    groups = get_merge_whitelist_groups(scene)

    if groups is None:
        return []

    result: list[dict[str, Any]] = []

    for group in groups:
        entries = [
            item.value.strip()
            for item in group.entries
            if item.value and item.value.strip()
        ]

        if not entries:
            continue

        result.append(
            {
                "name": group.name or "Additional",
                "entries": entries,
            }
        )

    return result


def clear_merge_whitelist_groups(scene: Scene | None) -> None:
    groups = get_merge_whitelist_groups(scene)

    if groups is None:
        return

    while len(groups) != 0:
        groups.remove(len(groups) - 1)

    if hasattr(scene, "merge_extra_bone_group_active_index"):
        scene.merge_extra_bone_group_active_index = -1


def add_merge_whitelist_group(
    scene: Scene,
    name: str,
    entries: Sequence[str] | None = None,
    expanded: bool = True,
):
    groups = get_merge_whitelist_groups(scene)

    if groups is None:
        return None

    group = groups.add()
    group.name = name
    group.expanded = expanded
    group.active_index = -1

    for value in entries or []:
        cleaned_value = str(value).strip()

        if not cleaned_value:
            continue

        item = group.entries.add()
        item.value = cleaned_value

    group.active_index = len(group.entries) - 1 if len(group.entries) else -1

    if hasattr(scene, "merge_extra_bone_group_active_index"):
        scene.merge_extra_bone_group_active_index = len(groups) - 1

    return group


def reset_merge_whitelist_groups(scene: Scene | None) -> None:
    if scene is None:
        return

    clear_merge_whitelist_groups(scene)

    for group_data in DEFAULT_MERGE_EXTRA_BONE_GROUPS:
        add_merge_whitelist_group(
            scene,
            name=str(group_data.get("name") or "Additional"),
            entries=group_data.get("entries", []),
            expanded=True,
        )


def ensure_merge_whitelist_groups(scene: Scene | None) -> None:
    groups = get_merge_whitelist_groups(scene)

    if groups is None:
        return

    if len(groups) > 0:
        return

    reset_merge_whitelist_groups(scene)


# Alter Name bleibt absichtlich erhalten, weil noch mehrere Dateien diesen Import nutzen können.
def ensure_merge_whitelist(scene: Scene | None) -> None:
    ensure_merge_whitelist_groups(scene)


# ============================================================
# Whitelist-Optionen / nächster Vorschlagswert
# ============================================================

def _iter_cached_bone_names(scene: Scene | None) -> Iterator[str]:
    if scene is None:
        return

    cached_bone_names = getattr(scene, "cached_bone_names", None)

    if cached_bone_names is None:
        return

    for item in cached_bone_names:
        bone_name = getattr(item, "name", "")

        if bone_name:
            yield bone_name


def get_merge_whitelist_option_values(context: Context | None) -> list[str]:
    option_values: list[str] = []

    def append_unique(value: str) -> None:
        if value and value not in option_values:
            option_values.append(value)

    for value in DEFAULT_MERGE_EXTRA_BONE_WHITELIST:
        append_unique(value)

    scene = getattr(context, "scene", None) if context is not None else None

    for value in iter_merge_whitelist_group_entries(scene):
        append_unique(value)

    cached_names = list(_iter_cached_bone_names(scene))

    if cached_names:
        bone_names = cached_names
    else:
        bone_names = get_current_bone_names(context)

    for bone_name in bone_names:
        append_unique(bone_name)

    return option_values


def get_next_merge_whitelist_value(scene: Scene, context: Context | None) -> str:
    existing_values = set(iter_merge_whitelist_group_entries(scene))

    for value in get_merge_whitelist_option_values(context):
        if value not in existing_values:
            return value

    if DEFAULT_MERGE_EXTRA_BONE_WHITELIST:
        return DEFAULT_MERGE_EXTRA_BONE_WHITELIST[0]

    return ""


# ============================================================
# Timer / Lazy Initialisierung
# ============================================================

def initialize_pending_merge_whitelist():
    global _MERGE_WHITELIST_INIT_SCENE

    scene_name = _MERGE_WHITELIST_INIT_SCENE
    _MERGE_WHITELIST_INIT_SCENE = None

    if scene_name is None:
        return None

    scene = bpy.data.scenes.get(scene_name)

    if scene is None:
        return None

    ensure_merge_whitelist_groups(scene)
    tag_redraw_all_areas()

    return None


def schedule_merge_whitelist_initialization(scene: Scene | None) -> None:
    global _MERGE_WHITELIST_INIT_SCENE

    if scene is None:
        return

    groups = get_merge_whitelist_groups(scene)

    if groups is None:
        return

    if len(groups) != 0:
        return

    _MERGE_WHITELIST_INIT_SCENE = scene.name

    if not bpy.app.timers.is_registered(initialize_pending_merge_whitelist):
        bpy.app.timers.register(
            initialize_pending_merge_whitelist,
            first_interval=0.0,
        )


def ensure_pose_mode_data(scene: Scene | None, context: Context | None) -> None:
    if scene is None or context is None:
        return

    if not is_pose_armature_context(context):
        return

    ensure_merge_whitelist_groups(scene)


# ============================================================
# UI Redraw
# ============================================================

def tag_redraw_all_areas() -> None:
    window_manager = getattr(bpy.context, "window_manager", None)

    if window_manager is None:
        return

    for window in window_manager.windows:
        screen = getattr(window, "screen", None)

        if screen is None:
            continue

        for area in screen.areas:
            area.tag_redraw()