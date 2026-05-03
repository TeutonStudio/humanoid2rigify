import bpy
import os

from __methoden__ import get_mapping_folder

class MappingDeleteOperator(bpy.types.Operator):

    bl_idname = "opr.mapping_delete_operator"
    bl_label = "mapping_templates_delete"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        json_file = f"{get_mapping_folder()}/{context.scene.presets}"
        print(json_file)
        protected_files = [
            "fortnite.json",
            "mixamo.json",
        ]
        if context.scene.presets not in protected_files:
            delete_preset = context.scene.presets
            os.remove(json_file)
            self.report({"INFO"}, f"{delete_preset} reset was deleted")
        else:
            self.report(
                {"ERROR"}, f"{context.scene.presets} is restricted file")

        return {"FINISHED"}
