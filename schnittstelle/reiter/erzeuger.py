import bpy

from ..eigenschaften import (
    DEFAULT_MERGE_EXTRA_BONE_WHITELIST,
    get_next_merge_whitelist_value,
    ensure_merge_whitelist,
)


class OPR_add_merge_whitelist_item(bpy.types.Operator):
    bl_idname = "opr.add_merge_whitelist_item"
    bl_label = "Whitelist-Eintrag hinzufuegen"

    def execute(self, context):
        ensure_merge_whitelist(context.scene)
        item = context.scene.merge_extra_bone_whitelist.add()
        item.value = get_next_merge_whitelist_value(context.scene, context)
        return {"FINISHED"}


class OPR_remove_merge_whitelist_item(bpy.types.Operator):
    bl_idname = "opr.remove_merge_whitelist_item"
    bl_label = "Whitelist-Eintrag entfernen"

    item_index: bpy.props.IntProperty(default=-1)

    def execute(self, context):
        ensure_merge_whitelist(context.scene)
        whitelist = context.scene.merge_extra_bone_whitelist
        index = self.item_index
        if 0 <= index < len(whitelist):
            whitelist.remove(index)
        return {"FINISHED"}


class OPR_reset_merge_whitelist(bpy.types.Operator):
    bl_idname = "opr.reset_merge_whitelist"
    bl_label = "Whitelist zuruecksetzen"

    def execute(self, context):
        ensure_merge_whitelist(context.scene)
        whitelist = context.scene.merge_extra_bone_whitelist
        while len(whitelist) != 0:
            whitelist.remove(len(whitelist) - 1)

        for pattern in DEFAULT_MERGE_EXTRA_BONE_WHITELIST:
            item = whitelist.add()
            item.value = pattern

        return {"FINISHED"}


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
        ensure_merge_whitelist(scn)

        box = self.layout.box()
        box.label(text="Generate")
        box.prop(scn, "generation_mode")
        box.operator("opr.object_operator", text="Generate Rigify")
        box.prop(scn, "copy_loc_constr")


class MERGE_WHITELIST_panel(bpy.types.Panel):
    bl_idname = "MERGE_WHITELIST_PT_panel"
    bl_label = "Merge Whitelist"
    bl_category = "Any Rig to Rigify"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        ensure_merge_whitelist(scn)

        box = layout.box()
        box.label(text="Knochen-Uebernahme")
        box.label(text="Standardmuster und Bones des aktuellen Rigs")

        if len(scn.merge_extra_bone_whitelist) == 0:
            box.label(text="Keine Eintraege vorhanden")

        row = box.row()
        col = row.column()
        for index, item in enumerate(scn.merge_extra_bone_whitelist):
            item_row = col.row(align=True)
            item_row.prop(item, "value", text=f"{index + 1}")
            remove_op = item_row.operator("opr.remove_merge_whitelist_item", text="", icon="X")
            remove_op.item_index = index

        button_row = box.row(align=True)
        button_row.operator("opr.add_merge_whitelist_item", icon="ADD")
        box.operator("opr.reset_merge_whitelist", icon="FILE_REFRESH")
