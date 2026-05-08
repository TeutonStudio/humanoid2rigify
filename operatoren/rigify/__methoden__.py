import re

import bpy
import rigify
from mathutils import Vector, Color

from ...__eigenschaften__ import Wirbelsäule
from .kontext import GenerationContext, RIGIFY_UI_ROWS, EXTRA_GROUP_UI_START_ROW, RIGIFY_UI_TITLES, \
    EXTRA_GROUP_COLLECTION_PREFIX, STANDARD_LAYER_UI_ORDER, LAYER_COLLECTION_NAMES, STANDARD_COLLECTION_NAMES, \
    INTERNAL_RIGIFY_PREFIXES, COLLECTION_LAYER_BY_NAME, FALLBACK_COLOR, FarbGattung, GENERIC_CIRCLE_WIDGET_VERTEX_COUNT


def convert_source_roll_axis_to_target_space(source_obj, target_obj, source_bone) -> Vector:
    source_matrix = source_obj.matrix_world.to_3x3()
    target_matrix_inv = target_obj.matrix_world.inverted().to_3x3()
    source_bone_matrix = source_bone.matrix_local.to_3x3()
    roll_axis = target_matrix_inv @ source_matrix @ source_bone_matrix @ Vector((0.0, 0.0, 1.0))
    return Vector((0.0, 0.0, 1.0)) if roll_axis.length == 0 else roll_axis.normalized()


def copy_edit_bone_roll_from_source(source_obj, target_obj, source_bone_name: str, target_bone_name: str | None = None) -> None:
    target_bone_name = target_bone_name or source_bone_name
    source_bone = source_obj.data.bones.get(source_bone_name)
    target_edit_bone = target_obj.data.edit_bones.get(target_bone_name)

    if source_bone is None or target_edit_bone is None:
        return

    try:
        target_edit_bone.align_roll(
            convert_source_roll_axis_to_target_space(source_obj, target_obj, source_bone)
        )
    except RuntimeError:
        pass


def ensure_rigify_enabled() -> None:
    if "rigify" not in bpy.context.preferences.addons:
        bpy.ops.preferences.addon_enable(module="rigify")


def make_object_active(obj) -> None:
    if bpy.context.object is not None and bpy.context.object.mode != "OBJECT":
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except RuntimeError:
            pass

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def ensure_mode(obj, mode_name: str) -> None:
    if bpy.context.view_layer.objects.active != obj:
        make_object_active(obj)

    if bpy.context.object is not None and bpy.context.object.mode != mode_name:
        bpy.ops.object.mode_set(mode=mode_name)


def get_all_bone_names(obj, mode_name: str = "DATA") -> list[str]:
    if obj is None or obj.type != "ARMATURE":
        return []

    if mode_name == "EDIT":
        ensure_mode(obj, "EDIT")
        return [bone.name for bone in obj.data.edit_bones]

    if mode_name == "POSE":
        ensure_mode(obj, "POSE")
        return [bone.name for bone in obj.pose.bones]

    return [bone.name for bone in obj.data.bones]


def get_or_create_bone_collection(armature_data, layer_index: int):
    return get_or_create_collection_by_layer(armature_data, layer_index)


def get_or_create_collection_by_layer(armature_data, layer_index: int):
    collection_name = get_collection_name(layer_index)
    bone_collection = armature_data.collections_all.get(collection_name)

    if bone_collection is None:
        bone_collection = armature_data.collections.new(collection_name)

    if hasattr(bone_collection, "rigify_ui_row"):
        bone_collection.rigify_ui_row = RIGIFY_UI_ROWS.get(layer_index, EXTRA_GROUP_UI_START_ROW)

    if hasattr(bone_collection, "rigify_ui_title"):
        bone_collection.rigify_ui_title = RIGIFY_UI_TITLES.get(layer_index, collection_name)

    bone_collection.is_visible = True
    return bone_collection


def get_collection_name(layer_index: int) -> str:
    return LAYER_COLLECTION_NAMES.get(layer_index, f"Layer {layer_index + 1}")


def sanitize_extra_group_name(value: str, fallback: str = "Additional") -> str:
    value = (value or "").strip()
    return value if value else fallback


def extra_group_collection_name(group_name: str) -> str:
    return f"{EXTRA_GROUP_COLLECTION_PREFIX}: {sanitize_extra_group_name(group_name)}"


def is_extra_group_collection(collection) -> bool:
    return collection.name.startswith(f"{EXTRA_GROUP_COLLECTION_PREFIX}:")


