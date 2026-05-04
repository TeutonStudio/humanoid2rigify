from fnmatch import fnmatchcase

from ...__methoden__ import DEFAULT_MERGE_EXTRA_BONE_WHITELIST

PARAM_BONE_KEYS = [
    "head",
    "first_neck",
    "last_neck",
    "first_spine",
    "last_spine",
    "clav_r",
    "clav_l",
    "uparm_l",
    "uparm_r",
    "lowarm_l",
    "lowarm_r",
    "hand_l",
    "hand_r",
    "palm_pinky_r",
    "pinky_01_r",
    "pinky_02_r",
    "pinky_03_r",
    "palm_ring_r",
    "ring_01_r",
    "ring_02_r",
    "ring_03_r",
    "palm_middle_r",
    "middle_01_r",
    "middle_02_r",
    "middle_03_r",
    "palm_index_r",
    "index_01_r",
    "index_02_r",
    "index_03_r",
    "thumb_01_r",
    "thumb_02_r",
    "thumb_03_r",
    "palm_pinky_l",
    "pinky_01_l",
    "pinky_02_l",
    "pinky_03_l",
    "palm_ring_l",
    "ring_01_l",
    "ring_02_l",
    "ring_03_l",
    "palm_middle_l",
    "middle_01_l",
    "middle_02_l",
    "middle_03_l",
    "palm_index_l",
    "index_01_l",
    "index_02_l",
    "index_03_l",
    "thumb_01_l",
    "thumb_02_l",
    "thumb_03_l",
    "thigh_l",
    "thigh_r",
    "calf_l",
    "calf_r",
    "foot_l",
    "foot_r",
    "toe_l",
    "toe_r",
    "heel_l",
    "heel_r",
]

GENERATED_HELPER_BONES = {
    "heel_l",
    "heel_r",
    "new_torso",
    "skeleton:TransformationTarget",
    "skeleton:torso_bone",
}

DEF_EXCLUDED_TARGET_NAMES = {"torso", "neck", "chest"}


def unique_non_empty(values):
    return list(dict.fromkeys([value for value in values if value]))


def get_merge_extra_bone_whitelist(params):
    whitelist = params.get("merge_extra_bone_whitelist", [])
    cleaned_whitelist = [pattern.strip() for pattern in whitelist if pattern and pattern.strip()]
    if cleaned_whitelist:
        return cleaned_whitelist

    return DEFAULT_MERGE_EXTRA_BONE_WHITELIST


def is_merge_extra_bone_name(bone_name, params):
    return any(
        fnmatchcase(bone_name, pattern)
        for pattern in get_merge_extra_bone_whitelist(params)
    )


def get_standard_source_bone_names(params):
    return unique_non_empty([params.get(key, "") for key in PARAM_BONE_KEYS])


def get_bone(armature_obj, bone_name):
    if not bone_name:
        return None

    return armature_obj.data.bones.get(bone_name)


def build_parent_chain_to_ancestor(armature_obj, ancestor_name, descendant_name):
    descendant_bone = get_bone(armature_obj, descendant_name)
    if descendant_bone is None:
        return []

    chain = []
    current = descendant_bone
    while current is not None:
        chain.append(current.name)
        if current.name == ancestor_name:
            chain.reverse()
            return chain
        current = current.parent

    return []


def build_path_by_children(start_bone, goal_name):
    if start_bone is None:
        return []

    if start_bone.name == goal_name:
        return [start_bone.name]

    for child in start_bone.children:
        child_path = build_path_by_children(child, goal_name)
        if child_path:
            return [start_bone.name] + child_path

    return []


def derive_spine_data(armature_obj, params):
    first_spine = params.get("first_spine", "")
    last_spine = params.get("last_spine", "") or first_spine

    spine_chain = build_parent_chain_to_ancestor(
        armature_obj,
        first_spine,
        last_spine,
    )
    if not spine_chain:
        spine_chain = unique_non_empty([first_spine, last_spine])

    second_spine = first_spine
    if len(spine_chain) > 1:
        second_spine = spine_chain[1]

    return {
        "first_spine": first_spine,
        "second_spine": second_spine,
        "last_spine": last_spine,
        "all_spines": spine_chain,
        "less_spine_bones": len(spine_chain) <= 2,
    }


