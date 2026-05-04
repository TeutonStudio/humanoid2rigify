import os

import bpy

from ...__methoden__ import get_mapping_folder
from ..__operator__ import Operator, Operatoren


class MappingRenameOperator(Operator):
    bl_idname = Operatoren.UMBENNENEN
    bl_label = "mapping_templates_rename"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        json_file = f"{get_mapping_folder()}/{context.scene.presets}"
        protected_files = [
            "fortnite.json",
            "mixamo.json",
        ]

        old_file_name = context.scene.presets
        if context.scene.presets not in protected_files:
            new_name = f"{context.scene.rename_preset}.json"
            new_file_name = json_file.replace(context.scene.presets, new_name)
            os.rename(json_file, new_file_name)
            self.report(
                {"INFO"}, f"{old_file_name} renamed to {context.scene.presets}")
            context.scene.rename_preset = ""
        else:
            self.report(
                {"ERROR"}, f"{context.scene.presets} is restricted file")

        return {"FINISHED"}