def get_max_rigify_ui_row(armature_data) -> int:
    if not uses_bone_collections(armature_data):
        return 0

    return max(
        [
            getattr(collection, "rigify_ui_row", 0)
            for collection in armature_data.collections_all
            if not is_extra_group_collection(collection)
        ]
        or [0]
    )


def uses_bone_collections(armature_data) -> bool:
    return hasattr(armature_data, "collections_all")


def build_extra_group_ui_rows(context: GenerationContext, armature_data) -> dict[str, int]:
    start_row = EXTRA_GROUP_UI_START_ROW
    rows: dict[str, int] = {}

    for data in context.extra_bone_data.values():
        if not data.get("needs_new_merge_bone", False):
            continue

        group_name = sanitize_extra_group_name(data.get("whitelist_group_name", "Additional"))
        rows.setdefault(group_name, start_row + len(rows))

    return rows


def get_or_create_extra_group_collection(armature_data, group_name: str, ui_row: int):
    group_name = sanitize_extra_group_name(group_name)
    collection_name = extra_group_collection_name(group_name)
    bone_collection = armature_data.collections_all.get(collection_name)

    if bone_collection is None:
        bone_collection = armature_data.collections.new(collection_name)

    if hasattr(bone_collection, "rigify_ui_row"):
        bone_collection.rigify_ui_row = ui_row

    if hasattr(bone_collection, "rigify_ui_title"):
        bone_collection.rigify_ui_title = group_name

    bone_collection.is_visible = True
    return bone_collection


def assign_bone_to_layer_group(obj, bone_name: str, layer_index: int) -> None:
    armature_data = obj.data
    bone = armature_data.bones.get(bone_name)

    if bone is None:
        return

    if uses_bone_collections(armature_data):
        target_collection = get_or_create_bone_collection(armature_data, layer_index)

        for collection in armature_data.collections_all:
            try:
                collection.unassign(bone)
            except RuntimeError:
                pass

        target_collection.assign(bone)
        return

    bone.layers[layer_index] = True

    for index in range(32):
        if index != layer_index:
            bone.layers[index] = False


def assign_bone_to_extra_group_collection(obj, bone_name: str, group_name: str, ui_row: int) -> None:
    armature_data = obj.data
    bone = armature_data.bones.get(bone_name)

    if bone is None:
        return

    if not uses_bone_collections(armature_data):
        assign_bone_to_layer_group(obj, bone_name, 27)
        return

    target_collection = get_or_create_extra_group_collection(armature_data, group_name, ui_row)

    for collection in armature_data.collections_all:
        try:
            collection.unassign(bone)
        except RuntimeError:
            pass

    target_collection.assign(bone)


def apply_extra_group_collections(context: GenerationContext, obj, extra_group_ui_rows: dict[str, int]) -> list[str]:
    if obj is None or obj.type != "ARMATURE" or not uses_bone_collections(obj.data):
        return []

    assigned_collection_names: list[str] = []

    for source_bone_name, data in context.extra_bone_data.items():
        if not data.get("needs_new_merge_bone", False):
            continue

        group_name = sanitize_extra_group_name(data.get("whitelist_group_name", "Additional"))
        ui_row = extra_group_ui_rows.get(group_name)

        if ui_row is None:
            continue

        collection_name = extra_group_collection_name(group_name)
        candidate_bone_names = [
            data.get("constraint_target"),
            source_bone_name,
            data.get("merge_target"),
        ]

        for candidate_bone_name in dict.fromkeys(name for name in candidate_bone_names if name):
            if obj.data.bones.get(candidate_bone_name) is None:
                continue

            assign_bone_to_extra_group_collection(obj, candidate_bone_name, group_name, ui_row)

            if collection_name not in assigned_collection_names:
                assigned_collection_names.append(collection_name)

            break

    return assigned_collection_names


def set_visible_rig_layers(obj, layer_indices, extra_collection_names=()) -> None:
    armature_data = obj.data

    if uses_bone_collections(armature_data):
        visible_collections = {get_collection_name(layer_index) for layer_index in layer_indices}
        visible_collections.update(extra_collection_names)

        for collection in armature_data.collections_all:
            collection.is_visible = collection.name in visible_collections

        return

    for index in range(32):
        armature_data.layers[index] = index in layer_indices


