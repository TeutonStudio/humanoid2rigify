from __future__ import annotations

from ..rigify import RigifyBauModus


class RigVerschmelzer(RigifyBauModus):
    def erzeuge(self) -> bool:
        self.report(
            {"ERROR"},
            "Der Verschmelzungsmodus ist aktuell deaktiviert.",
        )
        return False