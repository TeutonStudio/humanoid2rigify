
def _liste_seite(liste) -> list[str]:
    ausgabe = []
    for seite in SEITE:
        for inhalt in liste:
            ausgabe.append(inhalt+seite)
    return ausgabe

SEITE = ["r","l"]

WURZEL = "root"

WIRBEL = [
    "first_spine",
    "last_spine",
]
TORSO = [
    "head",
    "first_neck",
    "last_neck",
    "clav_r",
    "clav_l",
]
BEINE = [
    "thigh_",
    "calf_",
    "foot_",
    "toe_",
    "heel_",
]
ARME = [
    "uparm_",
    "lowarm_",
    "hand_",
]
FINGER = [
    "thumb_01_",
    "thumb_02_",
    "thumb_03_",
    "palm_index_",
    "index_01_",
    "index_02_",
    "index_03_",
    "palm_middle_",
    "middle_01_",
    "middle_02_",
    "middle_03_",
    "palm_ring_",
    "ring_01_",
    "ring_02_",
    "ring_03_",
    "palm_pinky_",
    "pinky_01_",
    "pinky_02_",
    "pinky_03_",
]

KNOCHEN = TORSO + WIRBEL + _liste_seite(ARME) + _liste_seite(BEINE) + _liste_seite(FINGER)
