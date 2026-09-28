---
name: tov
description: Kalibriert den Ton-of-Voice für E-Mails an Guntrams echten Schreibstil. Vorher/Nachher-Paare messen, Regler nachziehen, Drafts vor dem Absenden prüfen. Nutze diesen Skill bei "tov", "Ton kalibrieren", "Vorher/Nachher", "so hätte ich das geschrieben", "prüf den Draft", "warum ist die Mail so lang", wenn Guntram eine korrigierte Fassung einer generierten Mail zeigt, oder wenn beim Touchdown gesendete Mails gegen gespeicherte Drafts abgeglichen werden sollen.
---

# ToV: Ton kalibrieren

Der Stil wird nicht beschrieben, sondern gemessen. Grundlage sind sieben Achsen mit
Zählregeln: **W**ärme · **O**ptimismus · **L**astverteilung · **K**ompaktheit ·
**E**xplizitheit · **S**truktur · **F**ührung.

Methode und Achsendefinitionen: `PROJEKT/calibration/METHOD.md`
Kalibrierte Werte, Klarnamen, Belege: `PROJEKT/data/tone-of-voice-email.md`
wobei `PROJEKT` = `/Users/guntrambechtold/Documents/Projects/260928-ToneOfVoice`

Die verbindliche Kurzfassung steht in AGENTS.md §5 und gilt für **jeden** Draft, auch ohne
diesen Skill.

## Drei Modi

Erkenne am Auftrag, welcher gemeint ist. Im Zweifel frag in einem Satz.

| Auftrag | Modus |
|---|---|
| „so hätte ich das geschrieben", korrigierte Fassung wird gezeigt | **1 · Paar einpflegen** |
| „prüf den Draft", „passt der Ton" | **2 · Draft prüfen** |
| Touchdown, „gleich die Mails ab", „was habe ich geändert" | **3 · Gmail-Abgleich** |

---

## Modus 1 · Paar einpflegen

Der Hauptmodus. Ein Paar ist: der generierte Text und Guntrams korrigierte Fassung.

**Schritt 1 - ablegen.** Beide Fassungen als Dateien in
`PROJEKT/data/pairs/JJJJ-MM-TT-empfaenger/` als `before.txt` und `after.txt`. Datum ist der
Tag des Versands. Kurzer Slug, keine Umlaute im Ordnernamen.

**Schritt 2 - messen.** Nie von Hand zählen:

```
python3 PROJEKT/calibration/tools/compare.py \
  PROJEKT/data/pairs/<ordner>/before.txt \
  PROJEKT/data/pairs/<ordner>/after.txt \
  --label "<Empfaenger>, <Thema> (<Datum>)"
```

Das Werkzeug liefert die Achsen-Deltas, die umformulierten Sätze, die ersatzlos
gestrichenen und die **neu eingesetzte Substanz**. Letztere ist das wertvollste Signal:
Wo Guntram etwas hinzufügt, fehlte im Draft eine Entscheidung.

**Schritt 3 - interpretieren.** Für jede bewegte Achse eine Zeile: Was hat sich bewegt,
und **warum**. Die Regel ohne Grund ist wertlos.

Dabei diese Fehlerquellen ausschließen:
- Bewegte sich die Achse, weil der Sachverhalt anders war, oder weil der Ton anders war?
  Nur Letzteres ist Kalibrierung.
- Ist es ein Muster oder ein Einzelfall? Ein Paar ist eine Beobachtung, drei sind eine
  Regel. Das sagen, statt es zu verschweigen.
- Wurde etwas **behalten**, das du gestrichen hättest? Das ist genauso lehrreich. Beispiel
  aus der Erstkalibrierung: Bedauern bei schlechten Nachrichten bleibt stehen, nur die
  Selbstrechtfertigung fällt.

**Schritt 4. Beleg schreiben.** `PROJEKT/data/pairs/<ordner>/README.md` nach diesem Muster:

```markdown
# <Empfänger>: <Thema>, <Datum>

Profil: <Profilname>  ·  Regler vorher → nachher: W4 O4 L1 K1 E2 S1 F5 → W5 O5 L5 K5 E1 S5 F5

## Was sich bewegt hat
- **L +4**: <Zitat aus before> wurde <Zitat aus after>. Grund: …

## Was bestätigt wurde
- …

## Was widerlegt wurde
- …
```

Und eine Zeile in `PROJEKT/data/measurements.csv` (Header steht dort).

**Schritt 5. Regler nachziehen: Vorschlag, nie eigenmächtig.**
Das ist ein WRITE-GATE nach AGENTS.md §3. Zeige:

1. **Diff**: welche Zeile in `tone-of-voice-email.md` sich ändert, im Format 🔴 VORHER /
   🟢 NACHHER.
2. **Beleg**: wie viele Paare stützen das, mit Datum.
3. **Blast-Radius**: was schreibt Claude ab dieser Änderung anders. Auch: welche Mails
   wären mit der neuen Regel schlechter geworden.
4. **Frage**: „Freigabe?"

Erst nach Freigabe editieren. Wenn ein Muster nur einmal auftrat: in die Beleg-Datei, nicht
in die Regeldatei. Sag das offen - „eine Beobachtung, noch keine Regel".

