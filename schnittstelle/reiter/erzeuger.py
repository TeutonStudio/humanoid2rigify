import bpy

from ...__methoden__ import is_pose_armature_context
from ..__panel__ import Panel


class GENERATE_panel(Panel):
    bl_idname = "GENERATE_PT_panel"
    bl_label = "Generate"
    # bl_options = {"DEFAULT_OPENED"}

    @classmethod
    def poll(cls, context):
        return is_pose_armature_context(context)

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        box = self.layout.box()
        box.label(text="Generate")
        box.prop(scn, "generation_mode")
        box.operator("opr.object_operator", text="Generate Rigify")
        box.prop(scn, "copy_loc_constr")
