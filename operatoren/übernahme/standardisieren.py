from ...__methoden__ import reset_merge_whitelist_groups
from ..__operator__ import Operator, Operatoren


class OPR_reset_merge_whitelist_groups(Operator):
    bl_idname = Operatoren.WHITELIST_GRUPPE_STANDARDISIEREN.value
    bl_label = "Whitelist-Gruppen zurücksetzen"
    bl_options = {"UNDO"}

    def execute(self, context):
        reset_merge_whitelist_groups(context.scene)
        return {"FINISHED"}