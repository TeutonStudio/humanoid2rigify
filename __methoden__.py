import bpy

from pathlib import Path


_MERGE_WHITELIST_INIT_SCENE = None
_BONE_NAME_CACHE_INIT_SCENE = None
_BONE_NAME_CACHE_INIT_ARMATURE = None
_BONE_NAME_CACHE = {}

DEFAULT_MERGE_EXTRA_BONE_WHITELIST = [
    "rig",
    "properties",
    "clothes",
]

def get_mapping_folder():
    mapping_folder = Path(__file__).resolve().parent / "mapping_templates"
    mapping_folder.mkdir(parents=True, exist_ok=True)
    return mapping_folder.as_posix()

def get_cached_bone_names(armature_obj):
    if armature_obj is None:
        return ()

    cache_key = get_armature_cache_key(armature_obj)
    cached = _BONE_NAME_CACHE.get(cache_key)
    if cached is not None:
        return cached

    _BONE_NAME_CACHE.clear()
    bone_names = cache_key[1]
    _BONE_NAME_CACHE[cache_key] = bone_names
    return bone_names

def get_merge_whitelist_option_values(context):
    option_values = list(DEFAULT_MERGE_EXTRA_BONE_WHITELIST)
    scene = getattr(context, "scene", None) if context is not None else None
    armature_obj = get_current_armature(context)
    if armature_obj is None:
        return option_values

    if scene is not None and is_bone_name_cache_valid(scene, armature_obj):
        bone_names = (item.name for item in scene.cached_bone_names)
    else:
        bone_names = get_cached_bone_names(armature_obj)

    for bone_name in bone_names:
        if bone_name not in option_values:
            option_values.append(bone_name)

    return option_values

def get_cached_bone_items(context):
    scene = getattr(context, "scene", None) if context is not None else None
    armature_obj = get_current_armature(context)
    if armature_obj is None:
        return []

    if scene is not None and is_bone_name_cache_valid(scene, armature_obj):
        bone_names = [item.name for item in scene.cached_bone_names]
    else:
        bone_names = list(get_cached_bone_names(armature_obj))

    return [
        (bone_name, bone_name, bone_name)
        for bone_name in bone_names
    ]

def get_next_merge_whitelist_value(scene, context):
    existing_values = {
        item.value
        for item in scene.merge_extra_bone_whitelist
        if item.value
    }
    for value in get_merge_whitelist_option_values(context):
        if value not in existing_values:
            return value

    return DEFAULT_MERGE_EXTRA_BONE_WHITELIST[0]

def ensure_merge_whitelist(scene):
    collection = getattr(scene, "merge_extra_bone_whitelist", None)
    if collection is None or len(collection) != 0:
        return

    for pattern in DEFAULT_MERGE_EXTRA_BONE_WHITELIST:
        item = collection.add()
        item.value = pattern

def rebuild_bone_name_cache(scene, armature_obj):
    scene.cached_bone_names.clear()
    for bone_name in get_cached_bone_names(armature_obj):
        item = scene.cached_bone_names.add()
        item.name = bone_name

    scene.cached_bone_names_armature = armature_obj.name
    scene.cached_bone_names_count = len(armature_obj.data.bones)

def initialize_pending_bone_name_cache():
    global _BONE_NAME_CACHE_INIT_SCENE
    global _BONE_NAME_CACHE_INIT_ARMATURE

    scene_name = _BONE_NAME_CACHE_INIT_SCENE
    armature_name = _BONE_NAME_CACHE_INIT_ARMATURE
    _BONE_NAME_CACHE_INIT_SCENE = None
    _BONE_NAME_CACHE_INIT_ARMATURE = None
    if scene_name is None or armature_name is None:
        return None

    scene = bpy.data.scenes.get(scene_name)
    armature_obj = bpy.data.objects.get(armature_name)
    if scene is None or armature_obj is None or armature_obj.type != "ARMATURE":
        return None

    rebuild_bone_name_cache(scene, armature_obj)
    tag_redraw_all_areas()
    return None

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

def ensure_pose_mode_data(scene, context):
    if scene is None or context is None or not is_pose_armature_context(context):
        return

    ensure_merge_whitelist(scene)

def schedule_bone_name_cache_refresh(scene, context):
    global _BONE_NAME_CACHE_INIT_SCENE
    global _BONE_NAME_CACHE_INIT_ARMATURE

    armature_obj = get_current_armature(context)
    if scene is None or armature_obj is None:
        return

    if is_bone_name_cache_valid(scene, armature_obj):
        return

    _BONE_NAME_CACHE_INIT_SCENE = scene.name
    _BONE_NAME_CACHE_INIT_ARMATURE = armature_obj.name
    if not bpy.app.timers.is_registered(initialize_pending_bone_name_cache):
        bpy.app.timers.register(initialize_pending_bone_name_cache, first_interval=0.0)

def schedule_merge_whitelist_initialization(scene):
    global _MERGE_WHITELIST_INIT_SCENE

    if scene is None or len(scene.merge_extra_bone_whitelist) != 0:
        return

    _MERGE_WHITELIST_INIT_SCENE = scene.name
    if not bpy.app.timers.is_registered(initialize_pending_merge_whitelist):
        bpy.app.timers.register(initialize_pending_merge_whitelist, first_interval=0.0)

def get_armature_cache_key(armature_obj):
    if armature_obj is None:
        return None

    bone_names = tuple(bone.name for bone in armature_obj.data.bones)
    return (armature_obj.as_pointer(), bone_names)

def get_current_armature(context):
    if context is None:
        return None

    context_object = getattr(context, "object", None)
    if context_object is not None and context_object.type == "ARMATURE":
        return context_object

    active_object = getattr(context, "active_object", None)
    if active_object is not None and active_object.type == "ARMATURE":
        return active_object

    for obj in getattr(context, "selected_objects", []):
        if obj.type == "ARMATURE":
            return obj

    return None

def is_pose_armature_context(context):
    armature = get_current_armature(context)
    return (
        armature is not None
        and (
            getattr(context, "mode", None) == "POSE"
            or getattr(armature, "mode", None) == "POSE"
        )
    )

def is_bone_name_cache_valid(scene, armature_obj):
    if scene is None or armature_obj is None:
        return False

    return (
        scene.cached_bone_names_armature == armature_obj.name
        and scene.cached_bone_names_count == len(armature_obj.data.bones)
        and len(scene.cached_bone_names) != 0
    )

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
