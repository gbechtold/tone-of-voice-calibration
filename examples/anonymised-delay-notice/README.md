# Beispielpaar: Verzögerungsmeldung

Anonymisiert. Zeigt den lehrreichsten Einzelfall der Methode.

Regler: `W5 O3 L5 K2 E2 S1 F1` → `W5 O4 L5 K3 E1 S1 F5`

Nachvollziehen:

```bash
python3 ../../tools/compare.py before.txt after.txt --label "Verzögerung"
```

## Der Befund

**F springt von 1 auf 5.** 44 Wörter mit einer Entscheidungsfrage an den Kunden wurden
18 Wörter Handlungsansage. Die Fragezahl fällt auf null. Eine schlechte Nachricht wird
nicht durch eine Rückfrage weitergegeben, sondern mit dem nächsten Schritt geliefert.

**Die Entschuldigungen bleiben.** „Leider muss ich dir mitteilen" und „Es tut mir leid"
stehen unverändert. Wer hier kürzt, kürzt das Falsche. Gefallen ist stattdessen die
Selbstrechtfertigung — 33 Wörter darüber, wann der Absender es gemerkt hat und was zu
diesem Zeitpunkt nicht absehbar war.

**Substanz kommt dazu, während Gerüst fällt.** Der Hoster wird benannt, das Ticket bekommt
Datum und Uhrzeit, und aus „Termin" wird „Termin für die Rückmeldung … und dann machen wir
den Import". Der Termin wird dadurch ehrlicher, nicht optimistischer.
