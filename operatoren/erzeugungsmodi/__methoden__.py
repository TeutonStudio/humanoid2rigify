from __future__ import annotations

import bpy

from mathutils import Vector
from dataclasses import dataclass, field

from .bone_mapping import (
    build_extra_bone_data,
    build_standard_constraint_map,
    collect_extra_bones,
    derive_neck_data,
    derive_spine_data,
)

LEGACY_LAYER_TO_COLLECTION = {
    0: "Face",
    3: "Torso",
    5: "Fingers",
    6: "Fingers (Detail)",
    7: "Arm.L (IK)",
    8: "Arm.L (FK)",
    9: "Arm.L (Tweak)",
    10: "Arm.R (IK)",
    11: "Arm.R (FK)",
    12: "Arm.R (Tweak)",
    13: "Leg.L (IK)",
    14: "Leg.L (FK)",
    15: "Leg.L (Tweak)",
    16: "Leg.R (IK)",
    17: "Leg.R (FK)",
    18: "Leg.R (Tweak)",
    27: "Additional",
    31: "Root",
}


COLLECTION_UI_ROWS = {
    "Additional": 11,
}

@dataclass
class GenerationContext:
    operator: object
    source_armature: object
    params: dict
    generation_mode: str
    bound_meshes: list = field(default_factory=list)
    backup_collection: object = None
    backup_armature: object = None
    backup_meshes: list = field(default_factory=list)
    derived_bones: dict = field(default_factory=dict)
    weighted_vertex_groups: set = field(default_factory=set)
    used_deform_bones: list = field(default_factory=list)
    standard_constraint_map: dict = field(default_factory=dict)
    source_to_target_map: dict = field(default_factory=dict)
    extra_bones: list = field(default_factory=list)
    extra_bone_data: dict = field(default_factory=dict)


def create_generation_context(operator, armature_obj, params):
    context = GenerationContext(
        operator=operator,
        source_armature=armature_obj,
        params=params,
        generation_mode=params.get("generation_mode", "CONSTRAINT_NEW_RIGIFY"),
        bound_meshes=collect_bound_meshes(armature_obj),
    )

    derived_bones = {
        "spines": derive_spine_data(armature_obj, params),
        "necks": derive_neck_data(armature_obj, params),
    }
    weighted_vertex_groups = collect_weighted_vertex_group_names(context.bound_meshes)
    standard_constraint_map = build_standard_constraint_map(params, derived_bones)
    extra_bones = collect_extra_bones(armature_obj, params, derived_bones)
    extra_bone_data = build_extra_bone_data(
        armature_obj,
        extra_bones,
        weighted_vertex_groups,
        params,
    )

    used_deform_bones = sorted(
        bone.name
        for bone in armature_obj.data.bones
        if bone.use_deform and bone.name in weighted_vertex_groups
    )

    context.derived_bones = derived_bones
    context.weighted_vertex_groups = weighted_vertex_groups
    context.used_deform_bones = used_deform_bones
    context.standard_constraint_map = standard_constraint_map
    context.source_to_target_map = {
        **standard_constraint_map,
        **extra_bone_data,
    }
    context.extra_bones = extra_bones
    context.extra_bone_data = extra_bone_data

    return context


# ============================================================
# Rigify / Bone Collections
# ============================================================

def get_generated_rigify_name(source_armature) -> str:
    return f"{source_armature.name}_rigify"


def get_generated_rigify_object(source_armature):
    return bpy.data.objects.get(get_generated_rigify_name(source_armature))


def uses_bone_collections(armature_data) -> bool:
    return hasattr(armature_data, "collections_all")


def get_collection_name(layer_index: int) -> str:
    return LEGACY_LAYER_TO_COLLECTION.get(layer_index, f"Layer {layer_index + 1}")


def get_or_create_bone_collection(armature_data, layer_index: int):
    collection_name = get_collection_name(layer_index)
    bone_collection = armature_data.collections_all.get(collection_name)

    if bone_collection is None:
        bone_collection = armature_data.collections.new(collection_name)

        if hasattr(bone_collection, "rigify_ui_row"):
            bone_collection.rigify_ui_row = COLLECTION_UI_ROWS.get(collection_name, 0)

    bone_collection.is_visible = True
    return bone_collection


