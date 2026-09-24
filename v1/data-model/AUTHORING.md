# Framework: Seiten unter v1/data-model/ erstellen

Internes Arbeitsdokument, kein Kundeninhalt. Destilliert aus dem Review-Auftrag
[Asana 1218785508795822](https://app.asana.com/1/1207811178165063/project/1211659549321545/task/1218785508795822)
("API-Doku: inhaltliche Korrekturen") und seinen 8 Subtasks — die Befunde dort
wiederholten sich über Overview/Accounting/Contracts/Depreciation/Operations
hinweg. Ziel: dieselben Fehler nicht bei jeder neuen `v1/data-model/*.mdx`-Seite
neu machen.

Fachlichen Kontext zum aktuellen v1-Rollout-Stand (welche Tabellen `v1_reviewed`,
welche Felder gecastet/umbenannt) liefert `v1/data-model-handoff.md` (gitignored,
Append-only). Dieses Dokument hier ist das Gegenstück: keine Fakten zum aktuellen
Stand, sondern die Regeln, nach denen jede Seite geschrieben wird.

## Wiederkehrende Fehlerkategorien (aus dem Review)

**A. Diagramm zeigt nicht die Realität**
Accounting-Diagramm fehlten vier zentrale Kanten (`contract_debits`→`accounts`,
`property_structure`→`accounts`, `creditor`→`accounts`, `properties`→`accounts`).
Diagramm und Fließtext dürfen sich nicht widersprechen (bekannter Fall:
`overview.mdx` zeichnete `contract_debit_diffs -.->|account_id| accounts`,
der Text sagte korrekt das Gegenteil). Jede Kante im Diagramm muss live gegen
echte Daten verifiziert sein (`scripts/rest_v1/verify_*_joins.py` in
`trassets-data-api`), nie aus Namensmustern geraten.

**B. Spalten ohne nachvollziehbaren Kundenbezug**
Operations nannte ein `hierarchy`-Array ohne Erklärung. Genereller Fehler:
Felder auflisten, die "zufällig" wirken, weil kein Grund genannt wird, warum sie
für den Kunden relevant sind. Jedes erwähnte Feld braucht entweder eine
Erklärung, die ein externer Kunde versteht, oder fliegt raus.

**C. Verweise auf unsichtbare interne Strukturen**
Keine internen Tabellennamen/Systemdetails nennen, die ein Kunde nie sieht.
Tabellen-Referenzen zeigen auf
[`data-lake/transformed/Refactor/README-TABLE-DEFINITIONS.md`](https://github.com/Trassets-ai/data-lake/blob/main/transformed/Refactor/README-TABLE-DEFINITIONS.md)
oder entfallen ganz.

**D. Unbelegte Zahlen, Werkstatt-Sprache**
Kein nicht hergeleiteter Prozentwert in der allgemeinen Doku (Fall: 3,55 % ohne
Kontext). Keine Zwischenstands-Kommentare ("Stand: ...", Model-Self-Talk) im
kundenseitigen Text — das ist Commit-/PR-Beschreibung, nicht MDX.

**E. `*_name_concat`-Felder falsch erklärt**
Diese Felder existieren für zusammengesetzte Anzeige-Strings in Power BI, nicht
für eine Verknüpfung. Nie als Join-Mechanismus beschreiben.

**F. Datentyp-Inkonsistenz zwischen Endpunkten**
Dieselbe fachliche Spalte muss über alle Endpunkte, die sie referenzieren, den
gleichen JSON-Typ liefern — sonst muss der Client casten, um zu joinen. Cast
passiert, falls nötig, sync-seitig in `data-lake` (ADR-0003 "Ort der
Transformation"), nie API-seitig und nie stillschweigend in der Doku
weggeschrieben. Vor dem Schreiben einer Seite:
`trassets-data-api/scripts/check_*_join_key_types.py`-Familie gegen die live
`openapi-v1.json` laufen lassen. Bleibt ein Mismatch bestehen, gehört er als
Hinweis in die Seite — nicht verschwiegen.

**G. Fachliche Kategorisierung nicht hinterfragt**
Beispiel: Servicevertäge (Wartung etc.) landeten unter "Contracts", obwohl
"Contracts" für Mietverhältnisse reserviert sein sollte. Domain-Zuordnung mit
dem fachlichen Reviewer abstimmen, nicht nach Namensgefühl sortieren — und die
Begründung für die gewählte Sortierung in der Seite oder im PR festhalten.

**H. Modell-Self-Talk statt Kundendokumentation**
Übergreifender Befund aus dem Review: Korrekturen an bestehenden Seiten werden
**manuell redigiert**, nicht durch erneutes Prompten "gefixt". Offene fachliche
Zusammenhänge werden mit dem Reviewer geklärt, nicht selbst angenommen.

## Checkliste: neue Seite unter v1/data-model/

1. **Scope prüfen** — nur Tabellen mit `api_model.categories.v1_reviewed = true`
   aufnehmen (Live-Stand siehe `v1/data-model-handoff.md`). Keine Seite/Sektion
   für nicht reviewte Tabellen, auch nicht als "coming soon".
2. **Live-Schema als Quelle** — Felder und Typen aus `DESCRIBE` gegen
   `<kunde>.api_v1.*` bzw. `https://api.trassets.ai/openapi-v1.json` ziehen,
   nicht aus dem ADR oder Namensmustern ableiten (beides schon mehrfach durch
   Live-Check widerlegt).
3. **Diagramm** — jede gezeichnete Kante live verifizieren (Match-Rate-Skript),
   Text und Diagramm gegenlesen (Kategorie A).
4. **Jedes Feld** — `<ResponseField>` mit Erklärung, die für einen externen
   Kunden Sinn ergibt (Kategorie B); `*_name_concat` korrekt als
   Power-BI-Convenience kennzeichnen (Kategorie E); keine internen
   Tabellenverweise ohne README-TABLE-DEFINITIONS.md-Link (Kategorie C).
5. **Datentyp-Check** — `check_*_join_key_types.py` laufen lassen (Kategorie F),
   Ergebnis in der Seite oder im PR vermerken.
6. **Fachliche Fallstricke aktiv benennen** — nicht nur beschreiben, was ein
   Feld ist, sondern auch was es *nicht* kann (Beispiel: Buchungen auf
   Personenkonten sind nur je Objekt verknüpfbar, nicht je Fläche).
7. **Domain-Zuordnung** — bei Unsicherheit mit dem fachlichen Reviewer
   abstimmen (Kategorie G), nicht selbst entscheiden.
8. **Manuelles Review** — Text von einem Menschen redigieren lassen, kein
   Re-Prompt als Fix (Kategorie H). Keine unbelegten Zahlen, keine
   Zwischenstands-Sprache (Kategorie D).