def derive_neck_data(armature_obj, params):
    first_neck = params.get("first_neck", "")
    last_neck = params.get("last_neck", "") or first_neck

    first_neck_bone = get_bone(armature_obj, first_neck)
    neck_chain = build_path_by_children(first_neck_bone, last_neck)
    if not neck_chain:
        neck_chain = unique_non_empty([first_neck, last_neck])

    return {
        "first_neck": first_neck,
        "last_neck": last_neck,
        "all_necks": neck_chain or unique_non_empty([first_neck]),
    }


def normalize_constraint_target_name(target_name):
    if not target_name:
        return ""

    if "skeleton:torso_bone" in target_name.lower():
        return "torso"

    if "chest" in target_name:
        return "chest"

    if target_name in DEF_EXCLUDED_TARGET_NAMES:
        return target_name

    return f"DEF-{target_name}"


def build_standard_constraint_map(params, derived_data):
    first_spine = derived_data["spines"]["first_spine"]
    second_spine = derived_data["spines"]["second_spine"]
    last_spine = derived_data["spines"]["last_spine"]
    all_spines = derived_data["spines"]["all_spines"]
    all_necks = derived_data["necks"]["all_necks"]
    less_spine_bones = derived_data["spines"]["less_spine_bones"]

    raw_map = {
        "skeleton:torso_bone": ["torso", True],
        params.get("head", ""): [params.get("head", ""), False],
        params.get("first_neck", ""): [params.get("first_neck", ""), True],
        first_spine: [first_spine, True],
        second_spine: [second_spine, True],
        last_spine: [last_spine, True],
        params.get("clav_r", ""): [params.get("clav_r", ""), True],
        params.get("clav_l", ""): [params.get("clav_l", ""), True],
        params.get("uparm_r", ""): [params.get("uparm_r", ""), False],
        params.get("lowarm_r", ""): [params.get("lowarm_r", ""), False],
        params.get("hand_r", ""): [params.get("hand_r", ""), False],
        params.get("uparm_l", ""): [params.get("uparm_l", ""), False],
        params.get("lowarm_l", ""): [params.get("lowarm_l", ""), False],
        params.get("hand_l", ""): [params.get("hand_l", ""), False],
        params.get("palm_pinky_r", ""): [params.get("palm_pinky_r", ""), False],
        params.get("pinky_01_r", ""): [params.get("pinky_01_r", ""), False],
        params.get("pinky_02_r", ""): [params.get("pinky_02_r", ""), False],
        params.get("pinky_03_r", ""): [params.get("pinky_03_r", ""), False],
        params.get("palm_ring_r", ""): [params.get("palm_ring_r", ""), False],
        params.get("ring_01_r", ""): [params.get("ring_01_r", ""), False],
        params.get("ring_02_r", ""): [params.get("ring_02_r", ""), False],
        params.get("ring_03_r", ""): [params.get("ring_03_r", ""), False],
        params.get("palm_middle_r", ""): [params.get("palm_middle_r", ""), False],
        params.get("middle_01_r", ""): [params.get("middle_01_r", ""), False],
        params.get("middle_02_r", ""): [params.get("middle_02_r", ""), False],
        params.get("middle_03_r", ""): [params.get("middle_03_r", ""), False],
        params.get("palm_index_r", ""): [params.get("palm_index_r", ""), False],
        params.get("index_01_r", ""): [params.get("index_01_r", ""), False],
        params.get("index_02_r", ""): [params.get("index_02_r", ""), False],
        params.get("index_03_r", ""): [params.get("index_03_r", ""), False],
        params.get("thumb_01_r", ""): [params.get("thumb_01_r", ""), False],
        params.get("thumb_02_r", ""): [params.get("thumb_02_r", ""), False],
        params.get("thumb_03_r", ""): [params.get("thumb_03_r", ""), False],
        params.get("palm_pinky_l", ""): [params.get("palm_pinky_l", ""), False],
        params.get("pinky_01_l", ""): [params.get("pinky_01_l", ""), False],
        params.get("pinky_02_l", ""): [params.get("pinky_02_l", ""), False],
        params.get("pinky_03_l", ""): [params.get("pinky_03_l", ""), False],
        params.get("palm_ring_l", ""): [params.get("palm_ring_l", ""), False],
        params.get("ring_01_l", ""): [params.get("ring_01_l", ""), False],
        params.get("ring_02_l", ""): [params.get("ring_02_l", ""), False],
        params.get("ring_03_l", ""): [params.get("ring_03_l", ""), False],
        params.get("palm_middle_l", ""): [params.get("palm_middle_l", ""), False],
        params.get("middle_01_l", ""): [params.get("middle_01_l", ""), False],
        params.get("middle_02_l", ""): [params.get("middle_02_l", ""), False],
        params.get("middle_03_l", ""): [params.get("middle_03_l", ""), False],
        params.get("palm_index_l", ""): [params.get("palm_index_l", ""), False],
        params.get("index_01_l", ""): [params.get("index_01_l", ""), False],
        params.get("index_02_l", ""): [params.get("index_02_l", ""), False],
        params.get("index_03_l", ""): [params.get("index_03_l", ""), False],
        params.get("thumb_01_l", ""): [params.get("thumb_01_l", ""), False],
        params.get("thumb_02_l", ""): [params.get("thumb_02_l", ""), False],
        params.get("thumb_03_l", ""): [params.get("thumb_03_l", ""), False],
        params.get("thigh_r", ""): [params.get("thigh_r", ""), True],
        params.get("calf_r", ""): [params.get("calf_r", ""), False],
        params.get("foot_r", ""): [params.get("foot_r", ""), False],
        params.get("toe_r", ""): [params.get("toe_r", ""), False],
        params.get("thigh_l", ""): [params.get("thigh_l", ""), True],
        params.get("calf_l", ""): [params.get("calf_l", ""), False],
        params.get("foot_l", ""): [params.get("foot_l", ""), False],
        params.get("toe_l", ""): [params.get("toe_l", ""), False],
    }

    if less_spine_bones and "skeleton:torso_bone" in raw_map:
        del raw_map["skeleton:torso_bone"]

    for bone_name in all_spines:
        raw_map[bone_name] = [bone_name, True]

    for bone_name in all_necks:
        raw_map[bone_name] = [bone_name, True]

    constraint_map = {}
    for source_bone, config in raw_map.items():
        if not source_bone:
            continue

        target_seed, copy_location = config
        if not target_seed:
            continue

        constraint_map[source_bone] = {
            "source_bone": source_bone,
            "target_seed": target_seed,
            "constraint_target": normalize_constraint_target_name(target_seed),
            "merge_target": normalize_constraint_target_name(target_seed),
            "copy_location": copy_location,
            "is_standard": True,
        }

    return constraint_map


