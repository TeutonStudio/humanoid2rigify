import bpy

class GENERATE_panel(bpy.types.Panel):
    bl_idname = "GENERATE_PT_panel"
    bl_label = "Generate"
    bl_category = "Any Rig to Rigify"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    # bl_options = {"DEFAULT_OPENED"}

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        box = self.layout.box()
        box.label(text="Generate")
        box.prop(scn, "generation_mode")
        box.operator("opr.object_operator", text="Generate Rigify")
        box.prop(scn, "copy_loc_constr")
