import bpy
from mathutils import Vector

from operatoren.any_rig_to_rigify_v2 import assign_bone_to_layer_group


def get_generated_rigify_name(source_armature):
    return f"{source_armature.name}_rigify"


def get_generated_rigify_object(source_armature):
    return bpy.data.objects.get(get_generated_rigify_name(source_armature))


def make_object_active(obj):
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


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
    axis = target_matrix_inv @ source_matrix @ bone_matrix @ Vector((0.0, 0.0, 1.0))
    if axis.length == 0:
        return Vector((0.0, 0.0, 1.0))
    return axis.normalized()


def resolve_target_parent_name(context, source_bone_name):
    source_bone = context.source_armature.data.bones.get(source_bone_name)
    if source_bone is None or source_bone.parent is None:
        return None

    parent_name = source_bone.parent.name
    parent_mapping = context.source_to_target_map.get(parent_name)
    if parent_mapping is not None:
        return parent_mapping.get("merge_target")

    return parent_name


def ensure_target_bone_from_source(context, rigify_obj, source_bone_name, target_bone_name):
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

    head, tail = convert_bone_head_tail(context.source_armature, rigify_obj, source_bone)
    edit_bone.head = head
    edit_bone.tail = tail

    if (edit_bone.tail - edit_bone.head).length == 0:
        edit_bone.tail = edit_bone.head + Vector((0.0, 0.05, 0.0))

    parent_name = resolve_target_parent_name(context, source_bone_name)
    if parent_name and parent_name in edit_bones:
        edit_bone.parent = edit_bones[parent_name]

    try:
        edit_bone.align_roll(
            convert_bone_roll_axis(context.source_armature, rigify_obj, source_bone)
        )
    except RuntimeError:
        pass

    bpy.ops.object.mode_set(mode="POSE")
    pose_bone = rigify_obj.pose.bones.get(target_bone_name)
    if pose_bone is not None:
        pose_bone.bone.use_deform = True
        pose_bone.bone.inherit_scale = 'NONE'

    assign_bone_to_layer_group(rigify_obj, target_bone_name, 27)
    bpy.ops.object.mode_set(mode="OBJECT")
    return target_bone_name