**Schritt 6 - synchron halten.** Ändert sich das Default-Profil oder eine Zählregel, muss
die Kurzfassung in `/Users/guntrambechtold/.claude/AGENTS.md` §5 mitwandern. Sonst gilt im
Alltag der alte Wert, weil AGENTS.md immer geladen ist und diese Datei nicht.

Danach committen (siehe „Repos" unten).

---

## Modus 2 · Draft prüfen

Vor dem Anlegen eines Gmail-Drafts oder auf Zuruf.

1. Text in eine Datei, dann `python3 PROJEKT/calibration/tools/measure.py <datei>`.
2. Ist-Werte gegen das Profil des Empfängers stellen (Profiltabelle in
   `tone-of-voice-email.md` §7).
3. Jede Achse, die unter dem Profilwert liegt, mit einem konkreten Satzvorschlag heilen -
   nicht mit dem Hinweis, dass sie darunter liegt.
4. Die Checkliste in `tone-of-voice-email.md` §12 durchgehen.

Zwei Dinge, die das Werkzeug **nicht** sieht und die du selbst prüfen musst:

- **Kennt Guntram hier jemanden?** Jede Rollenbezeichnung ohne Namen („eine Ansprechperson
  der Ortsgruppe", „euer Dienstleister", „wer bei euch zuständig ist") gegen
  `/Users/guntrambechtold/Documents/Projects/People/PEOPLE.md` prüfen und gegen den
  Projektkontext. Ist die Person bekannt, wird sie benannt und selbst gefragt - die Bitte
  verschwindet. Dieses Muster trat in der Erstkalibrierung dreimal in einer Woche auf.
- **Ist die Länge vom Sachverhalt gedeckt?** Ein langer Detailteil ist erlaubt, solange die
  Antwort im ersten Absatz steht.

---

## Modus 3 · Gmail-Abgleich

Findet Korrekturen, die Guntram gemacht hat, ohne sie zu melden. Das ist die eigentliche
Datenquelle im Alltag.

**Voraussetzung:** Gmail löscht den Draft beim Senden. Deshalb legt der PostToolUse-Hook
`tools/draft_snapshot.py` bei jedem `create_draft` eine Kopie unter
`PROJEKT/data/_snapshots/` ab. Ohne diese Kopie ist kein Abgleich möglich.

Der Hook ist bewusst fehlertolerant: Er lässt einen Tool-Call **niemals** scheitern und
schweigt bei Problemen. Der Preis ist, dass ein Defekt unbemerkt bleibt. Wenn
`_snapshots/` nach mehreren Drafts leer ist, prüf ihn von Hand:

```
echo '{"tool_input":{"subject":"T","htmlBody":"Hallo,<br><br>Gr&uuml;&szlig;e"}}' \
  | python3 PROJEKT/calibration/tools/draft_snapshot.py --verbose
```

`--verbose` macht genau die Fehler sichtbar, die im Hook-Betrieb verschwinden.

Ablauf:

1. Snapshots auflisten, die noch kein `matched`-Flag haben.
2. Je Snapshot die gesendete Fassung suchen:
   `search_threads` mit `in:sent` und dem Betreff, dann `get_message` mit
   `messageFormat: PLAIN_TEXT`.
3. Zitat-Historie abschneiden (`compare.py` macht das selbst).
4. `compare.py` laufen lassen. **Kein Delta auf allen sieben Achsen → überspringen,**
   Snapshot als `matched` markieren, nichts berichten. Nur Abweichungen sind Signal.
5. Bei Delta: Modus 1 ab Schritt 3.

Nichts gefunden heißt: nichts berichten. Ein Abgleich, der jedes Mal etwas meldet, wird
ignoriert.

Gefundene und verarbeitete Snapshots nach 90 Tagen löschen - sie enthalten Kundendaten.

---

## Repos

Zwei Repos, bewusst getrennt:

- **`calibration/`**: öffentlich (`gbechtold/tone-of-voice-calibration`). Methode, Achsen,
  Werkzeuge, dieser Skill. **Keine Klarnamen, keine Telefonnummern, keine Kundenzahlen.**
- **`data/`**: privat, als Submodul (`gbechtold/tone-of-voice-calibration-data`). Die
  kalibrierte Regeldatei, die Paare, die Messreihe.

Vor jedem Commit ins öffentliche Repo prüfen:

```
python3 PROJEKT/calibration/tools/check_public.py
```

Findet das Skript einen Klarnamen, eine Telefonnummer oder eine Kundenzahl im öffentlichen
Teil, wird nicht committet, sondern anonymisiert.

Commits: erst `data/` (privat), dann `calibration/` mit dem neuen Submodul-Zeiger.
Nie pushen, ohne dass Guntram es gesagt hat. Repos sind ein produktives System nach
AGENTS.md §3.

## Woran du merkst, dass es trägt

Nach drei bis vier Paaren bewegt sich fast nichts mehr. Bleiben die Deltas groß, stimmt
etwas an der Methode nicht - nicht an Guntrams Stil. Dann lieber eine fehlende Achse
suchen, als die bestehenden Werte hin und her zu schieben. Genau so kamen S und F
dazu: Sie fehlten in der ersten Fassung und waren dann der größte Effekt.
