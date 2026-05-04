from enum import Enum

import bpy

from ..__methoden__ import is_pose_armature_context

class Panele(str,Enum):
    # Körper
    DEFINITION = "VIEW3D_PT_definition"
    ERZEUGUNG = "GENERATE_PT_panel"
    #   FINGER = "FINGERS_PT_panel"
    #   ARME = "ARMS_PT_panel"
    #   TORSO = "UPPER_BODY_PT_panel"
    #   WIRBEL = "SPINES_PT_panel"
    #   BEINE = "LEGS_PT_panel"
    # Funktionen
    VERSCHMELZUNG = "MERGE_WHITELIST_PT_panel"
    ZUORDNUNG = "MAPPING_PT_panel"

class Panel(bpy.types.Panel):
    bl_category = "Any Rig to Rigify"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return is_pose_armature_context(context)

