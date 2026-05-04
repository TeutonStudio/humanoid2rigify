from ..__operator__ import Operatoren, Operator


class OPR_add_merge_whitelist_group(Operator):
    bl_idname = Operatoren.WHITELIST_GRUPPE_HINZUFUEGEN
    bl_label = "Whitelist-Gruppe hinzufügen"
    bl_options = {"UNDO"}

    def execute(self, context):
        group = context.scene.merge_extra_bone_groups.add()
        group.name = "Neue Gruppe"
        group.expanded = True
        context.scene.merge_extra_bone_group_active_index = (
            len(context.scene.merge_extra_bone_groups) - 1
        )
        return {"FINISHED"}