# Umbauplan Any Rig to Rigify

## Ziel

Das Add-on soll drei Erzeugungsmodi unter einer gemeinsamen UI anbieten:

1. `Constraint auf neues Rigify`
2. `rig zu deformationsrig constraint auf neues rigify`
3. `mit neuem rigify verschmelzen`

Die UI-Auswahl ist bereits vorhanden. Der folgende Plan beschreibt den kompletten technischen Umbau auf Basis der neuen Projektstruktur.

## Aktuelle Struktur

- `__init__.py`
  Einstiegspunkt, delegiert nur an `schnittstelle` und `operatoren`.
- `schnittstelle/`
  UI, Scene-Properties und Panel-Registrierung.
- `operatoren/`
  Blender-Operatoren und die eigentliche Erzeugungslogik.
- `operatoren/any_rig_to_rigify_v2.py`
  Monolithischer Kern mit Rigify-Erzeugung, Metarig-Aufbau und Constraint-Anlage.

## Bereits festgelegte Anforderungen

- Modus 1 soll exakt das bisherige Verhalten abbilden.
- Modus 2:
  Das alte Rig bleibt das Deformationsrig.
- Modus 2:
  Nicht-Deformationsknochen im alten Rig werden geloescht.
- Modus 2:
  Im alten Rig bleiben nur deformierende Knochen erhalten, die tatsaechlich von Meshes benutzt werden.
- Modus 2:
  Das alte Rig wird weiter vom neuen Rigify bewegt.
- Modus 2:
  Meshes bleiben am alten Rig gebunden.
- Modus 2:
  Zusaetzliche Bones werden in das neue Rig uebernommen; deformierende Zusatzknochen bleiben im alten Rig erhalten.
- Modus 3:
  Am Ende soll nur das neue Rigify-Rig uebrig bleiben.
- Modus 3:
  Das neue Rigify-Rig soll die Meshes direkt deformieren.
- Modus 3:
  Vertex Groups sollen auf passende Rigify-`DEF-...`-Bones ueberfuehrt werden.
- Modus 3:
  Falls kein passender Rigify-Deform-Knochen existiert, soll ein neuer Bone `DEF-{alter knochenname}` erzeugt werden.
- Modus 3:
  Zusatzknochen sollen in das neue Rig uebernommen werden.
- Modus 3:
  Das alte Rig soll nach erfolgreichem Abschluss automatisch geloescht werden.
- Vor destruktiven Schritten soll automatisch ein Backup erzeugt werden.
- Wenn das Quellrig bereits ein Rigify-Rig ist, soll abgebrochen werden mit Rueckmeldung `nichts zu tun`.
- Der Erzeugungsmodus bleibt reine UI-Einstellung und wird nicht in Presets gespeichert.

## Zielarchitektur

Der Umbau sollte nicht direkt weiter in `operatoren/any_rig_to_rigify_v2.py` gestapelt werden. Die Datei hat aktuell 1725 Zeilen und enthaelt sowohl Generierung als auch Nachbearbeitung. Sinnvoll ist eine Aufteilung in orchestrierende und spezialisierte Bausteine.

### Empfohlene Modulaufteilung

- `operatoren/__methoden__.py`
  Bleibt der einfache Einstieg fuer den Operator, ruft aber kuenftig nur noch den Dispatcher auf.
- `operatoren/objekt.py`
  Bleibt fuer das Sammeln der UI-Parameter zustaendig.
- `operatoren/any_rig_to_rigify_v2.py`
  Wird zunaechst als Kern fuer Metarig- und Rigify-Erzeugung weiterverwendet.
- `operatoren/erzeugung_dispatcher.py`
  Neuer Dispatcher fuer Moduswahl, Validierung, Backup und Fehlerfluss.
- `operatoren/kontext.py`
  Baut ein gemeinsames Arbeitsobjekt fuer Quelle, erzeugtes Rigify, betroffene Meshes, Backup-Namen und Bone-Mapping.
- `operatoren/validierung.py`
  Erkennt Rigify-Quellrigs und prueft Vorbedingungen.
- `operatoren/backup.py`
  Erstellt Backups von Armature, Meshes und Armature-Modifiers.
- `operatoren/mesh_analyse.py`
  Ermittelt alle Meshes, Vertex Groups und tatsaechlich genutzte deformierende Bones.
