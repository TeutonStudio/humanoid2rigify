from typing import Any

from ...__methoden__ import get_current_bone_names, build_merge_extra_bone_groups
from ..__operator__ import Operator
from ...__eigenschaften__ import KNOCHEN
from bpy.types import Context


def build_params(scene) -> dict[str,str | list[str]]:
    params = {
        str(name): getattr(scene, name)
        for name in KNOCHEN
    }
    merge_groups = build_merge_extra_bone_groups(scene)

    params.update({
        "fingers_bool_r": scene.fingers_bool_r,
        "fingers_bool_l": scene.fingers_bool_l,
        "copy_loc_constr": scene.copy_loc_constr,
        "generation_mode": scene.generation_mode,

        # Neu:
        "merge_extra_bone_groups": merge_groups,

        # Kompatibilität:
        "merge_extra_bone_whitelist": [
            entry
            for group in merge_groups
            for entry in group["entries"]
        ],
    })

    return params

def bone_item_list(self: Operator, context: Context) -> list[tuple[str, str, str]]:
    bone_names = get_current_bone_names(context)

    return [
        (bone_name, bone_name, bone_name)
        for bone_name in bone_names
    ]

#   def build_merge_extra_bone_groups(scene) -> list[dict]:
#       groups = []
#
#       for group in scene.merge_extra_bone_groups:
#           entries = [
#               item.value
#               for item in group.entries
#               if item.value
#           ]
#
#           if not entries:
#               continue
#
#           groups.append({
#               "name": group.name or "Additional",
#               "entries": entries,
#           })
#
#       return groups