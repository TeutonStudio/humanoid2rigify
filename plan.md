# Plan: Gesicht-Reiter fuer Rigify-Face-Generierung

## Zusammenfassung

Der aktuelle Generator entfernt nach dem Erzeugen des Human-Metarigs alle Standard-Bones und baut nur Koerper, Arme, Beine und Finger aus dem Fremdrig neu auf. Dadurch gehen die vorbereiteten Rigify-Face-Strukturen verloren und die Collections `Face (Primary)` / `Face (Secondary)` werden nicht erzeugt.

Geplant ist ein neuer Reiter `Gesicht`, ueber den der Nutzer die Quell-Bones fuer den kompletten Rigify-`faces.super_face`-Umfang definiert. Die Generierung behaelt dann die Rigify-Gesichtsstruktur des Human-Metarigs bei, richtet ihre Bones auf die angegebenen Quell-Bones aus und laesst Rigify daraus die vollstaendige Face-Rig-Struktur erzeugen.

## Wichtige Schnittstellen- und Verhaltensaenderungen

- Neuer UI-Reiter `Gesicht` unter `schnittstelle/reiter/gesicht.py`, registriert in `schnittstelle/reiter/__init__.py`.
- Neue Scene-Properties in `schnittstelle/eigenschaften.py` fuer den vollstaendigen Face-Mapping-Satz, gruppiert nach Regionen:
  - Basis: `jaw`, `eye_l`, `eye_r`, `tongue`, `tongue_001`, `tongue_002`
  - Nase: `nose`, `nose_001`, `nose_002`, `nose_003`, `nose_004`, `nose_l`, `nose_l_001`, `nose_r`, `nose_r_001`
  - Lippen: `lip_t_l`, `lip_t_l_001`, `lip_t_r`, `lip_t_r_001`, `lip_b_l`, `lip_b_l_001`, `lip_b_r`, `lip_b_r_001`
  - Augenbrauen unten: `brow_b_l`, `brow_b_l_001`, `brow_b_l_002`, `brow_b_l_003`, `brow_b_r`, `brow_b_r_001`, `brow_b_r_002`, `brow_b_r_003`
  - Augenbrauen oben: `brow_t_l`, `brow_t_l_001`, `brow_t_l_002`, `brow_t_l_003`, `brow_t_r`, `brow_t_r_001`, `brow_t_r_002`, `brow_t_r_003`
  - Ohren/Kieferseiten: `ear_l`, `ear_l_001`, `ear_l_002`, `ear_l_003`, `ear_l_004`, `ear_r`, `ear_r_001`, `ear_r_002`, `ear_r_003`, `ear_r_004`, `jaw_l`, `jaw_l_001`, `jaw_r`, `jaw_r_001`
- Kein separates `face_root`-Feld: Der Metarig-Bone `face` wird intern automatisch aus `head` abgeleitet und bleibt fuer den Nutzer unsichtbar.
- `operatoren/objekt.py` erweitert den `params`-Payload um alle Face-Keys.
- `operatoren/importieren.py`, `operatoren/speichern.py` und `operatoren/bone_mapping.py` werden um dieselben Face-Keys erweitert, damit Presets konsistent importiert, gespeichert und spaeter auch in Merge-/Constraint-Logik bekannt sind.
- `mapping_templates/*.json` bleiben abwaertskompatibel:
  - Import verwendet fuer neue Face-Keys `data.get(key, "")`, damit alte Presets ohne Fehler geladen werden.
  - Save schreibt immer den vollstaendigen neuen Schluesselsatz.
- `operatoren/any_rig_to_rigify_v2.py` bekommt eine getrennte Face-Behandlung:
  - Die Human-Metarig-Face-Bones werden nicht mehr pauschal geloescht.
  - Koerper-/Finger-/Bein-Bones werden weiterhin wie heute auf Basis des Fremdrigs aufgebaut.
  - Face-Bones aus dem Human-Metarig bleiben als Rigify-Vorlage erhalten und werden per expliziter Mapping-Tabelle auf die Quell-Bones ausgerichtet.
  - Nicht gesetzte Face-Properties fuehren dazu, dass der jeweilige Face-Bone auf der Rigify-Seite unangetastet bleibt; der v1-Plan geht aber davon aus, dass fuer vollstaendige Face-Generierung alle benoetigten Felder gesetzt werden.
- Die Face-Bone-Collections des Human-Metarigs bleiben erhalten, damit Rigify wie vorgesehen `Face`, `Face (Primary)` und `Face (Secondary)` erzeugt.
- Die Constraint-Erzeugung fuer den Standardmodus wird um Face-Bones erweitert, damit vorhandene Quell-Gesichtsbones auf die generierten Rigify-DEF-/Face-Bones gemappt werden koennen. Dabei werden Face-Bones nicht als `extra_bones` behandelt, sondern als eigener Standardbereich.