def set_rigify_layer_param(obj, rigify_param, attr_name: str, layer_index: int | None) -> None:
    if layer_index is None:
        return

    coll_refs_name = f"{attr_name}_coll_refs"
    coll_refs = getattr(rigify_param, coll_refs_name, None)

    if coll_refs is not None and uses_bone_collections(obj.data):
        while len(coll_refs):
            coll_refs.remove(len(coll_refs) - 1)

        coll_refs.add().set_collection(
            get_or_create_bone_collection(obj.data, layer_index)
        )
        return

    if not hasattr(rigify_param, attr_name):
        return

    layer_config = getattr(rigify_param, attr_name)

    if hasattr(layer_config, "__len__") and not isinstance(layer_config, bool):
        for index in range(len(layer_config)):
            layer_config[index] = False

        if layer_index < len(layer_config):
            layer_config[layer_index] = True


def make_bone(
        obj,
        bone_name: str,
        bone_parent: str | None = None,
        head=(0.0, 0.0, 0.0),
        tail=(0.5, 0.0, 0.0),
):
    if not bone_name:
        return None

    ensure_mode(obj, "EDIT")
    edit_bones = obj.data.edit_bones
    existing_bone = edit_bones.get(bone_name)

    if existing_bone is not None:
        return existing_bone

    new_bone = edit_bones.new(bone_name)
    new_bone.head = head
    new_bone.tail = tail

    if bone_parent and bone_parent in edit_bones:
        new_bone.parent = edit_bones[bone_parent]

    return new_bone


def average_vectors(vectors):
    vectors = [vector for vector in vectors if vector is not None]
    return None if not vectors else sum(vectors, Vector()) / len(vectors)


def average_bone_points(bones, attr_name: str = "tail"):
    return average_vectors([getattr(bone, attr_name).copy() for bone in bones])


def get_rotation_diff(source_pose_bone, source_obj, target_pose_bone, target_obj):
    source_world_matrix = source_obj.matrix_world @ source_pose_bone.matrix
    target_world_matrix = target_obj.matrix_world @ target_pose_bone.matrix
    return source_world_matrix.to_quaternion(), target_world_matrix.to_quaternion()


def remove_constraint_if_present(pose_bone, constraint_name: str) -> None:
    constraint = pose_bone.constraints.get(constraint_name)

    if constraint is not None:
        pose_bone.constraints.remove(constraint)


def create_constraint(
        owner_pose_bone,
        owner_obj,
        target_bone_name: str,
        target_obj,
        rotation,
        rot_order: str = "XYZ",
        copy_loc: bool = False,
        copy_stretch_location: bool = False,
        transform_space: str = "WORLD",
) -> None:
    remove_constraint_if_present(owner_pose_bone, "H2R Copy Rotation")
    remove_constraint_if_present(owner_pose_bone, "H2R Root Rotation Offset")
    remove_constraint_if_present(owner_pose_bone, "H2R Copy Location")

    rot_constraint = owner_pose_bone.constraints.new("COPY_ROTATION")
    rot_constraint.name = "H2R Copy Rotation"
    rot_constraint.target = target_obj
    rot_constraint.subtarget = target_bone_name
    rot_constraint.show_expanded = False

    transform_constraint = owner_pose_bone.constraints.new("TRANSFORM")
    transform_constraint.name = "H2R Root Rotation Offset"
    transform_constraint.target = owner_obj
    transform_constraint.subtarget = "skeleton:TransformationTarget"
    transform_constraint.map_from = "ROTATION"
    transform_constraint.map_to = "ROTATION"
    transform_constraint.to_euler_order = rot_order
    transform_constraint.to_min_x_rot = rotation.x
    transform_constraint.to_min_y_rot = rotation.y
    transform_constraint.to_min_z_rot = rotation.z
    transform_constraint.owner_space = transform_space
    transform_constraint.mix_mode_rot = "AFTER"
    transform_constraint.show_expanded = False

    if copy_loc or copy_stretch_location:
        loc_constraint = owner_pose_bone.constraints.new("COPY_LOCATION")
        loc_constraint.name = "H2R Copy Location"
        loc_constraint.target = target_obj
        loc_constraint.subtarget = target_bone_name
        loc_constraint.show_expanded = False


def initialisiere_standard_bone_collections(armature_data) -> None:
    if not uses_bone_collections(armature_data):
        return

    for layer_index in STANDARD_LAYER_UI_ORDER:
        get_or_create_collection_by_layer(armature_data, layer_index)


