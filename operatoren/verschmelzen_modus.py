import bpy

from . import any_rig_to_rigify_v2
from .backup import create_backups
from .rigify_access import (
    ensure_target_bone_from_source,
    get_generated_rigify_object,
    make_object_active,
)


def ensure_required_merge_bones(context, rigify_obj):
    ensured_targets = {}

    for source_bone_name, mapping in context.source_to_target_map.items():
        if source_bone_name not in context.weighted_vertex_groups:
            continue

        target_bone_name = mapping.get("merge_target")
        if not target_bone_name:
            continue

        if rigify_obj.data.bones.get(target_bone_name) is None:
            ensured_name = ensure_target_bone_from_source(
                context,
                rigify_obj,
                source_bone_name,
                target_bone_name,
            )
            if ensured_name is not None:
                ensured_targets[source_bone_name] = ensured_name
        else:
            ensured_targets[source_bone_name] = target_bone_name

    return ensured_targets


def find_group_weight(vertex, group_index):
    for assignment in vertex.groups:
        if assignment.group == group_index:
            return assignment.weight
    return None


def move_vertex_group_weights(mesh_obj, source_group_name, target_group_name):
    if source_group_name == target_group_name:
        return False

    source_group = mesh_obj.vertex_groups.get(source_group_name)
    if source_group is None:
        return False

    target_group = mesh_obj.vertex_groups.get(target_group_name)
    if target_group is None:
        source_group.name = target_group_name
        return True

    target_index = target_group.index
    source_index = source_group.index
    for vertex in mesh_obj.data.vertices:
        weight = find_group_weight(vertex, source_index)
        if weight is None:
            continue

        existing_weight = find_group_weight(vertex, target_index)
        if existing_weight is None or weight > existing_weight:
            target_group.add([vertex.index], weight, 'REPLACE')

    mesh_obj.vertex_groups.remove(source_group)
    return True


def migrate_vertex_groups(context, rigify_obj):
    migrated_groups = 0
    for mesh_obj in context.bound_meshes:
        for source_bone_name, mapping in context.source_to_target_map.items():
            if source_bone_name not in context.weighted_vertex_groups:
                continue

            target_bone_name = mapping.get("merge_target")
            if not target_bone_name:
                continue

            if rigify_obj.data.bones.get(target_bone_name) is None:
                continue

            if move_vertex_group_weights(mesh_obj, source_bone_name, target_bone_name):
                migrated_groups += 1

    return migrated_groups


def rebind_meshes_to_rigify(context, rigify_obj):
    rebound_meshes = 0

    for mesh_obj in context.bound_meshes:
        if mesh_obj.parent == context.source_armature:
            mesh_obj.parent = rigify_obj
            if mesh_obj.parent_type == 'BONE':
                mapping = context.source_to_target_map.get(mesh_obj.parent_bone)
                if mapping is not None:
                    mesh_obj.parent_bone = mapping.get("merge_target", mesh_obj.parent_bone)

        updated = False
        for modifier in mesh_obj.modifiers:
            if modifier.type == "ARMATURE" and modifier.object == context.source_armature:
                modifier.object = rigify_obj
                updated = True

        if updated:
            rebound_meshes += 1

    return rebound_meshes


def delete_source_armature(source_armature):
    make_object_active(source_armature)
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.data.objects.remove(source_armature, do_unlink=True)


def run_merge_mode(context):
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

    rigify_obj = get_generated_rigify_object(context.source_armature)
    if rigify_obj is None:
        context.operator.report(
            {"ERROR"},
            "Generiertes Rigify-Rig konnte nicht gefunden werden",
        )
        return False

    ensured_targets = ensure_required_merge_bones(context, rigify_obj)
    migrated_groups = migrate_vertex_groups(context, rigify_obj)
    rebound_meshes = rebind_meshes_to_rigify(context, rigify_obj)

    delete_source_armature(context.source_armature)
    make_object_active(rigify_obj)
    bpy.ops.object.mode_set(mode="POSE")

    context.operator.report(
        {"INFO"},
        (
            f"Backup erstellt: {context.backup_collection.name}. "
            f"Verschmolzen, {len(ensured_targets)} Zielknochen gesichert, "
            f"{migrated_groups} Vertex-Groups migriert, "
            f"{rebound_meshes} Meshes umgehaengt."
        ),
    )
    return True
