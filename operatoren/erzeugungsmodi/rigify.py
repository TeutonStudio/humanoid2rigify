# from typing import Literal
#
# import bpy
# import rigify
# import re
# from mathutils import Vector, Color
#
# from ...__eigenschaften__ import Wirbelsäule
# from ...operatoren.erzeugungsmodi.__methoden__ import get_generated_rigify_object, GenerationContext
#
# DEFAULT_VISIBLE_RIG_LAYER_INDICES = [
#     0,
#     1,
#     2,
#     3,
#     4,
#     5,
#     6,
#
#     7,
#     8,
#     9,
#     10,
#     11,
#     12,
#
#     13,
#     14,
#     15,
#     16,
#     17,
#     18,
#
#     31,
# ]
# GENERIC_CIRCLE_WIDGET_VERTEX_COUNT = 32
# INTERNAL_RIGIFY_PREFIXES = ("DEF-", "MCH-", "ORG-")
# EXTRA_GROUP_COLLECTION_PREFIX = "Extra"
#
# EXTRA_GROUP_UI_START_ROW = 18
#
# LAYER_COLLECTION_NAMES = {
#     0: "Face",
#     1: "Face (Primary)",
#     2: "Face (Secondary)",
#
#     3: "Torso",
#     4: "Torso (Tweak)",
#
#     5: "Fingers",
#     6: "Fingers (Detail)",
#
#     7: "Arm.L (IK)",
#     8: "Arm.L (FK)",
#     9: "Arm.L (Tweak)",
#
#     10: "Arm.R (IK)",
#     11: "Arm.R (FK)",
#     12: "Arm.R (Tweak)",
#
#     13: "Leg.L (IK)",
#     14: "Leg.L (FK)",
#     15: "Leg.L (Tweak)",
#
#     16: "Leg.R (IK)",
#     17: "Leg.R (FK)",
#     18: "Leg.R (Tweak)",
#
#     27: "Additional",
#     31: "Root",
# }
#
# # Name, der im Rigify-UI angezeigt wird.
# # Die Collection-Namen bleiben eindeutig, weil Blender doppelte Namen sonst wieder
# # in .001-Höllen verwandelt.
# RIGIFY_UI_TITLES = {
#     0: "Face",
#     1: "Primary",
#     2: "Secondary",
#
#     3: "Torso",
#     4: "Tweak",
#
#     5: "Fingers",
#     6: "Detail",
#
#     7: "Arm.L (IK)",
#     10: "Arm.R (IK)",
#
#     8: "FK",
#     11: "FK",
#
#     9: "Tweak",
#     12: "Tweak",
#
#     13: "Leg.L (IK)",
#     16: "Leg.R (IK)",
#
#     14: "FK",
#     17: "FK",
#
#     15: "Tweak",
#     18: "Tweak",
#
#     27: "Additional",
#     31: "Root",
# }
#
# RIGIFY_UI_ROWS = {
#     # Face
#     0: 1,
#
#     # Primary / Secondary
#     1: 2,
#     2: 2,
#
#     # Separator row 3
#
#     # Torso
#     3: 4,
#     4: 5,
#
#     # Fingers
#     5: 6,
#     6: 7,
#
#     # Separator row 8
#
#     # Arms
#     7: 9,
#     10: 9,
#
#     8: 10,
#     11: 10,
#
#     9: 11,
#     12: 11,
#
#     # Separator row 12
#
#     # Legs
#     13: 13,
#     16: 13,
#
#     14: 14,
#     17: 14,
#
#     15: 15,
#     18: 15,
#
#     # Separator row 16
#
#     # Root
#     31: 17,
#
#     # Whitelist / Additional
#     27: EXTRA_GROUP_UI_START_ROW,
# }
#
# STANDARD_LAYER_UI_ORDER = [
#     0,
#     1,
#     2,
#     3,
#     4,
#     5,
#     6,
#
#     7,
#     10,
#     8,
#     11,
#     9,
#     12,
#
#     13,
#     16,
#     14,
#     17,
#     15,
#     18,
#
#     31,
#     27,
# ]
#
# STANDARD_COLLECTION_NAMES = set(LAYER_COLLECTION_NAMES.values())
#
# KnochenGattung = Literal["IK", "FK", "Tweak"]
# FarbGattung = Literal["normal", "select", "active"]
#
# FALLBACK_COLOR: dict[KnochenGattung,dict[FarbGattung,Color]] = {
#     "IK": {
#         "normal": Color((0.85, 0.15, 0.12)),
#         "select": Color((1.00, 0.35, 0.30)),
#         "active": Color((1.00, 0.65, 0.55)),
#     },
#     "FK": {
#         "normal": Color((0.15, 0.75, 0.20)),
#         "select": Color((0.45, 1.00, 0.45)),
#         "active": Color((0.75, 1.00, 0.75)),
#     },
#     "Tweak": {
#         "normal": Color((0.2196078431, 0.4980392157, 0.7843137255)),
#         "select": Color((0.5960784314, 0.8980392157, 1.0)),
#         "active": Color((0.7686274510, 1.0, 1.0)),
#     }
# }
#
# COLLECTION_LAYER_BY_NAME = {
#     collection_name: layer_index
#     for layer_index, collection_name in LAYER_COLLECTION_NAMES.items()
# }
#
# # ============================================================
# # Globale Rigify-Helfer: Collections / Farben
# # ============================================================
#
# def get_collection_name(layer_index: int) -> str:
#     return LAYER_COLLECTION_NAMES.get(layer_index, f"Layer {layer_index + 1}")
#
#
# def uses_bone_collections(armature_data) -> bool:
#     return hasattr(armature_data, "collections_all")
#
#
# def ist_interner_rigify_knochen(bone_name: str) -> bool:
#     return bone_name.startswith(INTERNAL_RIGIFY_PREFIXES)
#
# def finde_seite_aus_name(bone_name: str) -> str | None:
#     name = bone_name.lower()
#
#     # Erlaubt z.B. ".L", ".L.001", "_l", "_l.001", "-r", "-r.001"
#     if re.search(r"(\.l|_l|-l)(?:\.\d+)?$", name):
#         return "L"
#
#     if re.search(r"(\.r|_r|-r)(?:\.\d+)?$", name):
#         return "R"
#
#     # Erlaubt Seitenmarker in der Mitte, z.B. "hand.L_tweak"
#     if re.search(r"(\.l|_l|-l)(?=[._-])", name):
#         return "L"
#
#     if re.search(r"(\.r|_r|-r)(?=[._-])", name):
#         return "R"
#
#     return None
#
#
# def ist_linke_seite(bone_name: str) -> bool:
#     return finde_seite_aus_name(bone_name) == "L"
#
#
# def ist_rechte_seite(bone_name: str) -> bool:
#     return finde_seite_aus_name(bone_name) == "R"
#
#
# def ist_fk_control_bone(bone_name: str) -> bool:
#     name = bone_name.lower()
#
#     if ist_interner_rigify_knochen(bone_name):
#         return False
#
#     return any(token in name for token in (
#         "_fk",
#         ".fk",
#         "-fk",
#         "fk_",
#         "fk.",
#         "fk-",
#     ))
#
#
# def ist_ik_control_bone(bone_name: str) -> bool:
#     name = bone_name.lower()
#
#     if ist_interner_rigify_knochen(bone_name):
#         return False
#
#     return any(token in name for token in (
#         "_ik",
#         ".ik",
#         "-ik",
#         "ik_",
#         "ik.",
#         "ik-",
#         "ik_target",
#         "ik_pole",
#     ))
#
#
# def ist_tweak_control_bone(bone_name: str) -> bool:
#     name = bone_name.lower()
#
#     if ist_interner_rigify_knochen(bone_name):
#         return False
#
#     return any(token in name for token in (
#         "_tweak",
#         ".tweak",
#         "-tweak",
#         "tweak_",
#         "tweak.",
#         "tweak-",
#     ))
#
#
# def ist_torso_tweak_control_bone(bone_name: str) -> bool:
#     name = bone_name.lower()
#
#     if ist_interner_rigify_knochen(bone_name):
#         return False
#
#     return (
#         name.startswith("tweak_pelvis")
#         or name.startswith("tweak_spine")
#         or name.startswith("tweak_neck")
#         or name.startswith("tweak_chest")
#         or name.startswith("tweak_torso")
#         or "spine_tweak" in name
#         or "neck_tweak" in name
#         or "pelvis_tweak" in name
#     )
#
#
# def ist_arm_control_bone(bone_name: str) -> bool:
#     name = bone_name.lower()
#
#     return any(part in name for part in (
#         "upperarm",
#         "upper_arm",
#         "lowerarm",
#         "lower_arm",
#         "forearm",
#         "hand",
#         "arm_",
#         "arm.",
#         "arm-",
#     ))
#
#
# def ist_bein_control_bone(bone_name: str) -> bool:
#     name = bone_name.lower()
#
#     return any(part in name for part in (
#         "thigh",
#         "shin",
#         "calf",
#         "foot",
#         "toe",
#         "heel",
#         "leg_",
#         "leg.",
#         "leg-",
#     ))
#
#
# def setze_bone_color(bone_color: Color, normal, select, active) -> None:
#     if bone_color is None:
#         return
#
#     bone_color.palette = "CUSTOM"
#     bone_color.custom.normal = normal
#     bone_color.custom.select = select
#     bone_color.custom.active = active
#
#
# def setze_pose_bone_color(pose_bone, color_data: dict[FarbGattung,Color]) -> None:
#     setze_bone_color(
#         getattr(pose_bone, "color", None),
#         color_data["normal"],
#         color_data["select"],
#         color_data["active"],
#     )
#
#     setze_bone_color(
#         getattr(pose_bone.bone, "color", None),
#         color_data["normal"],
#         color_data["select"],
#         color_data["active"],
#     )
#
#
# def get_bone_standard_layer_indices(armature_data, bone) -> set[int]:
#     layer_indices: set[int] = set()
#
#     if bone is None:
#         return layer_indices
#
#     if not uses_bone_collections(armature_data):
#         for index, enabled in enumerate(getattr(bone, "layers", [])):
#             if enabled:
#                 layer_indices.add(index)
#
#         return layer_indices
#
#     for collection in getattr(bone, "collections", []):
#         collection_name = getattr(collection, "name", str(collection))
#         layer_index = COLLECTION_LAYER_BY_NAME.get(collection_name)
#
#         if layer_index is not None:
#             layer_indices.add(layer_index)
#
#     return layer_indices
#
#
# def finde_seite_aus_aktueller_collection(armature_data, bone, bereich: str) -> str | None:
#     layer_indices = get_bone_standard_layer_indices(armature_data, bone)
#
#     if bereich == "arm":
#         if layer_indices & {7, 8, 9}:
#             return "L"
#
#         if layer_indices & {10, 11, 12}:
#             return "R"
#
#     if bereich == "bein":
#         if layer_indices & {13, 14, 15}:
#             return "L"
#
#         if layer_indices & {16, 17, 18}:
#             return "R"
#
#     return None
#
#
# def layer_fuer_seite_und_typ(seite: str | None, links_layer: int, rechts_layer: int) -> int | None:
#     if seite == "L":
#         return links_layer
#
#     if seite == "R":
#         return rechts_layer
#
#     return None
#
# def get_or_create_collection_by_layer(armature_data, layer_index: int):
#     collection_name = get_collection_name(layer_index)
#     bone_collection = armature_data.collections_all.get(collection_name)
#
#     if bone_collection is None:
#         bone_collection = armature_data.collections.new(collection_name)
#
#     if hasattr(bone_collection, "rigify_ui_row"):
#         bone_collection.rigify_ui_row = RIGIFY_UI_ROWS.get(layer_index, EXTRA_GROUP_UI_START_ROW)
#
#     if hasattr(bone_collection, "rigify_ui_title"):
#         bone_collection.rigify_ui_title = RIGIFY_UI_TITLES.get(layer_index, collection_name)
#
#     bone_collection.is_visible = True
#     return bone_collection
#
# def initialisiere_standard_bone_collections(armature_data) -> None:
#     if not uses_bone_collections(armature_data):
#         return
#
#     for layer_index in STANDARD_LAYER_UI_ORDER:
#         get_or_create_collection_by_layer(armature_data, layer_index)
#
# def assign_standard_bone_collection(rig_obj, bone_name: str, layer_index: int) -> None:
#     armature_data = rig_obj.data
#     bone = armature_data.bones.get(bone_name)
#
#     if bone is None:
#         return
#
#     if not uses_bone_collections(armature_data):
#         bone.layers[layer_index] = True
#
#         for index in range(32):
#             if index != layer_index:
#                 bone.layers[index] = False
#
#         return
#
#     target_collection = get_or_create_collection_by_layer(armature_data, layer_index)
#
#     # Nur Standard-Rigify-Collections entfernen. Extra-Gruppen bleiben erhalten.
#     for collection in armature_data.collections_all:
#         if collection.name not in STANDARD_COLLECTION_NAMES:
#             continue
#
#         try:
#             collection.unassign(bone)
#         except RuntimeError:
#             pass
#
#     target_collection.assign(bone)
#
#
# def errate_standard_layer_fuer_control(rig_obj, pose_bone) -> int | None:
#     bone_name = pose_bone.name
#     bone = pose_bone.bone
#     armature_data = rig_obj.data
#
#     # Torso-Tweaks zuerst, sonst landen tweak_spine_* im Torso.
#     if ist_torso_tweak_control_bone(bone_name):
#         return 4
#
#     ist_fk = ist_fk_control_bone(bone_name)
#     ist_ik = ist_ik_control_bone(bone_name)
#     ist_tweak = ist_tweak_control_bone(bone_name)
#
#     # Sonderfall: manche Rigify-Tweak-Bones heißen nicht sauber *_tweak,
#     # sondern z.B. lowerarm_.001. Danke, Blender, sehr hilfreich.
#     name = bone_name.lower()
#     if not ist_tweak and re.search(r"(upperarm|upper_arm|lowerarm|lower_arm|forearm|calf|shin|thigh|foot|toe|heel).*\.\d+$", name):
#         ist_tweak = True
#
#     if not (ist_fk or ist_ik or ist_tweak):
#         return None
#
#     if ist_arm_control_bone(bone_name):
#         seite = finde_seite_aus_name(bone_name)
#         seite = seite or finde_seite_aus_aktueller_collection(armature_data, bone, "arm")
#
#         if ist_tweak:
#             return layer_fuer_seite_und_typ(seite, 9, 12)
#
#         if ist_fk:
#             return layer_fuer_seite_und_typ(seite, 8, 11)
#
#         if ist_ik:
#             return layer_fuer_seite_und_typ(seite, 7, 10)
#
#     if ist_bein_control_bone(bone_name):
#         seite = finde_seite_aus_name(bone_name)
#         seite = seite or finde_seite_aus_aktueller_collection(armature_data, bone, "bein")
#
#         if ist_tweak:
#             return layer_fuer_seite_und_typ(seite, 15, 18)
#
#         if ist_fk:
#             return layer_fuer_seite_und_typ(seite, 14, 17)
#
#         if ist_ik:
#             return layer_fuer_seite_und_typ(seite, 13, 16)
#
#     return None
#
#
# def repariere_standard_control_collections(rig_obj) -> None:
#     if rig_obj is None or rig_obj.type != "ARMATURE":
#         return
#
#     for pose_bone in rig_obj.pose.bones:
#         layer_index = errate_standard_layer_fuer_control(rig_obj, pose_bone)
#
#         if layer_index is None:
#             continue
#
#         assign_standard_bone_collection(rig_obj, pose_bone.name, layer_index)
#
#
# def normalisiere_rigify_standardfarben(rig_obj) -> None:
#     if rig_obj is None or rig_obj.type != "ARMATURE":
#         return
#
#     rig_obj.data.show_bone_colors = True
#
#     for pose_bone in rig_obj.pose.bones:
#         if ist_tweak_control_bone(pose_bone.name) or ist_torso_tweak_control_bone(pose_bone.name):
#             setze_pose_bone_color(pose_bone,FALLBACK_COLOR["Tweak"])
#             continue
#
#         if ist_fk_control_bone(pose_bone.name):
#             setze_pose_bone_color(pose_bone,FALLBACK_COLOR["FK"])
#             continue
#
#         if ist_ik_control_bone(pose_bone.name):
#             setze_pose_bone_color(pose_bone,FALLBACK_COLOR["IK"])
#
#
# # ============================================================
# # Bau-Modus
# # ============================================================
#
# class RigifyBauModus:
#     def __init__(self, context: GenerationContext):
#         self.context = context
#
#     def erzeuge(self) -> bool:
#         raise NotImplementedError
#
#     @property
#     def operator(self):
#         return self.context.operator
#
#     @property
#     def source_armature(self):
#         return self.context.source_armature
#
#     @property
#     def params(self) -> dict:
#         return self.context.params
#
#     def report(self, status: set[str], text: str) -> None:
#         self.operator.report(status, text)
#
#     def erzeuge_rigify_rig(self):
#         self.generiere_rigify_rig(
#             self.source_armature,
#             self.params,
#         )
#
#         rigify_obj = get_generated_rigify_object(self.source_armature)
#         repariere_standard_control_collections(rigify_obj)
#         normalisiere_rigify_sichtbarkeit(rigify_obj)
#         normalisiere_rigify_standardfarben(rigify_obj)
#
#         return rigify_obj
#
#     def generiere_rigify_rig(self, skeleton_model, parameters) -> None:
#         def convert_source_roll_axis_to_target_space(source_obj, target_obj, source_bone):
#             source_matrix = source_obj.matrix_world.to_3x3()
#             target_matrix_inv = target_obj.matrix_world.inverted().to_3x3()
#             source_bone_matrix = source_bone.matrix_local.to_3x3()
#             roll_axis = target_matrix_inv @ source_matrix @ source_bone_matrix @ Vector((0.0, 0.0, 1.0))
#             return Vector((0.0, 0.0, 1.0)) if roll_axis.length == 0 else roll_axis.normalized()
#
#         def copy_edit_bone_roll_from_source(
#             source_obj,
#             target_obj,
#             source_bone_name: str,
#             target_bone_name: str | None = None,
#         ) -> None:
#             target_bone_name = target_bone_name or source_bone_name
#             source_bone = source_obj.data.bones.get(source_bone_name)
#             target_edit_bone = target_obj.data.edit_bones.get(target_bone_name)
#
#             if source_bone is None or target_edit_bone is None:
#                 return
#
#             try:
#                 target_edit_bone.align_roll(
#                     convert_source_roll_axis_to_target_space(source_obj, target_obj, source_bone)
#                 )
#             except RuntimeError:
#                 pass
#
#         def ensure_rigify_enabled() -> None:
#             if "rigify" not in bpy.context.preferences.addons:
#                 bpy.ops.preferences.addon_enable(module="rigify")
#
#         def make_object_active(obj) -> None:
#             if bpy.context.object is not None and bpy.context.object.mode != "OBJECT":
#                 try:
#                     bpy.ops.object.mode_set(mode="OBJECT")
#                 except RuntimeError:
#                     pass
#
#             bpy.ops.object.select_all(action="DESELECT")
#             obj.select_set(True)
#             bpy.context.view_layer.objects.active = obj
#
#         def ensure_mode(obj, mode_name: str) -> None:
#             if bpy.context.view_layer.objects.active != obj:
#                 make_object_active(obj)
#
#             if bpy.context.object is not None and bpy.context.object.mode != mode_name:
#                 bpy.ops.object.mode_set(mode=mode_name)
#
#         def get_all_bone_names(obj, mode_name: str = "DATA") -> list[str]:
#             if obj is None or obj.type != "ARMATURE":
#                 return []
#
#             if mode_name == "EDIT":
#                 ensure_mode(obj, "EDIT")
#                 return [bone.name for bone in obj.data.edit_bones]
#
#             if mode_name == "POSE":
#                 ensure_mode(obj, "POSE")
#                 return [bone.name for bone in obj.pose.bones]
#
#             return [bone.name for bone in obj.data.bones]
#
#         def get_or_create_bone_collection(armature_data, layer_index: int):
#             return get_or_create_collection_by_layer(armature_data, layer_index)
#
#         def sanitize_extra_group_name(value: str, fallback: str = "Additional") -> str:
#             value = (value or "").strip()
#             return value if value else fallback
#
#         def extra_group_collection_name(group_name: str) -> str:
#             return f"{EXTRA_GROUP_COLLECTION_PREFIX}: {sanitize_extra_group_name(group_name)}"
#
#         def is_extra_group_collection(collection) -> bool:
#             return collection.name.startswith(f"{EXTRA_GROUP_COLLECTION_PREFIX}:")
#
#         def get_max_rigify_ui_row(armature_data) -> int:
#             if not uses_bone_collections(armature_data):
#                 return 0
#
#             return max(
#                 [
#                     getattr(collection, "rigify_ui_row", 0)
#                     for collection in armature_data.collections_all
#                     if not is_extra_group_collection(collection)
#                 ]
#                 or [0]
#             )
#
#         def build_extra_group_ui_rows(armature_data) -> dict[str, int]:
#             start_row = EXTRA_GROUP_UI_START_ROW
#             rows: dict[str, int] = {}
#
#             for data in self.context.extra_bone_data.values():
#                 if not data.get("needs_new_merge_bone", False):
#                     continue
#
#                 group_name = sanitize_extra_group_name(data.get("whitelist_group_name", "Additional"))
#                 rows.setdefault(group_name, start_row + len(rows))
#
#             return rows
#
#         def get_or_create_extra_group_collection(armature_data, group_name: str, ui_row: int):
#             group_name = sanitize_extra_group_name(group_name)
#             collection_name = extra_group_collection_name(group_name)
#             bone_collection = armature_data.collections_all.get(collection_name)
#
#             if bone_collection is None:
#                 bone_collection = armature_data.collections.new(collection_name)
#
#             if hasattr(bone_collection, "rigify_ui_row"):
#                 bone_collection.rigify_ui_row = ui_row
#
#             if hasattr(bone_collection, "rigify_ui_title"):
#                 bone_collection.rigify_ui_title = group_name
#
#             bone_collection.is_visible = True
#             return bone_collection
#
#         def assign_bone_to_layer_group(obj, bone_name: str, layer_index: int) -> None:
#             armature_data = obj.data
#             bone = armature_data.bones.get(bone_name)
#
#             if bone is None:
#                 return
#
#             if uses_bone_collections(armature_data):
#                 target_collection = get_or_create_bone_collection(armature_data, layer_index)
#
#                 for collection in armature_data.collections_all:
#                     try:
#                         collection.unassign(bone)
#                     except RuntimeError:
#                         pass
#
#                 target_collection.assign(bone)
#                 return
#
#             bone.layers[layer_index] = True
#
#             for index in range(32):
#                 if index != layer_index:
#                     bone.layers[index] = False
#
#         def assign_bone_to_extra_group_collection(obj, bone_name: str, group_name: str, ui_row: int) -> None:
#             armature_data = obj.data
#             bone = armature_data.bones.get(bone_name)
#
#             if bone is None:
#                 return
#
#             if not uses_bone_collections(armature_data):
#                 assign_bone_to_layer_group(obj, bone_name, 27)
#                 return
#
#             target_collection = get_or_create_extra_group_collection(armature_data, group_name, ui_row)
#
#             for collection in armature_data.collections_all:
#                 try:
#                     collection.unassign(bone)
#                 except RuntimeError:
#                     pass
#
#             target_collection.assign(bone)
#
#         def apply_extra_group_collections(obj, extra_group_ui_rows: dict[str, int]) -> list[str]:
#             if obj is None or obj.type != "ARMATURE" or not uses_bone_collections(obj.data):
#                 return []
#
#             assigned_collection_names: list[str] = []
#
#             for source_bone_name, data in self.context.extra_bone_data.items():
#                 if not data.get("needs_new_merge_bone", False):
#                     continue
#
#                 group_name = sanitize_extra_group_name(data.get("whitelist_group_name", "Additional"))
#                 ui_row = extra_group_ui_rows.get(group_name)
#
#                 if ui_row is None:
#                     continue
#
#                 collection_name = extra_group_collection_name(group_name)
#                 candidate_bone_names = [
#                     data.get("constraint_target"),
#                     source_bone_name,
#                     data.get("merge_target"),
#                 ]
#
#                 for candidate_bone_name in dict.fromkeys(name for name in candidate_bone_names if name):
#                     if obj.data.bones.get(candidate_bone_name) is None:
#                         continue
#
#                     assign_bone_to_extra_group_collection(obj, candidate_bone_name, group_name, ui_row)
#
#                     if collection_name not in assigned_collection_names:
#                         assigned_collection_names.append(collection_name)
#
#                     break
#
#             return assigned_collection_names
#
#         def set_visible_rig_layers(obj, layer_indices, extra_collection_names=()) -> None:
#             armature_data = obj.data
#
#             if uses_bone_collections(armature_data):
#                 visible_collections = {get_collection_name(layer_index) for layer_index in layer_indices}
#                 visible_collections.update(extra_collection_names)
#
#                 for collection in armature_data.collections_all:
#                     collection.is_visible = collection.name in visible_collections
#
#                 return
#
#             for index in range(32):
#                 armature_data.layers[index] = index in layer_indices
#
#         def set_rigify_layer_param(obj, rigify_param, attr_name: str, layer_index: int | None) -> None:
#             if layer_index is None:
#                 return
#
#             coll_refs_name = f"{attr_name}_coll_refs"
#             coll_refs = getattr(rigify_param, coll_refs_name, None)
#
#             if coll_refs is not None and uses_bone_collections(obj.data):
#                 while len(coll_refs):
#                     coll_refs.remove(len(coll_refs) - 1)
#
#                 coll_refs.add().set_collection(
#                     get_or_create_bone_collection(obj.data, layer_index)
#                 )
#                 return
#
#             if not hasattr(rigify_param, attr_name):
#                 return
#
#             layer_config = getattr(rigify_param, attr_name)
#
#             if hasattr(layer_config, "__len__") and not isinstance(layer_config, bool):
#                 for index in range(len(layer_config)):
#                     layer_config[index] = False
#
#                 if layer_index < len(layer_config):
#                     layer_config[layer_index] = True
#
#         def make_bone(
#             obj,
#             bone_name: str,
#             bone_parent: str | None = None,
#             head=(0.0, 0.0, 0.0),
#             tail=(0.5, 0.0, 0.0),
#         ):
#             if not bone_name:
#                 return None
#
#             ensure_mode(obj, "EDIT")
#             edit_bones = obj.data.edit_bones
#             existing_bone = edit_bones.get(bone_name)
#
#             if existing_bone is not None:
#                 return existing_bone
#
#             new_bone = edit_bones.new(bone_name)
#             new_bone.head = head
#             new_bone.tail = tail
#
#             if bone_parent and bone_parent in edit_bones:
#                 new_bone.parent = edit_bones[bone_parent]
#
#             return new_bone
#
#         def average_vectors(vectors):
#             vectors = [vector for vector in vectors if vector is not None]
#             return None if not vectors else sum(vectors, Vector()) / len(vectors)
#
#         def average_bone_points(bones, attr_name: str = "tail"):
#             return average_vectors([getattr(bone, attr_name).copy() for bone in bones])
#
#         def get_rotation_diff(source_pose_bone, source_obj, target_pose_bone, target_obj):
#             source_world_matrix = source_obj.matrix_world @ source_pose_bone.matrix
#             target_world_matrix = target_obj.matrix_world @ target_pose_bone.matrix
#             return source_world_matrix.to_quaternion(), target_world_matrix.to_quaternion()
#
#         def remove_constraint_if_present(pose_bone, constraint_name: str) -> None:
#             constraint = pose_bone.constraints.get(constraint_name)
#
#             if constraint is not None:
#                 pose_bone.constraints.remove(constraint)
#
#         def create_constraint(
#             owner_pose_bone,
#             owner_obj,
#             target_bone_name: str,
#             target_obj,
#             rotation,
#             rot_order: str = "XYZ",
#             copy_loc: bool = False,
#             copy_stretch_location: bool = False,
#             transform_space: str = "WORLD",
#         ) -> None:
#             remove_constraint_if_present(owner_pose_bone, "H2R Copy Rotation")
#             remove_constraint_if_present(owner_pose_bone, "H2R Root Rotation Offset")
#             remove_constraint_if_present(owner_pose_bone, "H2R Copy Location")
#
#             rot_constraint = owner_pose_bone.constraints.new("COPY_ROTATION")
#             rot_constraint.name = "H2R Copy Rotation"
#             rot_constraint.target = target_obj
#             rot_constraint.subtarget = target_bone_name
#             rot_constraint.show_expanded = False
#
#             transform_constraint = owner_pose_bone.constraints.new("TRANSFORM")
#             transform_constraint.name = "H2R Root Rotation Offset"
#             transform_constraint.target = owner_obj
#             transform_constraint.subtarget = "skeleton:TransformationTarget"
#             transform_constraint.map_from = "ROTATION"
#             transform_constraint.map_to = "ROTATION"
#             transform_constraint.to_euler_order = rot_order
#             transform_constraint.to_min_x_rot = rotation.x
#             transform_constraint.to_min_y_rot = rotation.y
#             transform_constraint.to_min_z_rot = rotation.z
#             transform_constraint.owner_space = transform_space
#             transform_constraint.mix_mode_rot = "AFTER"
#             transform_constraint.show_expanded = False
#
#             if copy_loc or copy_stretch_location:
#                 loc_constraint = owner_pose_bone.constraints.new("COPY_LOCATION")
#                 loc_constraint.name = "H2R Copy Location"
#                 loc_constraint.target = target_obj
#                 loc_constraint.subtarget = target_bone_name
#                 loc_constraint.show_expanded = False
#
#         def require_source_bone(bone_name: str, label: str) -> None:
#             if not bone_name:
#                 raise RuntimeError(f"Pflichtknochen fehlt im Mapping: {label}")
#
#             if skeleton_model.data.bones.get(bone_name) is None:
#                 raise RuntimeError(
#                     f"Pflichtknochen '{bone_name}' für '{label}' existiert nicht in {skeleton_model.name}"
#                 )
#
#         def safe_param(name: str, default=""):
#             return parameters.get(name, default)
#
#         ensure_rigify_enabled()
#         bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
#
#         external_obj = skeleton_model
#         external_name = external_obj.name
#         make_object_active(external_obj)
#
#         target_rig_name = f"{external_name}_rigify"
#         existing_rig = bpy.data.objects.get(target_rig_name)
#
#         if existing_rig is not None:
#             bpy.data.objects.remove(existing_rig, do_unlink=True)
#
#         head = safe_param("head")
#         first_neck = safe_param("first_neck")
#         last_neck = safe_param("last_neck") or first_neck
#         first_spine = safe_param("first_spine")
#         last_spine = safe_param("last_spine") or first_spine
#
#         clav_r = safe_param("clav_r")
#         clav_l = safe_param("clav_l")
#         uparm_l = safe_param("uparm_l")
#         uparm_r = safe_param("uparm_r")
#         lowarm_l = safe_param("lowarm_l")
#         lowarm_r = safe_param("lowarm_r")
#         hand_l = safe_param("hand_l")
#         hand_r = safe_param("hand_r")
#
#         palm_pinky_r = safe_param("palm_pinky_r")
#         pinky_01_r = safe_param("pinky_01_r")
#         pinky_02_r = safe_param("pinky_02_r")
#         pinky_03_r = safe_param("pinky_03_r")
#         palm_ring_r = safe_param("palm_ring_r")
#         ring_01_r = safe_param("ring_01_r")
#         ring_02_r = safe_param("ring_02_r")
#         ring_03_r = safe_param("ring_03_r")
#         palm_middle_r = safe_param("palm_middle_r")
#         middle_01_r = safe_param("middle_01_r")
#         middle_02_r = safe_param("middle_02_r")
#         middle_03_r = safe_param("middle_03_r")
#         palm_index_r = safe_param("palm_index_r")
#         index_01_r = safe_param("index_01_r")
#         index_02_r = safe_param("index_02_r")
#         index_03_r = safe_param("index_03_r")
#         thumb_01_r = safe_param("thumb_01_r")
#         thumb_02_r = safe_param("thumb_02_r")
#         thumb_03_r = safe_param("thumb_03_r")
#
#         palm_pinky_l = safe_param("palm_pinky_l")
#         pinky_01_l = safe_param("pinky_01_l")
#         pinky_02_l = safe_param("pinky_02_l")
#         pinky_03_l = safe_param("pinky_03_l")
#         palm_ring_l = safe_param("palm_ring_l")
#         ring_01_l = safe_param("ring_01_l")
#         ring_02_l = safe_param("ring_02_l")
#         ring_03_l = safe_param("ring_03_l")
#         palm_middle_l = safe_param("palm_middle_l")
#         middle_01_l = safe_param("middle_01_l")
#         middle_02_l = safe_param("middle_02_l")
#         middle_03_l = safe_param("middle_03_l")
#         palm_index_l = safe_param("palm_index_l")
#         index_01_l = safe_param("index_01_l")
#         index_02_l = safe_param("index_02_l")
#         index_03_l = safe_param("index_03_l")
#         thumb_01_l = safe_param("thumb_01_l")
#         thumb_02_l = safe_param("thumb_02_l")
#         thumb_03_l = safe_param("thumb_03_l")
#
#         thigh_l = safe_param("thigh_l")
#         thigh_r = safe_param("thigh_r")
#         calf_l = safe_param("calf_l")
#         calf_r = safe_param("calf_r")
#         foot_l = safe_param("foot_l")
#         foot_r = safe_param("foot_r")
#         toe_l = safe_param("toe_l")
#         toe_r = safe_param("toe_r")
#         heel_l = safe_param("heel_l")
#         heel_r = safe_param("heel_r")
#
#         fingers_bool_r = bool(safe_param("fingers_bool_r", True))
#         fingers_bool_l = bool(safe_param("fingers_bool_l", True))
#         copy_loc_constr = bool(safe_param("copy_loc_constr", True))
#
#         require_source_bone(first_spine, "first_spine")
#         require_source_bone(last_spine, "last_spine")
#         require_source_bone(head, "head")
#
#         right_fingers = [
#             palm_pinky_r,
#             pinky_01_r,
#             pinky_02_r,
#             pinky_03_r,
#             palm_ring_r,
#             ring_01_r,
#             ring_02_r,
#             ring_03_r,
#             palm_middle_r,
#             middle_01_r,
#             middle_02_r,
#             middle_03_r,
#             palm_index_r,
#             index_01_r,
#             index_02_r,
#             index_03_r,
#             thumb_01_r,
#             thumb_02_r,
#             thumb_03_r,
#         ]
#
#         left_fingers = [
#             palm_pinky_l,
#             pinky_01_l,
#             pinky_02_l,
#             pinky_03_l,
#             palm_ring_l,
#             ring_01_l,
#             ring_02_l,
#             ring_03_l,
#             palm_middle_l,
#             middle_01_l,
#             middle_02_l,
#             middle_03_l,
#             palm_index_l,
#             index_01_l,
#             index_02_l,
#             index_03_l,
#             thumb_01_l,
#             thumb_02_l,
#             thumb_03_l,
#         ]
#
#         excluded_bones_to_create = set()
#
#         if not fingers_bool_r:
#             excluded_bones_to_create.update(bone for bone in right_fingers if bone)
#             right_fingers = []
#
#         if not fingers_bool_l:
#             excluded_bones_to_create.update(bone for bone in left_fingers if bone)
#             left_fingers = []
#
#         derived_data = getattr(self.context, "derived_bones", {}) or {}
#         spine_data = derived_data.get("spines", {})
#         all_spines = list(spine_data.get("all_spines", []))
#
#         if not all_spines:
#             all_spines = [first_spine]
#             current = external_obj.data.bones.get(last_spine)
#
#             while current is not None:
#                 all_spines.append(current.name)
#
#                 if current.name == first_spine:
#                     break
#
#                 current = current.parent
#
#             all_spines = list(reversed(list(dict.fromkeys(all_spines))))
#
#         if first_spine not in all_spines:
#             all_spines.insert(0, first_spine)
#
#         if last_spine not in all_spines:
#             all_spines.append(last_spine)
#
#         second_spine = spine_data.get("second_spine") or (all_spines[1] if len(all_spines) > 1 else first_spine)
#         less_spine_bones = len(all_spines) <= 2
#
#         neck_data = derived_data.get("necks", {})
#         all_necks = list(neck_data.get("all_necks", []))
#
#         if not all_necks and first_neck:
#             all_necks = [first_neck]
#
#         if all_necks:
#             first_neck = all_necks[0]
#             last_neck = all_necks[-1]
#
#         spine_parenting = {}
#         all_spines_set = set(all_spines)
#
#         for spine_name in all_spines:
#             source_bone = external_obj.data.bones.get(spine_name)
#
#             if source_bone is None:
#                 continue
#
#             for child in source_bone.children:
#                 if child.name in all_spines_set:
#                     spine_parenting[child.name] = [spine_name, True]
#
#         neck_parenting = {}
#         all_necks_set = set(all_necks)
#
#         for neck_name in all_necks:
#             source_bone = external_obj.data.bones.get(neck_name)
#
#             if source_bone is None:
#                 continue
#
#             for child in source_bone.children:
#                 if child.name in all_necks_set:
#                     neck_parenting[child.name] = [neck_name, True]
#
#         # ------------------------------------------------------------
#         # Hilfsknochen im Originalrig
#         # ------------------------------------------------------------
#
#         ensure_mode(external_obj, "EDIT")
#         first_spine_edit = external_obj.data.edit_bones[first_spine]
#         second_spine_edit = external_obj.data.edit_bones.get(second_spine) or first_spine_edit
#
#         make_bone(external_obj, "skeleton:TransformationTarget")
#
#         torso_start = first_spine_edit.head.copy()
#         torso_end = second_spine_edit.head.copy()
#
#         if torso_start == torso_end:
#             torso_end = second_spine_edit.tail.copy()
#
#         make_bone(
#             external_obj,
#             "skeleton:torso_bone",
#             first_spine,
#             (torso_start + torso_end) / 2.0,
#             second_spine_edit.tail.copy(),
#         )
#
#         if copy_loc_constr:
#             for edit_bone in external_obj.data.edit_bones:
#                 edit_bone.inherit_scale = "NONE"
#
#         # ------------------------------------------------------------
#         # Metarig erzeugen
#         # ------------------------------------------------------------
#
#         ensure_mode(external_obj, "OBJECT")
#         bpy.ops.object.armature_human_metarig_add()
#
#         metarig_obj = bpy.context.active_object
#         metarig_obj.name = f"{external_name}_metarig"
#         metarig_obj.data.name = f"{external_name}_metarig_data"
#
#         ensure_mode(metarig_obj, "EDIT")
#
#         for edit_bone in list(metarig_obj.data.edit_bones):
#             metarig_obj.data.edit_bones.remove(edit_bone)
#
#         whitelisted_extra_bones = {
#             bone_name
#             for bone_name, data in self.context.extra_bone_data.items()
#             if data.get("needs_new_merge_bone", False)
#         }
#
#         standard_source_bones = {
#             value
#             for value in parameters.values()
#             if isinstance(value, str) and value
#         }
#         standard_source_bones.update(all_spines)
#         standard_source_bones.update(all_necks)
#
#         generated_helper_bones = {
#             "heel_l",
#             "heel_r",
#             "new_torso",
#             "skeleton:TransformationTarget",
#             "skeleton:torso_bone",
#         }
#
#         allowed_metarig_bones = standard_source_bones | whitelisted_extra_bones | generated_helper_bones
#
#         for bone_name in get_all_bone_names(external_obj, "DATA"):
#             if bone_name in excluded_bones_to_create or bone_name not in allowed_metarig_bones:
#                 continue
#
#             source_bone = external_obj.data.bones.get(bone_name)
#
#             if source_bone is None:
#                 continue
#
#             make_bone(
#                 metarig_obj,
#                 bone_name,
#                 None,
#                 external_obj.matrix_world @ source_bone.head_local,
#                 external_obj.matrix_world @ source_bone.tail_local,
#             )
#
#         make_bone(metarig_obj, "new_torso")
#
#         # ------------------------------------------------------------
#         # Heels erzeugen, falls keine existieren
#         # ------------------------------------------------------------
#
#         ensure_mode(metarig_obj, "EDIT")
#
#         if not heel_r and not heel_l:
#             generated_heels = {"heel_r": foot_r, "heel_l": foot_l}
#             heel_r = "heel_r"
#             heel_l = "heel_l"
#
#             for heel_name, parent_name in generated_heels.items():
#                 if not parent_name or parent_name not in metarig_obj.data.edit_bones:
#                     continue
#
#                 heel_bone = make_bone(metarig_obj, heel_name)
#                 parent_bone = metarig_obj.data.edit_bones[parent_name]
#
#                 if heel_bone is None:
#                     continue
#
#                 heel_bone.parent = parent_bone
#                 heel_bone.tail = parent_bone.head.copy()
#                 heel_bone.tail.z = parent_bone.head.z / 2.0
#
#                 delta = 1 if parent_bone.head.x > 0 else -1
#                 heel_bone.tail.x += (parent_bone.length / 2.0) * delta
#                 heel_bone.head = heel_bone.tail.copy()
#                 heel_bone.head.x -= parent_bone.length * delta
#
#         # ------------------------------------------------------------
#         # Parenting im Metarig
#         # ------------------------------------------------------------
#
#         parenting_bones = {}
#
#         def add_parent(child, parent, use_connect: bool) -> None:
#             if child:
#                 parenting_bones[child] = [parent, use_connect]
#
#         add_parent(head, last_neck, True)
#         add_parent(first_neck, last_spine, False)
#         add_parent(second_spine, first_spine, True)
#
#         for child, parent, connected in [
#             (thigh_l, first_spine, False),
#             (thigh_r, first_spine, False),
#             (calf_r, thigh_r, True),
#             (foot_r, calf_r, True),
#             (toe_r, foot_r, True),
#             (calf_l, thigh_l, True),
#             (foot_l, calf_l, True),
#             (toe_l, foot_l, True),
#             (clav_r, last_spine, False),
#             (uparm_r, clav_r, False),
#             (lowarm_r, uparm_r, True),
#             (hand_r, lowarm_r, True),
#             (clav_l, last_spine, False),
#             (uparm_l, clav_l, False),
#             (lowarm_l, uparm_l, True),
#             (hand_l, lowarm_l, True),
#         ]:
#             add_parent(child, parent, connected)
#
#         finger_parenting = {
#             palm_pinky_r: [hand_r, False],
#             pinky_01_r: [palm_pinky_r or hand_r, False],
#             pinky_02_r: [pinky_01_r, True],
#             pinky_03_r: [pinky_02_r, True],
#             palm_ring_r: [hand_r, False],
#             ring_01_r: [palm_ring_r or hand_r, False],
#             ring_02_r: [ring_01_r, True],
#             ring_03_r: [ring_02_r, True],
#             palm_middle_r: [hand_r, False],
#             middle_01_r: [palm_middle_r or hand_r, False],
#             middle_02_r: [middle_01_r, True],
#             middle_03_r: [middle_02_r, True],
#             palm_index_r: [hand_r, False],
#             index_01_r: [palm_index_r or hand_r, False],
#             index_02_r: [index_01_r, True],
#             index_03_r: [index_02_r, True],
#             thumb_01_r: [hand_r, False],
#             thumb_02_r: [thumb_01_r, True],
#             thumb_03_r: [thumb_02_r, True],
#             palm_pinky_l: [hand_l, False],
#             pinky_01_l: [palm_pinky_l or hand_l, False],
#             pinky_02_l: [pinky_01_l, True],
#             pinky_03_l: [pinky_02_l, True],
#             palm_ring_l: [hand_l, False],
#             ring_01_l: [palm_ring_l or hand_l, False],
#             ring_02_l: [ring_01_l, True],
#             ring_03_l: [ring_02_l, True],
#             palm_middle_l: [hand_l, False],
#             middle_01_l: [palm_middle_l or hand_l, False],
#             middle_02_l: [middle_01_l, True],
#             middle_03_l: [middle_02_l, True],
#             palm_index_l: [hand_l, False],
#             index_01_l: [palm_index_l or hand_l, False],
#             index_02_l: [index_01_l, True],
#             index_03_l: [index_02_l, True],
#             thumb_01_l: [hand_l, False],
#             thumb_02_l: [thumb_01_l, True],
#             thumb_03_l: [thumb_02_l, True],
#         }
#
#         for child, parent_config in finger_parenting.items():
#             add_parent(child, parent_config[0], parent_config[1])
#
#         parenting_bones.update(spine_parenting)
#         parenting_bones.update(neck_parenting)
#
#         ensure_mode(metarig_obj, "EDIT")
#         metarig_edit_bones = metarig_obj.data.edit_bones
#         all_metarig_edit_names = {bone.name for bone in metarig_edit_bones}
#         first_spine_bone = metarig_edit_bones.get(first_spine)
#         second_spine_bone = metarig_edit_bones.get(second_spine)
#         hip_spine_bool = False
#         second_spine_head_copy = None
#
#         if first_spine_bone is not None and second_spine_bone is not None:
#             second_spine_head_copy = second_spine_bone.head.copy()
#
#             if first_spine_bone.head == second_spine_bone.head and len(all_spines) > 1:
#                 hip_spine_bool = True
#                 first_spine_head = first_spine_bone.head.copy()
#                 first_spine_tail = first_spine_bone.tail.copy()
#                 first_spine_bone.head = first_spine_tail
#                 first_spine_bone.tail = first_spine_head
#
#         exclude_align = {
#             first_spine: second_spine,
#             last_spine: first_neck,
#             palm_index_l: index_01_l,
#             palm_index_r: index_01_r,
#             hand_l: None,
#             hand_r: None,
#             head: None,
#         }
#
#         if less_spine_bones:
#             exclude_align[first_spine] = None
#
#         for child_name, parent_config in parenting_bones.items():
#             parent_name, use_connect = parent_config
#
#             if not child_name or not parent_name:
#                 continue
#
#             if child_name not in all_metarig_edit_names or parent_name not in all_metarig_edit_names:
#                 continue
#
#             child_bone = metarig_edit_bones[child_name]
#             parent_bone = metarig_edit_bones[parent_name]
#             child_bone.parent = parent_bone
#
#             if parent_name in exclude_align:
#                 align_target = exclude_align[parent_name]
#
#                 if align_target and align_target in all_metarig_edit_names:
#                     parent_bone.tail = metarig_edit_bones[align_target].head.copy()
#             else:
#                 parent_bone.tail = child_bone.head.copy()
#
#             child_bone.use_connect = use_connect
#
#         for bone_name in whitelisted_extra_bones:
#             copy_edit_bone_roll_from_source(external_obj, metarig_obj, bone_name)
#
#         if hip_spine_bool and less_spine_bones and second_spine_bone is not None and second_spine_head_copy is not None:
#             second_spine_bone.head = second_spine_head_copy
#
#         if (
#             not hip_spine_bool
#             and less_spine_bones
#             and len(all_spines) == 2
#             and first_spine_bone is not None
#             and second_spine_head_copy is not None
#         ):
#             first_spine_bone.tail = second_spine_head_copy
#
#         # ------------------------------------------------------------
#         # Zusatzknochen bestimmen
#         # ------------------------------------------------------------
#
#         extra_bones = sorted(whitelisted_extra_bones)
#
#         for bone_name in extra_bones:
#             if bone_name not in metarig_obj.data.edit_bones:
#                 continue
#
#             source_bone = external_obj.data.bones.get(bone_name)
#             meta_bone = metarig_obj.data.edit_bones[bone_name]
#
#             if source_bone is None or source_bone.parent is None:
#                 continue
#
#             parent_name = source_bone.parent.name
#
#             if parent_name in metarig_obj.data.edit_bones:
#                 meta_bone.parent = metarig_obj.data.edit_bones[parent_name]
#
#         # ------------------------------------------------------------
#         # Hand-Tails korrigieren
#         # ------------------------------------------------------------
#
#         ensure_mode(metarig_obj, "EDIT")
#
#         for hand_name, thumb_name, finger_roots, fingers_bool in [
#             (hand_l, thumb_01_l, [pinky_01_l, ring_01_l, middle_01_l, index_01_l], fingers_bool_l),
#             (hand_r, thumb_01_r, [pinky_01_r, ring_01_r, middle_01_r, index_01_r], fingers_bool_r),
#         ]:
#             hand_bone = metarig_obj.data.edit_bones.get(hand_name)
#
#             if hand_bone is None:
#                 continue
#
#             children = [child for child in hand_bone.children if child.name != thumb_name]
#
#             if not children:
#                 children = [
#                     metarig_obj.data.edit_bones[name]
#                     for name in finger_roots
#                     if name in metarig_obj.data.edit_bones
#                 ]
#
#             median = average_bone_points(children, "head")
#
#             if fingers_bool and median is not None:
#                 hand_bone.tail = median
#
#         # ------------------------------------------------------------
#         # Hand-Orientierung ohne Finger grob reparieren
#         # ------------------------------------------------------------
#
#         hands_orient = {
#             hand_r: [lowarm_r, fingers_bool_r],
#             hand_l: [lowarm_l, fingers_bool_l],
#         }
#
#         for hand_name, orient_config in hands_orient.items():
#             parent_arm_name, has_fingers = orient_config
#
#             if has_fingers:
#                 continue
#
#             if hand_name not in metarig_obj.data.edit_bones or parent_arm_name not in metarig_obj.data.edit_bones:
#                 continue
#
#             hand_bone = metarig_obj.data.edit_bones[hand_name]
#             parent_arm_bone = metarig_obj.data.edit_bones[parent_arm_name]
#             original_length = parent_arm_bone.length
#             parent_arm_bone.length *= 1.5
#             hand_bone.tail = parent_arm_bone.tail.copy()
#             parent_arm_bone.length = original_length
#
#         # ------------------------------------------------------------
#         # Letzte Fingerknochen anhand Vertex Groups verlängern
#         # ------------------------------------------------------------
#
#         last_finger_bones = [
#             pinky_03_r,
#             ring_03_r,
#             middle_03_r,
#             index_03_r,
#             thumb_03_r,
#             pinky_03_l,
#             ring_03_l,
#             middle_03_l,
#             index_03_l,
#             thumb_03_l,
#         ]
#
#         for finger_name in last_finger_bones:
#             if not finger_name or finger_name not in metarig_obj.data.edit_bones:
#                 continue
#
#             metarig_finger = metarig_obj.data.edit_bones[finger_name]
#             source_finger = external_obj.data.bones.get(finger_name)
#
#             if source_finger is None or source_finger.children or metarig_finger.children:
#                 continue
#
#             for mesh_obj in self.context.bound_meshes:
#                 vertex_group = mesh_obj.vertex_groups.get(finger_name)
#
#                 if vertex_group is None:
#                     continue
#
#                 weighted_vectors = [
#                     mesh_obj.matrix_world @ vertex.co
#                     for vertex in mesh_obj.data.vertices
#                     if vertex_group.index in {group.group for group in vertex.groups}
#                 ]
#
#                 median = average_vectors(weighted_vectors)
#
#                 if median is not None:
#                     metarig_finger.tail = median
#                     break
#
#         # ------------------------------------------------------------
#         # Finger-Roll
#         # ------------------------------------------------------------
#
#         all_fingers_but_thumbs = list(dict.fromkeys(right_fingers + left_fingers))
#
#         for thumb_name in [
#             thumb_01_r,
#             thumb_02_r,
#             thumb_03_r,
#             thumb_01_l,
#             thumb_02_l,
#             thumb_03_l,
#         ]:
#             if thumb_name in all_fingers_but_thumbs:
#                 all_fingers_but_thumbs.remove(thumb_name)
#
#         all_fingers_but_thumbs = [finger_name for finger_name in all_fingers_but_thumbs if finger_name]
#         metarig_obj.data.show_axes = True
#
#         for finger_name in all_fingers_but_thumbs:
#             if finger_name not in metarig_obj.data.edit_bones:
#                 continue
#
#             finger_bone = metarig_obj.data.edit_bones[finger_name]
#             roll = finger_bone.tail.copy()
#             roll.z -= 1.0
#             finger_bone.align_roll(-roll)
#
#         ensure_mode(metarig_obj, "POSE")
#
#         for finger_name in all_fingers_but_thumbs:
#             pose_bone = metarig_obj.pose.bones.get(finger_name)
#
#             if pose_bone is not None and hasattr(pose_bone.rigify_parameters, "primary_rotation_axis"):
#                 pose_bone.rigify_parameters.primary_rotation_axis = "X"
#
#         # ------------------------------------------------------------
#         # Rigify-Typen setzen
#         # ------------------------------------------------------------
#
#         rigify_types = {
#             first_neck: "spines.super_head",
#             clav_l: "basic.super_copy",
#             clav_r: "basic.super_copy",
#             uparm_r: "limbs.super_limb",
#             uparm_l: "limbs.super_limb",
#             palm_index_r: "limbs.super_palm",
#             pinky_01_r: "limbs.super_finger",
#             ring_01_r: "limbs.super_finger",
#             middle_01_r: "limbs.super_finger",
#             index_01_r: "limbs.super_finger",
#             thumb_01_r: "limbs.super_finger",
#             palm_index_l: "limbs.super_palm",
#             pinky_01_l: "limbs.super_finger",
#             ring_01_l: "limbs.super_finger",
#             middle_01_l: "limbs.super_finger",
#             index_01_l: "limbs.super_finger",
#             thumb_01_l: "limbs.super_finger",
#             first_spine: "spines.basic_spine",
#             thigh_l: "limbs.leg",
#             thigh_r: "limbs.leg",
#         }
#
#         if less_spine_bones:
#             for spine_name in all_spines:
#                 rigify_types[spine_name] = "basic.super_copy"
#
#             rigify_types[first_neck] = "basic.super_copy"
#             rigify_types[head] = "basic.super_copy"
#
#         all_metarig_pose_names = get_all_bone_names(metarig_obj, "POSE")
#
#         for bone_name, rig_type in rigify_types.items():
#             if not bone_name or bone_name not in all_metarig_pose_names:
#                 continue
#
#             pose_bone = metarig_obj.pose.bones[bone_name]
#             pose_bone.rigify_type = rig_type
#             rigify_param = pose_bone.rigify_parameters
#
#             if bone_name in {thigh_r, thigh_l} and hasattr(rigify_param, "extra_ik_toe"):
#                 rigify_param.extra_ik_toe = True
#
#             if bone_name == last_neck and hasattr(rigify_param, "connect_chain"):
#                 rigify_param.connect_chain = True
#
#             if bone_name in {clav_r, clav_l} and hasattr(rigify_param, "super_copy_widget_type"):
#                 rigify_param.super_copy_widget_type = "shoulder"
#
#         # ------------------------------------------------------------
#         # Bone Collections / Layer im Metarig
#         # ------------------------------------------------------------
#
#         layer_bones = {
#             head: 0,
#             uparm_l: 7,
#             lowarm_l: 7,
#             hand_l: 7,
#             uparm_r: 10,
#             lowarm_r: 10,
#             hand_r: 10,
#             thigh_l: 13,
#             calf_l: 13,
#             foot_l: 13,
#             toe_l: 13,
#             heel_l: 13,
#             thigh_r: 16,
#             calf_r: 16,
#             foot_r: 16,
#             toe_r: 16,
#             heel_r: 16,
#             clav_r: 3,
#             clav_l: 3,
#             "skeleton:torso_bone": 3,
#             "new_torso": 3,
#             first_neck: 3,
#         }
#
#         for spine_name in all_spines:
#             layer_bones[spine_name] = 3
#
#         for neck_name in all_necks:
#             layer_bones[neck_name] = 3
#
#         finger_bones = [
#             palm_pinky_r,
#             pinky_01_r,
#             pinky_02_r,
#             pinky_03_r,
#             palm_ring_r,
#             ring_01_r,
#             ring_02_r,
#             ring_03_r,
#             palm_middle_r,
#             middle_01_r,
#             middle_02_r,
#             middle_03_r,
#             palm_index_r,
#             index_01_r,
#             index_02_r,
#             index_03_r,
#             thumb_01_r,
#             thumb_02_r,
#             thumb_03_r,
#             palm_pinky_l,
#             pinky_01_l,
#             pinky_02_l,
#             pinky_03_l,
#             palm_ring_l,
#             ring_01_l,
#             ring_02_l,
#             ring_03_l,
#             palm_middle_l,
#             middle_01_l,
#             middle_02_l,
#             middle_03_l,
#             palm_index_l,
#             index_01_l,
#             index_02_l,
#             index_03_l,
#             thumb_01_l,
#             thumb_02_l,
#             thumb_03_l,
#         ]
#
#         for bone_name in finger_bones:
#             if bone_name:
#                 layer_bones[bone_name] = 5
#
#         if less_spine_bones:
#             layer_bones[first_spine] = 3
#             layer_bones[first_neck] = 3
#             layer_bones[head] = 3
#
#         all_metarig_data_names = set(get_all_bone_names(metarig_obj, "DATA"))
#
#         for bone_name, layer_index in layer_bones.items():
#             if bone_name in all_metarig_data_names:
#                 assign_bone_to_layer_group(metarig_obj, bone_name, layer_index)
#
#         ensure_mode(metarig_obj, "POSE")
#         initialisiere_standard_bone_collections(metarig_obj.data)
#         metarig_extra_group_ui_rows = build_extra_group_ui_rows(metarig_obj.data)
#
#         for bone_name in extra_bones:
#             pose_bone = metarig_obj.pose.bones.get(bone_name)
#
#             if pose_bone is None:
#                 continue
#
#             pose_bone.rigify_type = "basic.super_copy"
#             extra_data = self.context.extra_bone_data.get(bone_name, {})
#             group_name = sanitize_extra_group_name(extra_data.get("whitelist_group_name", "Additional"))
#             ui_row = metarig_extra_group_ui_rows.get(group_name)
#
#             if ui_row is not None:
#                 assign_bone_to_extra_group_collection(metarig_obj, bone_name, group_name, ui_row)
#             else:
#                 assign_bone_to_layer_group(metarig_obj, bone_name, 27)
#
#         # ------------------------------------------------------------
#         # new_torso orientieren
#         # ------------------------------------------------------------
#
#         ensure_mode(metarig_obj, "EDIT")
#         new_torso_bone = metarig_obj.data.edit_bones.get("new_torso")
#         spine_bone = metarig_obj.data.edit_bones.get(second_spine)
#         first_spine_bone = metarig_obj.data.edit_bones.get(first_spine)
#
#         if new_torso_bone is not None and spine_bone is not None and first_spine_bone is not None:
#             new_torso_bone.tail = (first_spine_bone.head + first_spine_bone.tail) / 2.0
#             new_torso_bone.head = (spine_bone.head + spine_bone.tail) / 2.0
#
#         # ------------------------------------------------------------
#         # kleine Positionskorrektur für Arme/Beine
#         # ------------------------------------------------------------
#
#         all_z = [(external_obj.matrix_world @ Vector(corner)).z for corner in external_obj.bound_box]
#         skeleton_height = max(all_z) - min(all_z) if all_z else 1.0
#         skeleton_height_percent = skeleton_height * 0.002
#
#         for bone_name, offset in {
#             uparm_l: skeleton_height_percent,
#             uparm_r: skeleton_height_percent,
#             thigh_l: -skeleton_height_percent,
#             thigh_r: -skeleton_height_percent,
#         }.items():
#             if bone_name in metarig_obj.data.edit_bones:
#                 metarig_obj.data.edit_bones[bone_name].tail.y += offset
#
#         first_spine_bone = metarig_obj.data.edit_bones.get(first_spine)
#
#         if hip_spine_bool and first_spine_bone is not None:
#             first_spine_bone.head = first_spine_bone.tail.copy()
#             first_spine_bone.head.z -= skeleton_height_percent
#
#         # ------------------------------------------------------------
#         # IK / FK / Tweak Layer-Parameter
#         # ------------------------------------------------------------
#
#         ensure_mode(metarig_obj, "POSE")
#
#         limb_layer_params = {
#             uparm_l: {"ik_layers": 7, "fk_layers": 8, "tweak_layers": 9},
#             uparm_r: {"ik_layers": 10, "fk_layers": 11, "tweak_layers": 12},
#             thigh_l: {"ik_layers": 13, "fk_layers": 14, "tweak_layers": 15},
#             thigh_r: {"ik_layers": 16, "fk_layers": 17, "tweak_layers": 18},
#         }
#
#         for bone_name, layer_config in limb_layer_params.items():
#             if bone_name not in metarig_obj.pose.bones:
#                 continue
#
#             rigify_param = metarig_obj.pose.bones[bone_name].rigify_parameters
#
#             for attr_name, layer_index in layer_config.items():
#                 set_rigify_layer_param(metarig_obj, rigify_param, attr_name, layer_index)
#
#         extra_layer_params = {
#             first_spine: {"fk_layers": 4, "tweak_layers": 4},
#             first_neck: {"tweak_layers": 1},
#         }
#
#         for finger_name in finger_bones:
#             if finger_name in all_metarig_pose_names:
#                 extra_layer_params[finger_name] = {"tweak_layers": 6}
#
#         for bone_name, layer_config in extra_layer_params.items():
#             if bone_name not in metarig_obj.pose.bones:
#                 continue
#
#             rigify_param = metarig_obj.pose.bones[bone_name].rigify_parameters
#
#             for attr_name, layer_index in layer_config.items():
#                 set_rigify_layer_param(metarig_obj, rigify_param, attr_name, layer_index)
#
#         root_pose_bone = metarig_obj.pose.bones.get("root")
#
#         if root_pose_bone is not None:
#             root_pose_bone.rigify_type = ""
#
#         # ------------------------------------------------------------
#         # Rig erzeugen
#         # ------------------------------------------------------------
#
#         ensure_mode(metarig_obj, "OBJECT")
#         make_object_active(metarig_obj)
#         rigify.generate.generate_rig(bpy.context, metarig_obj)
#
#         rigify_obj = bpy.context.active_object
#
#         if rigify_obj is None or rigify_obj.type != "ARMATURE":
#             raise RuntimeError("Rigify hat kein gültiges Rig erzeugt")
#
#         rigify_obj.name = target_rig_name
#         rigify_obj.data.name = f"{target_rig_name}_data"
#
#         initialisiere_standard_bone_collections(rigify_obj.data)
#         rigify_extra_group_ui_rows = build_extra_group_ui_rows(rigify_obj.data)
#         extra_collection_names = apply_extra_group_collections(rigify_obj, rigify_extra_group_ui_rows)
#
#         repariere_standard_control_collections(rigify_obj)
#         normalisiere_rigify_sichtbarkeit(rigify_obj)
#         normalisiere_rigify_standardfarben(rigify_obj)
#
#         set_visible_rig_layers(
#             rigify_obj,
#             DEFAULT_VISIBLE_RIG_LAYER_INDICES,
#             extra_collection_names,
#         )
#
#         # ------------------------------------------------------------
#         # Constraints vom erzeugten Rigify-Rig zum Originalrig
#         # ------------------------------------------------------------
#
#         ensure_mode(external_obj, "OBJECT")
#         ensure_mode(rigify_obj, "OBJECT")
#
#         external_obj.data.pose_position = "REST"
#         rigify_obj.data.pose_position = "REST"
#
#         all_external_pose_names = get_all_bone_names(external_obj, "POSE")
#         all_rigify_pose_names = get_all_bone_names(rigify_obj, "POSE")
#
#         for bone_name in extra_bones:
#             if bone_name in all_rigify_pose_names:
#                 rigify_obj.pose.bones[bone_name].bone.inherit_scale = "NONE"
#
#         for ik_fk_name in [
#             "upperarm_parent_r",
#             "thigh_parent_r",
#             "upperarm_parent_l",
#             "thigh_parent_l",
#             "upper_arm_parent.R",
#             "thigh_parent.R",
#             "upper_arm_parent.L",
#             "thigh_parent.L",
#         ]:
#             pose_bone = rigify_obj.pose.bones.get(ik_fk_name)
#
#             if pose_bone is not None and "IK_FK" in pose_bone:
#                 pose_bone["IK_FK"] = 0
#
#         constraints_map = {}
#
#         for source_name, mapping in self.context.standard_constraint_map.items():
#             target_name = mapping.get("constraint_target")
#
#             if source_name and target_name:
#                 constraints_map[source_name] = [target_name, bool(mapping.get("copy_location", False))]
#
#         for spine_name in all_spines:
#             target_name = f"DEF-{spine_name}"
#
#             if target_name in all_rigify_pose_names:
#                 constraints_map[spine_name] = [target_name, True]
#
#         for neck_name in all_necks:
#             target_name = f"DEF-{neck_name}"
#
#             if target_name in all_rigify_pose_names:
#                 constraints_map[neck_name] = [target_name, True]
#
#         if less_spine_bones:
#             constraints_map.pop("skeleton:torso_bone", None)
#
#         ensure_mode(external_obj, "POSE")
#
#         for source_name, target_config in constraints_map.items():
#             target_name, copy_location = target_config
#
#             if source_name not in all_external_pose_names or target_name not in all_rigify_pose_names:
#                 continue
#
#             source_pose_bone = external_obj.pose.bones[source_name]
#             target_pose_bone = rigify_obj.pose.bones[target_name]
#             source_rotation, target_rotation = get_rotation_diff(
#                 source_pose_bone,
#                 external_obj,
#                 target_pose_bone,
#                 rigify_obj,
#             )
#             rotation_diff = target_rotation.rotation_difference(source_rotation).to_euler()
#
#             create_constraint(
#                 source_pose_bone,
#                 external_obj,
#                 target_name,
#                 rigify_obj,
#                 rotation_diff,
#                 rotation_diff.order,
#                 copy_location,
#                 copy_loc_constr,
#             )
#
#         for bone_name in extra_bones:
#             if bone_name not in all_external_pose_names or bone_name not in all_rigify_pose_names:
#                 continue
#
#             source_pose_bone = external_obj.pose.bones[bone_name]
#             target_pose_bone = rigify_obj.pose.bones[bone_name]
#             source_rotation, target_rotation = get_rotation_diff(
#                 source_pose_bone,
#                 external_obj,
#                 target_pose_bone,
#                 rigify_obj,
#             )
#             rotation_diff = target_rotation.rotation_difference(source_rotation).to_euler()
#
#             create_constraint(
#                 source_pose_bone,
#                 external_obj,
#                 bone_name,
#                 rigify_obj,
#                 rotation_diff,
#                 rotation_diff.order,
#                 True,
#                 False,
#             )
#
#         # ------------------------------------------------------------
#         # Custom Shape Sonderfälle + finale Normalisierung
#         # ------------------------------------------------------------
#
#         head_pose_bone = rigify_obj.pose.bones.get("head")
#
#         if head_pose_bone is not None:
#             head_pose_bone.custom_shape_scale_xyz = (1.5, 1.5, 1.5)
#
#         extra_collection_names = apply_extra_group_collections(rigify_obj, rigify_extra_group_ui_rows)
#         repariere_standard_control_collections(rigify_obj)
#         normalisiere_rigify_sichtbarkeit(rigify_obj)
#         normalisiere_rigify_standardfarben(rigify_obj)
#
#         set_visible_rig_layers(
#             rigify_obj,
#             DEFAULT_VISIBLE_RIG_LAYER_INDICES,
#             extra_collection_names,
#         )
#
#         rigify_obj.data.pose_position = "POSE"
#         external_obj.data.pose_position = "POSE"
#
#         ensure_mode(external_obj, "OBJECT")
#         bpy.ops.object.select_all(action="DESELECT")
#
#         metarig_obj.hide_set(True)
#         external_obj.select_set(True)
#         rigify_obj.select_set(True)
#         bpy.context.view_layer.objects.active = external_obj
#         ensure_mode(external_obj, "POSE")
#
#     # ============================================================
#     # Custom Shapes übernehmen
#     # ============================================================
#
#     def uebernehme_custom_shapes(self, rigify_obj, target_name_key: str) -> int:
#         if rigify_obj is None:
#             return 0
#
#         copied_count = self.inherit_missing_custom_shapes(rigify_obj, target_name_key)
#         repariere_standard_control_collections(rigify_obj)
#         normalisiere_rigify_sichtbarkeit(rigify_obj)
#         normalisiere_rigify_standardfarben(rigify_obj)
#         return copied_count
#
#     def copy_bone_color(self, source_color, target_color) -> None:
#         target_color.palette = source_color.palette
#
#         for custom_field in ("normal", "select", "active"):
#             color = getattr(source_color.custom, custom_field)
#             setattr(target_color.custom, custom_field, color)
#
#     def resolve_target_transform_bone(self, source_pose_bone, rigify_obj, target_name_key: str):
#         transform_bone = getattr(source_pose_bone, "custom_shape_transform", None)
#
#         if transform_bone is None:
#             return None
#
#         if transform_bone.name == Wirbelsäule.WURZEL:
#             return rigify_obj.pose.bones.get(Wirbelsäule.WURZEL)
#
#         transform_mapping = self.context.source_to_target_map.get(transform_bone.name)
#
#         if transform_mapping is not None:
#             for key in (target_name_key, "constraint_target", "merge_target"):
#                 target_name = transform_mapping.get(key)
#
#                 if target_name and rigify_obj.pose.bones.get(target_name) is not None:
#                     return rigify_obj.pose.bones[target_name]
#
#         return rigify_obj.pose.bones.get(transform_bone.name)
#
#     def copy_custom_shape_settings(self, source_pose_bone, target_pose_bone, target_transform_bone) -> None:
#         target_pose_bone.custom_shape = source_pose_bone.custom_shape
#         target_pose_bone.custom_shape_translation = source_pose_bone.custom_shape_translation.copy()
#         target_pose_bone.custom_shape_rotation_euler = source_pose_bone.custom_shape_rotation_euler.copy()
#         target_pose_bone.custom_shape_scale_xyz = tuple(source_pose_bone.custom_shape_scale_xyz)
#         target_pose_bone.use_custom_shape_bone_size = source_pose_bone.use_custom_shape_bone_size
#         target_pose_bone.custom_shape_wire_width = source_pose_bone.custom_shape_wire_width
#         target_pose_bone.custom_shape_transform = target_transform_bone
#
#     def is_generic_circle_widget(self, widget_obj) -> bool:
#         if widget_obj is None or getattr(widget_obj, "type", None) != "MESH":
#             return False
#
#         mesh = getattr(widget_obj, "data", None)
#
#         if mesh is None or len(mesh.polygons) != 0:
#             return False
#
#         return (
#             len(mesh.vertices) == GENERIC_CIRCLE_WIDGET_VERTEX_COUNT
#             and len(mesh.edges) == GENERIC_CIRCLE_WIDGET_VERTEX_COUNT
#         )
#
#     def should_replace_custom_shape(self, source_pose_bone, target_pose_bone, mapping) -> bool:
#         if source_pose_bone.custom_shape is None:
#             return False
#
#         if not mapping.get("is_standard", True) and source_pose_bone.bone.hide:
#             return False
#
#         if target_pose_bone.custom_shape is None:
#             return True
#
#         if target_pose_bone.name == Wirbelsäule.WURZEL:
#             return True
#
#         if not mapping.get("is_standard", True):
#             return True
#
#         return self.is_generic_circle_widget(target_pose_bone.custom_shape)
#
#     def iter_shape_mappings(self, rigify_obj, target_name_key: str):
#         yielded_pairs = set()
#
#         for source_bone_name, mapping in self.context.source_to_target_map.items():
#             target_bone_name = mapping.get(target_name_key)
#
#             if not target_bone_name:
#                 continue
#
#             pair_key = (source_bone_name, target_bone_name)
#
#             if pair_key in yielded_pairs:
#                 continue
#
#             yielded_pairs.add(pair_key)
#             yield source_bone_name, target_bone_name, mapping
#
#         source_root = self.source_armature.pose.bones.get(Wirbelsäule.WURZEL)
#         target_root = rigify_obj.pose.bones.get(Wirbelsäule.WURZEL)
#
#         if source_root is None or target_root is None:
#             return
#
#         pair_key = (Wirbelsäule.WURZEL, Wirbelsäule.WURZEL)
#
#         if pair_key not in yielded_pairs:
#             yield Wirbelsäule.WURZEL, Wirbelsäule.WURZEL, {
#                 "source_bone": Wirbelsäule.WURZEL,
#                 "is_standard": False,
#             }
#
#     def inherit_missing_custom_shapes(self, rigify_obj, target_name_key: str) -> int:
#         copied_count = 0
#
#         for source_bone_name, target_bone_name, mapping in self.iter_shape_mappings(
#             rigify_obj,
#             target_name_key,
#         ):
#             source_pose_bone = self.source_armature.pose.bones.get(source_bone_name)
#             target_pose_bone = rigify_obj.pose.bones.get(target_bone_name)
#
#             if source_pose_bone is None or target_pose_bone is None:
#                 continue
#
#             if not self.should_replace_custom_shape(source_pose_bone, target_pose_bone, mapping):
#                 continue
#
#             target_transform_bone = self.resolve_target_transform_bone(
#                 source_pose_bone,
#                 rigify_obj,
#                 target_name_key,
#             )
#
#             self.copy_custom_shape_settings(source_pose_bone, target_pose_bone, target_transform_bone)
#
#             if not mapping.get("is_standard", True):
#                 self.copy_pose_transform(source_pose_bone, target_pose_bone)
#                 self.copy_bone_color(source_pose_bone.color, target_pose_bone.color)
#                 self.copy_bone_color(source_pose_bone.bone.color, target_pose_bone.bone.color)
#
#             copied_count += 1
#
#         return copied_count
#
#     def copy_pose_transform(self, source_pose_bone, target_pose_bone) -> None:
#         target_pose_bone.location = source_pose_bone.location.copy()
#         target_pose_bone.scale = source_pose_bone.scale.copy()
#         target_pose_bone.rotation_mode = source_pose_bone.rotation_mode
#
#         if source_pose_bone.rotation_mode == "QUATERNION":
#             target_pose_bone.rotation_quaternion = source_pose_bone.rotation_quaternion.copy()
#         elif source_pose_bone.rotation_mode == "AXIS_ANGLE":
#             target_pose_bone.rotation_axis_angle = source_pose_bone.rotation_axis_angle[:]
#         else:
#             target_pose_bone.rotation_euler = source_pose_bone.rotation_euler.copy()
#
# def verstecke_interne_rigify_knochen(rig_obj) -> None:
#     if rig_obj is None or rig_obj.type != "ARMATURE":
#         return
#
#     for bone in rig_obj.data.bones:
#         if ist_interner_rigify_knochen(bone.name):
#             bone.hide = True
#             bone.hide_select = True
#
# def entferne_interne_knochen_aus_standard_collections(rig_obj) -> None:
#     if rig_obj is None or rig_obj.type != "ARMATURE":
#         return
#
#     armature_data = rig_obj.data
#
#     if not uses_bone_collections(armature_data):
#         return
#
#     for bone in armature_data.bones:
#         if not ist_interner_rigify_knochen(bone.name):
#             continue
#
#         for collection in armature_data.collections_all:
#             if collection.name not in STANDARD_COLLECTION_NAMES:
#                 continue
#
#             try:
#                 collection.unassign(bone)
#             except RuntimeError:
#                 pass
#
# def normalisiere_rigify_sichtbarkeit(rig_obj) -> None:
#     verstecke_interne_rigify_knochen(rig_obj)
#     entferne_interne_knochen_aus_standard_collections(rig_obj)
