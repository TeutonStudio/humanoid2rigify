import time

import bpy


BACKUP_ROOT_NAME = "Any Rig to Rigify Backups"


def ensure_collection_link(parent_collection, child_collection):
    child_names = {collection.name for collection in parent_collection.children}
    if child_collection.name not in child_names:
        parent_collection.children.link(child_collection)


def ensure_backup_root(scene):
    backup_root = bpy.data.collections.get(BACKUP_ROOT_NAME)
    if backup_root is None:
        backup_root = bpy.data.collections.new(BACKUP_ROOT_NAME)

    ensure_collection_link(scene.collection, backup_root)
    return backup_root


def make_unique_collection_name(base_name):
    if bpy.data.collections.get(base_name) is None:
        return base_name

    cnt = 1
    while bpy.data.collections.get(f"{base_name}_{cnt}") is not None:
        cnt += 1

    return f"{base_name}_{cnt}"


def duplicate_object_with_data(source_obj, name_suffix):
    backup_obj = source_obj.copy()
    if source_obj.data is not None:
        backup_obj.data = source_obj.data.copy()

    backup_obj.name = f"{source_obj.name}{name_suffix}"

    if source_obj.animation_data is not None:
        backup_obj.animation_data_create()
        if source_obj.animation_data.action is not None:
            backup_obj.animation_data.action = source_obj.animation_data.action.copy()

    return backup_obj


def rewire_mesh_backup(backup_mesh, source_mesh, source_armature, backup_armature):
    if source_mesh.parent == source_armature:
        backup_mesh.parent = backup_armature
        backup_mesh.parent_type = source_mesh.parent_type
        backup_mesh.parent_bone = source_mesh.parent_bone

    for modifier in backup_mesh.modifiers:
        if modifier.type == "ARMATURE" and modifier.object == source_armature:
            modifier.object = backup_armature


def create_backups(context):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_root = ensure_backup_root(bpy.context.scene)
    collection_name = make_unique_collection_name(
        f"{context.source_armature.name}_backup_{timestamp}"
    )
    backup_collection = bpy.data.collections.new(collection_name)
    ensure_collection_link(backup_root, backup_collection)

    backup_armature = duplicate_object_with_data(context.source_armature, "_backup")
    backup_collection.objects.link(backup_armature)

    backup_meshes = []
    for mesh_obj in context.bound_meshes:
        backup_mesh = duplicate_object_with_data(mesh_obj, "_backup")
        rewire_mesh_backup(
            backup_mesh,
            mesh_obj,
            context.source_armature,
            backup_armature,
        )
        backup_collection.objects.link(backup_mesh)
        backup_meshes.append(backup_mesh)

    context.backup_collection = backup_collection
    context.backup_armature = backup_armature
    context.backup_meshes = backup_meshes

    return context
