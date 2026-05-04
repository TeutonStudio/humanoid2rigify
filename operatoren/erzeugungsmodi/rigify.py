from ...__eigenschaften__ import Wirbelsäule
from ...operatoren.erzeugungsmodi.__methoden__ import get_generated_rigify_object

GENERIC_CIRCLE_WIDGET_VERTEX_COUNT = 32


class RigifyBauModus:
    def __init__(self, context):
        self.context = context

    def erzeuge(self) -> bool:
        raise NotImplementedError

    @property
    def operator(self):
        return self.context.operator

    @property
    def source_armature(self):
        return self.context.source_armature

    @property
    def params(self) -> dict:
        return self.context.params

    def report(self, status: set[str], text: str) -> None:
        self.operator.report(status, text)

    def erzeuge_rigify_rig(self):
        self.generiere_rigify_rig(
            self.source_armature,
            self.params,
        )

        return get_generated_rigify_object(self.source_armature)

    def generiere_rigify_rig(self, skeleton_model, parameters) -> None:
        """
        Hierhin gehört der Körper von any_rig_to_rigify_v2.the_script(...).

        Wichtig:
        - Nicht mehr any_rig_to_rigify_v2.the_script(...) aufrufen.
        - Den alten Inhalt direkt hier einfügen.
        - Hilfsfunktionen wie make_bone, get_all_bone_names,
          assign_bone_to_layer_group, set_visible_rig_layers usw.
          sind jetzt in dieser Datei vorhanden.
        """
        raise NotImplementedError(
            "Der alte the_script(...)-Körper muss nach generiere_rigify_rig(...) verschoben werden."
        )

    def uebernehme_custom_shapes(self, rigify_obj, target_name_key: str) -> int:
        if rigify_obj is None:
            return 0

        return self.inherit_missing_custom_shapes(
            rigify_obj,
            target_name_key,
        )

    def copy_bone_color(self, source_color, target_color) -> None:
        target_color.palette = source_color.palette

        for custom_field in ("normal", "select", "active"):
            color = getattr(source_color.custom, custom_field)
            setattr(target_color.custom, custom_field, color)

    def resolve_target_transform_bone(
        self,
        source_pose_bone,
        rigify_obj,
        target_name_key: str,
    ):
        transform_bone = getattr(source_pose_bone, "custom_shape_transform", None)
        if transform_bone is None:
            return None

        if transform_bone.name == Wirbelsäule.WURZEL:
            return rigify_obj.pose.bones.get(Wirbelsäule.WURZEL)

        transform_mapping = self.context.source_to_target_map.get(transform_bone.name)
        if transform_mapping is not None:
            target_name = transform_mapping.get(target_name_key)
            if target_name and rigify_obj.pose.bones.get(target_name) is not None:
                return rigify_obj.pose.bones[target_name]

            fallback_name = transform_mapping.get("constraint_target")
            if fallback_name and rigify_obj.pose.bones.get(fallback_name) is not None:
                return rigify_obj.pose.bones[fallback_name]

        return rigify_obj.pose.bones.get(transform_bone.name)

    def copy_custom_shape_settings(
        self,
        source_pose_bone,
        target_pose_bone,
        target_transform_bone,
    ) -> None:
        target_pose_bone.custom_shape = source_pose_bone.custom_shape
        target_pose_bone.custom_shape_translation = (
            source_pose_bone.custom_shape_translation.copy()
        )
        target_pose_bone.custom_shape_rotation_euler = (
            source_pose_bone.custom_shape_rotation_euler.copy()
        )
        target_pose_bone.custom_shape_scale_xyz = tuple(
            source_pose_bone.custom_shape_scale_xyz
        )
        target_pose_bone.use_custom_shape_bone_size = (
            source_pose_bone.use_custom_shape_bone_size
        )
        target_pose_bone.custom_shape_wire_width = (
            source_pose_bone.custom_shape_wire_width
        )
        target_pose_bone.custom_shape_transform = target_transform_bone

    def is_generic_circle_widget(self, widget_obj) -> bool:
        if widget_obj is None or getattr(widget_obj, "type", None) != "MESH":
            return False

        mesh = getattr(widget_obj, "data", None)
        if mesh is None or len(mesh.polygons) != 0:
            return False

        return (
            len(mesh.vertices) == GENERIC_CIRCLE_WIDGET_VERTEX_COUNT
            and len(mesh.edges) == GENERIC_CIRCLE_WIDGET_VERTEX_COUNT
        )

    def should_replace_custom_shape(
        self,
        source_pose_bone,
        target_pose_bone,
        mapping,
    ) -> bool:
        if source_pose_bone.custom_shape is None:
            return False

        if not mapping.get("is_standard", True) and source_pose_bone.bone.hide:
            return False

        if target_pose_bone.custom_shape is None:
            return True

        if target_pose_bone.name == Wirbelsäule.WURZEL:
            return True

        if not mapping.get("is_standard", True):
            return True

        return self.is_generic_circle_widget(target_pose_bone.custom_shape)

    def iter_shape_mappings(self, rigify_obj, target_name_key: str):
        yielded_pairs = set()

        for source_bone_name, mapping in self.context.source_to_target_map.items():
            target_bone_name = mapping.get(target_name_key)
            if not target_bone_name:
                continue

            pair_key = (source_bone_name, target_bone_name)
            if pair_key in yielded_pairs:
                continue

            yielded_pairs.add(pair_key)

            yield source_bone_name, target_bone_name, mapping

        source_root = self.source_armature.pose.bones.get(Wirbelsäule.WURZEL)
        target_root = rigify_obj.pose.bones.get(Wirbelsäule.WURZEL)

        if source_root is None or target_root is None:
            return

        pair_key = (Wirbelsäule.WURZEL, Wirbelsäule.WURZEL)
        if pair_key in yielded_pairs:
            return

        yield Wirbelsäule.WURZEL, Wirbelsäule.WURZEL, {
            "source_bone": Wirbelsäule.WURZEL,
            "is_standard": False,
        }

    def inherit_missing_custom_shapes(self, rigify_obj, target_name_key: str) -> int:
        copied_count = 0

        for source_bone_name, target_bone_name, mapping in self.iter_shape_mappings(
            rigify_obj,
            target_name_key,
        ):
            source_pose_bone = self.source_armature.pose.bones.get(source_bone_name)
            target_pose_bone = rigify_obj.pose.bones.get(target_bone_name)

            if source_pose_bone is None or target_pose_bone is None:
                continue

            if not self.should_replace_custom_shape(
                source_pose_bone,
                target_pose_bone,
                mapping,
            ):
                continue

            target_transform_bone = self.resolve_target_transform_bone(
                source_pose_bone,
                rigify_obj,
                target_name_key,
            )

            self.copy_custom_shape_settings(
                source_pose_bone,
                target_pose_bone,
                target_transform_bone,
            )

            self.copy_bone_color(source_pose_bone.color, target_pose_bone.color)
            self.copy_bone_color(source_pose_bone.bone.color, target_pose_bone.bone.color)

            copied_count += 1

        return copied_count
