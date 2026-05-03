from operatoren import any_rig_to_rigify_v2
from operatoren.backup import create_backups
from operatoren.kontext import create_generation_context
from operatoren.validierung import get_generation_blocker_message


MODE_CONSTRAINT_NEW_RIGIFY = "CONSTRAINT_NEW_RIGIFY"
MODE_DEFORM_RIG_CONSTRAINT_NEW_RIGIFY = "DEFORM_RIG_CONSTRAINT_NEW_RIGIFY"
MODE_MERGE_WITH_NEW_RIGIFY = "MERGE_WITH_NEW_RIGIFY"


def run_constraint_mode(context):
    create_backups(context)
    any_rig_to_rigify_v2.the_script(context.source_armature, context.params)
    context.operator.report(
        {"INFO"},
        f"Backup erstellt: {context.backup_collection.name}",
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
        operator.report(
            {"INFO"},
            (
                "Analyse vorbereitet: "
                f"{len(context.used_deform_bones)} benutzte Deform-Bones, "
                f"{len(context.extra_bones)} Zusatzknochen. "
                "Der Deformationsrig-Modus folgt im naechsten Umbauabschnitt."
            ),
        )
        return False

    if context.generation_mode == MODE_MERGE_WITH_NEW_RIGIFY:
        operator.report(
            {"INFO"},
            (
                "Analyse vorbereitet: "
                f"{len(context.used_deform_bones)} benutzte Deform-Bones, "
                f"{len(context.extra_bones)} Zusatzknochen. "
                "Der Verschmelzungs-Modus folgt im naechsten Umbauabschnitt."
            ),
        )
        return False

    operator.report({"ERROR"}, "Unbekannter Erzeugungsmodus")
    return False
