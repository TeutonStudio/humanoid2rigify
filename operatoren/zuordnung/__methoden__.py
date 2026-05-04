from typing import Any

from bpy.types import Scene

from ...__methoden__ import clear_merge_whitelist_groups, add_merge_whitelist_group, reset_merge_whitelist_groups


def load_merge_whitelist_groups_from_data(
    scene: Scene | None,
    data: dict[str, Any],
) -> None:
    if scene is None:
        return

    clear_merge_whitelist_groups(scene)

    group_data = data.get("merge_extra_bone_groups")

    if isinstance(group_data, list):
        for raw_group in group_data:
            if not isinstance(raw_group, dict):
                continue

            name = str(raw_group.get("name") or "Additional")
            entries = raw_group.get("entries", [])

            if not isinstance(entries, list):
                entries = []

            add_merge_whitelist_group(
                scene,
                name=name,
                entries=[
                    str(value)
                    for value in entries
                    if value
                ],
                expanded=True,
            )

        if len(scene.merge_extra_bone_groups) == 0:
            reset_merge_whitelist_groups(scene)

        return

    # Fallback für alte Presets
    whitelist_values = data.get("merge_extra_bone_whitelist")

    if isinstance(whitelist_values, list):
        add_merge_whitelist_group(
            scene,
            name="Additional",
            entries=[
                str(value)
                for value in whitelist_values
                if value
            ],
            expanded=True,
        )
        return

    reset_merge_whitelist_groups(scene)