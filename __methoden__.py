import os
from typing import Any, Sequence

import bpy
from bpy.types import Object,Context,Scene,Armature
from pathlib import Path

DEFAULT_MERGE_EXTRA_BONE_WHITELIST = [
    "rig",
    "properties",
    "clothes",
]

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

def get_mapping_folder():
    mapping_folder = Path(__file__).resolve().parent / "mapping_templates"
    mapping_folder.mkdir(parents=True, exist_ok=True)
    return mapping_folder.as_posix()

def get_merge_whitelist_option_values(context: Context) -> list[str]:
    option_values = list(DEFAULT_MERGE_EXTRA_BONE_WHITELIST)
    scene = getattr(context, "scene", None) if context is not None else None
    armature_obj = get_current_armature(context)
    if armature_obj is None:
        return option_values

    if scene is not None: # and is_bone_name_cache_valid(scene,armature_obj):
        bone_names = (item.name for item in scene.cached_bone_names)
    else: bone_names = " " # get_cached_bone_names(armature_obj) TODO

    for bone_name in bone_names:
        if bone_name not in option_values:
            option_values.append(bone_name)

    return option_values

def get_next_merge_whitelist_value(scene: Scene, context: Context) -> str:
    existing_values = {
        item.value
        for item in scene.merge_extra_bone_whitelist
        if item.value
    }
    for value in get_merge_whitelist_option_values(context):
        if value not in existing_values:
            return value

    return DEFAULT_MERGE_EXTRA_BONE_WHITELIST[0]

def ensure_merge_whitelist(scene: Scene):
    collection = getattr(scene, "merge_extra_bone_whitelist", None)
    if collection is None or len(collection) != 0:
        return

    for pattern in DEFAULT_MERGE_EXTRA_BONE_WHITELIST:
        item = collection.add()
        item.value = pattern

def initialize_pending_merge_whitelist():
    global _MERGE_WHITELIST_INIT_SCENE

    scene_name = _MERGE_WHITELIST_INIT_SCENE
    _MERGE_WHITELIST_INIT_SCENE = None
    if scene_name is None:
        return None

    scene = bpy.data.scenes.get(scene_name)
    if scene is None:
        return None

    ensure_merge_whitelist(scene)
    tag_redraw_all_areas()
    return None

def ensure_pose_mode_data(scene: Scene, context: Context):
    if scene is None or context is None or not is_pose_armature_context(context):
        return

    ensure_merge_whitelist(scene)

def schedule_merge_whitelist_initialization(scene: Scene):
    global _MERGE_WHITELIST_INIT_SCENE

    if scene is None or len(scene.merge_extra_bone_whitelist) != 0:
        return

    _MERGE_WHITELIST_INIT_SCENE = scene.name
    if not bpy.app.timers.is_registered(initialize_pending_merge_whitelist):
        bpy.app.timers.register(initialize_pending_merge_whitelist, first_interval=0.0)

def get_current_armature(context: Context) -> Armature | None:
    if context is None:
        return None

    context_object: Object = getattr(context, "object", None)
    if context_object is not None and context_object.type == "ARMATURE":
        return context_object

    active_object: Object = getattr(context, "active_object", None)
    if active_object is not None and active_object.type == "ARMATURE":
        return active_object

    selects: Sequence[Object] = getattr(context, "selected_objects", [])
    for obj in selects:
        if obj.type == "ARMATURE":
            return obj

    return None

def is_pose_armature_context(context) -> bool:
    armature = get_current_armature(context)
    boolwert = lambda etwas: getattr(etwas, "mode", None) == "POSE"
    return armature is not None and (boolwert(context) or boolwert(armature))

def tag_redraw_all_areas():
    window_manager = getattr(bpy.context, "window_manager", None)
    if window_manager is None:
        return

    for window in window_manager.windows:
        screen = getattr(window, "screen", None)
        if screen is None:
            continue
        for area in screen.areas:
            area.tag_redraw()

def my_settings_callback(scene: Scene, context: Context) -> list[tuple]:
    # get to mapping_templates folder or create if there isn't one
    mapping_folder = get_mapping_folder()

    json_presets = []
    files = sorted(os.listdir(mapping_folder))
    # get only json files
    for file in files:
        _, file_extension = os.path.splitext(file)
        if file_extension == ".json":
            json_presets.append(file)

    items = []
    for i in json_presets:
        s = (i, i, "")
        items.append(s)

    return items