- `operatoren/deform_modus.py`
  Implementiert Modus 2.
- `operatoren/verschmelzen_modus.py`
  Implementiert Modus 3.
- `operatoren/zusatzknochen.py`
  Uebernahme von Bones ausserhalb des Standard-Mappings.
- `operatoren/vertex_groups.py`
  Umbenennen, Kopieren und Anlegen von Vertex Groups fuer DEF-Bones.
- `operatoren/armature_cleanup.py`
  Aufraeumen, Loeschen, Ausblenden und Modifier-Umbau.

Dateinamen koennen noch an den vorhandenen deutschen Stil angepasst werden; entscheidend ist die Trennung der Verantwortung.

## Geplanter Ablauf je Modus

### Gemeinsamer Ablauf

1. Selektion und aktive Armature bestimmen.
2. Pruefen, ob das Quellrig bereits ein Rigify-Rig ist.
3. Betroffene Meshes finden.
4. Backup aller betroffenen Objekte anlegen.
5. Baseline-Rigify wie bisher erzeugen.
6. Bone-Mapping zwischen Quellrig und neuem Rigify herstellen.
7. Modusspezifische Nachbearbeitung ausfuehren.
8. Erfolg oder klare Fehler-/Warnmeldungen reporten.

### Modus 1: Constraint auf neues Rigify

Soll funktional identisch zum heutigen Verhalten bleiben.

Geplante Massnahme:

- Den bisherigen Constraint-Pfad aus `any_rig_to_rigify_v2.the_script(...)` unveraendert kapseln.
- Nur Vorvalidierung und optionales Backup davor setzen.

### Modus 2: rig zu deformationsrig constraint auf neues rigify

Ziel:
Das alte Rig bleibt Deformationsrig fuer die Meshes, verliert aber alle unnoetigen Nicht-Deform-Knochen.

Geplanter Ablauf:

1. Standard-Rigify wie heute erzeugen.
2. Standard-Constraints wie heute vom neuen Rigify auf das alte Rig anlegen.
3. Alle Meshes am alten Rig sammeln.
4. Menge der wirklich benutzten deformierenden Bones bestimmen:
   Nur Bones beruecksichtigen, deren Vertex Groups in mindestens einem Mesh Gewichte tragen.
5. Zusatzknochen klassifizieren:
   deformierend benutzt / nicht deformierend / rein steuernd.
6. Nicht benoetigte Bones im alten Rig loeschen:
   Alle Nicht-Deform-Bones entfernen.
7. Deformierende Zusatzknochen im alten Rig erhalten.
8. Falls zusaetzliche Steuer- oder Hilfsknochen im neuen Rig gebraucht werden, dort als neue Bones anlegen und passend constrainen.
9. Final pruefen, dass alle Armature-Modifier weiterhin auf das alte Rig zeigen.

Offene technische Konsequenz:
Bone-Loeschungen duerfen erst nach dem Constraint-Aufbau und nach sauberer Ermittlung der benoetigten deformierenden Bones passieren.

### Modus 3: mit neuem rigify verschmelzen

Ziel:
Das neue Rigify-Rig deformiert direkt. Das alte Rig wird am Ende entfernt.

Geplanter Ablauf:

1. Standard-Rigify erzeugen.
2. Bone-Mapping fuer alle Standard-Knochen auf passende Rigify-DEF-Bones aufbauen.
3. Zusatzknochen uebernehmen:
   Falls fuer einen alten deformierenden Bone kein passender Rigify-DEF-Bone existiert, im neuen Rig `DEF-{alter knochenname}` erzeugen.
4. Uebernommene Zusatzknochen in die Rigify-Hierarchie sauber einhaengen.
5. Meshes analysieren und Vertex-Group-Migration vorbereiten.
6. Vertex Groups migrieren:
   Vorhandene Gruppen auf neue DEF-Bones umbenennen oder in diese kopieren.
7. Armature-Modifier aller betroffenen Meshes vom alten Rig auf das neue Rigify umstellen.
8. Optional verbleibende Constraints oder Hilfsdaten bereinigen.
9. Altes Rig loeschen.
10. Erfolg pruefen:
    Meshes haben weiterhin gueltige Modifier und alle benoetigten Vertex Groups zeigen auf Bones des neuen Rigs.

## Kernprobleme, die der Umbau loesen muss