def repariere_standard_control_collections(rig_obj) -> None:
    if rig_obj is None or rig_obj.type != "ARMATURE":
        return

    for pose_bone in rig_obj.pose.bones:
        layer_index = errate_standard_layer_fuer_control(rig_obj, pose_bone)

        if layer_index is None:
            continue

        assign_standard_bone_collection(rig_obj, pose_bone.name, layer_index)


def errate_standard_layer_fuer_control(rig_obj, pose_bone) -> int | None:
    bone_name = pose_bone.name
    bone = pose_bone.bone
    armature_data = rig_obj.data

    # Torso-Tweaks zuerst, sonst landen tweak_spine_* im Torso.
    if ist_torso_tweak_control_bone(bone_name):
        return 4

    ist_fk = ist_fk_control_bone(bone_name)
    ist_ik = ist_ik_control_bone(bone_name)
    ist_tweak = ist_tweak_control_bone(bone_name)

    # Sonderfall: manche Rigify-Tweak-Bones heißen nicht sauber *_tweak,
    # sondern z.B. lowerarm_.001. Danke, Blender, sehr hilfreich.
    name = bone_name.lower()
    if not ist_tweak and re.search(r"(upperarm|upper_arm|lowerarm|lower_arm|forearm|calf|shin|thigh|foot|toe|heel).*\.\d+$", name):
        ist_tweak = True

    if not (ist_fk or ist_ik or ist_tweak):
        return None

    if ist_arm_control_bone(bone_name):
        seite = finde_seite_aus_name(bone_name)
        seite = seite or finde_seite_aus_aktueller_collection(armature_data, bone, "arm")

        if ist_tweak:
            return layer_fuer_seite_und_typ(seite, 9, 12)

        if ist_fk:
            return layer_fuer_seite_und_typ(seite, 8, 11)

        if ist_ik:
            return layer_fuer_seite_und_typ(seite, 7, 10)

    if ist_bein_control_bone(bone_name):
        seite = finde_seite_aus_name(bone_name)
        seite = seite or finde_seite_aus_aktueller_collection(armature_data, bone, "bein")

        if ist_tweak:
            return layer_fuer_seite_und_typ(seite, 15, 18)

        if ist_fk:
            return layer_fuer_seite_und_typ(seite, 14, 17)

        if ist_ik:
            return layer_fuer_seite_und_typ(seite, 13, 16)

    return None


def layer_fuer_seite_und_typ(seite: str | None, links_layer: int, rechts_layer: int) -> int | None:
    if seite == "L":
        return links_layer

    if seite == "R":
        return rechts_layer

    return None


def finde_seite_aus_name(bone_name: str) -> str | None:
    name = bone_name.lower()

    # Erlaubt z.B. ".L", ".L.001", "_l", "_l.001", "-r", "-r.001"
    if re.search(r"(\.l|_l|-l)(?:\.\d+)?$", name):
        return "L"

    if re.search(r"(\.r|_r|-r)(?:\.\d+)?$", name):
        return "R"

    # Erlaubt Seitenmarker in der Mitte, z.B. "hand.L_tweak"
    if re.search(r"(\.l|_l|-l)(?=[._-])", name):
        return "L"

    if re.search(r"(\.r|_r|-r)(?=[._-])", name):
        return "R"

    return None


def assign_standard_bone_collection(rig_obj, bone_name: str, layer_index: int) -> None:
    armature_data = rig_obj.data
    bone = armature_data.bones.get(bone_name)

    if bone is None:
        return

    if not uses_bone_collections(armature_data):
        bone.layers[layer_index] = True

        for index in range(32):
            if index != layer_index:
                bone.layers[index] = False

        return

    target_collection = get_or_create_collection_by_layer(armature_data, layer_index)

    # Nur Standard-Rigify-Collections entfernen. Extra-Gruppen bleiben erhalten.
    for collection in armature_data.collections_all:
        if collection.name not in STANDARD_COLLECTION_NAMES:
            continue

        try:
            collection.unassign(bone)
        except RuntimeError:
            pass

    target_collection.assign(bone)


def ist_torso_tweak_control_bone(bone_name: str) -> bool:
    name = bone_name.lower()

    if ist_interner_rigify_knochen(bone_name):
        return False

    return (
        name.startswith("tweak_pelvis")
        or name.startswith("tweak_spine")
        or name.startswith("tweak_neck")
        or name.startswith("tweak_chest")
        or name.startswith("tweak_torso")
        or "spine_tweak" in name
        or "neck_tweak" in name
        or "pelvis_tweak" in name
    )


