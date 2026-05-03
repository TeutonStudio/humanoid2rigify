def is_generated_rigify_rig(armature_obj):
    if armature_obj is None or armature_obj.type != "ARMATURE":
        return False

    if "rig_id" in armature_obj.keys():
        return True

    armature_data = armature_obj.data
    if armature_data is not None and "rig_id" in armature_data.keys():
        return True

    bone_names = [bone.name for bone in armature_obj.data.bones]
    def_bones = [name for name in bone_names if name.startswith("DEF-")]
    org_bones = [name for name in bone_names if name.startswith("ORG-")]
    mch_bones = [name for name in bone_names if name.startswith("MCH-")]

    if len(def_bones) >= 5 and (len(org_bones) >= 1 or len(mch_bones) >= 1):
        return True

    if len(def_bones) >= 10 and "root" in bone_names:
        return True

    return False


def get_generation_blocker_message(armature_obj):
    if is_generated_rigify_rig(armature_obj):
        return "nichts zu tun"

    return None
