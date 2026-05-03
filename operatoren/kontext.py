from dataclasses import dataclass, field

from operatoren.mesh_analyse import collect_bound_meshes


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


def create_generation_context(operator, armature_obj, params):
    return GenerationContext(
        operator=operator,
        source_armature=armature_obj,
        params=params,
        generation_mode=params.get("generation_mode", "CONSTRAINT_NEW_RIGIFY"),
        bound_meshes=collect_bound_meshes(armature_obj),
    )