### 1. Rigify-Erkennung fuer `nichts zu tun`

Es braucht eine robuste Erkennung fuer Quellrigs, die bereits Rigify sind. Geplanter Ansatz:

- Primar ueber Rigify-spezifische Custom Properties oder bekannte Daten am erzeugten Rig pruefen.
- Sekundaer ueber typische Rigify-Struktur als Fallback.
- Keine rein namensbasierte Erkennung.

### 2. Backup vor destruktiven Schritten

Backup muss mindestens enthalten:

- Quell-Armature
- alle direkt daran gebundenen Meshes
- deren Armature-Modifier-Konfiguration

Geplanter Ansatz:

- Duplikate in derselben Szene erzeugen
- klar mit Prefix oder Suffix markieren, zum Beispiel `_backup`
- Sammlung fuer Backups verwenden, falls sinnvoll

### 3. Bestimmung “tatsaechlich benutzter deformierender Bones”

Geplante Regel:

- Bone zaehlt als benutzt, wenn mindestens ein Mesh eine Vertex Group gleichen Namens hat und mindestens ein Vertex dieser Gruppe zugeordnet ist.

### 4. Migration von Zusatzknochen

Es braucht einen systematischen Unterschied zwischen:

- Standard-Bones, die bereits ins Mapping fallen
- Zusatzknochen mit Deformationsfunktion
- Zusatzknochen ohne Deformationsfunktion

Fuer Modus 3 muessen deformierende Zusatzknochen als `DEF-*` im neuen Rig vorhanden sein.
Fuer Modus 2 muessen deformierende Zusatzknochen im alten Rig erhalten bleiben.

### 5. Vertex-Group-Migration

Nicht jede Gruppe darf nur stumpf umbenannt werden. Es braucht Regeln fuer:

- direktes Umbenennen
- Kopieren in neue Gruppe
- Zusammenfuehren mehrerer alter Gruppen auf eine neue DEF-Gruppe
- Anlegen neuer Gruppen fuer uebernommene Zusatzknochen

### 6. Restpose- und Achsdifferenzen

Der heutige Constraint-Pfad kompensiert Rotationsdifferenzen zwischen Alt- und Neu-Rig. Beim Verschmelzen reicht das nicht aus, weil das Mesh direkt auf dem neuen Rig haengen wird.

Der Plan muss daher absichern:

- Standard-DEF-Bones werden nur dort direkt verwendet, wo ihre Reststruktur zur bisherigen Mapping-Logik passt.
- Fuer Zusatzknochen, die neu erzeugt werden, muessen Head, Tail, Roll und Parent aus dem alten Rig konsistent uebernommen werden.

## Geplante Refactor-Phasen

### Phase 1: Infrastruktur fuer den Umbau

- Dispatcher fuer `generation_mode` einfuehren.
- Gemeinsamen Erzeugungskontext bauen.
- Rigify-Erkennung und Abbruchpfad `nichts zu tun` einbauen.
- Backup-System einfuehren.
- Heutiges Verhalten als Modus 1 unveraendert einkapseln.

Ergebnis:
Es gibt einen stabilen Einstiegspunkt fuer alle drei Modi, ohne das bisherige Verhalten zu brechen.

### Phase 2: Analyse- und Mapping-Schicht

- Helfer fuer Quellrig, Meshes, Modifier und Vertex Groups erstellen.
- Bone-Nutzung ueber Meshdaten auswerten.
- Zentralen Bone-Mapping-Container erstellen:
  Alt-Bone -> Ziel-DEF-Bone oder neu anzulegender DEF-Bone.
- Zusatzknochen-Erkennung einfuehren.

Ergebnis:
Der Code weiss fuer jeden Modus, welche Bones deformieren und wohin sie spaeter gehoeren.

### Phase 3: Modus 2 implementieren

- Constraint-Grundpfad des bisherigen Systems wiederverwenden.
- Benutzte Deform-Bones im alten Rig identifizieren.
- Nicht-Deform-Bones loeschen.
- Zusatzknochen-Regeln fuer Deformationsmodus umsetzen.
- Tests mit gemischten Rigs und Zusatzknochen.

Ergebnis:
Das alte Rig bleibt schlank als Deformationsrig erhalten.

### Phase 4: Modus 3 implementieren

