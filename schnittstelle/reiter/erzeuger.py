import bpy

from ..eigenschaften import (
    DEFAULT_MERGE_EXTRA_BONE_WHITELIST,
    get_cached_bone_items,
    get_current_armature,
    get_next_merge_whitelist_value,
    is_bone_name_cache_valid,
    rebuild_bone_name_cache,
    ensure_merge_whitelist,
    is_pose_armature_context,
    schedule_merge_whitelist_initialization,
)


class OPR_pick_scene_bone_prop(bpy.types.Operator):
    bl_idname = "opr.pick_scene_bone_prop"
    bl_label = "Knochen waehlen"
    bl_property = "selected_bone"

    prop_name: bpy.props.StringProperty(default="")
    selected_bone: bpy.props.EnumProperty(
        name="Bone",
        items=lambda self, context: get_cached_bone_items(context),
    )

    def invoke(self, context, _event):
        if not self.prop_name or not hasattr(context.scene, self.prop_name):
            return {"CANCELLED"}

        armature = get_current_armature(context)
        if armature is None:
            self.report({"WARNING"}, "Keine Armature aktiv")
            return {"CANCELLED"}

        if not is_bone_name_cache_valid(context.scene, armature):
            rebuild_bone_name_cache(context.scene, armature)

        current_value = getattr(context.scene, self.prop_name)
        bone_items = get_cached_bone_items(context)
        if bone_items:
            valid_values = {item[0] for item in bone_items}
            self.selected_bone = (
                current_value if current_value in valid_values else bone_items[0][0]
            )

        context.window_manager.invoke_search_popup(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        if hasattr(context.scene, self.prop_name):
            setattr(context.scene, self.prop_name, self.selected_bone)
            return {"FINISHED"}

        return {"CANCELLED"}


class OPR_add_merge_whitelist_item(bpy.types.Operator):
    bl_idname = "opr.add_merge_whitelist_item"
    bl_label = "Whitelist-Eintrag hinzufügen"

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


class OPR_pick_merge_whitelist_bone(bpy.types.Operator):
    bl_idname = "opr.pick_merge_whitelist_bone"
    bl_label = "Whitelist-Knochen waehlen"
    bl_property = "selected_bone"

    item_index: bpy.props.IntProperty(default=-1)
    selected_bone: bpy.props.EnumProperty(
        name="Bone",
        items=lambda self, context: get_cached_bone_items(context),
    )

    def invoke(self, context, _event):
        if self.item_index < 0:
            return {"CANCELLED"}

        armature = get_current_armature(context)
        if armature is None:
            self.report({"WARNING"}, "Keine Armature aktiv")
            return {"CANCELLED"}

        if not is_bone_name_cache_valid(context.scene, armature):
            rebuild_bone_name_cache(context.scene, armature)

        whitelist = context.scene.merge_extra_bone_whitelist
        if self.item_index >= len(whitelist):
            return {"CANCELLED"}

        current_value = whitelist[self.item_index].value
        bone_items = get_cached_bone_items(context)
        if bone_items:
            valid_values = {item[0] for item in bone_items}
            self.selected_bone = (
                current_value if current_value in valid_values else bone_items[0][0]
            )

        context.window_manager.invoke_search_popup(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        whitelist = context.scene.merge_extra_bone_whitelist
        if 0 <= self.item_index < len(whitelist):
            whitelist[self.item_index].value = self.selected_bone
            return {"FINISHED"}

        return {"CANCELLED"}


class OPR_reset_merge_whitelist(bpy.types.Operator):
    bl_idname = "opr.reset_merge_whitelist"
    bl_label = "Whitelist zurücksetzen"

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


class MERGE_WHITELIST_panel(bpy.types.Panel):
    bl_idname = "MERGE_WHITELIST_PT_panel"
    bl_label = "Merge Whitelist"
    bl_category = "Any Rig to Rigify"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        armature = get_current_armature(context)

        box = layout.box()
        box.label(text="Knochen-Übernahme")

        schedule_merge_whitelist_initialization(scn)
        box.label(text="Standardmuster und Bones des aktuellen Rigs")

        if len(scn.merge_extra_bone_whitelist) == 0:
            box.label(text="Keine Einträge vorhanden")

        row = box.row()
        col = row.column()
        for index, item in enumerate(scn.merge_extra_bone_whitelist):
            item_row = col.row(align=True)
            item_row.prop(item, "value", text=f"{index + 1}")
            pick_button = item_row.row(align=True)
            pick_button.enabled = armature is not None
            pick_op = pick_button.operator("opr.pick_merge_whitelist_bone", text="", icon="BONE_DATA")
            pick_op.item_index = index
            remove_op = item_row.operator("opr.remove_merge_whitelist_item", text="", icon="X")
            remove_op.item_index = index

        button_row = box.row(align=True)
        button_row.operator("opr.add_merge_whitelist_item", icon="ADD")
        box.operator("opr.reset_merge_whitelist", icon="FILE_REFRESH")
