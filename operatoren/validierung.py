import bpy


def is_generated_rigify_rig(armature_obj):
    if armature_obj is None or armature_obj.type != "ARMATURE":
        return False

    armature_data = getattr(armature_obj, "data", None)
    if armature_data is None:
        return False

    rig_id = armature_data.get("rig_id")
    if not isinstance(rig_id, str) or not rig_id:
        return False

    has_rig_ui_script = armature_obj.get("rig_ui") is not None
    has_rig_ui_panel = hasattr(bpy.types, f"VIEW3D_PT_rig_ui_{rig_id}")
    has_rig_layers_panel = hasattr(bpy.types, f"VIEW3D_PT_rig_layers_{rig_id}")

    return has_rig_ui_script or has_rig_ui_panel or has_rig_layers_panel


def get_generation_blocker_message(armature_obj):
    if is_generated_rigify_rig(armature_obj):
        return "nichts zu tun"

    return None
