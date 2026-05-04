from typing import Any

from ...__methoden__ import get_current_bone_names
from ..__operator__ import Operator
from ...__eigenschaften__ import KNOCHEN
from bpy.types import Context


def build_params(scene) -> dict[str,str | list[str]]:
    params = {
        str(name): getattr(scene, name)
        for name in KNOCHEN
    }

    params.update({
        "fingers_bool_r": scene.fingers_bool_r,
        "fingers_bool_l": scene.fingers_bool_l,
        "copy_loc_constr": scene.copy_loc_constr,
        "generation_mode": scene.generation_mode,
        "merge_extra_bone_whitelist": [
            item.value
            for item in scene.merge_extra_bone_whitelist
            if item.value
        ],
    })

    return params

def bone_item_list(self: Operator, context: Context) -> list[tuple[str, str, str]]:
    bone_names = get_current_bone_names(context)

    return [
        (bone_name, bone_name, bone_name)
        for bone_name in bone_names
    ]
