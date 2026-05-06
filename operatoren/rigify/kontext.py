from dataclasses import dataclass, field
from typing import Literal

from mathutils import Color

KnochenGattung = Literal["IK", "FK", "Tweak"]
FarbGattung = Literal["normal", "select", "active"]

FALLBACK_COLOR: dict[KnochenGattung,dict[FarbGattung,Color]] = {
    "IK": {
        "normal": Color((0.85, 0.15, 0.12)),
        "select": Color((1.00, 0.35, 0.30)),
        "active": Color((1.00, 0.65, 0.55)),
    },
    "FK": {
        "normal": Color((0.15, 0.75, 0.20)),
        "select": Color((0.45, 1.00, 0.45)),
        "active": Color((0.75, 1.00, 0.75)),
    },
    "Tweak": {
        "normal": Color((0.2196078431, 0.4980392157, 0.7843137255)),
        "select": Color((0.5960784314, 0.8980392157, 1.0)),
        "active": Color((0.7686274510, 1.0, 1.0)),
    }
}

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
    derived_bones: dict = field(default_factory=dict)
    weighted_vertex_groups: set = field(default_factory=set)
    used_deform_bones: list = field(default_factory=list)
    standard_constraint_map: dict = field(default_factory=dict)
    source_to_target_map: dict = field(default_factory=dict)
    extra_bones: list = field(default_factory=list)
    extra_bone_data: dict = field(default_factory=dict)

INTERNAL_RIGIFY_PREFIXES = ("DEF-", "MCH-", "ORG-")
EXTRA_GROUP_COLLECTION_PREFIX = "Extra"
EXTRA_GROUP_UI_START_ROW = 18
GENERIC_CIRCLE_WIDGET_VERTEX_COUNT = 32

LAYER_COLLECTION_NAMES = {
    0: "Face",
    1: "Face (Primary)",
    2: "Face (Secondary)",

    3: "Torso",
    4: "Torso (Tweak)",

    5: "Fingers",
    6: "Fingers (Detail)",

    7: "Arm.L (IK)",
    8: "Arm.L (FK)",
    9: "Arm.L (Tweak)",

    10: "Arm.R (IK)",
    11: "Arm.R (FK)",
    12: "Arm.R (Tweak)",

    13: "Leg.L (IK)",
    14: "Leg.L (FK)",
    15: "Leg.L (Tweak)",

    16: "Leg.R (IK)",
    17: "Leg.R (FK)",
    18: "Leg.R (Tweak)",

    27: "Additional",
    31: "Root",
}

RIGIFY_UI_ROWS = {
    # Face
    0: 1,

    # Primary / Secondary
    1: 2,
    2: 2,

    # Separator row 3

    # Torso
    3: 4,
    4: 5,

    # Fingers
    5: 6,
    6: 7,

    # Separator row 8

    # Arms
    7: 9,
    10: 9,

    8: 10,
    11: 10,

    9: 11,
    12: 11,

    # Separator row 12

    # Legs
    13: 13,
    16: 13,

    14: 14,
    17: 14,

    15: 15,
    18: 15,

    # Separator row 16

    # Root
    31: 17,

    # Whitelist / Additional
    27: EXTRA_GROUP_UI_START_ROW,
}

RIGIFY_UI_TITLES = {
    0: "Face",
    1: "Primary",
    2: "Secondary",

    3: "Torso",
    4: "Tweak",

    5: "Fingers",
    6: "Detail",

    7: "Arm.L (IK)",
    10: "Arm.R (IK)",

    8: "FK",
    11: "FK",

    9: "Tweak",
    12: "Tweak",

    13: "Leg.L (IK)",
    16: "Leg.R (IK)",

    14: "FK",
    17: "FK",

    15: "Tweak",
    18: "Tweak",

    27: "Additional",
    31: "Root",
}

STANDARD_LAYER_UI_ORDER = [
    0,
    1,
    2,
    3,
    4,
    5,
    6,

    7,
    10,
    8,
    11,
    9,
    12,

    13,
    16,
    14,
    17,
    15,
    18,

    31,
    27,
]

DEFAULT_VISIBLE_RIG_LAYER_INDICES = [
    0,
    1,
    2,
    3,
    4,
    5,
    6,

    7,
    8,
    9,
    10,
    11,
    12,

    13,
    14,
    15,
    16,
    17,
    18,

    31,
]

STANDARD_COLLECTION_NAMES = set(LAYER_COLLECTION_NAMES.values())

COLLECTION_LAYER_BY_NAME = {
    collection_name: layer_index
    for layer_index, collection_name in LAYER_COLLECTION_NAMES.items()
}