def ist_arm_control_bone(bone_name: str) -> bool:
    name = bone_name.lower()

    return any(part in name for part in (
        "upperarm",
        "upper_arm",
        "lowerarm",
        "lower_arm",
        "forearm",
        "hand",
        "arm_",
        "arm.",
        "arm-",
    ))


def ist_bein_control_bone(bone_name: str) -> bool:
    name = bone_name.lower()

    return any(part in name for part in (
        "thigh",
        "shin",
        "calf",
        "foot",
        "toe",
        "heel",
        "leg_",
        "leg.",
        "leg-",
    ))


def ist_fk_control_bone(bone_name: str) -> bool:
    name = bone_name.lower()

    if ist_interner_rigify_knochen(bone_name):
        return False

    return any(token in name for token in (
        "_fk",
        ".fk",
        "-fk",
        "fk_",
        "fk.",
        "fk-",
    ))


def ist_ik_control_bone(bone_name: str) -> bool:
    name = bone_name.lower()

    if ist_interner_rigify_knochen(bone_name):
        return False

    return any(token in name for token in (
        "_ik",
        ".ik",
        "-ik",
        "ik_",
        "ik.",
        "ik-",
        "ik_target",
        "ik_pole",
    ))


def ist_tweak_control_bone(bone_name: str) -> bool:
    name = bone_name.lower()

    if ist_interner_rigify_knochen(bone_name):
        return False

    return any(token in name for token in (
        "_tweak",
        ".tweak",
        "-tweak",
        "tweak_",
        "tweak.",
        "tweak-",
    ))


def finde_seite_aus_aktueller_collection(armature_data, bone, bereich: str) -> str | None:
    layer_indices = get_bone_standard_layer_indices(armature_data, bone)

    if bereich == "arm":
        if layer_indices & {7, 8, 9}:
            return "L"

        if layer_indices & {10, 11, 12}:
            return "R"

    if bereich == "bein":
        if layer_indices & {13, 14, 15}:
            return "L"

        if layer_indices & {16, 17, 18}:
            return "R"

    return None


def get_bone_standard_layer_indices(armature_data, bone) -> set[int]:
    layer_indices: set[int] = set()

    if bone is None:
        return layer_indices

    if not uses_bone_collections(armature_data):
        for index, enabled in enumerate(getattr(bone, "layers", [])):
            if enabled:
                layer_indices.add(index)

        return layer_indices

    for collection in getattr(bone, "collections", []):
        collection_name = getattr(collection, "name", str(collection))
        layer_index = COLLECTION_LAYER_BY_NAME.get(collection_name)

        if layer_index is not None:
            layer_indices.add(layer_index)

    return layer_indices


def ist_interner_rigify_knochen(bone_name: str) -> bool:
    return bone_name.startswith(INTERNAL_RIGIFY_PREFIXES)


def verstecke_interne_rigify_knochen(rig_obj) -> None:
    if rig_obj is None or rig_obj.type != "ARMATURE":
        return

    for bone in rig_obj.data.bones:
        if ist_interner_rigify_knochen(bone.name):
            bone.hide = True
            bone.hide_select = True


def entferne_interne_knochen_aus_standard_collections(rig_obj) -> None:
    if rig_obj is None or rig_obj.type != "ARMATURE":
        return

    armature_data = rig_obj.data

    if not uses_bone_collections(armature_data):
        return

    for bone in armature_data.bones:
        if not ist_interner_rigify_knochen(bone.name):
            continue

        for collection in armature_data.collections_all:
            if collection.name not in STANDARD_COLLECTION_NAMES:
                continue

            try:
                collection.unassign(bone)
            except RuntimeError:
                pass


def normalisiere_rigify_sichtbarkeit(rig_obj) -> None:
    verstecke_interne_rigify_knochen(rig_obj)
    entferne_interne_knochen_aus_standard_collections(rig_obj)


def normalisiere_rigify_standardfarben(rig_obj) -> None:
    if rig_obj is None or rig_obj.type != "ARMATURE":
        return

    rig_obj.data.show_bone_colors = True

    for pose_bone in rig_obj.pose.bones:
        if ist_tweak_control_bone(pose_bone.name) or ist_torso_tweak_control_bone(pose_bone.name):
            setze_pose_bone_color(pose_bone,FALLBACK_COLOR["Tweak"])
            continue

        if ist_fk_control_bone(pose_bone.name):
            setze_pose_bone_color(pose_bone,FALLBACK_COLOR["FK"])
            continue

        if ist_ik_control_bone(pose_bone.name):
            setze_pose_bone_color(pose_bone,FALLBACK_COLOR["IK"])


