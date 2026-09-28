# Die sieben Ton-Achsen

Eine Methode, um den Schreibstil einer Person messbar zu machen und ein
Sprachmodell darauf zu kalibrieren. Sprache der Beispiele: Deutsch,
Geschäftskorrespondenz. Die Achsen selbst sind sprachunabhängig.

## Warum Achsen und nicht Adjektive

„Schreib kürzer und persönlicher" ist keine Anweisung, sondern eine Hoffnung. Jede
Beschreibung eines Schreibstils, die aus Adjektiven besteht, lässt sich nicht prüfen -
weder von einem Menschen noch von einem Modell. Eine Achse mit Zählregel lässt sich prüfen.

Der Aufbau ist immer derselbe:

1. Eine Person korrigiert einen generierten Text.
2. Die Korrektur wird gegen das Original gemessen.
3. Die Achse, die sich bewegt hat, wird nachgezogen.

Nach drei bis vier Paaren stehen die Werte. Danach bewegt sich fast nichts mehr - und
genau das ist das Signal, dass die Kalibrierung trägt.

## Die Achsen

Höhere Zahl heißt mehr von der Eigenschaft. Einzige Ausnahme ist E, wo niedrig knapp
bedeutet.

### W: Wärme

Wie viel Distanz die Anrede, der Gruß und die Signatur herstellen.

