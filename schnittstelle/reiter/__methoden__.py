import bpy

def get_selected_armature(context):
    active_object = context.active_object
    if active_object is not None and active_object.type == "ARMATURE":
        return active_object

    for obj in context.selected_objects:
        if obj.type == "ARMATURE":
            return obj

    return None


def get_bone_status(context, bone_name):
    armature = get_selected_armature(context)
    if armature is None:
        return "missing_armature"

    if bone_name and bone_name in armature.data.bones:
        return "found"

    return "missing_bone"


def draw_bone_status(layout, context, bone_name):
    status = get_bone_status(context, bone_name)
    status_row = layout.row()

    if status == "missing_armature":
        status_row.enabled = False
        status_row.label(text="Kein Skelett ausgewählt", icon="INFO")
        return

    if status == "found":
        status_row.label(text="Knochen gefunden", icon="CHECKMARK")
        return

    status_row.alert = True
    status_row.label(
        text="Knochen existiert im aktuellen Skelett nicht",
        icon="ERROR",
    )


def draw_bone_prop_with_status(layout, context, scene, prop_name):
    armature = get_selected_armature(context)
    prop_label = scene.bl_rna.properties[prop_name].name

    if armature is not None:
        layout.prop_search(
            scene,
            prop_name,
            armature.data,
            "bones",
            text=prop_label,
        )
    else:
        row = layout.row()
        row.enabled = False
        row.prop(scene, prop_name, text=prop_label)
