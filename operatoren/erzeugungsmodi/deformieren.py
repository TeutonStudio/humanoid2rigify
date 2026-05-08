from __future__ import annotations

import re

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

        self.report(
            {"INFO"},
            f"Behalte {len(keep_bones)} gewichtete Deform-Knochen: {sorted(keep_bones)}",
        )
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

        for edit_bone in list(edit_bones):
            if edit_bone.name not in keep_bones:
                continue

            if edit_bone.parent is not None and edit_bone.parent.name not in keep_bones:
                edit_bone.use_connect = False
                edit_bone.parent = None

        removable_bones = [
            edit_bone.name
            for edit_bone in edit_bones
            if edit_bone.name not in keep_bones
        ]

        for bone_name in removable_bones:
            edit_bone = edit_bones.get(bone_name)
            if edit_bone is not None:
                edit_bones.remove(edit_bone)

        return removable_bones

    # def delete_non_keep_bones(self, keep_bones: set[str]) -> list[str]:
    #     bpy.ops.object.mode_set(mode="EDIT")
    #
    #     edit_bones = self.source_armature.data.edit_bones
    #
    #     removable_bones = [
    #         bone.name
    #         for bone in edit_bones
    #         if bone.name not in keep_bones
    #     ]
    #
    #     for bone_name in removable_bones:
    #         edit_bone = edit_bones.get(bone_name)
    #         if edit_bone is not None:
    #             edit_bones.remove(edit_bone)
    #
    #     return removable_bones

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

    def collect_whitelist_keep_bones(self) -> set[str]:
        return {
            bone_name
            for bone_name, data in self.context.extra_bone_data.items()
            if data.get("needs_new_merge_bone", False)
        }

    def compute_deform_mode_keep_bones(self) -> set[str]:
        weighted_deform_bones = set(self.context.used_deform_bones)
        whitelist_bones = self.collect_whitelist_keep_bones()
        driver_used_bones = self.collect_driver_used_bones()

        keep_bones = set()
        keep_bones.update(weighted_deform_bones)
        #   keep_bones.update(whitelist_bones)
        #   keep_bones.update(driver_used_bones)
        return keep_bones

    # def compute_deform_mode_keep_bones(self) -> set[str]:
    #     weighted_deform_bones = set(self.context.used_deform_bones)
    #     if not weighted_deform_bones:
    #         return set()
    #
    #     keep_bones = set(weighted_deform_bones)
    #     keep_bones.update(
    #         self.collect_bone_ancestors(weighted_deform_bones),
    #     )
    #
    #     constraint_helpers = self.collect_constraint_subtargets(keep_bones)
    #
    #     keep_bones.update(constraint_helpers)
    #     keep_bones.update(
    #         self.collect_bone_ancestors(constraint_helpers),
    #     )
    #
    #     return keep_bones
    def collect_bone_names_from_driver_path(self, data_path: str) -> set[str]:
        if not data_path:
            return set()

        bone_names: set[str] = set()

        # Findet:
        # pose.bones["BoneName"]
        # bones["BoneName"]
        # data.bones["BoneName"]
        pattern = re.compile(r'(?:pose\.)?bones\["((?:[^"\\]|\\.)*)"\]')

        for match in pattern.finditer(data_path):
            raw_name = match.group(1)

            # Blender escaped in RNA-Pfaden z.B. \" und \\.
            bone_name = raw_name.replace(r"\"", '"').replace(r"\\", "\\")

            if bone_name in self.source_armature.data.bones:
                bone_names.add(bone_name)

        return bone_names

    def collect_driver_used_bones_from_fcurve(self, fcurve) -> set[str]:
        used_bones: set[str] = set()

        # 1. Der Knochen, AUF dem der Driver liegt.
        # Beispiel:
        # pose.bones["Jaw"].location
        # pose.bones["Tail"].constraints["Copy"].influence
        used_bones.update(
            self.collect_bone_names_from_driver_path(
                getattr(fcurve, "data_path", ""),
            )
        )

        driver = getattr(fcurve, "driver", None)
        if driver is None:
            return used_bones

        # 2. Knochen, die in Driver-Variablen benutzt werden.
        for variable in driver.variables:
            for target in variable.targets:
                target_id = getattr(target, "id", None)

                # Transform-Channel-Driver benutzen oft bone_target.
                bone_target = getattr(target, "bone_target", "")
                if (
                        target_id == self.source_armature
                        and bone_target
                        and bone_target in self.source_armature.data.bones
                ):
                    used_bones.add(bone_target)

                # SINGLE_PROP oder andere Driver-Ziele können data_path benutzen.
                target_data_path = getattr(target, "data_path", "")
                if target_id in {self.source_armature, self.source_armature.data}:
                    used_bones.update(
                        self.collect_bone_names_from_driver_path(target_data_path)
                    )

        return used_bones

    def iter_driver_fcurves_for_source_armature(self):
        # Driver direkt auf dem Armature-Objekt.
        animation_data = getattr(self.source_armature, "animation_data", None)
        if animation_data is not None:
            for fcurve in animation_data.drivers:
                yield fcurve

        # Driver auf den Armature-Daten.
        armature_data = getattr(self.source_armature, "data", None)
        data_animation_data = getattr(armature_data, "animation_data", None)
        if data_animation_data is not None:
            for fcurve in data_animation_data.drivers:
                yield fcurve

    def collect_driver_used_bones(self) -> set[str]:
        driver_used_bones: set[str] = set()

        for fcurve in self.iter_driver_fcurves_for_source_armature():
            driver_used_bones.update(
                self.collect_driver_used_bones_from_fcurve(fcurve)
            )

        return driver_used_bones