def assign_bone_to_layer_group(obj, bone_name: str, layer_index: int) -> None:
    armature_data = obj.data

    bone = armature_data.bones.get(bone_name)
    if bone is None:
        return

    if uses_bone_collections(armature_data):
        target_collection = get_or_create_bone_collection(
            armature_data,
            layer_index,
        )

        for collection in armature_data.collections_all:
            collection.unassign(bone)

        target_collection.assign(bone)
        return

    bone.layers[layer_index] = True

    for index in range(32):
        if index != layer_index:
            bone.layers[index] = False


def set_visible_rig_layers(obj, layer_indices: set[int] | list[int]) -> None:
    armature_data = obj.data

    if uses_bone_collections(armature_data):
        visible_collections = {
            get_collection_name(layer_index)
            for layer_index in layer_indices
        }

        for collection in armature_data.collections_all:
            collection.is_visible = collection.name in visible_collections

        return

    for index in range(32):
        armature_data.layers[index] = index in layer_indices


def set_rigify_collection_param(
    armature_data,
    rigify_param,
    attr_name: str,
    collection_name: str,
) -> bool:
    ref_list = getattr(rigify_param, f"{attr_name}_coll_refs", None)
    if ref_list is None:
        return False

    while len(ref_list) != 0:
        ref_list.remove(len(ref_list) - 1)

    bone_collection = armature_data.collections_all.get(collection_name)
    if bone_collection is None:
        return False

    ref_list.add().set_collection(bone_collection)
    return True


# ============================================================
# Object / Armature Helpers
# ============================================================

def make_object_active(obj) -> None:
    active_object = bpy.context.view_layer.objects.active

    if active_object is not None:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except RuntimeError:
            pass

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def make_armature_active(armature_obj) -> None:
    make_object_active(armature_obj)


def ensure_edit_mode(obj) -> None:
    if bpy.context.view_layer.objects.active != obj:
        make_object_active(obj)

    if bpy.context.object is None or bpy.context.object.mode != "EDIT":
        bpy.ops.object.mode_set(mode="EDIT")


def ensure_pose_mode(obj) -> None:
    if bpy.context.view_layer.objects.active != obj:
        make_object_active(obj)

    if bpy.context.object is None or bpy.context.object.mode != "POSE":
        bpy.ops.object.mode_set(mode="POSE")


def make_bone(
    obj,
    bone_name: str,
    bone_parent: str | None = None,
    head=(0.0, 0.0, 0.0),
    tail=(0.5, 0.0, 0.0),
):
    ensure_edit_mode(obj)

    edit_bones = obj.data.edit_bones

    existing_bone = edit_bones.get(bone_name)
    if existing_bone is not None:
        return existing_bone

    new_bone = edit_bones.new(bone_name)
    new_bone.head = head
    new_bone.tail = tail

    if bone_parent is not None and bone_parent in edit_bones:
        new_bone.parent = edit_bones[bone_parent]

    return new_bone


def get_all_bone_names(obj, mode: str = "DATA") -> list[str]:
    if obj is None or obj.type != "ARMATURE":
        return []

    if mode == "EDIT":
        ensure_edit_mode(obj)
        return [bone.name for bone in obj.data.edit_bones]

    if mode == "POSE":
        ensure_pose_mode(obj)
        return [bone.name for bone in obj.pose.bones]

    return [bone.name for bone in obj.data.bones]


# ============================================================
# Bone Conversion / Merge Helpers
# ============================================================

def convert_bone_head_tail(source_armature, target_armature, source_bone):
    source_matrix = source_armature.matrix_world
    target_matrix_inv = target_armature.matrix_world.inverted()

    head = target_matrix_inv @ (source_matrix @ source_bone.head_local)
    tail = target_matrix_inv @ (source_matrix @ source_bone.tail_local)

    return head, tail


def convert_bone_roll_axis(source_armature, target_armature, source_bone):
    source_matrix = source_armature.matrix_world.to_3x3()
    target_matrix_inv = target_armature.matrix_world.inverted().to_3x3()
    bone_matrix = source_bone.matrix_local.to_3x3()

    axis = (
        target_matrix_inv
        @ source_matrix
        @ bone_matrix
        @ Vector((0.0, 0.0, 1.0))
    )

    if axis.length == 0:
        return Vector((0.0, 0.0, 1.0))

    return axis.normalized()


