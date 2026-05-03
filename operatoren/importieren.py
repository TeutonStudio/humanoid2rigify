import bpy
import json

from __methoden__ import get_mapping_folder

class MappingImportOperator(bpy.types.Operator):

    bl_idname = "opr.mapping_import_operator"
    bl_label = "mapping_templates_import"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        json_file = f"{get_mapping_folder()}/{context.scene.presets}"
        # Opening JSON file
        with open(json_file, encoding="utf-8") as json_file:
            data = json.load(json_file)

        context.scene.head = data["head"]
        context.scene.first_neck = data["first_neck"]
        context.scene.last_neck = data["last_neck"]
        context.scene.first_spine = data["first_spine"]
        context.scene.last_spine = data["last_spine"]
        context.scene.clav_l = data["clav_l"]
        context.scene.clav_r = data["clav_r"]
        context.scene.uparm_r = data["uparm_r"]
        context.scene.uparm_l = data["uparm_l"]
        context.scene.lowarm_r = data["lowarm_r"]
        context.scene.lowarm_l = data["lowarm_l"]
        context.scene.hand_r = data["hand_r"]
        context.scene.hand_l = data["hand_l"]
        context.scene.palm_pinky_r = data["palm_pinky_r"]
        context.scene.pinky_01_r = data["pinky_01_r"]
        context.scene.pinky_02_r = data["pinky_02_r"]
        context.scene.pinky_03_r = data["pinky_03_r"]
        context.scene.palm_ring_r = data["palm_ring_r"]
        context.scene.ring_01_r = data["ring_01_r"]
        context.scene.ring_02_r = data["ring_02_r"]
        context.scene.ring_03_r = data["ring_03_r"]
        context.scene.palm_middle_r = data["palm_middle_r"]
        context.scene.middle_01_r = data["middle_01_r"]
        context.scene.middle_02_r = data["middle_02_r"]
        context.scene.middle_03_r = data["middle_03_r"]
        context.scene.palm_index_r = data["palm_index_r"]
        context.scene.index_01_r = data["index_01_r"]
        context.scene.index_02_r = data["index_02_r"]
        context.scene.index_03_r = data["index_03_r"]
        context.scene.thumb_01_r = data["thumb_01_r"]
        context.scene.thumb_02_r = data["thumb_02_r"]
        context.scene.thumb_03_r = data["thumb_03_r"]
        context.scene.palm_pinky_l = data["palm_pinky_l"]
        context.scene.pinky_01_l = data["pinky_01_l"]
        context.scene.pinky_02_l = data["pinky_02_l"]
        context.scene.pinky_03_l = data["pinky_03_l"]
        context.scene.palm_ring_l = data["palm_ring_l"]
        context.scene.ring_01_l = data["ring_01_l"]
        context.scene.ring_02_l = data["ring_02_l"]
        context.scene.ring_03_l = data["ring_03_l"]
        context.scene.palm_middle_l = data["palm_middle_l"]
        context.scene.middle_01_l = data["middle_01_l"]
        context.scene.middle_02_l = data["middle_02_l"]
        context.scene.middle_03_l = data["middle_03_l"]
        context.scene.palm_index_l = data["palm_index_l"]
        context.scene.index_01_l = data["index_01_l"]
        context.scene.index_02_l = data["index_02_l"]
        context.scene.index_03_l = data["index_03_l"]
        context.scene.thumb_01_l = data["thumb_01_l"]
        context.scene.thumb_02_l = data["thumb_02_l"]
        context.scene.thumb_03_l = data["thumb_03_l"]
        context.scene.thigh_l = data["thigh_l"]
        context.scene.thigh_r = data["thigh_r"]
        context.scene.calf_l = data["calf_l"]
        context.scene.calf_r = data["calf_r"]
        context.scene.foot_l = data["foot_l"]
        context.scene.foot_r = data["foot_r"]
        context.scene.toe_l = data["toe_l"]
        context.scene.toe_r = data["toe_r"]
        context.scene.heel_r = data["heel_r"]
        context.scene.heel_l = data["heel_l"]

        self.report({"INFO"}, f"{context.scene.presets} preset imported")
        return {"FINISHED"}