## Implementierungsdetails

- UI:
  - Der neue Reiter nutzt dasselbe Muster wie die bestehenden Reiter: `draw_bone_prop_with_status`.
  - Die Darstellung wird nach Regionen in mehrere Boxen geteilt, nicht als flache Langliste.
  - Feldnamen im UI koennen benutzerfreundlich sein, intern bleiben die Property-Keys ASCII-konsistent wie oben.
- Metarig-Aufbau:
  - Vor dem Loeschen vorhandener Human-Metarig-Bones wird eine feste Menge `protected_face_bones` definiert, die alle fuer `faces.super_face` benoetigten Bones enthaelt.
  - Die bestehende "alles loeschen und neu erzeugen"-Logik wird so umgebaut, dass nur nicht geschuetzte Bones entfernt werden.
  - Fuer jeden Face-Key wird der entsprechende geschuetzte Metarig-Bone anhand des Quell-Bones in Position, Tail und Roll ausgerichtet.
  - Elternbeziehungen innerhalb des Face-Baums bleiben die des Human-Metarigs; sie werden nicht aus dem Fremdrig rekonstruiert.
- Datenmodell:
  - Es wird eine zentrale `FACE_PARAM_KEYS`-Liste eingefuehrt, die von UI-nahen Teilen, Save/Import und Generator gemeinsam genutzt wird, um Duplikate zu reduzieren.
  - Falls sinnvoll, wird `PARAM_BONE_KEYS` in `operatoren/bone_mapping.py` um die Face-Keys erweitert oder in `BODY_PARAM_BONE_KEYS` plus `FACE_PARAM_KEYS` aufgeteilt und zusammengefuehrt.
- Constraint-/Mapping-Logik:
  - Face-Bones werden in eine dedizierte Standard-Mapping-Tabelle aufgenommen statt implizit als Zusatzknochen durchzulaufen.
  - Fuer Quell-Bones, deren Ziel nicht `DEF-*` ist, wird die bestehende Zielnamensnormalisierung nur dort erweitert, wo Rigify-Face-Bones abweichende Namen brauchen; die Implementierung soll das explizit pro Face-Key entscheiden und nicht ueber pauschales Prefixing.
- Fehlerverhalten:
  - Kein harter Abbruch bei einzelnen fehlenden Face-Bones im UI.
  - Statusanzeige im Panel markiert fehlende Bones wie bei den anderen Reitern.
  - Der Generate-Operator soll vor Start eine Face-Vollstaendigkeitspruefung ausfuehren, sobald mindestens ein Face-Feld befuellt ist:
    - Entweder ist kein Face-Mapping aktiv.
    - Oder alle Face-Pflichtfelder des gewaehlten Vollumfangs sind gesetzt.
  - Bei unvollstaendigem Face-Mapping wird mit `self.report({"ERROR"}, ...)` abgebrochen, damit keine halbe Face-Rig-Struktur entsteht.

## Tests und Abnahmekriterien

- UI:
  - Der neue Reiter erscheint in der Sidebar neben den bestehenden Reitern.
  - Alle Face-Felder zeigen den vorhandenen/fehlenden Bone-Status des aktuell selektierten Armatures.
- Presets:
  - Altes Preset ohne Face-Keys laesst sich importieren, ohne Ausnahme und mit leeren Face-Feldern.
  - Neues Preset speichert und laedt alle Face-Keys verlustfrei.
- Generierung ohne Gesicht:
  - Bestehende Rigs ohne Face-Mapping verhalten sich wie bisher fuer Koerper, Finger, Beine und Merge-Modi.
  - Es gibt keine Regression bei der bisherigen Rigify-Erzeugung.
- Generierung mit vollstaendigem Gesicht:
  - Nach `Generate Rigify` existieren im Ergebnis die Rigify-Face-Collections `Face`, `Face (Primary)` und `Face (Secondary)`.
  - Die Metarig-Face-Bones wurden nicht durch die generische Loeschlogik entfernt.
  - Das generierte Rig enthaelt die erwarteten Face-Controls und die Quell-Gesichtsbones koennen auf die Rigify-Ziele gemappt werden.
- Validierung:
  - Teilweise gesetzte Face-Mappings fuehren zu einer klaren Fehlermeldung statt zu einem unvollstaendig generierten Rig.
  - Alte Mapping-JSONs bleiben importierbar.

## Annahmen und Defaults

- Gewuenschter Umfang fuer v1 ist `vollstaendig`, also der komplette Rigify-`faces.super_face`-Satz und nicht nur ein reduziertes MVP.
- Der interne `face`-Root wird automatisch aus `head` abgeleitet; es gibt dafuer kein zusaetzliches Nutzerfeld.
