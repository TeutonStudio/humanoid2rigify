import bpy
from mathutils import Vector

from .__methoden__ import ensure_rigify_enabled, make_object_active, ensure_mode, make_bone, get_all_bone_names, \
    average_vectors, assign_bone_to_layer_group, initialisiere_standard_bone_collections, build_extra_group_ui_rows, \
    sanitize_extra_group_name, assign_bone_to_extra_group_collection, set_rigify_layer_param, \
    apply_extra_group_collections, repariere_standard_control_collections, normalisiere_rigify_sichtbarkeit, \
    normalisiere_rigify_standardfarben, set_visible_rig_layers, get_rotation_diff, create_constraint, \
    erhalte_generiertes_rigify_rig, get_generated_rigify_object, copy_edit_bone_roll_from_source, average_bone_points, \
    should_replace_custom_shape, copy_custom_shape_settings, copy_pose_transform, copy_bone_color, iter_shape_mappings, \
    resolve_target_transform_bone, setze_objekt_im_vordergrund
from .kontext import GenerationContext, DEFAULT_VISIBLE_RIG_LAYER_INDICES
from .skelett import Skelett


class RigifyBauModus:
    def __init__(self, context: GenerationContext):
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

        rigify_obj = get_generated_rigify_object(self.source_armature)
        setze_objekt_im_vordergrund(rigify_obj)
        repariere_standard_control_collections(rigify_obj)
        normalisiere_rigify_sichtbarkeit(rigify_obj)
        normalisiere_rigify_standardfarben(rigify_obj)

        return rigify_obj

    def generiere_rigify_rig(self, skeleton_model, parameters) -> None:
        skelett = Skelett(parameters,skeleton_model)

        ensure_rigify_enabled()
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)

        external_obj = skeleton_model
        external_name = external_obj.name
        make_object_active(external_obj)

        target_rig_name = f"{external_name}_rigify"
        existing_rig = bpy.data.objects.get(target_rig_name)

        if existing_rig is not None:
            bpy.data.objects.remove(existing_rig, do_unlink=True)

        derived_data = getattr(self.context, "derived_bones", {}) or {}
        spine_data = derived_data.get("spines", {})
        all_spines = list(spine_data.get("all_spines", []))

        if not all_spines:
            all_spines = [skelett.first_spine]
            current = external_obj.data.bones.get(skelett.last_spine)

            while current is not None:
                all_spines.append(current.name)

                if current.name == skelett.first_spine:
                    break

                current = current.parent

            all_spines = list(reversed(list(dict.fromkeys(all_spines))))

        if skelett.first_spine not in all_spines:
            all_spines.insert(0,skelett.first_spine)

        if skelett.last_spine not in all_spines:
            all_spines.append(skelett.last_spine)

        second_spine = spine_data.get("second_spine") or (all_spines[1] if len(all_spines) > 1 else skelett.first_spine)
        less_spine_bones = len(all_spines) <= 2

        neck_data = derived_data.get("necks", {})
        all_necks = list(neck_data.get("all_necks", []))

        if not all_necks and skelett.first_neck:
            all_necks = [skelett.first_neck]

        if all_necks:
            skelett.first_neck = all_necks[0]
            skelett.last_neck = all_necks[-1]

        spine_parenting = {}
        all_spines_set = set(all_spines)

        for spine_name in all_spines:
            source_bone = external_obj.data.bones.get(spine_name)

            if source_bone is None:
                continue

            for child in source_bone.children:
                if child.name in all_spines_set:
                    spine_parenting[child.name] = [spine_name, True]

        neck_parenting = {}
        all_necks_set = set(all_necks)

        for neck_name in all_necks:
            source_bone = external_obj.data.bones.get(neck_name)

            if source_bone is None:
                continue

            for child in source_bone.children:
                if child.name in all_necks_set:
                    neck_parenting[child.name] = [neck_name, True]

        # ------------------------------------------------------------
        # Hilfsknochen im Originalrig
        # ------------------------------------------------------------

        ensure_mode(external_obj, "EDIT")
        first_spine_edit = external_obj.data.edit_bones[skelett.first_spine]
        second_spine_edit = external_obj.data.edit_bones.get(second_spine) or first_spine_edit

        make_bone(external_obj, "skeleton:TransformationTarget")

        torso_start = first_spine_edit.head.copy()
        torso_end = second_spine_edit.head.copy()

        if torso_start == torso_end:
            torso_end = second_spine_edit.tail.copy()

        make_bone(
            external_obj,
            "skeleton:torso_bone",
            skelett.first_spine,
            (torso_start + torso_end) / 2.0,
            second_spine_edit.tail.copy(),
        )

        if skelett.copy_loc_constr:
            for edit_bone in external_obj.data.edit_bones:
                edit_bone.inherit_scale = "NONE"

        # ------------------------------------------------------------
        # Metarig erzeugen
        # ------------------------------------------------------------

        ensure_mode(external_obj, "OBJECT")
        bpy.ops.object.armature_human_metarig_add()

        metarig_obj = bpy.context.active_object
        metarig_obj.name = f"{external_name}_metarig"
        metarig_obj.data.name = f"{external_name}_metarig_data"

        ensure_mode(metarig_obj, "EDIT")

        for edit_bone in list(metarig_obj.data.edit_bones):
            metarig_obj.data.edit_bones.remove(edit_bone)

        whitelisted_extra_bones = {
            bone_name
            for bone_name, data in self.context.extra_bone_data.items()
            if data.get("needs_new_merge_bone", False)
        }

        standard_source_bones = {
            value
            for value in parameters.values()
            if isinstance(value, str) and value
        }
        standard_source_bones.update(all_spines)
        standard_source_bones.update(all_necks)

        generated_helper_bones = {
            "heel_l",
            "heel_r",
            "new_torso",
            "skeleton:TransformationTarget",
            "skeleton:torso_bone",
        }

        allowed_metarig_bones = standard_source_bones | whitelisted_extra_bones | generated_helper_bones

        for bone_name in get_all_bone_names(external_obj, "DATA"):
            if bone_name in skelett.excluded_bones_to_create or bone_name not in allowed_metarig_bones:
                continue

            source_bone = external_obj.data.bones.get(bone_name)

            if source_bone is None:
                continue

            make_bone(
                metarig_obj,
                bone_name,
                None,
                external_obj.matrix_world @ source_bone.head_local,
                external_obj.matrix_world @ source_bone.tail_local,
            )

        make_bone(metarig_obj, "new_torso")

        # ------------------------------------------------------------
        # Heels erzeugen, falls keine existieren
        # ------------------------------------------------------------

        ensure_mode(metarig_obj, "EDIT")

        if not skelett.heel_r and not skelett.heel_l:
            generated_heels = {"heel_r": skelett.foot_r, "heel_l": skelett.foot_l}
            heel_r = "heel_r"
            heel_l = "heel_l"

            for heel_name, parent_name in generated_heels.items():
                if not parent_name or parent_name not in metarig_obj.data.edit_bones:
                    continue

                heel_bone = make_bone(metarig_obj, heel_name)
                parent_bone = metarig_obj.data.edit_bones[parent_name]

                if heel_bone is None:
                    continue

                heel_bone.parent = parent_bone
                heel_bone.tail = parent_bone.head.copy()
                heel_bone.tail.z = parent_bone.head.z / 2.0

                delta = 1 if parent_bone.head.x > 0 else -1
                heel_bone.tail.x += (parent_bone.length / 2.0) * delta
                heel_bone.head = heel_bone.tail.copy()
                heel_bone.head.x -= parent_bone.length * delta

        # ------------------------------------------------------------
        # Parenting im Metarig
        # ------------------------------------------------------------

        parenting_bones = {}

        def add_parent(child, parent, use_connect: bool) -> None:
            if child: parenting_bones[child] = [parent, use_connect]

        add_parent(skelett.head, skelett.last_neck, True)
        add_parent(skelett.first_neck, skelett.last_spine, False)
        add_parent(second_spine, skelett.first_spine, True)

        for child, parent, connected in skelett.parenting_list():
            add_parent(child, parent, connected)

        for child, parent_config in skelett.finger_parenting_list().items():
            add_parent(child, parent_config[0], parent_config[1])

        parenting_bones.update(spine_parenting)
        parenting_bones.update(neck_parenting)

        ensure_mode(metarig_obj, "EDIT")
        metarig_edit_bones = metarig_obj.data.edit_bones
        all_metarig_edit_names = {bone.name for bone in metarig_edit_bones}
        first_spine_bone = metarig_edit_bones.get(skelett.first_spine)
        second_spine_bone = metarig_edit_bones.get(second_spine)
        hip_spine_bool = False
        second_spine_head_copy = None

        if first_spine_bone is not None and second_spine_bone is not None:
            second_spine_head_copy = second_spine_bone.head.copy()

            if first_spine_bone.head == second_spine_bone.head and len(all_spines) > 1:
                hip_spine_bool = True
                first_spine_head = first_spine_bone.head.copy()
                first_spine_tail = first_spine_bone.tail.copy()
                first_spine_bone.head = first_spine_tail
                first_spine_bone.tail = first_spine_head

        exclude_align = {
            skelett.first_spine: second_spine,
            skelett.last_spine: skelett.first_neck,
            skelett.palm_index_l: skelett.index_01_l,
            skelett.palm_index_r: skelett.index_01_r,
            skelett.hand_l: None,
            skelett.hand_r: None,
            skelett.head: None,
        }

        if less_spine_bones:
            exclude_align[skelett.first_spine] = None

        for child_name, parent_config in parenting_bones.items():
            parent_name, use_connect = parent_config

            if not child_name or not parent_name:
                continue

            if child_name not in all_metarig_edit_names or parent_name not in all_metarig_edit_names:
                continue

            child_bone = metarig_edit_bones[child_name]
            parent_bone = metarig_edit_bones[parent_name]
            child_bone.parent = parent_bone

            if parent_name in exclude_align:
                align_target = exclude_align[parent_name]

                if align_target and align_target in all_metarig_edit_names:
                    parent_bone.tail = metarig_edit_bones[align_target].head.copy()
            else:
                parent_bone.tail = child_bone.head.copy()

            child_bone.use_connect = use_connect

        for bone_name in whitelisted_extra_bones:
            copy_edit_bone_roll_from_source(external_obj, metarig_obj, bone_name)

        if hip_spine_bool and less_spine_bones and second_spine_bone is not None and second_spine_head_copy is not None:
            second_spine_bone.head = second_spine_head_copy

        if (
            not hip_spine_bool
            and less_spine_bones
            and len(all_spines) == 2
            and first_spine_bone is not None
            and second_spine_head_copy is not None
        ):
            first_spine_bone.tail = second_spine_head_copy

        # ------------------------------------------------------------
        # Zusatzknochen bestimmen
        # ------------------------------------------------------------

        extra_bones = sorted(whitelisted_extra_bones)

        for bone_name in extra_bones:
            if bone_name not in metarig_obj.data.edit_bones:
                continue

            source_bone = external_obj.data.bones.get(bone_name)
            meta_bone = metarig_obj.data.edit_bones[bone_name]

            if source_bone is None or source_bone.parent is None:
                continue

            parent_name = source_bone.parent.name

            if parent_name in metarig_obj.data.edit_bones:
                meta_bone.parent = metarig_obj.data.edit_bones[parent_name]

        # ------------------------------------------------------------
        # Hand-Tails korrigieren
        # ------------------------------------------------------------

        ensure_mode(metarig_obj, "EDIT")

        for hand_name, thumb_name, finger_roots, fingers_bool in [
            (skelett.hand_l, skelett.thumb_01_l, [skelett.pinky_01_l, skelett.ring_01_l, skelett.middle_01_l, skelett.index_01_l], skelett.fingers_bool_l),
            (skelett.hand_r, skelett.thumb_01_r, [skelett.pinky_01_r, skelett.ring_01_r, skelett.middle_01_r, skelett.index_01_r], skelett.fingers_bool_r),
        ]:
            hand_bone = metarig_obj.data.edit_bones.get(hand_name)

            if hand_bone is None:
                continue

            children = [child for child in hand_bone.children if child.name != thumb_name]

            if not children:
                children = [
                    metarig_obj.data.edit_bones[name]
                    for name in finger_roots
                    if name in metarig_obj.data.edit_bones
                ]

            median = average_bone_points(children, "head")

            if fingers_bool and median is not None:
                hand_bone.tail = median

        # ------------------------------------------------------------
        # Hand-Orientierung ohne Finger grob reparieren
        # ------------------------------------------------------------

        hands_orient = {
            skelett.hand_r: [skelett.lowarm_r, skelett.fingers_bool_r],
            skelett.hand_l: [skelett.lowarm_l, skelett.fingers_bool_l],
        }

        for hand_name, orient_config in hands_orient.items():
            parent_arm_name, has_fingers = orient_config

            if has_fingers:
                continue

            if hand_name not in metarig_obj.data.edit_bones or parent_arm_name not in metarig_obj.data.edit_bones:
                continue

            hand_bone = metarig_obj.data.edit_bones[hand_name]
            parent_arm_bone = metarig_obj.data.edit_bones[parent_arm_name]
            original_length = parent_arm_bone.length
            parent_arm_bone.length *= 1.5
            hand_bone.tail = parent_arm_bone.tail.copy()
            parent_arm_bone.length = original_length

        # ------------------------------------------------------------
        # Letzte Fingerknochen anhand Vertex Groups verlängern
        # ------------------------------------------------------------

        for finger_name in skelett.finger_end_list():
            if not finger_name or finger_name not in metarig_obj.data.edit_bones:
                continue

            metarig_finger = metarig_obj.data.edit_bones[finger_name]
            source_finger = external_obj.data.bones.get(finger_name)

            if source_finger is None or source_finger.children or metarig_finger.children:
                continue

            for mesh_obj in self.context.bound_meshes:
                vertex_group = mesh_obj.vertex_groups.get(finger_name)

                if vertex_group is None:
                    continue

                weighted_vectors = [
                    mesh_obj.matrix_world @ vertex.co
                    for vertex in mesh_obj.data.vertices
                    if vertex_group.index in {group.group for group in vertex.groups}
                ]

                median = average_vectors(weighted_vectors)

                if median is not None:
                    metarig_finger.tail = median
                    break

        # ------------------------------------------------------------
        # Finger-Roll
        # ------------------------------------------------------------

        all_fingers_but_thumbs = skelett.finger_list_no_thumb()
        all_fingers_but_thumbs = [finger_name for finger_name in all_fingers_but_thumbs if finger_name]
        metarig_obj.data.show_axes = True

        for finger_name in all_fingers_but_thumbs:
            if finger_name not in metarig_obj.data.edit_bones:
                continue

            finger_bone = metarig_obj.data.edit_bones[finger_name]
            roll = finger_bone.tail.copy()
            roll.z -= 1.0
            finger_bone.align_roll(-roll)

        ensure_mode(metarig_obj, "POSE")

        for finger_name in all_fingers_but_thumbs:
            pose_bone = metarig_obj.pose.bones.get(finger_name)

            if pose_bone is not None and hasattr(pose_bone.rigify_parameters, "primary_rotation_axis"):
                pose_bone.rigify_parameters.primary_rotation_axis = "X"

        # ------------------------------------------------------------
        # Rigify-Typen setzen
        # ------------------------------------------------------------

        rigify_types = skelett.rigify_types()

        if less_spine_bones:
            for spine_name in all_spines:
                rigify_types[spine_name] = "basic.super_copy"

            rigify_types[skelett.first_neck] = "basic.super_copy"
            rigify_types[skelett.head] = "basic.super_copy"

        all_metarig_pose_names = get_all_bone_names(metarig_obj, "POSE")

        for bone_name, rig_type in rigify_types.items():
            if not bone_name or bone_name not in all_metarig_pose_names:
                continue

            pose_bone = metarig_obj.pose.bones[bone_name]
            pose_bone.rigify_type = rig_type
            rigify_param = pose_bone.rigify_parameters

            if bone_name in {skelett.thigh_r, skelett.thigh_l} and hasattr(rigify_param, "extra_ik_toe"):
                rigify_param.extra_ik_toe = True

            if bone_name == skelett.last_neck and hasattr(rigify_param, "connect_chain"):
                rigify_param.connect_chain = True

            if bone_name in {skelett.clav_r, skelett.clav_l} and hasattr(rigify_param, "super_copy_widget_type"):
                rigify_param.super_copy_widget_type = "shoulder"

        # ------------------------------------------------------------
        # Bone Collections / Layer im Metarig
        # ------------------------------------------------------------

        layer_bones = {
            skelett.head: 0,
            skelett.uparm_l: 7,
            skelett.lowarm_l: 7,
            skelett.hand_l: 7,
            skelett.uparm_r: 10,
            skelett.lowarm_r: 10,
            skelett.hand_r: 10,
            skelett.thigh_l: 13,
            skelett.calf_l: 13,
            skelett.foot_l: 13,
            skelett.toe_l: 13,
            skelett.heel_l: 13,
            skelett.thigh_r: 16,
            skelett.calf_r: 16,
            skelett.foot_r: 16,
            skelett.toe_r: 16,
            skelett.heel_r: 16,
            skelett.clav_r: 3,
            skelett.clav_l: 3,
            "skeleton:torso_bone": 3,
            "new_torso": 3,
            skelett.first_neck: 3,
        }

        for spine_name in all_spines:
            layer_bones[spine_name] = 3

        for neck_name in all_necks:
            layer_bones[neck_name] = 3

        finger_bones = skelett.finger_list_all()

        for bone_name in finger_bones:
            if bone_name:
                layer_bones[bone_name] = 5

        if less_spine_bones:
            layer_bones[skelett.first_spine] = 3
            layer_bones[skelett.first_neck] = 3
            layer_bones[skelett.head] = 3

        all_metarig_data_names = set(get_all_bone_names(metarig_obj, "DATA"))

        for bone_name, layer_index in layer_bones.items():
            if bone_name in all_metarig_data_names:
                assign_bone_to_layer_group(metarig_obj, bone_name, layer_index)

        ensure_mode(metarig_obj, "POSE")
        initialisiere_standard_bone_collections(metarig_obj.data)
        metarig_extra_group_ui_rows = build_extra_group_ui_rows(self.context,metarig_obj.data)

        for bone_name in extra_bones:
            pose_bone = metarig_obj.pose.bones.get(bone_name)

            if pose_bone is None:
                continue

            pose_bone.rigify_type = "basic.super_copy"
            extra_data = self.context.extra_bone_data.get(bone_name, {})
            group_name = sanitize_extra_group_name(extra_data.get("whitelist_group_name", "Additional"))
            ui_row = metarig_extra_group_ui_rows.get(group_name)

            if ui_row is not None:
                assign_bone_to_extra_group_collection(metarig_obj, bone_name, group_name, ui_row)
            else:
                assign_bone_to_layer_group(metarig_obj, bone_name, 27)

        # ------------------------------------------------------------
        # new_torso orientieren
        # ------------------------------------------------------------

        ensure_mode(metarig_obj, "EDIT")
        new_torso_bone = metarig_obj.data.edit_bones.get("new_torso")
        spine_bone = metarig_obj.data.edit_bones.get(second_spine)
        first_spine_bone = metarig_obj.data.edit_bones.get(skelett.first_spine)

        if new_torso_bone is not None and spine_bone is not None and first_spine_bone is not None:
            new_torso_bone.tail = (first_spine_bone.head + first_spine_bone.tail) / 2.0
            new_torso_bone.head = (spine_bone.head + spine_bone.tail) / 2.0

        # ------------------------------------------------------------
        # kleine Positionskorrektur für Arme/Beine
        # ------------------------------------------------------------

        all_z = [(external_obj.matrix_world @ Vector(corner)).z for corner in external_obj.bound_box]
        skeleton_height = max(all_z) - min(all_z) if all_z else 1.0
        skeleton_height_percent = skeleton_height * 0.002

        for bone_name, offset in {
            skelett.uparm_l: skeleton_height_percent,
            skelett.uparm_r: skeleton_height_percent,
            skelett.thigh_l: -skeleton_height_percent,
            skelett.thigh_r: -skeleton_height_percent,
        }.items():
            if bone_name in metarig_obj.data.edit_bones:
                metarig_obj.data.edit_bones[bone_name].tail.y += offset

        first_spine_bone = metarig_obj.data.edit_bones.get(skelett.first_spine)

        if hip_spine_bool and first_spine_bone is not None:
            first_spine_bone.head = first_spine_bone.tail.copy()
            first_spine_bone.head.z -= skeleton_height_percent

        # ------------------------------------------------------------
        # IK / FK / Tweak Layer-Parameter
        # ------------------------------------------------------------

        ensure_mode(metarig_obj, "POSE")

        limb_layer_params = {
            skelett.uparm_l: {"ik_layers": 7, "fk_layers": 8, "tweak_layers": 9},
            skelett.uparm_r: {"ik_layers": 10, "fk_layers": 11, "tweak_layers": 12},
            skelett.thigh_l: {"ik_layers": 13, "fk_layers": 14, "tweak_layers": 15},
            skelett.thigh_r: {"ik_layers": 16, "fk_layers": 17, "tweak_layers": 18},
        }

        for bone_name, layer_config in limb_layer_params.items():
            if bone_name not in metarig_obj.pose.bones:
                continue

            rigify_param = metarig_obj.pose.bones[bone_name].rigify_parameters

            for attr_name, layer_index in layer_config.items():
                set_rigify_layer_param(metarig_obj, rigify_param, attr_name, layer_index)

        extra_layer_params = {
            skelett.first_spine: {"fk_layers": 4, "tweak_layers": 4},
            skelett.first_neck: {"tweak_layers": 1},
        }

        for finger_name in finger_bones:
            if finger_name in all_metarig_pose_names:
                extra_layer_params[finger_name] = {"tweak_layers": 6}

        for bone_name, layer_config in extra_layer_params.items():
            if bone_name not in metarig_obj.pose.bones:
                continue

            rigify_param = metarig_obj.pose.bones[bone_name].rigify_parameters

            for attr_name, layer_index in layer_config.items():
                set_rigify_layer_param(metarig_obj, rigify_param, attr_name, layer_index)

        root_pose_bone = metarig_obj.pose.bones.get("root")

        if root_pose_bone is not None:
            root_pose_bone.rigify_type = ""

        # ------------------------------------------------------------
        # Rig erzeugen
        # ------------------------------------------------------------

        rigify_obj = erhalte_generiertes_rigify_rig(metarig_obj)

        if rigify_obj is None or rigify_obj.type != "ARMATURE":
            raise RuntimeError("Rigify hat kein gültiges Rig erzeugt")

        rigify_obj.name = target_rig_name
        rigify_obj.data.name = f"{target_rig_name}_data"

        initialisiere_standard_bone_collections(rigify_obj.data)
        rigify_extra_group_ui_rows = build_extra_group_ui_rows(self.context,rigify_obj.data)
        extra_collection_names = apply_extra_group_collections(self.context,rigify_obj, rigify_extra_group_ui_rows)

        repariere_standard_control_collections(rigify_obj)
        normalisiere_rigify_sichtbarkeit(rigify_obj)
        normalisiere_rigify_standardfarben(rigify_obj)

        set_visible_rig_layers(
            rigify_obj,
            DEFAULT_VISIBLE_RIG_LAYER_INDICES,
            extra_collection_names,
        )

        # ------------------------------------------------------------
        # Constraints vom erzeugten Rigify-Rig zum Originalrig
        # ------------------------------------------------------------

        ensure_mode(external_obj, "OBJECT")
        ensure_mode(rigify_obj, "OBJECT")

        external_obj.data.pose_position = "REST"
        rigify_obj.data.pose_position = "REST"

        all_external_pose_names = get_all_bone_names(external_obj, "POSE")
        all_rigify_pose_names = get_all_bone_names(rigify_obj, "POSE")

        for bone_name in extra_bones:
            if bone_name in all_rigify_pose_names:
                rigify_obj.pose.bones[bone_name].bone.inherit_scale = "NONE"

        for ik_fk_name in [
            "upperarm_parent_r",
            "thigh_parent_r",
            "upperarm_parent_l",
            "thigh_parent_l",
            "upper_arm_parent.R",
            "thigh_parent.R",
            "upper_arm_parent.L",
            "thigh_parent.L",
        ]:
            pose_bone = rigify_obj.pose.bones.get(ik_fk_name)

            if pose_bone is not None and "IK_FK" in pose_bone:
                pose_bone["IK_FK"] = 0

        constraints_map = {}

        for source_name, mapping in self.context.standard_constraint_map.items():
            target_name = mapping.get("constraint_target")

            if source_name and target_name:
                constraints_map[source_name] = [target_name, bool(mapping.get("copy_location", False))]

        for spine_name in all_spines:
            target_name = f"DEF-{spine_name}"

            if target_name in all_rigify_pose_names:
                constraints_map[spine_name] = [target_name, True]

        for neck_name in all_necks:
            target_name = f"DEF-{neck_name}"

            if target_name in all_rigify_pose_names:
                constraints_map[neck_name] = [target_name, True]

        if less_spine_bones:
            constraints_map.pop("skeleton:torso_bone", None)

        ensure_mode(external_obj, "POSE")

        for source_name, target_config in constraints_map.items():
            target_name, copy_location = target_config

            if source_name not in all_external_pose_names or target_name not in all_rigify_pose_names:
                continue

            source_pose_bone = external_obj.pose.bones[source_name]
            target_pose_bone = rigify_obj.pose.bones[target_name]
            source_rotation, target_rotation = get_rotation_diff(
                source_pose_bone,
                external_obj,
                target_pose_bone,
                rigify_obj,
            )
            rotation_diff = target_rotation.rotation_difference(source_rotation).to_euler()

            create_constraint(
                source_pose_bone,
                external_obj,
                target_name,
                rigify_obj,
                rotation_diff,
                rotation_diff.order,
                copy_location,
                skelett.copy_loc_constr,
            )

        for bone_name in extra_bones:
            if bone_name not in all_external_pose_names or bone_name not in all_rigify_pose_names:
                continue

            source_pose_bone = external_obj.pose.bones[bone_name]
            target_pose_bone = rigify_obj.pose.bones[bone_name]
            source_rotation, target_rotation = get_rotation_diff(
                source_pose_bone,
                external_obj,
                target_pose_bone,
                rigify_obj,
            )
            rotation_diff = target_rotation.rotation_difference(source_rotation).to_euler()

            create_constraint(
                source_pose_bone,
                external_obj,
                bone_name,
                rigify_obj,
                rotation_diff,
                rotation_diff.order,
                True,
                False,
            )

        # ------------------------------------------------------------
        # Custom Shape Sonderfälle + finale Normalisierung
        # ------------------------------------------------------------

        head_pose_bone = rigify_obj.pose.bones.get("head")

        if head_pose_bone is not None:
            head_pose_bone.custom_shape_scale_xyz = (1.5, 1.5, 1.5)

        extra_collection_names = apply_extra_group_collections(self.context,rigify_obj, rigify_extra_group_ui_rows)
        repariere_standard_control_collections(rigify_obj)
        normalisiere_rigify_sichtbarkeit(rigify_obj)
        normalisiere_rigify_standardfarben(rigify_obj)

        set_visible_rig_layers(
            rigify_obj,
            DEFAULT_VISIBLE_RIG_LAYER_INDICES,
            extra_collection_names,
        )

        rigify_obj.data.pose_position = "POSE"
        external_obj.data.pose_position = "POSE"

        ensure_mode(external_obj, "OBJECT")
        bpy.ops.object.select_all(action="DESELECT")

        metarig_obj.hide_set(True)
        external_obj.select_set(True)
        rigify_obj.select_set(True)
        bpy.context.view_layer.objects.active = external_obj
        ensure_mode(external_obj, "POSE")

    def uebernehme_custom_shapes(self, rigify_obj, target_name_key: str) -> int:
        if rigify_obj is None:
         return 0

        copied_count = self.inherit_missing_custom_shapes(rigify_obj, target_name_key)
        repariere_standard_control_collections(rigify_obj)
        normalisiere_rigify_sichtbarkeit(rigify_obj)
        normalisiere_rigify_standardfarben(rigify_obj)
        return copied_count

    def inherit_missing_custom_shapes(self, rigify_obj, target_name_key: str) -> int:
        copied_count = 0
        for source_bone_name, target_bone_name, mapping in iter_shape_mappings(
            rigify_obj,
            target_name_key,
            self.context.source_to_target_map,
            self.source_armature.pose.bones,
        ):
            source_pose_bone = self.source_armature.pose.bones.get(source_bone_name)
            target_pose_bone = rigify_obj.pose.bones.get(target_bone_name)
            if source_pose_bone is None or target_pose_bone is None:
                continue
            if not should_replace_custom_shape(source_pose_bone, target_pose_bone, mapping):
                continue
            target_transform_bone = resolve_target_transform_bone(
                source_pose_bone,
                rigify_obj,
                target_name_key,
                self.context.source_to_target_map
            )
            copy_custom_shape_settings(source_pose_bone, target_pose_bone, target_transform_bone)
            if not mapping.get("is_standard", True):
                copy_pose_transform(source_pose_bone, target_pose_bone)
                copy_bone_color(source_pose_bone.color, target_pose_bone.color)
                copy_bone_color(source_pose_bone.bone.color, target_pose_bone.bone.color)
            copied_count += 1
        return copied_count
