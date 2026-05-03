import bpy

from operatoren.erzeugung_dispatcher import dispatch_generation


def generate_rig(self, objects, params):
    # pop up menu if no object were selected
    if len(objects) == 0:
        print("no objects selected")
        self.report({"ERROR"}, "No object was selected")
    else:
        # get armature from objects selected
        armature_objects = [a for a in objects if a.type == "ARMATURE"]

        # pop up menu if no armature in object selected
        if len(armature_objects) == 0:
            self.report({"ERROR"}, "No armature in object selected")

        for arm in armature_objects:
            # force exit from EDIT/POSE modes
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.select_all(action="DESELECT")

            # make armature active object
            arm.select_set(True)
            bpy.context.view_layer.objects.active = arm
            dispatch_generation(self, arm, params)