def resolve_target_parent_name(context, source_bone_name: str):
    source_bone = context.source_armature.data.bones.get(source_bone_name)
    if source_bone is None or source_bone.parent is None:
        return None

    parent_name = source_bone.parent.name
    parent_mapping = context.source_to_target_map.get(parent_name)

    if parent_mapping is not None:
        return parent_mapping.get("merge_target")

    return parent_name


def ensure_target_bone_from_source(
    context,
    rigify_obj,
    source_bone_name: str,
    target_bone_name: str,
):
    existing = rigify_obj.data.bones.get(target_bone_name)
    if existing is not None:
        return target_bone_name

    source_bone = context.source_armature.data.bones.get(source_bone_name)
    if source_bone is None:
        return None

    make_object_active(rigify_obj)
    bpy.ops.object.mode_set(mode="EDIT")

    edit_bones = rigify_obj.data.edit_bones
    edit_bone = edit_bones.new(target_bone_name)

    head, tail = convert_bone_head_tail(
        context.source_armature,
        rigify_obj,
        source_bone,
    )

    edit_bone.head = head
    edit_bone.tail = tail

    if (edit_bone.tail - edit_bone.head).length == 0:
        edit_bone.tail = edit_bone.head + Vector((0.0, 0.05, 0.0))

    parent_name = resolve_target_parent_name(context, source_bone_name)
    if parent_name and parent_name in edit_bones:
        edit_bone.parent = edit_bones[parent_name]

    try:
        edit_bone.align_roll(
            convert_bone_roll_axis(
                context.source_armature,
                rigify_obj,
                source_bone,
            )
        )
    except RuntimeError:
        pass

    bpy.ops.object.mode_set(mode="POSE")

    pose_bone = rigify_obj.pose.bones.get(target_bone_name)
    if pose_bone is not None:
        pose_bone.bone.use_deform = True
        pose_bone.bone.inherit_scale = "NONE"

    assign_bone_to_layer_group(rigify_obj, target_bone_name, 27)

    bpy.ops.object.mode_set(mode="OBJECT")
    return target_bone_name


# ============================================================
# Basis-Klasse für Modi
# ============================================================

def collect_bound_meshes(armature_obj):
    meshes = []
    seen = set()

    def remember(mesh_obj):
        if mesh_obj is None or mesh_obj.type != "MESH":
            return
        if mesh_obj.name in seen:
            return

        seen.add(mesh_obj.name)
        meshes.append(mesh_obj)

    for child in armature_obj.children:
        if child.type == "MESH":
            remember(child)

    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue

        if obj.parent == armature_obj:
            remember(obj)
            continue

        for modifier in obj.modifiers:
            if modifier.type == "ARMATURE" and modifier.object == armature_obj:
                remember(obj)
                break

    return meshes

def collect_weighted_vertex_group_names(mesh_objects):
    weighted_group_names = set()

    for mesh_obj in mesh_objects:
        index_to_name = {
            vertex_group.index: vertex_group.name
            for vertex_group in mesh_obj.vertex_groups
        }

        for vertex in mesh_obj.data.vertices:
            for group in vertex.groups:
                group_name = index_to_name.get(group.group)
                if group_name:
                    weighted_group_names.add(group_name)

    return weighted_group_names

def is_generated_rigify_rig(armature_obj):
    if armature_obj is None or armature_obj.type != "ARMATURE":
        return False

    armature_data = getattr(armature_obj, "data", None)
    if armature_data is None:
        return False

    rig_id = armature_data.get("rig_id")
    if not isinstance(rig_id, str) or not rig_id:
        return False

    has_rig_ui_script = armature_obj.get("rig_ui") is not None
    has_rig_ui_panel = hasattr(bpy.types, f"VIEW3D_PT_rig_ui_{rig_id}")
    has_rig_layers_panel = hasattr(bpy.types, f"VIEW3D_PT_rig_layers_{rig_id}")

    return has_rig_ui_script or has_rig_ui_panel or has_rig_layers_panel


def get_generation_blocker_message(armature_obj):
    if is_generated_rigify_rig(armature_obj):
        return "nichts zu tun"

    return None
