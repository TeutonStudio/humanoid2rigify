import bpy

from operatoren.__methoden__ import generate_rig


class ObjectOperator(bpy.types.Operator):
    bl_idname = "opr.object_operator"
    bl_label = "Any Rig to Rigify"
    bl_options = {"UNDO"}

    def execute(self, context):
        params = {
            "head": context.scene.head,
            "first_neck": context.scene.first_neck,
            "last_neck": context.scene.last_neck,
            "first_spine": context.scene.first_spine,
            "last_spine": context.scene.last_spine,
            "clav_r": context.scene.clav_r,
            "clav_l": context.scene.clav_l,
            "uparm_l": context.scene.uparm_l,
            "uparm_r": context.scene.uparm_r,
            "lowarm_l": context.scene.lowarm_l,
            "lowarm_r": context.scene.lowarm_r,
            "hand_l": context.scene.hand_l,
            "hand_r": context.scene.hand_r,

            "palm_pinky_r": context.scene.palm_pinky_r,
            "pinky_01_r": context.scene.pinky_01_r,
            "pinky_02_r": context.scene.pinky_02_r,
            "pinky_03_r": context.scene.pinky_03_r,
            "palm_ring_r": context.scene.palm_ring_r,
            "ring_01_r": context.scene.ring_01_r,
            "ring_02_r": context.scene.ring_02_r,
            "ring_03_r": context.scene.ring_03_r,
            "palm_middle_r": context.scene.palm_middle_r,
            "middle_01_r": context.scene.middle_01_r,
            "middle_02_r": context.scene.middle_02_r,
            "middle_03_r": context.scene.middle_03_r,
            "palm_index_r": context.scene.palm_index_r,
            "index_01_r": context.scene.index_01_r,
            "index_02_r": context.scene.index_02_r,
            "index_03_r": context.scene.index_03_r,
            "thumb_01_r": context.scene.thumb_01_r,
            "thumb_02_r": context.scene.thumb_02_r,
            "thumb_03_r": context.scene.thumb_03_r,

            "palm_pinky_l": context.scene.palm_pinky_l,
            "pinky_01_l": context.scene.pinky_01_l,
            "pinky_02_l": context.scene.pinky_02_l,
            "pinky_03_l": context.scene.pinky_03_l,
            "palm_ring_l": context.scene.palm_ring_l,
            "ring_01_l": context.scene.ring_01_l,
            "ring_02_l": context.scene.ring_02_l,
            "ring_03_l": context.scene.ring_03_l,
            "palm_middle_l": context.scene.palm_middle_l,
            "middle_01_l": context.scene.middle_01_l,
            "middle_02_l": context.scene.middle_02_l,
            "middle_03_l": context.scene.middle_03_l,
            "palm_index_l": context.scene.palm_index_l,
            "index_01_l": context.scene.index_01_l,
            "index_02_l": context.scene.index_02_l,
            "index_03_l": context.scene.index_03_l,
            "thumb_01_l": context.scene.thumb_01_l,
            "thumb_02_l": context.scene.thumb_02_l,
            "thumb_03_l": context.scene.thumb_03_l,
            "thigh_l": context.scene.thigh_l,
            "thigh_r": context.scene.thigh_r,
            "calf_l": context.scene.calf_l,
            "calf_r": context.scene.calf_r,
            "foot_l": context.scene.foot_l,
            "foot_r": context.scene.foot_r,
            "toe_l": context.scene.toe_l,
            "toe_r": context.scene.toe_r,
            "heel_l": context.scene.heel_l,
            "heel_r": context.scene.heel_r,

            "fingers_bool_r": context.scene.fingers_bool_r,
            "fingers_bool_l": context.scene.fingers_bool_l,
            "copy_loc_constr": context.scene.copy_loc_constr,
            "generation_mode": context.scene.generation_mode,
        }

        objects = bpy.context.selected_objects
        generate_rig(self, objects, params)

        return {"FINISHED"}