def setze_pose_bone_color(pose_bone, color_data: dict[FarbGattung,Color]) -> None:
    setze_bone_color(
        getattr(pose_bone, "color", None),
        color_data["normal"],
        color_data["select"],
        color_data["active"],
    )

    setze_bone_color(
        getattr(pose_bone.bone, "color", None),
        color_data["normal"],
        color_data["select"],
        color_data["active"],
    )


def setze_bone_color(bone_color: Color, normal, select, active) -> None:
    if bone_color is None:
        return

    bone_color.palette = "CUSTOM"
    bone_color.custom.normal = normal
    bone_color.custom.select = select
    bone_color.custom.active = active


def erhalte_generiertes_rigify_rig(metarig_obj):
    ensure_mode(metarig_obj, "OBJECT")
    make_object_active(metarig_obj)
    rigify.generate.generate_rig(bpy.context, metarig_obj)

    return bpy.context.active_object


def get_generated_rigify_name(source_armature) -> str:
    return f"{source_armature.name}_rigify"


def get_generated_rigify_object(source_armature):
    return bpy.data.objects.get(get_generated_rigify_name(source_armature))


def should_replace_custom_shape(source_pose_bone, target_pose_bone, mapping) -> bool:
    if source_pose_bone.custom_shape is None:
        return False
    if not mapping.get("is_standard", True) and source_pose_bone.bone.hide:
        return False
    if target_pose_bone.custom_shape is None:
        return True
    if target_pose_bone.name == Wirbelsäule.WURZEL:
        return True
    if not mapping.get("is_standard", True):
        return True
    return is_generic_circle_widget(target_pose_bone.custom_shape)

def is_generic_circle_widget(widget_obj) -> bool:
    if widget_obj is None or getattr(widget_obj, "type", None) != "MESH":
        return False
    mesh = getattr(widget_obj, "data", None)
    if mesh is None or len(mesh.polygons) != 0:
        return False
    return (
        len(mesh.vertices) == GENERIC_CIRCLE_WIDGET_VERTEX_COUNT
        and len(mesh.edges) == GENERIC_CIRCLE_WIDGET_VERTEX_COUNT
    )


def copy_custom_shape_settings(source_pose_bone, target_pose_bone, target_transform_bone) -> None:
    target_pose_bone.custom_shape = source_pose_bone.custom_shape
    target_pose_bone.custom_shape_translation = source_pose_bone.custom_shape_translation.copy()
    target_pose_bone.custom_shape_rotation_euler = source_pose_bone.custom_shape_rotation_euler.copy()
    target_pose_bone.custom_shape_scale_xyz = tuple(source_pose_bone.custom_shape_scale_xyz)
    target_pose_bone.use_custom_shape_bone_size = source_pose_bone.use_custom_shape_bone_size
    target_pose_bone.custom_shape_wire_width = source_pose_bone.custom_shape_wire_width
    target_pose_bone.custom_shape_transform = target_transform_bone


def copy_pose_transform(source_pose_bone, target_pose_bone) -> None:
    target_pose_bone.location = source_pose_bone.location.copy()
    target_pose_bone.scale = source_pose_bone.scale.copy()
    target_pose_bone.rotation_mode = source_pose_bone.rotation_mode
    if source_pose_bone.rotation_mode == "QUATERNION":
        target_pose_bone.rotation_quaternion = source_pose_bone.rotation_quaternion.copy()
    elif source_pose_bone.rotation_mode == "AXIS_ANGLE":
        target_pose_bone.rotation_axis_angle = source_pose_bone.rotation_axis_angle[:]
    else:
        target_pose_bone.rotation_euler = source_pose_bone.rotation_euler.copy()


def copy_bone_color(source_color, target_color) -> None:
    target_color.palette = source_color.palette
    for custom_field in ("normal", "select", "active"):
        color = getattr(source_color.custom, custom_field)
        setattr(target_color.custom, custom_field, color)


def iter_shape_mappings(rigify_obj, target_name_key: str,source_to_target_map,bones):
    yielded_pairs = set()
    for source_bone_name, mapping in source_to_target_map.items():
        target_bone_name = mapping.get(target_name_key)
        if not target_bone_name:
            continue
        pair_key = (source_bone_name, target_bone_name)
        if pair_key in yielded_pairs:
            continue
        yielded_pairs.add(pair_key)
        yield source_bone_name, target_bone_name, mapping
    source_root = bones.get(Wirbelsäule.WURZEL)
    target_root = rigify_obj.pose.bones.get(Wirbelsäule.WURZEL)
    if source_root is None or target_root is None:
        return
    pair_key = (Wirbelsäule.WURZEL, Wirbelsäule.WURZEL)
    if pair_key not in yielded_pairs:
        yield Wirbelsäule.WURZEL, Wirbelsäule.WURZEL, {
            "source_bone": Wirbelsäule.WURZEL,
            "is_standard": False,
        }


