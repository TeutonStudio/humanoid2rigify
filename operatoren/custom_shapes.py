def copy_bone_color(source_color, target_color):
    target_color.palette = source_color.palette
    for custom_field in ("normal", "select", "active"):
        color = getattr(source_color.custom, custom_field)
        setattr(target_color.custom, custom_field, color)


def resolve_target_transform_bone(context, source_pose_bone, rigify_obj, target_name_key):
    transform_bone = getattr(source_pose_bone, "custom_shape_transform", None)
    if transform_bone is None:
        return None

    transform_mapping = context.source_to_target_map.get(transform_bone.name)
    if transform_mapping is not None:
        target_name = transform_mapping.get(target_name_key)
        if target_name and rigify_obj.pose.bones.get(target_name) is not None:
            return rigify_obj.pose.bones[target_name]

        fallback_name = transform_mapping.get("constraint_target")
        if fallback_name and rigify_obj.pose.bones.get(fallback_name) is not None:
            return rigify_obj.pose.bones[fallback_name]

    return rigify_obj.pose.bones.get(transform_bone.name)


def copy_custom_shape_settings(source_pose_bone, target_pose_bone, target_transform_bone):
    target_pose_bone.custom_shape = source_pose_bone.custom_shape
    target_pose_bone.custom_shape_translation = source_pose_bone.custom_shape_translation.copy()
    target_pose_bone.custom_shape_rotation_euler = source_pose_bone.custom_shape_rotation_euler.copy()
    target_pose_bone.custom_shape_scale_xyz = tuple(source_pose_bone.custom_shape_scale_xyz)
    target_pose_bone.use_custom_shape_bone_size = source_pose_bone.use_custom_shape_bone_size
    target_pose_bone.custom_shape_wire_width = source_pose_bone.custom_shape_wire_width
    target_pose_bone.custom_shape_transform = target_transform_bone


def inherit_missing_custom_shapes(context, rigify_obj, target_name_key):
    copied_count = 0

    for source_bone_name, mapping in context.source_to_target_map.items():
        target_bone_name = mapping.get(target_name_key)
        if not target_bone_name:
            continue

        source_pose_bone = context.source_armature.pose.bones.get(source_bone_name)
        target_pose_bone = rigify_obj.pose.bones.get(target_bone_name)
        if source_pose_bone is None or target_pose_bone is None:
            continue

        if target_pose_bone.custom_shape is not None or source_pose_bone.custom_shape is None:
            continue

        target_transform_bone = resolve_target_transform_bone(
            context,
            source_pose_bone,
            rigify_obj,
            target_name_key,
        )
        copy_custom_shape_settings(
            source_pose_bone,
            target_pose_bone,
            target_transform_bone,
        )
        copy_bone_color(source_pose_bone.color, target_pose_bone.color)
        copy_bone_color(source_pose_bone.bone.color, target_pose_bone.bone.color)
        copied_count += 1

    return copied_count
