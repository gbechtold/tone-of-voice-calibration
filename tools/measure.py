#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Measure a German business email against the seven tone axes.

Usage:
    measure.py FILE [FILE ...]
    cat mail.txt | measure.py -
    measure.py --json FILE

The axes W (warmth), L (load) and F (lead) rely on pattern heuristics.
They propose a value; a human still has to confirm it. K, E, O and S are
counted directly and are reliable.
"""
import argparse
import json
import re
import sys
import unicodedata

# --- patterns -------------------------------------------------------------

SALUTATION = [
    (1, r"^\s*Sehr geehrte Damen und Herren"),
    (2, r"^\s*Sehr geehrte[rn]?\s+(Herr|Frau|Dr|Prof)"),
    (3, r"^\s*(Guten Tag|Grüß Gott|Werte[rn]?)\b"),
    (4, r"^\s*Liebe[rs]?\s+(Herr|Frau|Dr|Prof)"),
    (5, r"^\s*(Hallo|Hi|Servus|Liebe[rs]?)\s+[A-ZÄÖÜ][a-zäöüß]+\s*,"),
]
CLOSING = [
    (1, r"Mit freundlichen Grüßen"),
    (3, r"(Beste|Viele|Freundliche|Schöne) Grüße"),
    (5, r"(Liebe Grüße|LG\b|Servus)"),
]
# Bedingungssätze, die ein Scheitern vorwegnehmen (axis O)
NEGATIVE_PREMISE = [
    r"\bFalls\b[^.!?]{0,80}\bnicht\b",
    r"\bSollten? es\b[^.!?]{0,60}\b(nicht|länger|dauern)\b",
    r"\bFalls (keiner|keine|nichts|nie)\b",
    r"\bsofern\b[^.!?]{0,40}\bnicht\b",
    r"\bwobei ich das nicht\b",
    r"\bwäre aber weniger\b",
    r"\bist unglücklich\b",
]
# Belehrende Negation (axis O, zweiter Bestandteil): Saetze, die den Vorschlag
# oder die Annahme des Empfaengers als unzureichend markieren. Gemessen an einem
# echten Paar vom 28.09.2026: "Eine Checkliste allein beantwortet das nicht. Sie
# zeigt Maengel. Was die Maengel kosten, zeigt sie nicht." - vom Autor als "zu
# beschulend" zurueckgewiesen. Die sieben Achsen zeigten dabei KEINE Bewegung,
# die Negationszahl fiel von 3 auf 0. Deshalb dieser Marker.
BELEHREND = [
    (r"\b(beantwortet|zeigt|loest|liefert|erfasst|genuegt|reicht|hilft)\b[^.!?]{0,40}\bnicht\b", "Negation eines Vorschlags"),
    (r"\b(reicht|genügt)\s+(dafür\s+)?nicht\b", "reicht nicht"),
    (r"\b(allein|alleine)\b[^.!?]{0,30}\bnicht\b", "allein nicht"),
    (r"\bnicht\s+(aus|ausreichend|genug)\b", "nicht ausreichend"),
    (r"\bWas\b[^.!?]{0,40},\s*(zeigt|sagt|verrät)\s+\w+\s+nicht\b", "was X nicht zeigt"),
    (r"\bist kein\w*\s+\w+", "ist kein X"),
]

# echtes Bedauern — zählt NICHT gegen O (siehe METHOD.md, Achse O)
REGRET = [
    r"\bleider muss ich\b", r"\bEs tut mir leid\b", r"\bbedauere\b",
]
# Selbstrechtfertigung — zählt immer als Ballast
SELF_JUSTIFY = [
    r"\bIch habe das erst gemerkt\b", r"\bwar zu diesem Zeitpunkt nicht mehr absehbar\b",
    r"\bnachdem ich\b[^.!?]{0,60}\bgearbeitet habe\b",
    r"\bwobei ich\b[^.!?]{0,60}\bnicht garantieren\b",
    r"\bIch habe (gestern und heute|die letzten Tage)\b",
]
CONDITIONAL = r"\b([Ff]alls|[Ss]ollten?|sofern|wobei|[Ww]enn)\b"
# Bring-Bitten: Arbeit, die an den Empfänger geht (axis L)
BRING_REQUEST = [
    r"\bbräuchte ich (noch )?(von dir|von Ihnen)?\b",
    r"\bKönnt(est|en) (du|Sie) mir\b",
    r"\b(teilen|nennen|senden|schicken) Sie mir\b",
    r"\bsag(en Sie)? mir\b[^.!?]{0,40}\b(Nummer|Adresse|Termin|Namen)\b",
    r"\bbeantworten könnt(en|est)\b",
    r"\bwer bei (euch|Ihnen) für\b",
    r"\bwäre die Frage, ob\b",
    r"\bBitte (teilen|senden|nennen|schicken)\b",
]
# aufgefächerte Optionen statt Entscheidung (axis F)
OPTION_OFFER = [
    r"\bFalls du möchtest\b", r"\boder wir\b[^.!?]{0,60}\?",
    r"\bWas wäre (dir|Ihnen) lieber\b", r"\bwie (du|Sie) (es )?(möchte|wollen|willst)\b",
    r"\bstehe ich (Ihnen|dir) (dafür )?gerne zur Verfügung\b",
    r"\bwenn (du|Sie) (lieber|möchten|möchtest)\b",
]
# zurückgegebene Entscheidungen (axis F) — anders als eine reine Sachfrage
HANDBACK = [
    r"\bWas wäre (dir|Ihnen) lieber\b",
    r"\bwie (möchtest du|möchten Sie) (das )?(machen|vorgehen)\b",
    r"\b(Sag|Sagen Sie) mir,? (was|wie) (du|Sie)\b",
    r"\bentscheide (du|Sie)\b",
    r"\büberlasse ich (dir|Ihnen)\b",
    r"\bdas ist deine Entscheidung\b",
    r"\bwie (du|Sie) (es )?(lieber )?(hast|haben|willst|wollen)\b",
]
# Führungs-Marker: Guntram entscheidet (positiv für F)
LEAD_MARKER = [
    r"\bIch schlage vor\b", r"\bIch werde\b", r"\bIch mache\b", r"\bIch frage\b",
    r"\bich kläre\b", r"\bWir klären\b", r"\bich melde mich\b", r"\bdann mache ich\b",
]
FILLER = [
    r"Ich freue mich auf (Ihre|deine) Rückmeldung",
    r"stehe ich (Ihnen|dir) (dafür )?gerne zur Verfügung",
    r"vielen Dank für (Ihre|deine|das)",
    r"Melde dich einfach, wenn (du|Sie)",
    r"Ich hoffe,? es geht (dir|Ihnen) gut",
    r"Bei Fragen stehe ich",
    r"nicht zögern",
]
# Sprachmodell-Tells ("Slop"). Bewusst NICHT als achte Achse: Slop hat keine
# sinnvolle Zwischenstufe, jedes Profil müsste auf 5 stehen. Also harte Liste
# plus Messwert.
#
# EM_DASH steht separat, weil es der einzige Marker ist, der im Vergleich
# messbar auseinanderfällt: Claude-Dokumente 10–24 je 1000 Wörter, Guntrams
# gesendete Mails 0 auf 585 Wörter (gemessen 28.09.2026).
#
# Nicht auf die Liste gekommen, weil Guntram sie selbst benutzt: Dreierfiguren
# ("A, B und C"), Nominalstil-Ballungen, gelegentliche Wertadjektive. Eine
# Slop-Liste, die den eigenen Stil des Autors verbietet, ist Rauschen.
# NUR der Geviertstrich U+2014 (englische Typografie). Der Halbgeviertstrich
# U+2013 wird NICHT gezaehlt: als Bis-Strich ("15-45 Woerter") ist er korrektes
# Deutsch. Der Einwand von kein-ki-sprech gegen ein Em-Dash-Verbot zielt auf
# U+2013, nicht auf U+2014.
EM_DASH = "\u2014"
SLOP = [
    (r"nicht nur\b[^.!?]{0,60}\bsondern auch", "nicht nur/sondern auch"),
    (r"[Ee]s geht (dabei )?nicht (nur )?um\b[^.!?]{0,50}\bsondern", "es geht nicht um X, sondern"),
    (r"[Ii]n (der heutigen|Zeiten von|einer Welt, in der)", "in der heutigen Welt"),
    (r"\b(nahtlos|ganzheitlich|maßgeschneidert|zukunftsweisend|leistungsstark|passgenau|innovativ)\w*\b", "Werbe-Adjektiv"),
    (r"([Ll]assen Sie uns|[Tt]auchen wir|[Ww]erfen wir einen Blick)", "Lassen Sie uns / tauchen wir ein"),
    (r"([Kk]urz gesagt|[Zz]usammenfassend|[Ii]m Grunde|[Aa]bschließend lässt sich)", "Meta-Zusammenfassung"),
    (r"[Ee]s (ist|sei) (wichtig|anzumerken|erwähnenswert|hervorzuheben)", "es ist wichtig zu beachten"),
    (r"\b(wertvolle|spannende|tiefe) Einblicke\b", "wertvolle Einblicke"),
    (r"\b(Mehrwert|Synergi\w+|Ökosystem|Landschaft der)\b", "Buzzword"),
    (r"\b(das Beste daran|der größte Vorteil dabei)\b", "Doppelpunkt-Dramatik"),
    (r"\bReise\b(?![^.!?]{0,20}(nach|mit dem|Zug|Auto))", "Reise-Metapher"),
    # --- aus m-dohmen/kein-ki-sprech, fuer deutsche Texte ---
    # Gemessen 28.09.2026: Passiv ohne Akteur 4,9 je 1000 Woerter in Claude-Doku,
    # 0,0 bei Guntram. Der einzige neue Marker mit echtem Befund.
    (r"\b(wurde|wurden|wird|werden)\s+\w+(t|en)\b(?![^.!?]{0,40}\b(von|durch)\b)", "Passiv ohne Akteur"),
    # Die folgenden traten in keinem gemessenen Text auf. Vorbeugung.
    (r"\b(am Ende des Tages|[Ll]ow.Hanging|nicht wirklich|Deep Dive|Alignment|Learnings|Pain Points?|Roll.?out)\b", "Beraterdenglisch"),
    (r"\b(Darüber hinaus|Des Weiteren|Ferner|Nicht zuletzt)\b", "Konnektoren-Kette"),
    (r"\b(adressieren|abbilden|aufsetzen|ausrollen|abholen|verproben)\b", "Fassaden-Verb"),
    (r"\b(Im Folgenden|Werfen wir|Betrachten wir|Sehen wir uns)\b", "Reiseleiter-Satz"),
    (r"(^|\n)\s*(Grundsätzlich|Generell|Im Prinzip|Zunächst einmal|Vorab)\b", "Räuspern vorweg"),
    (r"\b(spielt eine (wichtige|zentrale) Rolle|ist entscheidend für den Erfolg|zeigt sich deutlich)\b", "Pseudo-Erkenntnis"),
]
# --- Auf ausdrueckliche Anordnung aktiviert (28.09.2026), obwohl die Messung sie
# --- nicht stuetzte. Die Muster sind so gefasst, dass sie den Slop treffen und
# --- nicht die Sachaussage. Jede Fassung ist unten begruendet.

# Emoji: raus aus Fliesstext und Ueberschriften. AUSNAHME sind die Marker 🔴/🟢,
# die AGENTS.md §6 fuer das Vorher/Nachher-Format vorschreibt, und alles, was
# ausdruecklich angefordert wurde.
EMOJI = "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]"
EMOJI_ERLAUBT = u"\U0001F534\U0001F7E2"   # rot/gruen fuer Vorher/Nachher

# Verstaerker und Weichmacher in SACHAUSSAGEN. Bewusst ohne "sehr gerne",
# "absolut lässig", "super": das sind Hoeflichkeits- und Zustimmungsformeln und
# damit die Stimme des Autors (10 Belege in seinen eigenen Mails).
FUELL_ADVERB = [
    (r"\b(deutlich|erheblich|signifikant|maßgeblich|wesentlich)\s+\w+(er|ere|eren)\b", "Verstärker vor Komparativ"),
    (r"\b(grundsätzlich|letztendlich|letzten Endes|zweifellos|bekanntlich|naturgemäß)\b", "Füll-Adverb"),
    (r"\b(durchaus|ziemlich|recht|relativ|einigermaßen|vergleichsweise)\s+\w+", "Weichmacher-Adverb"),
    (r"\b(selbstverständlich|natürlich|klarerweise)\s+(ist|sind|wird|werden|kann|können)\b", "Selbstverständlich-Floskel"),
]

# Rhetorische Dreierfigur: drei ADJEKTIVE oder Abstrakta zur Verstaerkung
# ("klar, schnell und verlaesslich"). Eine Sachaufzaehlung konkreter Dinge
# ("Muenchen, Stuttgart und Zuerich") ist KEINE Dreierfigur - die wird bei S4/S5
# ohnehin zur Bullet-Liste. Deshalb greift das Muster nur vor Satzende und nur
# bei klein geschriebenen Woertern, also nicht bei Eigennamen.
# \s+ statt Leerzeichen: in einer umbrochenen Mail steht der Zeilenwechsel
# mitten in der Figur ("schnell,\nsicher und zuverlaessig").
DREIERFIGUR = r"\b([a-zäöüß]{4,}),\s+([a-zäöüß]{4,})\s+und\s+([a-zäöüß]{4,})\s*[.!?]"

# Nominalstil: zwei Handlungssubstantive, die ein Verb ersetzen. Fachbegriff-
# Paare wie "Testumgebung auf die Live-Umgebung" sind ausgenommen, deshalb
# verlangt das Muster eine Praeposition der Verschachtelung dazwischen.
NOMINALSTIL = r"\b\w{4,}(ung|heit|keit|schaft)\s+(der|des|von|zur|zum|bei der)\s+\w{4,}(ung|heit|keit|schaft)\b"

# W-Satzanfang als RHETORISCHE FRAGE. Nur Fragezeichen-Varianten: eine
# Doppelpunkt-Marke wie "Was noch offen ist:" ist eine Abschnittsmarke der
# S-Achse, keine rhetorische Frage. Guntram hat genau diese Marke am 28.09.2026
# selbst gesetzt; ein Filter, der sie trifft, wuerde S gegen sich selbst wenden.
# Auch mitten im Absatz: eine rhetorische Frage steht selten am Zeilenanfang.
W_SATZANFANG = r"(^|\n|[.!?]\s+)#{0,4}\s*\**(Warum|Wieso|Weshalb)\b[^\n]{0,70}\?"

# Bewusst NICHT aufgenommen, weil an echten Texten geprueft und widerlegt:
#   Nominalstil-Ketten   Guntram 1,2 / Claude 1,3 je 1000 Woerter. Gleichauf.
#   Dreierfiguren        Guntram 2,4 / Claude 1,3 bis 2,1. Guntram nutzt sie MEHR.
#   Wertadjektive        Guntram 1,2 / Claude 0,4. Sein Ton.
#   Halbgeviertstrich    korrektes Deutsch als Bis-Strich.
#   Adverb- und W-Satz-Verbote, Emoji-Verbot: englischspezifisch bzw. Guntrams
#   AGENTS.md nutzt Emoji in Ueberschriften bewusst.
SUBSTANCE = [
    r"\d{1,2}\.\d{1,2}\.",            # Datum
    r"\d+[.,]?\d*\s?(€|Euro|Prozent|%)",
    r"\b\d{1,2}:\d{2}\b",             # Uhrzeit
    r"\+\d{2}[\d /-]{6,}",            # Telefon
    r"https?://\S+",
    r"\b[A-Za-zÄÖÜäöü.-]+\.(at|de|com|ch|li|cc)\b",
]

def _count(patterns, text):
    return sum(len(re.findall(p, text)) for p in patterns)

SALUTATION_LINE = r"^\s*(Sehr geehrte|Liebe[rs]?|Hallo|Hi|Servus|Guten Tag|Grüß Gott|Werte)\b.*,\s*$"
CLOSING_LINE = r"^\s*(Mit freundlichen Grüßen|(Beste|Viele|Freundliche|Schöne|Liebe) Grüße|LG|Servus)\b.*$"
DATA_LINE = r"(\d{1,2}\.\d{1,2}\.|\b\d{1,2}:\d{2}\b|^\s*(Mo|Di|Mi|Do|Fr|Sa|So|Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag)\b)"

def _split_frame(body):
    """Separate the salutation/closing/signature frame from the actual message body.

    The frame is measured for W; counting it as sentences would distort every
    length metric ("Liebe Grüße" is not a sentence).
    """
    lines = body.split("\n")
    frame, core, closed = [], [], False
    for ln in lines:
        if re.match(SALUTATION_LINE, ln):
            frame.append(ln)
            continue
        if re.match(CLOSING_LINE, ln):
            frame.append(ln)
            closed = True
            continue
        if closed:                      # signature block after the closing
            frame.append(ln)
            continue
        core.append(ln)
    return "\n".join(core), "\n".join(frame)

def _sentences(body, keep_data_lines=False):
    """Sentences of the message core.

    A standalone line without terminal punctuation that carries a date, a time or a
    weekday is a data line (an offered appointment, a figure), not a sentence. Counting
    it drags the median toward zero: three appointment lines took a real mail from a
    median of 9 down to 3.
    """
    core, _ = _split_frame(body)
    out = []
    for raw_line in core.split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        has_end = bool(re.search(r"[.!?]\s*$", line))
        n_words = len(re.findall(r"\S+", line))
        # Only a SHORT line can be a data line. A long paragraph that happens to
        # contain a date is still prose — without the word cap, a one-line mail
        # mentioning "13.10." was dropped whole and measured as zero sentences.
        if not keep_data_lines and not has_end and n_words <= 8:
            if re.search(DATA_LINE, line) or n_words <= 4:
                continue
        for part in re.split(r'(?<=[.!?])\s+', line):
            part = part.strip()
            if len(part) > 3:
                out.append(part)
    return out

def _strip_quote(text):
    """Drop quoted history: lines starting with > and everything after 'On ... wrote:'."""
    text = re.split(r"\n\s*(On .{5,60}wrote:|Am .{5,60}schrieb)", text)[0]
    return "\n".join(l for l in text.split("\n") if not l.lstrip().startswith(">"))

def _level(value, thresholds):
    """thresholds: list of (max_value, level) ascending by max_value."""
    for limit, lvl in thresholds:
        if value <= limit:
            return lvl
    return thresholds[-1][1]

def measure(raw, name="-"):
    body = _strip_quote(raw).strip()
    core, frame = _split_frame(body)
    sents = _sentences(body)
    if not sents:
        return None
    lengths = sorted(len(re.findall(r"\S+", s)) for s in sents)
    words = len(re.findall(r"\S+", body))
    per100 = (lambda n: round(100.0 * n / words, 1)) if words else (lambda n: 0.0)

    bullets = len(re.findall(r"^\s*([-–•*]|\d+[.)])\s+", body, re.M))
    colon_intro = len(re.findall(r":\s*$", body, re.M))
    prose_enum = len(re.findall(r",\s+(und|sowie)\s+(natürlich\s+)?(das|die|der)\b", body))
    # Kommas nur aus den gezaehlten Saetzen, nicht aus dem ganzen body: Anrede
    # ("Lieber Herr X,") und Terminzeilen ("Mittwoch, 30. September, 10:00 Uhr")
    # tragen je ein bis zwei Kommas, zaehlen aber nicht als Satz. In einer Mail mit
    # drei Terminvorschlaegen stammten 7 von 9 Kommas daraus, die Kennzahl war
    # dadurch fast dreifach zu hoch.
    commas = sum(x.count(",") for x in sents)
    no_comma = sum(1 for s in sents if "," not in s)

    neg = _count(NEGATIVE_PREMISE, body)
    lecture = [(l, len(re.findall(pt, core))) for pt, l in BELEHREND]
    lecture = [(l, n) for l, n in lecture if n]
    lecture_n = sum(n for _, n in lecture)
    regret = _count(REGRET, body)
    justify = _count(SELF_JUSTIFY, body)
    cond = len(re.findall(CONDITIONAL, body))
    bring = _count(BRING_REQUEST, body)
    options = _count(OPTION_OFFER, body)
    handback = _count(HANDBACK, body)
    lead = _count(LEAD_MARKER, body)
    filler = _count(FILLER, body)
    em_dash = len(re.findall(EM_DASH, body))
    emoji = [c for c in re.findall(EMOJI, body) if c not in EMOJI_ERLAUBT]
    adverbs = [(l, len(re.findall(pt, body))) for pt, l in FUELL_ADVERB]
    adverbs = [(l, n) for l, n in adverbs if n]
    dreier = len(re.findall(DREIERFIGUR, body))
    nominal = len(re.findall(NOMINALSTIL, body))
    w_anfang = len(re.findall(W_SATZANFANG, body))
    slop_hits = [(label, len(re.findall(pat, body))) for pat, label in SLOP]
    slop_hits = [(l, n) for l, n in slop_hits if n]
    slop = sum(n for _, n in slop_hits)
    substance = _count(SUBSTANCE, body)
    questions = body.count("?")

    sal = next((lvl for lvl, p in SALUTATION if re.search(p, body, re.M)), None)
    clo = next((lvl for lvl, p in CLOSING if re.search(p, body)), None)
    full_name_sig = bool(re.search(r"(Liebe Grüße|Grüßen)\s*\n+\s*\w+\s+\w+", body))

    med = lengths[len(lengths) // 2]
    axes = {
        "W": sal if sal else (clo if clo else 3),
        # O zaehlt beides: vorweggenommenes Scheitern UND belehrende Negation.
        "O": _level(per100(neg + lecture_n), [(0.0, 5), (1.2, 4), (2.5, 3), (99, 1)]),
        "L": _level(bring, [(0, 5), (1, 4), (2, 3), (99, 1)]),
        "K": _level(med, [(6, 5), (9, 4), (12, 3), (15, 2), (99, 1)]),
        "E": _level(per100(cond), [(1.2, 1), (2.2, 2), (3.2, 3), (99, 5)]),
        "S": _level(-bullets, [(-3, 5), (-2, 4), (-1, 3), (0, 1)]),
        # F zählt nur zurückgegebene ENTSCHEIDUNGEN, nicht Sachfragen. Vier nummerierte
        # Fragen im Erstkontakt-Briefing sind Informationsbedarf, kein Führungsdefizit.
        "F": _level(max(0, options + handback - lead), [(0, 5), (1, 4), (2, 3), (99, 1)]),
    }
    return {
        "name": name, "words": words, "sentences": len(sents),
        "median_sentence": med, "longest_sentence": lengths[-1],
        "commas_per_sentence": round(float(commas) / len(sents), 2),
        "pct_without_comma": int(round(100.0 * no_comma / len(sents))),
        "bullets": bullets, "colon_intros": colon_intro, "prose_enumerations": prose_enum,
        "negative_premises": neg, "regret": regret, "self_justification": justify,
        "lecturing": lecture_n, "lecturing_detail": lecture,
        "conditionals": cond, "bring_requests": bring, "option_offers": options,
        "lead_markers": lead, "fillers": filler, "substance_markers": substance,
        "questions": questions, "handbacks": handback,
        "em_dashes": em_dash, "em_dash_per_1000": round(1000.0 * em_dash / words, 1) if words else 0.0,
        "slop_markers": slop, "slop_detail": slop_hits,
        "emoji": len(emoji), "emoji_chars": "".join(sorted(set(emoji))),
        "fill_adverbs": sum(n for _, n in adverbs), "adverb_detail": adverbs,
        "rhetorical_triads": dreier, "nominal_style": nominal, "w_openings": w_anfang,
        "data_lines": len([l for l in core.split("\n")
                           if l.strip() and not re.search(r"[.!?]\s*$", l.strip())
                           and (re.search(DATA_LINE, l) or len(re.findall(r"\S+", l)) <= 4)]),
        "salutation_level": sal, "closing_level": clo, "full_name_in_signature": full_name_sig,
        "axes": axes,
    }

def render(m):
    a = m["axes"]
    print("%s" % m["name"])
    print("  Regler    W%d O%d L%d K%d E%d S%d F%d" % tuple(a[k] for k in "WOLKESF"))
    print("  Umfang    %d Wörter, %d Sätze | Median %d | längster %d"
          % (m["words"], m["sentences"], m["median_sentence"], m["longest_sentence"]))
    print("  Satzbau   %.2f Kommas/Satz | %d %% ohne Komma | %d Bullets, %d Doppelpunkt-Marken"
          % (m["commas_per_sentence"], m["pct_without_comma"], m["bullets"], m["colon_intros"]))
    print("  Ballast   %d Negativ-Prämissen | %d Konditionale | %d Floskeln | %d Selbstrechtfertigung"
          % (m["negative_premises"], m["conditionals"], m["fillers"], m["self_justification"]))
    if m["lecturing"]:
        print("  Belehrend %d %s" % (m["lecturing"],
              ", ".join("%s (%d)" % (l, n) for l, n in m["lecturing_detail"])))
    print("  Last      %d Bring-Bitten | %d Options-Angebote | %d zurückgegebene Entscheidungen"
          % (m["bring_requests"], m["option_offers"], m["handbacks"]))
    print("  Führung   %d Führungs-Marker | %d Fragen gesamt (Sachfragen zählen nicht gegen F)"
          % (m["lead_markers"], m["questions"]))
    print("  Substanz  %d Marker (Zahlen, Daten, Kontakte, Links) | %d Bedauern"
          % (m["substance_markers"], m["regret"]))
    slop_note = "" if not m["slop_detail"] else "  → " + ", ".join(
        "%s (%d)" % (l, n) for l, n in m["slop_detail"])
    print("  Slop      %d Em-Dash (%.1f je 1000 W, Ziel 0) | %d Modell-Tells%s"
          % (m["em_dashes"], m["em_dash_per_1000"], m["slop_markers"], slop_note))
    extra = [("Emoji", m["emoji"]), ("Füll-Adverb", m["fill_adverbs"]),
             ("Dreierfigur", m["rhetorical_triads"]), ("Nominalstil", m["nominal_style"]),
             ("W-Satzanfang", m["w_openings"])]
    hit = [(k, v) for k, v in extra if v]
    print("  Zusatz    %s" % (", ".join("%s %d" % (k, v) for k, v in hit) if hit
                              else "alle fünf Zusatzfilter sauber (Ziel 0)"))
    if m["emoji_chars"]:
        print("            Emoji im Text: %s" % m["emoji_chars"])

def main():
    ap = argparse.ArgumentParser(description="Messe eine Mail gegen die sieben Ton-Achsen.")
    ap.add_argument("files", nargs="+", help="Dateien oder - für stdin")
    ap.add_argument("--json", action="store_true", help="Rohwerte als JSON")
    args = ap.parse_args()
    out = []
    for f in args.files:
        raw = sys.stdin.read() if f == "-" else open(f, encoding="utf-8").read()
        m = measure(raw, "stdin" if f == "-" else f.split("/")[-1])
        if not m:
            print("%s: kein messbarer Text" % f, file=sys.stderr)
            continue
        out.append(m)
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        for m in out:
            render(m)
            print()

if __name__ == "__main__":
    main()