def resolve_target_transform_bone(source_pose_bone, rigify_obj, target_name_key: str, source_to_target_map):
    transform_bone = getattr(source_pose_bone, "custom_shape_transform", None)
    if transform_bone is None:
        return None
    if transform_bone.name == Wirbelsäule.WURZEL:
        return rigify_obj.pose.bones.get(Wirbelsäule.WURZEL)
    transform_mapping = source_to_target_map.get(transform_bone.name)
    if transform_mapping is not None:
        for key in (target_name_key, "constraint_target", "merge_target"):
            target_name = transform_mapping.get(key)
            if target_name and rigify_obj.pose.bones.get(target_name) is not None:
                return rigify_obj.pose.bones[target_name]
    return rigify_obj.pose.bones.get(transform_bone.name)


def setze_objekt_im_vordergrund(obj, enabled: bool = True) -> None:
    if obj is None:
        return

    obj.show_in_front = enabled

def finde_layer_collection(root_layer_collection, target_collection):
    if root_layer_collection.collection == target_collection:
        return root_layer_collection

    for child in root_layer_collection.children:
        found = finde_layer_collection(child, target_collection)

        if found is not None:
            return found

    return None

def setze_collection_exclude_from_scene_layers(collection, enabled: bool = True, scene=None) -> None:
    if collection is None:
        return

    scene = scene or bpy.context.scene

    for view_layer in scene.view_layers:
        layer_collection = finde_layer_collection(
            view_layer.layer_collection,
            collection,
        )

        if layer_collection is not None:
            layer_collection.exclude = enabled

def copy_id_properties(source_owner, target_owner) -> None:
    if source_owner is None or target_owner is None:
        return

    if not hasattr(source_owner, "keys"):
        return

    for key in source_owner.keys():
        if key == "_RNA_UI":
            continue

        try:
            target_owner[key] = source_owner[key]
        except (TypeError, ValueError, RuntimeError):
            pass


def build_pose_bone_path_map(source_obj, target_obj, bone_name_map: dict[str, str]) -> dict[str, str]:
    path_map: dict[str, str] = {}

    for source_bone_name, target_bone_name in bone_name_map.items():
        source_pose_bone = source_obj.pose.bones.get(source_bone_name)
        target_pose_bone = target_obj.pose.bones.get(target_bone_name)

        if source_pose_bone is None or target_pose_bone is None:
            continue

        path_map[source_pose_bone.path_from_id()] = target_pose_bone.path_from_id()

    return path_map