| | Anrede | Gruß | Signatur |
|---|---|---|---|
| 1 | Unpersönlich („Sehr geehrte Damen und Herren") | Formell | Vollname + Firma |
| 2 | Formell mit Namen | Formell | Vollname |
| 3 | Neutral („Guten Tag Herr X") | Neutral | Vorname |
| 4 | Warm in der Sie-Form („Lieber Herr X") | Formell oder warm | Vorname |
| 5 | Warm in der Du-Form | Warm | Vorname |

**Der Signaturblock löst den Zielkonflikt.** Wer warm grüßen und trotzdem seriös wirken
will, setzt „Liebe Grüße / Vorname" und darunter einen eigenen Block mit Vollname,
Funktion, Firma. Die Wärme steht im Gruß, das Formale in der Signatur. Erstkontakt
erzwingt keine niedrige Stufe.

### O: Optimismus

Zählregel: Bedingungssätze, die ein Scheitern vorwegnehmen, je 100 Wörter. Marker sind
„Falls … nicht", „Sollte es nicht klappen", „wäre aber weniger gut".

- **5**: keine. Jede Bedingung steht auf der Gelingens-Seite.
- **4**: höchstens eine.
- **3**: zwei.
- **1–2**: Risiko-Modus, siehe Grenze unten.

**Was O nicht regelt.** Ein eingetretenes Problem wird benannt und bedauert. „Leider muss
ich Ihnen mitteilen" und „Es tut mir leid" sind kein Pessimismus, sondern Anstand. Was
stattdessen fällt, ist die **Selbstrechtfertigung**:

🔴 „Ich habe das erst gemerkt, als der Vorgang bereits lief, und zu diesem Zeitpunkt war
nicht absehbar, wie lange die Klärung dauern würde."
🟢 ersatzlos gestrichen, dafür eingesetzt: „Wir klären mit dem Support, wie wir das lösen
und wie lange es dauert."

Die Erklärung, wie es dazu kam, interessiert niemanden. Der nächste Schritt schon.

### L: Lastverteilung

Zählregel: Bring-Bitten an den Empfänger. Jede Information, die der Absender selbst
beschaffen kann, gehört nicht in eine Bitte.

- **5**: null Bring-Bitten, alles selbst geliefert.
- **4**: höchstens eine, und nur was der Empfänger exklusiv hat.
- **3**: zwei.
- **1**: beliebig viele.

**Das häufigste Muster generierter Texte.** Ein Modell kennt das Beziehungsnetz des
Absenders nicht. Es sieht eine Informationslücke und löst sie auf die einzige Art, die ihm
zur Verfügung steht: als Bitte an den Empfänger. Personen werden dabei zu Rollen, Orte zu
Platzhaltern.

🔴 „Könnten Sie mir eine Ansprechperson der Ortsgruppe nennen, mit Foto und Telefonnummer?"
🟢 „Die Ansprechperson frage ich selbst."

🔴 „Sagen Sie mir dafür einfach Ihre Nummer."
🟢 „(Mobil: …) - sagen Sie mir einfach Bescheid."

Die zweite Zeile ist kürzer, persönlicher, und der Empfänger hat eine Aufgabe weniger.
**Diese Achse ist die teuerste:** Eine überflüssige Bring-Bitte kostet einen Mailwechsel,
also Tage.

Gegenmittel: Vor dem Formulieren jeder Bitte die Namen und Orte im Text gegen das eigene
Kontaktverzeichnis prüfen. Jede Rollenbezeichnung ohne Namen ist verdächtig.

### K: Kompaktheit

Zählregel: **Median** der Satzlänge, nicht die Gesamtwortzahl.

- **5**: Median ≤ 6 Wörter.
- **4**: ≤ 9.
- **3**: ≤ 12.
- **2**: ≤ 15.
- **1**: ungeregelt. Sprachmodelle liegen unkalibriert bei 15 bis 19.

Der Median ist das richtige Maß, weil er robust gegen einen einzelnen langen Satz ist und
weil er das misst, was den Leser ermüdet: die typische Satzlänge.

**Kompakter heißt nicht kürzer.** In einer gemessenen Korrektur fiel die Mail von 94 auf
90 Wörter - vier Wörter. Der Median fiel von 14 auf 9, weil sieben Wörter Konditionalgerüst
verschwanden und acht Wörter echte Information dazukamen. Gleiche Länge, mehr Substanz.

**Vage Angaben werden präzisiert, nicht gestrichen:**

| generiert | korrigiert |
|---|---|
| „drei bis vier Bilder" | „**vier** Bilder (**High-Res, Menschen**)" |
| „der Hoster hat abgebrochen" | „der Hosting-Anbieter (**Firma**) hat abgebrochen" |
| „ich habe ein Ticket eröffnet" | „ich habe **am 28.09. 10:00** ein Ticket eröffnet" |
| „der Termin ist voraussichtlich der 02.10." | „der Termin **für die Rückmeldung** ist der 03.10., **dann machen wir den Import**" |

„Drei bis vier" ist keine Angabe, sondern eine vermiedene Entscheidung.

### E: Explizitheit

Zählregel: ausbuchstabierte Bedingungen und Erklärungen dessen, was ohnehin klar ist, je
100 Wörter. Bei den meisten Menschen ist **niedrig** der Normalfall.

- **1**: keine oder eine.
- **2**: zwei.
- **3**: drei.
- **5**: alles ausbuchstabiert.

Der häufigste Fall überflüssiger Explizitheit ist die vorweggenommene Rückfrage: ein Satz,
der einen Zweifel ausräumt, den niemand geäußert hat. Er macht den Text länger und den
Absender unsicher. Die Nachfrage kommt in einem von fünf Fällen - dann antwortet man in
drei Zeilen.

🔴 „Nachstellen können Sie es in zwei Minuten: Seite aufrufen, zustimmen, neu laden, dann
in der Konsole abfragen. Ich habe es in einem frischen Browser ohne Profil und in meinem
eigenen geprüft, auf beiden Sprachfassungen. Jedes Mal dasselbe Bild."
🟢 ersatzlos streichen. Wer zweifelt, fragt.

**Die harte Grenze.** Bei Dry-Run, Blast-Radius, Sicherheitsbefunden, Recht und
Angebotsumfang gilt **E5 und O3**, ohne Verhandlung. Dort wird nüchtern berichtet, nicht
ermutigt. Ein geschöntes Risiko ist ein verschwiegenes Risiko. Die Regler gelten für den
Umgangston, nie für die Substanz.

### S: Struktur

Zählregel: Jede Sachaufzählung ab zwei Gliedern wird zur Liste, eingeleitet mit einem
Doppelpunkt. Prosa bleibt für Bewertung, Begründung und Entscheidung.

- **5**: jede Aufzählung als Liste, Abschnittsmarken als Doppelpunkt-Zeile.
- **4**: wie 5, Prosa für alles Wertende.
- **3**: Mischung, Listen ab drei Gliedern.
- **1**: durchlaufende Prosa. Der Default eines Sprachmodells.

Diese Achse fiel in der ersten Fassung dieser Methode durch und war dann die auffälligste
Änderung überhaupt: Bullets 0 → 4 und 0 → 6 in zwei von drei gemessenen Korrekturen.

🔴 Ein Satz mit 33 Wörtern:
> Bei den Budgets bin ich von 1.200 Euro im Monat ausgegangen, was dem entspricht, was wir
> im Vorjahr eingesetzt haben, wobei ich den Betrag jederzeit anpassen kann, falls Sie das
> anders einplanen möchten.

🟢 Ein Listenglied mit 10 Wörtern:
> - Das Budget ist bei 1.200 Euro im Monat (wie Vorjahr)

**Überschriften werden Doppelpunkt-Zeilen**, keine Blockheadings:

| generiert | korrigiert |
|---|---|
| „Der aktuelle Stand" (eigene Zeile) | „Der aktuelle Stand**:**" + Liste |
| „Was passiert ist" | „**Zum Hintergrund:**" |
| „Erstens: … Zweitens: …" | „1. … 2. …" |

Eine Doppelpunkt-Zeile ist keine Überschrift, sie ist ein Satzanfang. In einer E-Mail ist
das der Unterschied zwischen einem Dokument und einer Nachricht.

### F: Führung

Zählregel: Entscheidungen, die an den Empfänger gehen, obwohl der Absender sie selbst
treffen kann. Der nächste Schritt wird **vorgeschlagen, nicht erfragt**.

- **5**: null. Der Absender nennt den nächsten Schritt und handelt.
- **4**: höchstens eine, und nur wo der Empfänger wirklich entscheiden muss.
- **3**: zwei.
- **1**: Optionen werden aufgefächert und zur Wahl gestellt. Modell-Default.

🔴 44 Wörter, eine Frage an den Kunden:
> Falls Sie möchten, kann ich sie bitten, die Veröffentlichung zu verschieben, oder wir
> lassen sie veröffentlichen und nehmen in Kauf, dass die Seite in den ersten Tagen noch
> nicht erreichbar ist. Was wäre Ihnen lieber?

🟢 18 Wörter, keine Frage:
> Ich stimme das Timing mit ihr ab, da sie diese Woche veröffentlichen wollte.

🔴 Wahl zwischen zwei Wegen:
> Sollten Sie das lieber im Gespräch besprechen wollen, stehe ich gerne zur Verfügung.
> Bitte teilen Sie mir mit, wann es Ihnen passen würde. Ich freue mich auf Ihre Rückmeldung.

🟢 Ein Weg in zwei Schritten:
> Ich schlage vor, Sie senden mir die Antworten kurz zu, und wir machen dann ein kurzes
> Gespräch (vor Ort oder telefonisch).

Eine schlechte Nachricht wird nicht durch eine Rückfrage an den Empfänger weitergegeben.
Sie wird mit dem nächsten Schritt geliefert.

**Abgrenzung zu L:** L betrifft Informationen, die der Absender selbst holen kann. F
betrifft Entscheidungen, die er selbst treffen kann. Beide laufen darauf hinaus, dass der
Empfänger so wenig Arbeit wie möglich hat.

## Anti-Slop: was keine Achse ist

Modell-typische Wendungen bekommen bewusst **keinen** Regler. Slop hat keine sinnvolle
Zwischenstufe, jedes Profil müsste auf 5 stehen. Also: harte Streichliste plus Messwert.

### Kandidaten gehören erst gegen die echten Texte geprüft

Der wichtigste Schritt, und der, den fertige Slop-Listen überspringen. Gemessen wird, wie
oft ein Marker in Modelltexten gegenüber den Texten des Autors vorkommt. Nur was
auseinanderfällt, kommt auf die Liste.

Ein Durchlauf über 841 Wörter Autortext gegen 3142 Wörter Modelltext ergab:

| Marker | Autor je 1000 W | Modell je 1000 W | Urteil |
|---|---|---|---|
| Em-Dash | **0,0** | 10 bis 24 | auf die Liste |
| Dreierfigur (A, B und C) | 2,4 | 1,3 bis 2,1 | **kein Slop**, eigener Stil |
| Nominalstil-Ballung | 1,2 | 1,3 bis 2,1 | **kein Slop** |
| Wertadjektive | 1,2 | 0,4 | **kein Slop** |
| „nicht nur, sondern auch" | 0 | 0 | vorbeugend |
| „In der heutigen Welt" | 0 | 0 | vorbeugend |

Eine Liste, die den eigenen Stil des Autors verbietet, ist Rauschen. Drei der geprüften
Marker fielen genau deshalb wieder heraus.

### Der eine belastbare Befund

Der Em-Dash ist der einzige Marker, der messbar auseinanderfällt, und der einzige mit
einem belegten Korrekturfall: In einer echten Mail ersetzte der Autor `— ` durch ` - `.

Der Strich ist nur das Symptom. Die Untugend dahinter ist der **Einschub statt des
Satzes**: Ein Gedanke wird nicht zu Ende gebracht, sondern angehängt. Wer den Strich durch
einen Punkt ersetzt, behebt beides und verbessert nebenbei K.

### Ehrlichkeit über die Reichweite

Die übrigen elf Marker in `measure.py` sind **Vorbeugung, kein Befund**. Sie traten in
keinem gemessenen Text auf. Ein Bigramm-Vergleich auf unbekannte Muster fand nichts, weil
bei dieser Textmenge keine Wendung dreimal vorkommt. Wer die Liste für erschöpfend hält,
täuscht sich über die Stichprobe.

## Profile

Ein Profil ist eine Kombination der sieben Werte für einen Empfängertyp. Beispielsatz -
die konkreten Zahlen gehören in die eigene Kalibrierdatei:

| Profil | W | O | L | K | E | S | F |
|---|---|---|---|---|---|---|---|
| Standard | 4 | 4 | 5 | 5 | 1 | 4 | 4 |
| Vertraute Kunden und Kollegen | 5 | 4 | 5 | 5 | 1 | 5 | 5 |
| Erstkontakt, Angebot, Pitch | 4 | 4 | 5 | 5 | 2 | 5 | 4 |
| Politik, Verband, unbekannt | 4 | 4 | 5 | 4 | 2 | 3 | 4 |
| Schlechte Nachricht, eigener Fehler | 5 | 2 | 5 | 4 | 3 | 3 | 5 |
| Behörde, Recht, Risikobericht | 2 | 3 | 4 | 3 | 5 | 4 | 3 |

Die Zeile „schlechte Nachricht" ist der lehrreiche Sonderfall: **O fällt auf 2**, weil
Bedauern und Problembenennung bleiben, während **F auf 5 steigt**: gerade dann keine
Rückfrage, sondern der nächste Schritt.

Notation im Gespräch: `W5 S5` nennt nur die Abweichung vom Standard.

## Was die Werkzeuge messen und was nicht

`tools/measure.py` zählt K, E, O und S direkt und zuverlässig. W, L und F beruhen auf
Musterlisten und liefern einen **Vorschlag**, den ein Mensch bestätigen muss. Eine
Bring-Bitte, die keine der bekannten Formulierungen benutzt, wird nicht erkannt. Die
Musterlisten wachsen mit jedem Paar - das ist Teil der Kalibrierung, kein Mangel.

Wer die Zahlen für mehr nimmt, als sie sind, kalibriert auf das Werkzeug statt auf den
Menschen.
