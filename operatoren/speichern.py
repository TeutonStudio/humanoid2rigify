import bpy
import json

from ..__methoden__ import get_mapping_folder

class MappingSaveOperator(bpy.types.Operator):

    bl_idname = "opr.mapping_save_operator"
    bl_label = "mapping_templates"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        prop_dict = {
            "head": context.scene.head,
            "first_neck": context.scene.first_neck,
            "last_neck": context.scene.last_neck,
            "first_spine": context.scene.first_spine,
            "last_spine": context.scene.last_spine,
            "clav_l": context.scene.clav_l,
            "clav_r": context.scene.clav_r,
            "uparm_r": context.scene.uparm_r,
            "uparm_l": context.scene.uparm_l,
            "lowarm_r": context.scene.lowarm_r,
            "lowarm_l": context.scene.lowarm_l,
            "hand_r": context.scene.hand_r,
            "hand_l": context.scene.hand_l,
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
            "heel_r": context.scene.heel_r,
            "heel_l": context.scene.heel_l,
        }

        # ===========================================================
        mapping_folder = get_mapping_folder()

        # ===========================================================
        # Serializing json
        json_object = json.dumps(prop_dict, indent=4)

        if context.scene.json_file_name != "":
            context.scene.json_file_name = context.scene.json_file_name.replace(
                ".json", "")
            json_file_name = f"{context.scene.json_file_name}.json"
            json_path = f"{mapping_folder}/{json_file_name}"

            # Writing to sample.json
            with open(json_path, "w", encoding="utf-8") as outfile:
                outfile.write(json_object)
            context.scene.json_file_name = ""
            self.report({"INFO"}, f"{context.scene.presets} preset saved")
        else:
            self.report({"ERROR"}, "Enter preset name fist")

        return {"FINISHED"}
