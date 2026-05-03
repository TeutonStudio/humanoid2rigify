import bpy


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
