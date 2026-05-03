from dataclasses import dataclass, field

from operatoren.bone_mapping import (
    build_extra_bone_data,
    build_standard_constraint_map,
    collect_extra_bones,
    derive_neck_data,
    derive_spine_data,
)
from operatoren.mesh_analyse import collect_bound_meshes
from operatoren.vertex_groups import collect_weighted_vertex_group_names


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
