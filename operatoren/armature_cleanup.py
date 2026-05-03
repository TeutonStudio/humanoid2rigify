def collect_bone_ancestors(armature_obj, bone_names):
    ancestors = set()

    for bone_name in bone_names:
        bone = armature_obj.data.bones.get(bone_name)
        while bone is not None:
            ancestors.add(bone.name)
            bone = bone.parent

    return ancestors


def collect_constraint_subtargets(armature_obj, bone_names):
    subtargets = set()

    for bone_name in bone_names:
        pose_bone = armature_obj.pose.bones.get(bone_name)
        if pose_bone is None:
            continue

        for constraint in pose_bone.constraints:
            if getattr(constraint, "target", None) != armature_obj:
                continue

            subtarget = getattr(constraint, "subtarget", "")
            if subtarget:
                subtargets.add(subtarget)

    return subtargets


def compute_deform_mode_keep_bones(context):
    weighted_deform_bones = set(context.used_deform_bones)
    if not weighted_deform_bones:
        return set()

    keep_bones = set(weighted_deform_bones)
    keep_bones.update(collect_bone_ancestors(context.source_armature, weighted_deform_bones))

    constraint_helpers = collect_constraint_subtargets(
        context.source_armature,
        keep_bones,
    )
    keep_bones.update(constraint_helpers)
    keep_bones.update(collect_bone_ancestors(context.source_armature, constraint_helpers))

    return keep_bones

