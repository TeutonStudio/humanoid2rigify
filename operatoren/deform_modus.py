import bpy

from operatoren import any_rig_to_rigify_v2
from operatoren.armature_cleanup import compute_deform_mode_keep_bones
from operatoren.backup import create_backups


def make_armature_active(armature_obj):
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    armature_obj.select_set(True)
    bpy.context.view_layer.objects.active = armature_obj


def delete_non_keep_bones(armature_obj, keep_bones):
    bpy.ops.object.mode_set(mode="EDIT")
    edit_bones = armature_obj.data.edit_bones
    removable_bones = [
        bone.name for bone in edit_bones
        if bone.name not in keep_bones
    ]

    for bone_name in removable_bones:
        edit_bone = edit_bones.get(bone_name)
        if edit_bone is not None:
            edit_bones.remove(edit_bone)

    return removable_bones


def normalize_deform_flags(armature_obj, weighted_deform_bones):
    for bone in armature_obj.data.bones:
        bone.use_deform = bone.name in weighted_deform_bones


def run_deform_mode(context):
    if not context.bound_meshes:
        context.operator.report(
            {"ERROR"},
            "Keine Meshes mit Armature-Modifier fuer das Quellrig gefunden",
        )
        return False

    if not context.used_deform_bones:
        context.operator.report(
            {"ERROR"},
            "Keine tatsaechlich benutzten Deformationsknochen gefunden",
        )
        return False

    create_backups(context)
    any_rig_to_rigify_v2.the_script(context.source_armature, context.params)

    make_armature_active(context.source_armature)
    keep_bones = compute_deform_mode_keep_bones(context)
    if not keep_bones:
        context.operator.report(
            {"ERROR"},
            "Das Deformationsrig konnte nicht reduziert werden",
        )
        return False

    removed_bones = delete_non_keep_bones(context.source_armature, keep_bones)
    bpy.ops.object.mode_set(mode="OBJECT")
    normalize_deform_flags(context.source_armature, set(context.used_deform_bones))

    context.operator.report(
        {"INFO"},
        (
            f"Backup erstellt: {context.backup_collection.name}. "
            f"Deformationsrig reduziert, {len(removed_bones)} Knochen entfernt."
        ),
    )
    return True