def collect_extra_bones(armature_obj, params, derived_data):
    excluded_names = set(get_standard_source_bone_names(params))
    excluded_names.update(derived_data["spines"]["all_spines"])
    excluded_names.update(derived_data["necks"]["all_necks"])
    excluded_names.update(GENERATED_HELPER_BONES)

    return sorted(
        bone.name
        for bone in armature_obj.data.bones
        if bone.name not in excluded_names
    )


def build_extra_bone_data(armature_obj, extra_bones, weighted_vertex_groups, params):
    extra_bone_data = {}

    for bone_name in extra_bones:
        bone = get_bone(armature_obj, bone_name)
        if bone is None:
            continue

        needs_new_merge_bone = is_merge_extra_bone_name(bone_name, params)

        # Harte Whitelist:
        # Nicht-whitelisted Extra-Bones bekommen kein Zielmapping
        # und dürfen später nicht im neuen Rigify-Rig landen.
        if not needs_new_merge_bone:
            continue

        has_weights = bone_name in weighted_vertex_groups

        extra_bone_data[bone_name] = {
            "source_bone": bone_name,
            "constraint_target": bone_name,
            "merge_target": f"DEF-{bone_name}",
            "is_standard": False,
            "use_deform": bone.use_deform,
            "has_weights": has_weights,
            "is_hidden": bone.hide,
            "keep_in_deform_mode": bone.use_deform and has_weights,
            "needs_new_merge_bone": True,
        }

    return extra_bone_data
