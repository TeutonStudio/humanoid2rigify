import bpy


class MAPPING_panel(bpy.types.Panel):
    bl_idname = "MAPPING_PT_panel"
    bl_label = "Mapping"
    bl_category = "Any Rig to Rigify"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    # bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        # row = layout.row()
        # icon = 'TRIA_DOWN' if scn.subpanel_status_upper else 'TRIA_RIGHT'
        # row.prop(scn, 'subpanel_status_mapping', icon=icon, icon_only=True)
        # row.label(text='Mapping')
        # if scn.subpanel_status_mapping:

        box = layout.box()
        box.label(text="save mapping")

        box.prop(scn, "json_file_name")
        box.operator("opr.mapping_save_operator", text="save mapping")

        box = layout.box()
        box.label(text="import presets")
        box.prop(scn, "presets")
        box.operator("opr.mapping_import_operator", text="import mapping")

        box = layout.box()
        box.label(text="delete active preset")
        box.operator("opr.mapping_delete_operator",
                     text=f"delete {scn.presets}")

        box = layout.box()
        box.label(text="rename active reset")
        box.prop(scn, "rename_preset")
        box.operator("opr.mapping_rename_operator", text="rename preset")
