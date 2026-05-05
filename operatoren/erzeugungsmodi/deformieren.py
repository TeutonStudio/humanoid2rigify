from __future__ import annotations

import bpy

from .__methoden__ import make_armature_active
from ..rigify import RigifyBauModus


class DeformRigErhalter(RigifyBauModus):
    def erzeuge(self) -> bool:
        if not self.context.bound_meshes:
            self.report(
                {"ERROR"},
                "Keine Meshes mit Armature-Modifier für das Quellrig gefunden",
            )
            return False

        if not self.context.used_deform_bones:
            self.report(
                {"ERROR"},
                "Keine tatsächlich benutzten Deformationsknochen gefunden",
            )
            return False

        rigify_obj = self.erzeuge_rigify_rig()

        copied_shapes = self.uebernehme_custom_shapes(
            rigify_obj,
            "constraint_target",
        )

        make_armature_active(self.source_armature)

        keep_bones = self.compute_deform_mode_keep_bones()
        if not keep_bones:
            self.report(
                {"ERROR"},
                "Das Deformationsrig konnte nicht reduziert werden",
            )
            return False

        removed_bones = self.delete_non_keep_bones(keep_bones)

        bpy.ops.object.mode_set(mode="OBJECT")

        self.normalize_deform_flags(
            set(self.context.used_deform_bones),
        )

        backup_name = (
            self.context.backup_collection.name
            if self.context.backup_collection is not None
            else "kein Backup"
        )

        self.report(
            {"INFO"},
            (
                f"Backup erstellt: {backup_name}. "
                f"Deformationsrig reduziert, {len(removed_bones)} Knochen entfernt. "
                f"{copied_shapes} Custom Shapes übernommen oder ersetzt."
            ),
        )

        return True

    def delete_non_keep_bones(self, keep_bones: set[str]) -> list[str]:
        bpy.ops.object.mode_set(mode="EDIT")

        edit_bones = self.source_armature.data.edit_bones

        removable_bones = [
            bone.name
            for bone in edit_bones
            if bone.name not in keep_bones
        ]

        for bone_name in removable_bones:
            edit_bone = edit_bones.get(bone_name)
            if edit_bone is not None:
                edit_bones.remove(edit_bone)

        return removable_bones

    def normalize_deform_flags(self, weighted_deform_bones: set[str]) -> None:
        for bone in self.source_armature.data.bones:
            bone.use_deform = bone.name in weighted_deform_bones

    def collect_bone_ancestors(self, bone_names: set[str]) -> set[str]:
        ancestors = set()

        for bone_name in bone_names:
            bone = self.source_armature.data.bones.get(bone_name)

            while bone is not None:
                ancestors.add(bone.name)
                bone = bone.parent

        return ancestors

    def collect_constraint_subtargets(self, bone_names: set[str]) -> set[str]:
        subtargets = set()

        for bone_name in bone_names:
            pose_bone = self.source_armature.pose.bones.get(bone_name)
            if pose_bone is None:
                continue

            for constraint in pose_bone.constraints:
                if getattr(constraint, "target", None) != self.source_armature:
                    continue

                subtarget = getattr(constraint, "subtarget", "")
                if subtarget:
                    subtargets.add(subtarget)

        return subtargets

    def compute_deform_mode_keep_bones(self) -> set[str]:
        weighted_deform_bones = set(self.context.used_deform_bones)
        if not weighted_deform_bones:
            return set()

        keep_bones = set(weighted_deform_bones)
        keep_bones.update(
            self.collect_bone_ancestors(weighted_deform_bones),
        )

        constraint_helpers = self.collect_constraint_subtargets(keep_bones)

        keep_bones.update(constraint_helpers)
        keep_bones.update(
            self.collect_bone_ancestors(constraint_helpers),
        )

        return keep_bones