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