def remap_data_path(data_path: str, path_map: dict[str, str]) -> str:
    if not data_path:
        return data_path

    for source_path, target_path in sorted(
        path_map.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        if (
            data_path == source_path
            or data_path.startswith(f"{source_path}.")
            or data_path.startswith(f"{source_path}[")
        ):
            return f"{target_path}{data_path[len(source_path):]}"

    return data_path


def copy_driver_target(
    source_target,
    target_target,
    source_obj,
    target_obj,
    bone_name_map: dict[str, str],
    path_map: dict[str, str],
) -> None:
    for attr_name in (
        "id_type",
        "transform_type",
        "transform_space",
        "rotation_mode",
    ):
        if not hasattr(source_target, attr_name) or not hasattr(target_target, attr_name):
            continue

        try:
            setattr(target_target, attr_name, getattr(source_target, attr_name))
        except (TypeError, ValueError, RuntimeError):
            pass

    try:
        if source_target.id == source_obj:
            target_target.id = target_obj
        elif source_target.id == source_obj.data:
            target_target.id = target_obj.data
        else:
            target_target.id = source_target.id
    except (TypeError, ValueError, RuntimeError):
        pass

    if hasattr(source_target, "bone_target") and hasattr(target_target, "bone_target"):
        source_bone_target = getattr(source_target, "bone_target", "")
        target_target.bone_target = bone_name_map.get(source_bone_target, source_bone_target)

    if hasattr(source_target, "data_path") and hasattr(target_target, "data_path"):
        target_target.data_path = remap_data_path(
            getattr(source_target, "data_path", ""),
            path_map,
        )


def copy_driver_variables(
    source_driver,
    target_driver,
    source_obj,
    target_obj,
    bone_name_map: dict[str, str],
    path_map: dict[str, str],
) -> None:
    while len(target_driver.variables):
        target_driver.variables.remove(target_driver.variables[0])

    for source_variable in source_driver.variables:
        target_variable = target_driver.variables.new()
        target_variable.name = source_variable.name
        target_variable.type = source_variable.type

        for index, source_target in enumerate(source_variable.targets):
            if index >= len(target_variable.targets):
                continue

            copy_driver_target(
                source_target,
                target_variable.targets[index],
                source_obj,
                target_obj,
                bone_name_map,
                path_map,
            )


def add_replacement_driver(target_obj, data_path: str, array_index: int):
    try:
        target_obj.driver_remove(data_path, array_index)
    except (TypeError, ValueError, RuntimeError):
        try:
            target_obj.driver_remove(data_path)
        except (TypeError, ValueError, RuntimeError):
            pass

    try:
        return target_obj.driver_add(data_path, array_index)
    except (TypeError, ValueError, RuntimeError):
        return target_obj.driver_add(data_path)


def copy_driver_fcurve(
    source_obj,
    target_obj,
    source_fcurve,
    target_data_path: str,
    bone_name_map: dict[str, str],
    path_map: dict[str, str],
) -> bool:
    try:
        target_fcurve = add_replacement_driver(
            target_obj,
            target_data_path,
            source_fcurve.array_index,
        )
    except (TypeError, ValueError, RuntimeError):
        return False

    target_fcurve.mute = source_fcurve.mute
    target_fcurve.hide = source_fcurve.hide
    target_fcurve.lock = source_fcurve.lock
    target_fcurve.extrapolation = source_fcurve.extrapolation

    source_driver = source_fcurve.driver
    target_driver = target_fcurve.driver

    target_driver.type = source_driver.type
    target_driver.use_self = source_driver.use_self

    copy_driver_variables(
        source_driver,
        target_driver,
        source_obj,
        target_obj,
        bone_name_map,
        path_map,
    )

    target_driver.expression = source_driver.expression
    return True


def copy_pose_bone_drivers_between_armatures(
    source_obj,
    target_obj,
    bone_name_map: dict[str, str],
) -> int:
    if source_obj is None or target_obj is None:
        return 0

    if source_obj.type != "ARMATURE" or target_obj.type != "ARMATURE":
        return 0

    if source_obj.animation_data is None:
        return 0

    source_drivers = source_obj.animation_data.drivers
    if not source_drivers:
        return 0

    valid_bone_name_map: dict[str, str] = {}

    for source_bone_name, target_bone_name in bone_name_map.items():
        source_pose_bone = source_obj.pose.bones.get(source_bone_name)
        target_pose_bone = target_obj.pose.bones.get(target_bone_name)

        if source_pose_bone is None or target_pose_bone is None:
            continue

        valid_bone_name_map[source_bone_name] = target_bone_name
        copy_id_properties(source_pose_bone, target_pose_bone)

    if not valid_bone_name_map:
        return 0

    path_map = build_pose_bone_path_map(
        source_obj,
        target_obj,
        valid_bone_name_map,
    )

    copied_count = 0
    target_obj.animation_data_create()

    for source_fcurve in source_drivers:
        target_data_path = remap_data_path(source_fcurve.data_path, path_map)

        if target_data_path == source_fcurve.data_path:
            continue

        if copy_driver_fcurve(
            source_obj,
            target_obj,
            source_fcurve,
            target_data_path,
            valid_bone_name_map,
            path_map,
        ):
            copied_count += 1

    return copied_count


def copy_whitelist_bone_drivers(
    context: GenerationContext,
    rigify_obj,
    target_name_key: str = "constraint_target",
) -> int:
    if rigify_obj is None or rigify_obj.type != "ARMATURE":
        return 0

    bone_name_map: dict[str, str] = {}

    for source_bone_name, data in context.extra_bone_data.items():
        if not data.get("needs_new_merge_bone", False):
            continue

        target_bone_name = (
            data.get(target_name_key)
            or data.get("constraint_target")
            or source_bone_name
        )

        if not target_bone_name:
            continue

        bone_name_map[source_bone_name] = target_bone_name

    return copy_pose_bone_drivers_between_armatures(
        context.source_armature,
        rigify_obj,
        bone_name_map,
    )