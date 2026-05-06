from typing import Literal


class Skelett:
    head: str
    first_neck: str
    last_neck: str
    first_spine: str
    last_spine: str
    clav_r: str
    clav_l: str
    uparm_l: str
    uparm_r: str
    lowarm_l: str
    lowarm_r: str
    hand_l: str
    hand_r: str
    palm_pinky_r: str
    pinky_01_r: str
    pinky_02_r: str
    pinky_03_r: str
    palm_ring_r: str
    ring_01_r: str
    ring_02_r: str
    ring_03_r: str
    palm_middle_r: str
    middle_01_r: str
    middle_02_r: str
    middle_03_r: str
    palm_index_r: str
    index_01_r: str
    index_02_r: str
    index_03_r: str
    thumb_01_r: str
    thumb_02_r: str
    thumb_03_r: str
    palm_pinky_l: str
    pinky_01_l: str
    pinky_02_l: str
    pinky_03_l: str
    palm_ring_l: str
    ring_01_l: str
    ring_02_l: str
    ring_03_l: str
    palm_middle_l: str
    middle_01_l: str
    middle_02_l: str
    middle_03_l: str
    palm_index_l: str
    index_01_l: str
    index_02_l: str
    index_03_l: str
    thumb_01_l: str
    thumb_02_l: str
    thumb_03_l: str
    thigh_l: str
    thigh_r: str
    calf_l: str
    calf_r: str
    foot_l: str
    foot_r: str
    toe_l: str
    toe_r: str
    heel_l: str
    heel_r: str
    fingers_bool_r: bool
    fingers_bool_l: bool
    copy_loc_constr: bool
    excluded_bones_to_create: set[str]

    def __init__(self,params: dict, skeleton_model):
        def safe_param(name:str,default=""): return params.get(name,default)

        self.head = safe_param("head")
        self.first_neck = safe_param("first_neck")
        self.last_neck = safe_param("last_neck") or self.first_neck
        self.first_spine = safe_param("first_spine")
        self.last_spine = safe_param("last_spine") or self.first_spine

        self.clav_r = safe_param("clav_r")
        self.clav_l = safe_param("clav_l")
        self.uparm_l = safe_param("uparm_l")
        self.uparm_r = safe_param("uparm_r")
        self.lowarm_l = safe_param("lowarm_l")
        self.lowarm_r = safe_param("lowarm_r")
        self.hand_l = safe_param("hand_l")
        self.hand_r = safe_param("hand_r")

        self.palm_pinky_r = safe_param("palm_pinky_r")
        self.pinky_01_r = safe_param("pinky_01_r")
        self.pinky_02_r = safe_param("pinky_02_r")
        self.pinky_03_r = safe_param("pinky_03_r")
        self.palm_ring_r = safe_param("palm_ring_r")
        self.ring_01_r = safe_param("ring_01_r")
        self.ring_02_r = safe_param("ring_02_r")
        self.ring_03_r = safe_param("ring_03_r")
        self.palm_middle_r = safe_param("palm_middle_r")
        self.middle_01_r = safe_param("middle_01_r")
        self.middle_02_r = safe_param("middle_02_r")
        self.middle_03_r = safe_param("middle_03_r")
        self.palm_index_r = safe_param("palm_index_r")
        self.index_01_r = safe_param("index_01_r")
        self.index_02_r = safe_param("index_02_r")
        self.index_03_r = safe_param("index_03_r")
        self.thumb_01_r = safe_param("thumb_01_r")
        self.thumb_02_r = safe_param("thumb_02_r")
        self.thumb_03_r = safe_param("thumb_03_r")

        self.palm_pinky_l = safe_param("palm_pinky_l")
        self.pinky_01_l = safe_param("pinky_01_l")
        self.pinky_02_l = safe_param("pinky_02_l")
        self.pinky_03_l = safe_param("pinky_03_l")
        self.palm_ring_l = safe_param("palm_ring_l")
        self.ring_01_l = safe_param("ring_01_l")
        self.ring_02_l = safe_param("ring_02_l")
        self.ring_03_l = safe_param("ring_03_l")
        self.palm_middle_l = safe_param("palm_middle_l")
        self.middle_01_l = safe_param("middle_01_l")
        self.middle_02_l = safe_param("middle_02_l")
        self.middle_03_l = safe_param("middle_03_l")
        self.palm_index_l = safe_param("palm_index_l")
        self.index_01_l = safe_param("index_01_l")
        self.index_02_l = safe_param("index_02_l")
        self.index_03_l = safe_param("index_03_l")
        self.thumb_01_l = safe_param("thumb_01_l")
        self.thumb_02_l = safe_param("thumb_02_l")
        self.thumb_03_l = safe_param("thumb_03_l")

        self.thigh_l = safe_param("thigh_l")
        self.thigh_r = safe_param("thigh_r")
        self.calf_l = safe_param("calf_l")
        self.calf_r = safe_param("calf_r")
        self.foot_l = safe_param("foot_l")
        self.foot_r = safe_param("foot_r")
        self.toe_l = safe_param("toe_l")
        self.toe_r = safe_param("toe_r")
        self.heel_l = safe_param("heel_l")
        self.heel_r = safe_param("heel_r")

        self.fingers_bool_r = bool(safe_param("fingers_bool_r", True))
        self.fingers_bool_l = bool(safe_param("fingers_bool_l", True))
        self.copy_loc_constr = bool(safe_param("copy_loc_constr", True))

        require_source_bone(skeleton_model,self.first_spine, "first_spine")
        require_source_bone(skeleton_model,self.last_spine, "last_spine")
        require_source_bone(skeleton_model,self.head, "head")

        self.excluded_bones_to_create = set()

        if not self.fingers_bool_r: # TODO
            self.excluded_bones_to_create.update(bone for bone in self.finger_list_per_side("r") if bone)
            right_fingers = []

        if not self.fingers_bool_l: # TODO
            self.excluded_bones_to_create.update(bone for bone in self.finger_list_per_side("l") if bone)
            left_fingers = []

    def finger_list_all(self) -> list[str]:
        return list(dict.fromkeys(self.finger_list_per_side("r") + self.finger_list_per_side("l")))
    def finger_list_per_side(self,seite: Literal["r","l"]) -> list[str]:
        if seite == "r" and self.fingers_bool_r: return [
            self.palm_pinky_r,
            self.pinky_01_r,
            self.pinky_02_r,
            self.pinky_03_r,
            self.palm_ring_r,
            self.ring_01_r,
            self.ring_02_r,
            self.ring_03_r,
            self.palm_middle_r,
            self.middle_01_r,
            self.middle_02_r,
            self.middle_03_r,
            self.palm_index_r,
            self.index_01_r,
            self.index_02_r,
            self.index_03_r,
            self.thumb_01_r,
            self.thumb_02_r,
            self.thumb_03_r,
        ]
        if seite == "l" and self.fingers_bool_l: return [
            self.palm_pinky_l,
            self.pinky_01_l,
            self.pinky_02_l,
            self.pinky_03_l,
            self.palm_ring_l,
            self.ring_01_l,
            self.ring_02_l,
            self.ring_03_l,
            self.palm_middle_l,
            self.middle_01_l,
            self.middle_02_l,
            self.middle_03_l,
            self.palm_index_l,
            self.index_01_l,
            self.index_02_l,
            self.index_03_l,
            self.thumb_01_l,
            self.thumb_02_l,
            self.thumb_03_l,
        ]
        return []
    def thumb_list(self) -> list[str]:
        return [
            self.thumb_01_r,
            self.thumb_02_r,
            self.thumb_03_r,
            self.thumb_01_l,
            self.thumb_02_l,
            self.thumb_03_l,
        ]
    def finger_list_no_thumb(self):
        ausgabe = []
        for finger in self.finger_list_all():
            if not finger in self.thumb_list():  ausgabe.append(finger)
        return ausgabe
    def finger_end_list(self) -> list[str]:
        return [
            self.pinky_03_r,
            self.ring_03_r,
            self.middle_03_r,
            self.index_03_r,
            self.thumb_03_r,
            self.pinky_03_l,
            self.ring_03_l,
            self.middle_03_l,
            self.index_03_l,
            self.thumb_03_l,
        ]
    def finger_parenting_list(self) ->  dict[str,list[str | bool]]:
        return {
            self.palm_pinky_r: [self.hand_r, False],
            self.pinky_01_r: [self.palm_pinky_r or self.hand_r, False],
            self.pinky_02_r: [self.pinky_01_r, True],
            self.pinky_03_r: [self.pinky_02_r, True],
            self.palm_ring_r: [self.hand_r, False],
            self.ring_01_r: [self.palm_ring_r or self.hand_r, False],
            self.ring_02_r: [self.ring_01_r, True],
            self.ring_03_r: [self.ring_02_r, True],
            self.palm_middle_r: [self.hand_r, False],
            self.middle_01_r: [self.palm_middle_r or self.hand_r, False],
            self.middle_02_r: [self.middle_01_r, True],
            self.middle_03_r: [self.middle_02_r, True],
            self.palm_index_r: [self.hand_r, False],
            self.index_01_r: [self.palm_index_r or self.hand_r, False],
            self.index_02_r: [self.index_01_r, True],
            self.index_03_r: [self.index_02_r, True],
            self.thumb_01_r: [self.hand_r, False],
            self.thumb_02_r: [self.thumb_01_r, True],
            self.thumb_03_r: [self.thumb_02_r, True],
            self.palm_pinky_l: [self.hand_l, False],
            self.pinky_01_l: [self.palm_pinky_l or self.hand_l, False],
            self.pinky_02_l: [self.pinky_01_l, True],
            self.pinky_03_l: [self.pinky_02_l, True],
            self.palm_ring_l: [self.hand_l, False],
            self.ring_01_l: [self.palm_ring_l or self.hand_l, False],
            self.ring_02_l: [self.ring_01_l, True],
            self.ring_03_l: [self.ring_02_l, True],
            self.palm_middle_l: [self.hand_l, False],
            self.middle_01_l: [self.palm_middle_l or self.hand_l, False],
            self.middle_02_l: [self.middle_01_l, True],
            self.middle_03_l: [self.middle_02_l, True],
            self.palm_index_l: [self.hand_l, False],
            self.index_01_l: [self.palm_index_l or self.hand_l, False],
            self.index_02_l: [self.index_01_l, True],
            self.index_03_l: [self.index_02_l, True],
            self.thumb_01_l: [self.hand_l, False],
            self.thumb_02_l: [self.thumb_01_l, True],
            self.thumb_03_l: [self.thumb_02_l, True],
        }
    def parenting_list(self) -> list[tuple[str, str, bool]]:
        return [
        (self.thigh_l, self.first_spine, False),
        (self.thigh_r, self.first_spine, False),
        (self.calf_r, self.thigh_r, True),
        (self.foot_r, self.calf_r, True),
        (self.toe_r, self.foot_r, True),
        (self.calf_l, self.thigh_l, True),
        (self.foot_l, self.calf_l, True),
        (self.toe_l, self.foot_l, True),
        (self.clav_r, self.last_spine, False),
        (self.uparm_r, self.clav_r, False),
        (self.lowarm_r, self.uparm_r, True),
        (self.hand_r, self.lowarm_r, True),
        (self.clav_l, self.last_spine, False),
        (self.uparm_l, self.clav_l, False),
        (self.lowarm_l, self.uparm_l, True),
        (self.hand_l, self.lowarm_l, True),
    ]

    def rigify_types(self) -> dict[str,str]:
        return {
            self.first_neck: "spines.super_head",
            self.clav_l: "basic.super_copy",
            self.clav_r: "basic.super_copy",
            self.uparm_r: "limbs.super_limb",
            self.uparm_l: "limbs.super_limb",
            self.palm_index_r: "limbs.super_palm",
            self.pinky_01_r: "limbs.super_finger",
            self.ring_01_r: "limbs.super_finger",
            self.middle_01_r: "limbs.super_finger",
            self.index_01_r: "limbs.super_finger",
            self.thumb_01_r: "limbs.super_finger",
            self.palm_index_l: "limbs.super_palm",
            self.pinky_01_l: "limbs.super_finger",
            self.ring_01_l: "limbs.super_finger",
            self.middle_01_l: "limbs.super_finger",
            self.index_01_l: "limbs.super_finger",
            self.thumb_01_l: "limbs.super_finger",
            self.first_spine: "spines.basic_spine",
            self.thigh_l: "limbs.leg",
            self.thigh_r: "limbs.leg",
        }


def require_source_bone(skeleton_model,bone_name: str, label: str) -> None:
    if not bone_name:
        raise RuntimeError(f"Pflichtknochen fehlt im Mapping: {label}")

    if skeleton_model.data.bones.get(bone_name) is None:
        raise RuntimeError(
            f"Pflichtknochen '{bone_name}' für '{label}' existiert nicht in {skeleton_model.name}"
        )
