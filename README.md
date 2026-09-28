# Tone of Voice Calibration

Ein Sprachmodell an den eigenen Schreibstil kalibrieren — nicht mit Adjektiven, sondern
mit Zählregeln.

## Das Problem

„Schreib kürzer und persönlicher" ist keine Anweisung, sondern eine Hoffnung. Niemand kann
prüfen, ob sie erfüllt wurde. Deshalb driften generierte Texte zurück in den Modell-Default,
egal wie ausführlich der Stil beschrieben wurde.

Gemessen an 26 selbst getippten gegen 35 generierte Sätze derselben Person:

| | selbst geschrieben | generiert |
|---|---|---|
| Median Satzlänge | **8 Wörter** | 15 |
| Sätze ab 20 Wörtern | 4 % | 23 % |
| Sätze ohne Komma | **65 %** | 14 % |

Fast doppelte Satzlänge, dreifache Kommadichte. Das ist der Unterschied, den Leser spüren —
nicht das Vokabular.

## Die Lösung

Sieben Achsen mit Zählregeln, kalibriert an Vorher/Nachher-Paaren:

| | Achse | Zählregel |
|---|---|---|
| **W** | Wärme | Anrede, Gruß, Signaturform |
| **O** | Optimismus | Bedingungssätze, die ein Scheitern vorwegnehmen |
| **L** | Lastverteilung | Bitten, die Arbeit beim Empfänger abladen |
| **K** | Kompaktheit | Median der Satzlänge |
| **E** | Explizitheit | ausbuchstabierte Bedingungen |
| **S** | Struktur | Aufzählungen als Liste statt als Prosa |
| **F** | Führung | zurückgegebene Entscheidungen |

Vollständige Definitionen: [METHOD.md](METHOD.md)

Der Loop ist einfach: Der Mensch korrigiert einen generierten Text, das Werkzeug misst die
Korrektur, die bewegte Achse wird nachgezogen. Nach drei bis vier Paaren stehen die Werte.

## Werkzeuge

```bash
# Eine Mail messen
python3 tools/measure.py mail.txt

# Draft gegen gesendete Fassung vergleichen
python3 tools/compare.py before.txt after.txt --label "Empfänger — Thema"

# Messreihe aus allen Paaren neu erzeugen
python3 tools/rebuild_measurements.py

# Öffentliches Repo gegen private Daten prüfen (braucht das private Submodul)
python3 tools/check_public.py

# Hook: Draft-Kopie anlegen, damit die gesendete Fassung später vergleichbar ist
echo '{"tool_input":{"subject":"T","htmlBody":"Hallo,<br><br>Gr&uuml;&szlig;e"}}' \
  | python3 tools/draft_snapshot.py --verbose
```

Nur Python 3 aus der Standardbibliothek, keine Abhängigkeiten.

**Was die Werkzeuge leisten:** K, E, O und S werden direkt gezählt und sind zuverlässig.
W, L und F beruhen auf Musterlisten und liefern einen Vorschlag, den ein Mensch bestätigen
muss. Eine Bring-Bitte in einer unbekannten Formulierung wird nicht erkannt. Die
Musterlisten wachsen mit jedem Paar.

## Aufbau

```
METHOD.md            Achsendefinitionen, Zählregeln, Beispiele
skill/SKILL.md       Claude-Code-Skill für den Alltags-Loop
tools/               Mess- und Vergleichswerkzeuge
examples/            anonymisiertes Beispielpaar
../data/             privates Submodul: eigene Regeln, Paare, Messreihe
```

Die Trennung ist Absicht. Methode und Werkzeuge sind allgemein, die kalibrierten Werte
enthalten Kundennamen und Geschäftszahlen und gehören in ein privates Repo.
`tools/check_public.py` hält beides auseinander; die Blockliste liegt im privaten Teil,
weil eine Liste zu schützender Namen im öffentlichen Repo sich selbst widerlegen würde.

## Was die Methode gelehrt hat

Drei Befunde, die ohne Messung nicht sichtbar geworden wären:

**Kompakter heißt nicht kürzer.** Eine korrigierte Mail verlor vier Wörter — und gewann
eine Telefonnummer, während sieben Wörter Konditionalgerüst fielen. Der Median fiel von 14
auf 9. Gleiche Länge, mehr Substanz. Vage Angaben werden präzisiert, nicht gestrichen:
„drei bis vier" ist keine Angabe, sondern eine vermiedene Entscheidung.

**Sprachmodelle laden Arbeit beim Empfänger ab.** Ein Modell kennt das Beziehungsnetz des
Absenders nicht. Es sieht eine Informationslücke und löst sie als Bitte — die einzige
Auflösung, die ihm zur Verfügung steht. „Nennen Sie mir eine Ansprechperson" statt „die
frage ich selbst". Dieses Muster trat in einer Woche dreimal auf und ist die teuerste
Achse: Eine überflüssige Bitte kostet einen Mailwechsel.

**Höflichkeit ist nicht Pessimismus.** Bei einer Verzögerungsmail blieben „leider muss ich
dir mitteilen" und „Es tut mir leid" unverändert stehen. Was fiel, war die
Selbstrechtfertigung: 33 Wörter darüber, warum es dazu kam. Das war eine Korrektur an der
Methode, nicht am Text — und der Grund, warum die O-Achse heute Bedauern und
vorweggenommenes Scheitern trennt.

Zwei der sieben Achsen (S und F) fehlten in der ersten Fassung vollständig und waren dann
der größte gemessene Effekt. Wenn die Deltas nach mehreren Paaren groß bleiben, fehlt eine
Achse — dann lohnt die Suche danach mehr, als bestehende Werte hin und her zu schieben.

## Lizenz

MIT
