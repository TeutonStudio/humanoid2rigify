from abc import abstractmethod
from enum import Enum
from itertools import chain
from typing import Callable, Iterator

from typing_extensions import override


def _liste_seite(liste:Callable[[str],Iterator[str]]) -> Iterator[str]:
    for seite in Seite: yield from liste(seite.value)

class Seite(str,Enum):
    LINKS = "l"
    RECHTS = "r"

    def erhalte_label(self) -> str:
        if self == Seite.LINKS: return "Links"
        if self == Seite.RECHTS: return "Rechts"
        return ""

type KEnum = type[KnochenEnum] | type[LRKnochenEnum]

class KnochenEnum(str,Enum):
    @classmethod
    def knochen(cls) -> Iterator[str]:
        for knochen in cls: yield f"{knochen.value}"

class LRKnochenEnum(str,Enum):
    @classmethod
    def knochen(cls,seiten_suffix:str) -> Iterator[str]:
        for knochen in cls: yield f"{knochen.value}_{seiten_suffix}"

#   WURZEL = "root"

#   WIRBEL = [
#       "first_spine",
#       "last_spine",
#   ]
#   TORSO = [
#       "head",
#       "first_neck",
#       "last_neck",
#       "clav_r",
#       "clav_l",
#   ]
#   BEINE = [
#       "thigh_",
#       "calf_",
#       "foot_",
#       "toe_",
#       "heel_",
#   ]
#   ARME = [
#       "uparm_",
#       "lowarm_",
#       "hand_",
#   ]
#   FINGER = [
#       "thumb_01_",
#       "thumb_02_",
#       "thumb_03_",
#       "palm_index_",
#       "index_01_",
#       "index_02_",
#       "index_03_",
#       "palm_middle_",
#       "middle_01_",
#       "middle_02_",
#       "middle_03_",
#       "palm_ring_",
#       "ring_01_",
#       "ring_02_",
#       "ring_03_",
#       "palm_pinky_",
#       "pinky_01_",
#       "pinky_02_",
#       "pinky_03_",
#   ]
class Wirbelsäule(KnochenEnum):
    WURZEL = "root"
    WIRBELANFANG = "first_spine"
    WIRBELABSCHLUSS = "last_spine"
    NACKENANFANG = "first_neck"
    NACKENABSCHLUSS = "last_neck"
    KOPF = "head"

    @classmethod
    def knochen(cls) -> Iterator[str]:
        for knochen in cls: yield f"{knochen.value}"

class Beine(LRKnochenEnum):
    SCHENKEL = "thigh"
    WADE = "calf"
    FUSS = "foot"
    ZEHEN = "toe"
    FERSE = "heel"

#    @classmethod
#    def knochen(cls, seiten_suffix: str) -> Iterator[str]:
#        for knochen in cls: yield f"{knochen.value}_{seiten_suffix}"

class Arme(LRKnochenEnum):
    SCHULTER = "clav"
    OBERARM = "uparm"
    UNTERARM = "lowarm"
    HAND = "hand"

#    @classmethod
#    def knochen(cls, seiten_suffix: str) -> Iterator[str]:
#        for knochen in cls: yield f"{knochen.value}_{seiten_suffix}"

class Finger(LRKnochenEnum):
    DAUMEN = "thumb"
    ZEIGE = "index"
    MITTEL = "middle"
    RING = "ring"
    KLEIN = "pinky"

    @classmethod
    @override
    def knochen(cls, seiten_suffix: str) -> Iterator[str]:
        for knochen in cls: yield from knochen.finger_knochen(seiten_suffix)

    def finger_knochen(self,seiten_suffix:str) -> Iterator[str]:
        if self is not Finger.DAUMEN:
            yield f"palm_{self.value}_{seiten_suffix}"

        for idx in range(1, 4):
            yield f"{self.value}_{idx:02d}_{seiten_suffix}"


#   KNOCHEN = [WURZEL] + TORSO + WIRBEL + _liste_seite(ARME) + _liste_seite(BEINE) + _liste_seite(FINGER)

KNOCHEN = list(chain(
    Wirbelsäule.knochen(),
    _liste_seite(Arme.knochen),
    _liste_seite(Beine.knochen),
    _liste_seite(Finger.knochen),
))
