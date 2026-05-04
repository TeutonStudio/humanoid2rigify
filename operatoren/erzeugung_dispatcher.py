from . import any_rig_to_rigify_v2
from .backup import create_backups
from .kontext import create_generation_context
from .custom_shapes import inherit_missing_custom_shapes
from .deform_modus import run_deform_mode
from .rigify_access import get_generated_rigify_object
from .verschmelzen_modus import run_merge_mode
from .validierung import get_generation_blocker_message


MODE_CONSTRAINT_NEW_RIGIFY = "CONSTRAINT_NEW_RIGIFY"
MODE_DEFORM_RIG_CONSTRAINT_NEW_RIGIFY = "DEFORM_RIG_CONSTRAINT_NEW_RIGIFY"
MODE_MERGE_WITH_NEW_RIGIFY = "MERGE_WITH_NEW_RIGIFY"


def run_constraint_mode(context):
    create_backups(context)
    any_rig_to_rigify_v2.the_script(context.source_armature, context.params)
    rigify_obj = get_generated_rigify_object(context.source_armature)
    copied_shapes = 0
    if rigify_obj is not None:
        copied_shapes = inherit_missing_custom_shapes(
            context,
            rigify_obj,
            "constraint_target",
        )
    context.operator.report(
        {"INFO"},
        (
            f"Backup erstellt: {context.backup_collection.name}. "
            f"{copied_shapes} Custom Shapes übernommen oder ersetzt."
        ),
    )
    return True


def dispatch_generation(operator, armature_obj, params):
    blocker_message = get_generation_blocker_message(armature_obj)
    if blocker_message is not None:
        operator.report({"INFO"}, blocker_message)
        return False

    context = create_generation_context(operator, armature_obj, params)

    if context.generation_mode == MODE_CONSTRAINT_NEW_RIGIFY:
        return run_constraint_mode(context)

    if context.generation_mode == MODE_DEFORM_RIG_CONSTRAINT_NEW_RIGIFY:
        return run_deform_mode(context)

    if context.generation_mode == MODE_MERGE_WITH_NEW_RIGIFY:
        return run_merge_mode(context)

    operator.report({"ERROR"}, "Unbekannter Erzeugungsmodus")
    return False