- Zusatz-DEF-Bones im neuen Rig anlegen.
- Vertex Groups migrieren.
- Armature-Modifier umhaengen.
- Altes Rig loeschen.
- Mesh-/Bone-Validierung nach Migration einbauen.

Ergebnis:
Nur das neue Rigify-Rig bleibt uebrig und deformiert direkt.

### Phase 5: Aufraeumen und Stabilisieren

- Monolithische Hilfslogik aus `any_rig_to_rigify_v2.py` schrittweise auslagern.
- Fehlertexte und Blender-Reports vereinheitlichen.
- Doppelausfuehrungsschutz verbessern.
- Smoke-Tests fuer alle drei Modi dokumentieren.

## Konkrete Dateiaenderungen

### Bereits vorhanden und weiter zu bearbeiten

- `schnittstelle/eigenschaften.py`
  UI-Property fuer den Modus ist bereits vorhanden.
- `schnittstelle/reiter/erzeuger.py`
  Dropdown ist bereits im Generate-Panel eingebunden.
- `operatoren/objekt.py`
  Uebergibt `generation_mode` bereits an den Param-Block.
- `operatoren/__methoden__.py`
  Muss vom direkten Aufruf des Monolithen auf den neuen Dispatcher umgestellt werden.
- `operatoren/any_rig_to_rigify_v2.py`
  Soll zuerst als Kernmodul bestehen bleiben, danach selektiv entlastet werden.

### Neu anzulegen oder klar aufzuteilen

- `operatoren/erzeugung_dispatcher.py`
- `operatoren/kontext.py`
- `operatoren/validierung.py`
- `operatoren/backup.py`
- `operatoren/mesh_analyse.py`
- `operatoren/deform_modus.py`
- `operatoren/verschmelzen_modus.py`
- `operatoren/zusatzknochen.py`
- `operatoren/vertex_groups.py`
- `operatoren/armature_cleanup.py`

## Technische Akzeptanzkriterien

### Modus 1

- Verhalten bleibt identisch zum heutigen Add-on.
- Bereits Rigify-basierte Quellrigs werden mit `nichts zu tun` abgewiesen.
- Backup wird vor dem Eingriff erstellt.

### Modus 2

- Neues Rigify wird erzeugt.
- Altes Rig wird vom neuen Rigify bewegt.
- Altes Rig enthaelt nur noch tatsaechlich benutzte deformierende Bones.
- Meshes bleiben auf das alte Rig gemodifiert.
- Deformierende Zusatzknochen bleiben erhalten.

### Modus 3

- Neues Rigify wird erzeugt.
- Meshes zeigen auf das neue Rigify.
- Fehlende deformierende Zielknochen werden als `DEF-*` im neuen Rig erstellt.
- Vertex Groups sind auf das neue Rig migriert.
- Zusatzknochen sind uebernommen.
- Altes Rig ist geloescht.

## Testplan

### Mindestfaelle

- Mixamo-Rig ohne Zusatzknochen
- Rig mit Gesicht-, Kleidungs- oder Prop-Bones
- Rig mit unbenutzten Bones
- Rig mit mehreren Meshes am selben Armature-Objekt
- Rig, das bereits Rigify ist

### Pro Modus pruefen

- Objektanzahl vor/nach Lauf
- Armature-Modifier-Ziel
- Vorhandene Vertex Groups
- Erhaltene Animation und Deformation
- Erfolgsmeldung oder definierte Fehlermeldung

## Empfohlene Implementierungsreihenfolge

1. Dispatcher, Validierung und Backup
2. Modus 1 stabil kapseln
3. Mesh- und Bone-Analyse
4. Modus 2 komplett
5. Zusatzknochen-Uebernahme abstrahieren
6. Vertex-Group-Migration
7. Modus 3 komplett
8. Monolith schrittweise entlasten

## Hinweise zur Umsetzung

- Zuerst Verhalten kapseln, dann umformen. Nicht gleichzeitig Refactor und Feature-Umbau mischen.
- Keine destruktiven Schritte ohne vorherigen Backup-Pfad.
- Fuer Modus 3 zuerst Mapping und Modifier-Umbau implementieren, erst danach automatisches Loeschen des alten Rigs aktivieren.
- Zusatzknochen sollten ueber einen separaten Datenpfad laufen und nicht zwischen Standard-Humanoid-Mapping und Sonderfaellen vermischt werden.
