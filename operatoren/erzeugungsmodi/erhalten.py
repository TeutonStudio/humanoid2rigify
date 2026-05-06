from __future__ import annotations

from ..rigify import RigifyBauModus


class OriginalErhalter(RigifyBauModus):
    def erzeuge(self) -> bool:
        rigify_obj = self.erzeuge_rigify_rig()

        copied_shapes = self.uebernehme_custom_shapes(
            rigify_obj,
            "constraint_target",
        )

        self.report(
            {"INFO"},
            (
                "Original behalten. "
                f"{copied_shapes} Custom Shapes übernommen oder ersetzt."
            ),
        )

        return True