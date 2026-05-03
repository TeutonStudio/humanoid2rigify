import bpy

from bpy.props import (
    StringProperty,
    BoolProperty,
    EnumProperty,
    CollectionProperty,
)

from .__methoden__ import my_settings_callback


DEFAULT_MERGE_EXTRA_BONE_WHITELIST = [
    "rig",
    "properties",
    "clothes",
    "gen_donger_*",
    "gen_teste_r",
    "gen_teste_l",
    "anus_open",
]


class MergeWhitelistItem(bpy.types.PropertyGroup):
    pattern: StringProperty(name="Pattern", default="")


def ensure_merge_whitelist(scene):
    collection = getattr(scene, "merge_extra_bone_whitelist", None)
    if collection is None or len(collection) != 0:
        return

    for pattern in DEFAULT_MERGE_EXTRA_BONE_WHITELIST:
        item = collection.add()
        item.pattern = pattern


def unregister():
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)


CLASSES = [
    MergeWhitelistItem,
]


PROPS = [
    ("copy_loc_constr", BoolProperty(name="Stretch", default=True)),
    ("fingers_bool_r", BoolProperty(name="right fingers", default=True)),
    ("fingers_bool_l", BoolProperty(name="left fingers", default=True)),
    ("merge_extra_bone_whitelist", CollectionProperty(type=MergeWhitelistItem)),
    (
        "generation_mode",
        EnumProperty(
            name="Erzeugungsmodus",
            items=[
                (
                    "CONSTRAINT_NEW_RIGIFY",
                    "Constraint auf neues Rigify",
                    "Das alte Rig wird per Constraints auf das neue Rigify gelegt",
                ),
                (
                    "DEFORM_RIG_CONSTRAINT_NEW_RIGIFY",
                    "rig zu deformationsrig constraint auf neues rigify",
                    "Das alte Rig wird auf ein Deformationsrig reduziert und vom neuen Rigify getrieben",
                ),
                (
                    "MERGE_WITH_NEW_RIGIFY",
                    "mit neuem rigify verschmelzen",
                    "Meshes und Deformation sollen direkt auf das neue Rigify uebergehen",
                ),
            ],
            default="CONSTRAINT_NEW_RIGIFY",
        ),
    ),

    # # ===========================================================
    # mapping
    ("json_file_name", StringProperty(name="File Name", default="")),
    ("rename_preset", StringProperty(name="New Name", default="")),
    ("presets", EnumProperty(name="Presets", items=my_settings_callback)),


    # # ===========================================================
    # # ===========================================================
    # # ===========================================================
    # # random fbx
    # ("head", StringProperty(name="head", default="head")),
    # ("first_neck", StringProperty(name="1st neck", default="neck01")),
    # ("last_neck", StringProperty(name="last neck", default="neck01")),

    # ("spine", StringProperty(name="spine", default="spine05")),
    # ("last_spine", StringProperty(name="last_spine", default="neck_01")),

    # ("clav_l", StringProperty(name="clav_l", default="shoulder01.L")),
    # ("clav_r", StringProperty(name="clav_r", default="shoulder01.R")),
    # ("uparm_l", StringProperty(name="uparm_l", default="upperarm02.L")),
    # ("uparm_r", StringProperty(name="uparm_l", default="upperarm02.R")),
    # ("lowarm_l", StringProperty(name="lowarm_l", default="lowerarm02.L")),
    # ("lowarm_r", StringProperty(name="lowarm_l", default="lowerarm02.R")),
    # ("hand_l", StringProperty(name="hand_l", default="wrist.L")),
    # ("hand_r", StringProperty(name="hand_r", default="wrist.R")),

    # # fingers
    # ("palm_pinky_r", StringProperty(name="palm_pinky_r", default="metacarpal4.R")),
    # ("pinky_01_r", StringProperty(name="pinky_1_r", default="finger5-1.R")),
    # ("pinky_02_r", StringProperty(name="pinky_2_r", default="finger5-2.R")),
    # ("pinky_03_r", StringProperty(name="pinky_3_r", default="finger5-3.R")),
    # ("palm_ring_r", StringProperty(name="palm_ring_r", default="metacarpal3.R")),
    # ("ring_01_r", StringProperty(name="ring_1_r", default="finger4-1.R")),
    # ("ring_02_r", StringProperty(name="ring_2_r", default="finger4-2.R")),
    # ("ring_03_r", StringProperty(name="ring_3_r", default="finger4-3.R")),
    # ("palm_middle_r", StringProperty(name="palm_middle_r", default="metacarpal2.R")),
    # ("middle_01_r", StringProperty(name="middle_1_r", default="finger3-1.R")),
    # ("middle_02_r", StringProperty(name="middle_2_r", default="finger3-2.R")),
    # ("middle_03_r", StringProperty(name="middle_3_r", default="finger3-3.R")),
    # ("palm_index_r", StringProperty(name="palm_index_r", default="metacarpal1.R")),
    # ("index_01_r", StringProperty(name="index_1_r", default="finger2-1.R")),
    # ("index_02_r", StringProperty(name="index_2_r", default="finger2-2.R")),
    # ("index_03_r", StringProperty(name="index_3_r", default="finger2-3.R")),
    # ("thumb_01_r", StringProperty(name="thumb_0_r", default="finger1-1.R")),
    # ("thumb_02_r", StringProperty(name="thumb_2_r", default="finger1-2.R")),
    # ("thumb_03_r", StringProperty(name="thumb_3_r", default="finger1-3.R")),
    # # left fingers
    # ("palm_pinky_l", StringProperty(name="palm_pinky_L", default="metacarpal4.L")),
    # ("pinky_01_l", StringProperty(name="pinky_1_L", default="finger5-1.L")),
    # ("pinky_02_l", StringProperty(name="pinky_2_L", default="finger5-2.L")),
    # ("pinky_03_l", StringProperty(name="pinky_3_L", default="finger5-3.L")),
    # ("palm_ring_l", StringProperty(name="palm_ring_L", default="metacarpal3.L")),
    # ("ring_01_l", StringProperty(name="ring_1_L", default="finger4-1.L")),
    # ("ring_02_l", StringProperty(name="ring_2_L", default="finger4-2.L")),
    # ("ring_03_l", StringProperty(name="ring_3_L", default="finger4-3.L")),
    # ("palm_middle_l", StringProperty(name="palm_middle_L", default="metacarpal2.L")),
    # ("middle_01_l", StringProperty(name="middle_1_L", default="finger3-1.L")),
    # ("middle_02_l", StringProperty(name="middle_2_L", default="finger3-2.L")),
    # ("middle_03_l", StringProperty(name="middle_3_L", default="finger3-3.L")),
    # ("palm_index_l", StringProperty(name="palm_index_L", default="metacarpal1.L")),
    # ("index_01_l", StringProperty(name="index_1_L", default="finger2-1.L")),
    # ("index_02_l", StringProperty(name="index_2_L", default="finger2-2.L")),
    # ("index_03_l", StringProperty(name="index_3_L", default="finger2-3.L")),
    # ("thumb_01_l", StringProperty(name="thumb_0_L", default="finger1-1.L")),
    # ("thumb_02_l", StringProperty(name="thumb_2_L", default="finger1-2.L")),
    # ("thumb_03_l", StringProperty(name="thumb_3_L", default="finger1-3.L")),

    # # legs
    # ("thigh_l", StringProperty(name="thigh_l", default="upperleg02.L")),
    # ("thigh_r", StringProperty(name="thigh_r", default="upperleg02.R")),
    # ("calf_l", StringProperty(name="calf_l", default="lowerleg01.L")),
    # ("calf_r", StringProperty(name="calf_r", default="lowerleg01.R")),
    # ("foot_l", StringProperty(name="foot_l", default="foot.L")),
    # ("foot_r", StringProperty(name="foot_r", default="foot.R")),
    # ("toe_l", StringProperty(name="toe_l", default="toe2-1.L")),
    # ("toe_r", StringProperty(name="toe_r", default="toe2-1.R")),
    # ("heel_r", StringProperty(name="heel_r", default="")),
    # ("heel_l", StringProperty(name="heel_l", default="")),

    # # ===========================================================
    # # fortnite
    # ("head", StringProperty(name="head", default="head")),
    # ("first_neck", StringProperty(name="1st neck", default="neck_01")),
    # ("last_neck", StringProperty(name="last neck", default="neck_01")),

    # ("first_spine", StringProperty(name="1st spine", default="spine_01")),
    # ("last_spine", StringProperty(name="last spine", default="spine_05")),

    # ("clav_l", StringProperty(name="clav_l", default="clavicle_l")),
    # ("clav_r", StringProperty(name="clav_r", default="clavicle_r")),
    # ("uparm_l", StringProperty(name="uparm_l", default="upperarm_l")),
    # ("uparm_r", StringProperty(name="uparm_l", default="upperarm_r")),
    # ("lowarm_l", StringProperty(name="lowarm_l", default="lowerarm_l")),
    # ("lowarm_r", StringProperty(name="lowarm_l", default="lowerarm_r")),
    # ("hand_l", StringProperty(name="hand_l", default="hand_l")),
    # ("hand_r", StringProperty(name="hand_r", default="hand_r")),

    # # fingers
    # ("palm_pinky_r", StringProperty(name="palm_pinky_r", default="pinky_metacarpal_r")),
    # ("pinky_01_r", StringProperty(name="pinky_1_r", default="pinky_01_r")),
    # ("pinky_02_r", StringProperty(name="pinky_2_r", default="pinky_02_r")),
    # ("pinky_03_r", StringProperty(name="pinky_3_r", default="pinky_03_r")),
    # ("palm_ring_r", StringProperty(name="palm_ring_r", default="ring_metacarpal_r")),
    # ("ring_01_r", StringProperty(name="ring_1_r", default="ring_01_r")),
    # ("ring_02_r", StringProperty(name="ring_2_r", default="ring_02_r")),
    # ("ring_03_r", StringProperty(name="ring_3_r", default="ring_03_r")),
    # ("palm_middle_r", StringProperty(
    #     name="palm_middle_r", default="middle_metacarpal_r")),
    # ("middle_01_r", StringProperty(name="middle_1_r", default="middle_01_r")),
    # ("middle_02_r", StringProperty(name="middle_2_r", default="middle_02_r")),
    # ("middle_03_r", StringProperty(name="middle_3_r", default="middle_03_r")),
    # ("palm_index_r", StringProperty(name="palm_index_r", default="index_metacarpal_r")),
    # ("index_01_r", StringProperty(name="index_1_r", default="index_01_r")),
    # ("index_02_r", StringProperty(name="index_2_r", default="index_02_r")),
    # ("index_03_r", StringProperty(name="index_3_r", default="index_03_r")),
    # ("thumb_01_r", StringProperty(name="thumb_0_r", default="thumb_01_r")),
    # ("thumb_02_r", StringProperty(name="thumb_2_r", default="thumb_02_r")),
    # ("thumb_03_r", StringProperty(name="thumb_3_r", default="thumb_03_r")),
    # # left fingers
    # ("palm_pinky_l", StringProperty(name="palm_pinky_l", default="pinky_metacarpal_l")),
    # ("pinky_01_l", StringProperty(name="pinky_1_l", default="pinky_01_l")),
    # ("pinky_02_l", StringProperty(name="pinky_2_l", default="pinky_02_l")),
    # ("pinky_03_l", StringProperty(name="pinky_3_l", default="pinky_03_l")),
    # ("palm_ring_l", StringProperty(name="palm_ring_l", default="ring_metacarpal_l")),
    # ("ring_01_l", StringProperty(name="ring_1_l", default="ring_01_l")),
    # ("ring_02_l", StringProperty(name="ring_2_l", default="ring_02_l")),
    # ("ring_03_l", StringProperty(name="ring_3_l", default="ring_03_l")),
    # ("palm_middle_l", StringProperty(
    #     name="palm_middle_l", default="middle_metacarpal_l")),
    # ("middle_01_l", StringProperty(name="middle_1_l", default="middle_01_l")),
    # ("middle_02_l", StringProperty(name="middle_2_l", default="middle_02_l")),
    # ("middle_03_l", StringProperty(name="middle_3_l", default="middle_03_l")),
    # ("palm_index_l", StringProperty(name="palm_index_l", default="index_metacarpal_l")),
    # ("index_01_l", StringProperty(name="index_1_l", default="index_01_l")),
    # ("index_02_l", StringProperty(name="index_2_l", default="index_02_l")),
    # ("index_03_l", StringProperty(name="index_3_l", default="index_03_l")),
    # ("thumb_01_l", StringProperty(name="thumb_0_l", default="thumb_01_l")),
    # ("thumb_02_l", StringProperty(name="thumb_2_l", default="thumb_02_l")),
    # ("thumb_03_l", StringProperty(name="thumb_3_l", default="thumb_03_l")),

    # # legs
    # ("thigh_l", StringProperty(name="thigh_l", default="thigh_l")),
    # ("thigh_r", StringProperty(name="thigh_r", default="thigh_r")),
    # ("calf_l", StringProperty(name="calf_l", default="calf_l")),
    # ("calf_r", StringProperty(name="calf_r", default="calf_r")),
    # ("foot_l", StringProperty(name="foot_l", default="foot_l")),
    # ("foot_r", StringProperty(name="foot_r", default="foot_r")),
    # ("toe_l", StringProperty(name="toe_l", default="ball_l")),
    # ("toe_r", StringProperty(name="toe_r", default="ball_r")),
    # ("heel_r", StringProperty(name="heel_r", default="")),
    # ("heel_l", StringProperty(name="heel_l", default="")),

    # ===========================================================
    # mixamo
    ("head", StringProperty(name="Head", default="mixamorig:Head")),
    ("first_neck", StringProperty(name="1st Neck", default="mixamorig:Neck")),
    ("last_neck", StringProperty(name="Last Neck", default="mixamorig:Neck")),

    ("first_spine", StringProperty(name="Hips", default="mixamorig:Hips")),
    ("last_spine", StringProperty(name="Last Spine", default="mixamorig:Spine2")),

    ("clav_l", StringProperty(name="Clavicle Left", default="mixamorig:LeftShoulder")),
    ("clav_r", StringProperty(name="Clavicle Right", default="mixamorig:RightShoulder")),
    ("uparm_r", StringProperty(name="Upper Arm Right", default="mixamorig:RightArm")),
    ("uparm_l", StringProperty(name="Upper Arm Left", default="mixamorig:LeftArm")),
    ("lowarm_r", StringProperty(name="Forearm Right", default="mixamorig:RightForeArm")),
    ("lowarm_l", StringProperty(name="Forearm Left", default="mixamorig:LeftForeArm")),
    ("hand_r", StringProperty(name="Hand Right", default="mixamorig:RightHand")),
    ("hand_l", StringProperty(name="Hand Left", default="mixamorig:LeftHand")),

    # fingers
    ("palm_pinky_r", StringProperty(name="palm_pinky_r", default="")),
    ("pinky_01_r", StringProperty(name="pinky_1_r",
                                  default="mixamorig:RightHandPinky1")),
    ("pinky_02_r", StringProperty(name="pinky_2_r",
                                  default="mixamorig:RightHandPinky2")),
    ("pinky_03_r", StringProperty(name="pinky_3_r",
                                  default="mixamorig:RightHandPinky3")),
    ("palm_ring_r", StringProperty(name="palm_ring_r", default="")),
    ("ring_01_r", StringProperty(name="ring_1_r",
                                 default="mixamorig:RightHandRing1")),
    ("ring_02_r", StringProperty(name="ring_2_r",
                                 default="mixamorig:RightHandRing2")),
    ("ring_03_r", StringProperty(name="ring_3_r",
                                 default="mixamorig:RightHandRing3")),
    ("palm_middle_r", StringProperty(name="palm_middle_r", default="")),
    ("middle_01_r", StringProperty(name="middle_1_r",
                                   default="mixamorig:RightHandMiddle1")),
    ("middle_02_r", StringProperty(name="middle_2_r",
                                   default="mixamorig:RightHandMiddle2")),
    ("middle_03_r", StringProperty(name="middle_3_r",
                                   default="mixamorig:RightHandMiddle3")),
    ("palm_index_r", StringProperty(name="palm_index_r", default="")),
    ("index_01_r", StringProperty(name="index_1_r",
                                  default="mixamorig:RightHandIndex1")),
    ("index_02_r", StringProperty(name="index_2_r",
                                  default="mixamorig:RightHandIndex2")),
    ("index_03_r", StringProperty(name="index_3_r",
                                  default="mixamorig:RightHandIndex3")),
    ("thumb_01_r", StringProperty(name="thumb_1_r",
                                  default="mixamorig:RightHandThumb1")),
    ("thumb_02_r", StringProperty(name="thumb_2_r",
                                  default="mixamorig:RightHandThumb2")),
    ("thumb_03_r", StringProperty(name="thumb_3_r",
                                  default="mixamorig:RightHandThumb3")),
    # left fingers
    ("palm_pinky_l", StringProperty(name="palm_pinky_l", default="")),
    ("pinky_01_l", StringProperty(
        name="pinky_1_l", default="mixamorig:LeftHandPinky1")),
    ("pinky_02_l", StringProperty(
        name="pinky_2_l", default="mixamorig:LeftHandPinky2")),
    ("pinky_03_l", StringProperty(
        name="pinky_3_l", default="mixamorig:LeftHandPinky3")),
    ("palm_ring_l", StringProperty(name="palm_ring_l", default="")),
    ("ring_01_l", StringProperty(name="ring_1_l", default="mixamorig:LeftHandRing1")),
    ("ring_02_l", StringProperty(name="ring_2_l", default="mixamorig:LeftHandRing2")),
    ("ring_03_l", StringProperty(name="ring_3_l", default="mixamorig:LeftHandRing3")),
    ("palm_middle_l", StringProperty(name="palm_middle_l", default="")),
    ("middle_01_l", StringProperty(
        name="middle_1_l", default="mixamorig:LeftHandMiddle1")),
    ("middle_02_l", StringProperty(
        name="middle_2_l", default="mixamorig:LeftHandMiddle2")),
    ("middle_03_l", StringProperty(
        name="middle_3_l", default="mixamorig:LeftHandMiddle3")),
    ("palm_index_l", StringProperty(name="palm_index_l", default="")),
    ("index_01_l", StringProperty(
        name="index_1_l", default="mixamorig:LeftHandIndex1")),
    ("index_02_l", StringProperty(
        name="index_2_l", default="mixamorig:LeftHandIndex2")),
    ("index_03_l", StringProperty(
        name="index_3_l", default="mixamorig:LeftHandIndex3")),
    ("thumb_01_l", StringProperty(
        name="thumb_1_l", default="mixamorig:LeftHandThumb1")),
    ("thumb_02_l", StringProperty(
        name="thumb_2_l", default="mixamorig:LeftHandThumb2")),
    ("thumb_03_l", StringProperty(
        name="thumb_3_l", default="mixamorig:LeftHandThumb3")),

    # legs
    ("thigh_l", StringProperty(name="Up Leg Left", default="mixamorig:LeftUpLeg")),
    ("thigh_r", StringProperty(name="Up Leg Right", default="mixamorig:RightUpLeg")),
    ("calf_l", StringProperty(name="Leg Left", default="mixamorig:LeftLeg")),
    ("calf_r", StringProperty(name="Leg Right", default="mixamorig:RightLeg")),
    ("foot_l", StringProperty(name="Foot Left", default="mixamorig:LeftFoot")),
    ("foot_r", StringProperty(name="Foot Right", default="mixamorig:RightFoot")),
    ("toe_l", StringProperty(name="Toe Left", default="mixamorig:LeftToeBase")),
    ("toe_r", StringProperty(name="Toe Right", default="mixamorig:RightToeBase")),
    ("heel_r", StringProperty(name="Heel Right", default="")),
    ("heel_l", StringProperty(name="Heel Left", default="")),

    # # ===========================================================
    # # mv
    # ("head", StringProperty(name="head", default="Head")),
    # ("first_neck", StringProperty(name="1st neck", default="Neck_base")),
    # ("last_neck", StringProperty(name="last neck", default="Neck_base")),

    # ("first_spine", StringProperty(name="spine", default="Hips")),
    # ("last_spine", StringProperty(name="last_spine", default="")),

    # ("clav_l", StringProperty(name="clav_l", default="LeftShoulder")),
    # ("clav_r", StringProperty(name="clav_r", default="RightShoulder")),
    # ("uparm_r", StringProperty(name="uparm_r", default="RightArm")),
    # ("uparm_l", StringProperty(name="uparm_l", default="LeftArm")),
    # ("lowarm_r", StringProperty(name="lowarm_r", default="RightForeArm")),
    # ("lowarm_l", StringProperty(name="lowarm_l", default="LeftForeArm")),
    # ("hand_r", StringProperty(name="hand_r", default="RightHand")),
    # ("hand_l", StringProperty(name="hand_l", default="LeftHand")),

    # # fingers
    # ("palm_pinky_r", StringProperty(name="palm_pinky_r", default="")),
    # ("pinky_01_r", StringProperty(name="pinky_1_r", default="RightHandPinky1")),
    # ("pinky_02_r", StringProperty(name="pinky_2_r", default="RightHandPinky2")),
    # ("pinky_03_r", StringProperty(name="pinky_3_r", default="RightHandPinky3")),
    # ("palm_ring_r", StringProperty(name="palm_ring_r", default="")),
    # ("ring_01_r", StringProperty(name="ring_1_r", default="RightHandRing1")),
    # ("ring_02_r", StringProperty(name="ring_2_r", default="RightHandRing2")),
    # ("ring_03_r", StringProperty(name="ring_3_r", default="RightHandRing3")),
    # ("palm_middle_r", StringProperty(name="palm_middle_r", default="")),
    # ("middle_01_r", StringProperty(name="middle_1_r", default="RightHandMiddle1")),
    # ("middle_02_r", StringProperty(name="middle_2_r", default="RightHandMiddle2")),
    # ("middle_03_r", StringProperty(name="middle_3_r", default="RightHandMiddle3")),
    # ("palm_index_r", StringProperty(name="palm_index_r", default="")),
    # ("index_01_r", StringProperty(name="index_1_r", default="RightHandIndex1")),
    # ("index_02_r", StringProperty(name="index_2_r", default="RightHandIndex2")),
    # ("index_03_r", StringProperty(name="index_3_r", default="RightHandIndex3")),
    # ("thumb_01_r", StringProperty(name="thumb_1_r", default="RightHandThumb1")),
    # ("thumb_02_r", StringProperty(name="thumb_2_r", default="RightHandThumb2")),
    # ("thumb_03_r", StringProperty(name="thumb_3_r", default="RightHandThumb3")),
    # # left fingers
    # ("palm_pinky_l", StringProperty(name="palm_pinky_l", default="")),
    # ("pinky_01_l", StringProperty(name="pinky_1_l", default="LeftHandPinky1")),
    # ("pinky_02_l", StringProperty(name="pinky_2_l", default="LeftHandPinky2")),
    # ("pinky_03_l", StringProperty(name="pinky_3_l", default="LeftHandPinky3")),
    # ("palm_ring_l", StringProperty(name="palm_ring_l", default="")),
    # ("ring_01_l", StringProperty(name="ring_1_l", default="LeftHandRing1")),
    # ("ring_02_l", StringProperty(name="ring_2_l", default="LeftHandRing2")),
    # ("ring_03_l", StringProperty(name="ring_3_l", default="LeftHandRing3")),
    # ("palm_middle_l", StringProperty(name="palm_middle_l", default="")),
    # ("middle_01_l", StringProperty(name="middle_1_l", default="LeftHandMiddle1")),
    # ("middle_02_l", StringProperty(name="middle_2_l", default="LeftHandMiddle2")),
    # ("middle_03_l", StringProperty(name="middle_3_l", default="LeftHandMiddle3")),
    # ("palm_index_l", StringProperty(name="palm_index_l", default="")),
    # ("index_01_l", StringProperty(name="index_1_l", default="LeftHandIndex1")),
    # ("index_02_l", StringProperty(name="index_2_l", default="LeftHandIndex2")),
    # ("index_03_l", StringProperty(name="index_3_l", default="LeftHandIndex3")),
    # ("thumb_01_l", StringProperty(name="thumb_1_l", default="LeftHandThumb1")),
    # ("thumb_02_l", StringProperty(name="thumb_2_l", default="LeftHandThumb2")),
    # ("thumb_03_l", StringProperty(name="thumb_3_l", default="LeftHandThumb3")),

    # # legs
    # ("thigh_l", StringProperty(name="thigh_l", default="LeftUpLeg")),
    # ("thigh_r", StringProperty(name="thigh_r", default="RightUpLeg")),
    # ("calf_l", StringProperty(name="calf_l", default="LeftLeg")),
    # ("calf_r", StringProperty(name="calf_r", default="RightLeg")),
    # ("foot_l", StringProperty(name="foot_l", default="LeftFoot")),
    # ("foot_r", StringProperty(name="foot_r", default="RightFoot")),
    # ("toe_l", StringProperty(name="toe_l", default="LeftToeBase")),
    # ("toe_r", StringProperty(name="toe_r", default="RightToeBase")),
    # ("heel_r", StringProperty(name="heel_r", default="")),
    # ("heel_l", StringProperty(name="heel_l", default="")),
]
