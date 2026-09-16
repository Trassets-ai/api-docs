# Handoff: v1 Data Model Dokumentation

Content-Übergabe, kein fertiger MDX-Text. Ziel: eigene `/v1/data-model/`-Seiten,
die das tatsächliche v1-Response-Schema beschreiben — nicht die im
`docs.json` aktuell verlinkten unversionierten `data-model/*.mdx`-Seiten.
Quelle der Wahrheit: `docs/adr/0003-v1-schema-simplification.md`
(trassets-data-api) + Live-`DESCRIBE` gegen `customer_mortensen.api_v1.*`
(2026-09-16). Nicht aus Namensmustern oder der ADR allein ableiten — mehrfach
per Live-Check widerlegt, siehe Abschnitt 5.

## 1. Strukturbefund: `docs.json` zeigt auf die falschen Seiten

`navigation.versions[].version == "v1"` → Gruppe "Data Model" (EN) bzw.
"Datenmodell" (DE) verlinkt exakt dieselben Pfade wie die `Current`-Version:

```
data-model/accounting, data-model/contracts, data-model/depreciation,
data-model/field-glossary, data-model/operations, data-model/overview,
data-model/stakeholder
```

Diese Seiten beschreiben das **unversionierte** Schema (`bko_hdr_id`,
`join_key`, `to_hdr_id`, `hierarchy_1..20`, `booking_sum_net/tax/gross` als
Einzelfelder). Für v1 sind diese Feldnamen bei den 7 reviewten Tabellen
falsch. Zusätzlicher Bug unabhängig von diesem Auftrag: die EN-v1-Gruppe
listet `data-model/property` gar nicht — Property-Domain fehlt komplett in
der v1-Navigation, obwohl `technical_objects` (Property-Domain) bereits
`v1_reviewed = true` ist.

**Empfehlung:** neue Seiten unter `v1/data-model/*.mdx` (+ `de/v1/data-model/*.mdx`),
in `docs.json` nur für die `v1`-Version verdrahten, `Current`-Version bleibt
unverändert auf die alten Seiten zeigen.

## 2. Scope: nur diese 7 Tabellen

Live-Stand `api_model.categories.v1_reviewed = true` (2026-09-16):

| Domain | Tabelle | ADR-0003 tatsächlich umgesetzt? |
|---|---|---|
| Accounting | `booking_positions` | ✅ vollständig (Konv. 1–3, 7) |
| Accounting | `booking_header` | ✅ vollständig (Konv. 1, 7) |
| Accounting | `budgets` | ⚠️ **nein** — siehe Abschnitt 5 |
| Operations | `notifications` | ✅ (Konv. 7) |
| Operations | `projects` | ✅ Konv. 4 (hierarchy-Array); Konv. 2/3 greifen laut ADR nicht |
| Property | `technical_objects` | ✅ inkl. OQ-005-Sonderfall |
| Stakeholder | `tenants` | ⚠️ **nein**, siehe Abschnitt 5 |

Alle anderen Tabellen (`orders`, `property_structure`, `assets`, `creditor`,
`contract_debits`, etc.) sind **nicht** reviewt — keine v1-Data-Model-Seite
dafür erstellen, auch nicht als "coming soon". Contracts- und
Depreciation-Domain haben aktuell 0 reviewte Tabellen → keine v1-Seite für
diese zwei Domains anlegen, bis die erste Tabelle dort durchläuft.

## 3. Dateistruktur-Vorschlag

Nur für Domains mit ≥1 reviewter Tabelle:

```
v1/data-model/overview.mdx       (Cards: nur Accounting/Operations/Property/Stakeholder)
v1/data-model/accounting.mdx     (booking_header, booking_positions, budgets)
v1/data-model/operations.mdx     (notifications, projects)
v1/data-model/property.mdx       (technical_objects)
v1/data-model/stakeholder.mdx    (tenants)
```

Plus deutsche Spiegelung unter `de/v1/data-model/`. `docs.json`: v1-Version,
Gruppe "Data Model"/"Datenmodell" → diese 5 Pfade statt der alten 7.

## 4. Was in jede Tabellenseite muss (Format wie bestehende `data-model/*.mdx`)

`<ResponseField>`-Blöcke mit echten v1-Feldnamen, plus **Before/After** nur
wo eine Umbenennung/Nesting stattgefunden hat (Leser kennt evtl. die
unversionierten Feldnamen aus der `Current`-Doku). Muster aus
`v1/response-shape-conventions.mdx` weiterverwenden, nicht neu erfinden.

### Accounting → `booking_positions`

Vollständig reshaped, ADR-Beispiel 1:1 übernehmbar (ADR Zeilen 234–256).
Kern-Felder: `property_id`, `creditor_id`, `person_id`,
`property_id_person_id` (bigint, **bewusst nicht redundant zu
property_id+person_id gestrichen** — 2.488 Abweichungen bei 1,55 Mio.
Zeilen, empirisch verifiziert, nicht selbst als Konkatenation dokumentieren),
`booking_header_id`, `booking_position_id`, `account_id`,
`period: {start, end}`, `amount: {net, tax, gross}`,
`amount_per_sqm: {net, tax, gross}`, `property_structure_account_id`
(umbenannt von `recommended_join_key`/`join_key` — **kein** ETL-Rauschen,
100 %-verifizierter FK auf `property_structure.account_id`), `sh` (bewusst
flach, kein Boolean — 3,55 % Storno-Buchungen widersprechen dem
Vorzeichen-Muster), `HNDL` (bewusst flach, Bedeutung ungeklärt, OQ-002
deferred — **nicht selbst benennen**), `contra_account_name` (bewusst nicht
gestrichen, 0 % Join-Treffer gegen `accounts`).

### Accounting → `booking_header`

Kein `period`/`amount`-Objekt — Tabelle hat nur je ein `booking_date`- und
ein `booking_value`-Feld, Konvention 2/3 greifen strukturell nicht. Gestrichen:
`cost_center_m2` (100 % rekonstruierbar aus `cost_center_id_name_concat` +
`m2`). **Nicht** gestrichen trotz `*_id_name_concat`-Namensmuster:
`cost_center_id_name_concat`, `ledger_id_name_concat`, `person_name_concat` —
das sind die einzigen Quellen dieser Information, keine Zieltabelle im
Schema erlaubt Rekonstruktion (Korrektur an Konvention 1 in der ADR).
`recommended_join_key` → `property_structure_account_id` (100 % verifiziert,
gleiches Muster wie `booking_positions`).

### Accounting → `budgets` — ⚠️ Doku darf keine ADR-Konformität behaupten

`v1_reviewed = true` seit Rollout (2026-09-07), aber Live-`DESCRIBE`
(2026-09-16) zeigt: `property_id_account_number` (bigint) ist **weiterhin
vorhanden**. Das ist exakt der Konvention-1-Verstoß, den OQ-001 als
Entscheidung ("v1-Korrektur, sofort fixen") klassifiziert hat — Umsetzung
liegt in `data-lake#602` Task 1, dort noch **kein Haken gesetzt**, nicht
deployed. `property_id` und `account_id` sind hier bereits als `int`
typisiert (kein Cast-Bedarf für dieses Kundenschema).

**Konsequenz für die Doku:** entweder (a) mit Implementierung von
`data-lake#602` Task 1 abstimmen und synchron veröffentlichen, oder (b) die
Seite **explizit mit einem Hinweis versehen**, dass `property_id_account_number`
noch ein bekanntes, offenes Sync-Artefakt ist und in Kürze entfernt wird —
nicht stillschweigend so dokumentieren, als wäre `budgets` bereits
Konvention-1-konform. Nicht schönfärben.

### Operations → `notifications`

Schlank, keine Nesting-Konventionen angewendet (ADR sieht dafür für diese
Tabelle auch nichts vor). Konvention 7: `to_reference_id`/`to_hdr_id` →
`technical_object_id` bereits umgesetzt und live (Live-Schema zeigt
`technical_object_id`, kein `to_hdr_id` mehr). `person_id` ist hier
**bigint**, nicht das 6-stellige lokale Schema wie in `booking_header`/
`tenants` — laut ADR ein anderes Subsystem, **nicht** als dieselbe Entität
wie `tenants.person_id` dokumentieren oder cross-referenzieren.
`report_id` ersetzt das alte `report_hdr_id`.

### Operations → `projects`

Konvention 4 vollständig umgesetzt: `hierarchy_1..20` → `hierarchy: [...]`
(Array, leere Stufen entfernt). `project_hdr_id` → `project_id`, das alte
`project_id` (Projektnummer) → `project_number` (gleiches Tausch-Muster wie
bei `accounts`/`assets`, siehe `trassets_api_sync.md`-Changelog).

**Zwei Felder mit Vorsicht dokumentieren, nicht als zuverlässige FKs
darstellen:**
- `to_hdr_id` bleibt bewusst **unverändert und flach** — Join-Test widerlegt
  jede vermutete Zielentität (3,5 % Match gegen `technical_objects.to_id`,
  auch nicht `orders`/`notifications`). OQ-003 ungeklärt, braucht
  Source-System-Kontakt. Nicht als `technical_object_id`-Alias oder FK
  bezeichnen.
- `creditor_id` matcht **0 %** gegen `creditor.creditor_id` — vorbestehender
  Datenfehler, unabhängig von dieser ADR (kein v1-spezifisches Problem).
  Wenn dokumentiert: als "derzeit nicht zuverlässig auflösbar" kennzeichnen,
  nicht als funktionierenden Join zu `Stakeholder.creditor` beschreiben (wie
  es die alte `operations.mdx`-Seite fälschlich tut).

`projektleitung` bleibt String (`'0'`/`'1'`), noch nicht Boolean — OQ-002
deferred, nicht selbst als Boolean umdeuten.

### Property → `technical_objects`

OQ-005-Sonderfall bereits live umgesetzt: neue Spalte
`property_structure_account_id`, nur für die 309 Zeilen ohne `floor_area_id`
befüllt, sonst `NULL` — für die übrigen 941 Zeilen bleibt `floor_area_id`
zuständig (Live-Verifikation 2026-09-16: exakt 309/0/0/941 gefüllt-korrekt/
fälschlich-null/fälschlich-gefüllt/mit-floor_area_id). `to_id` bleibt flach
(Konvention 8). `recommended_join_key` existiert in dieser Tabelle nicht mehr
als Spaltenname.

### Stakeholder → `tenants` — ⚠️ kein ADR-0003-Vorbild, Linkability-Risiko

`v1_reviewed = true`, aber laut vorheriger Recherche aus historisch
unklarem Grund, **nicht** Teil des ADR-0003-Rollouts. Live-`DESCRIBE`
bestätigt: **keine** der ADR-0003-Konventionen ist hier angewendet — die in
OQ-002 bereits als mergebar geklärten Felder
(`contract_end`/`contract_end_option`/`contract_end_actual`, 100 % identisch
wo mehrfach befüllt) sind weiterhin drei separate Spalten.

**Kritischer Befund für die Doku (nicht in bisherigen Session-Notizen
festgehalten):** Die unversionierte `stakeholder.mdx`-Seite dokumentiert
`floor_area_person_id` und `property_id_person_id` als Bridge-Keys, über die
`Contracts.contract_debits`/`contract_ends` eine Tenancy referenzieren. Die
v1-`tenants`-Tabelle hat **beide Spalten nicht** — Live-Schema zeigt nur
`property_id`, `floor_area_id`, `person_id` (kein Composite-Key). Aktuell
folgenlos, weil `contract_debits`/`contract_ends` selbst noch nicht
`v1_reviewed` sind — aber sobald eine dieser Tabellen reviewt wird, fehlt ihr
v1-Pendant von `tenants` der Join-Schlüssel, über den sie sich laut
unversionierter Doku heute verknüpft. Kein Konvention-1-Verstoß im
ADR-0003-Sinn (keine empirische Redundanz-Prüfung dafür durchgeführt, weil
`tenants` nie durch den ADR-0003-Prozess lief) — eher eine stille
Verknüpfbarkeitslücke, die die ADR mit Konvention 8 explizit verhindern
wollte. **Empfehlung:** vor Veröffentlichung der v1-`tenants`-Seite klären
(neues Issue oder Nachtrag zu `docs/adr/0003-v1-schema-simplification.md`),
nicht einfach dokumentieren als wäre das Fehlen beabsichtigt.

## 5. Begleitseiten, die mit angefasst werden müssen

- **`v1/response-shape-conventions.mdx`**: Frontmatter-Note sagt "status:
  Proposed" — ADR-0003 ist seit 2026-09-14 "Accepted". Beispiel-Zeile
  `"recommended_join_key": "1204"` → *entfernt* ist zur Hälfte falsch: bei
  `booking_positions`/`booking_header`/`technical_objects` wird die Spalte
  **umbenannt** zu `property_structure_account_id`, nicht gestrichen. Nur
  bei `property_structure` selbst soll `recommended_join_key` gestrichen
  werden (OQ-005/Konvention 1) — und das ist laut `data-lake#602` Task 3
  noch **nicht umgesetzt**. Zeile entsprechend präzisieren oder in zwei
  Fälle aufteilen.
- **`v1/data-model/field-glossary.mdx`** (neu, falls die v1-Felder stark
  genug von der unversionierten Glossar-Seite abweichen): mindestens
  `period`, `amount`, `amount_per_sqm`, `hierarchy`, `property_structure_account_id`
  als neue, v1-spezifische Einträge — bestehende Einträge zu `join_key`,
  `floor_area_person_id`, `property_id_person_id` (unversioniert) nicht
  einfach kopieren, da sie für v1 teils nicht mehr gelten (s. `tenants`
  oben).

## 6. Was explizit NICHT tun

- Keine Seite/Sektion für `orders` — Reshaping-Code existiert, aber
  Issue #586 (`vat_rate`-Zeilenduplikation) lebt live unverändert; jede
  Doku würde einen bekannten Datenfehler stillschweigend zertifizieren.
- Keine Seite für `property_structure` — kein normales Reshaping, sondern
  offenes Redesign-Ticket (`/properties/{id}/structure`-Vorschlag laut ADR),
  noch nicht als Issue angelegt.
- Keine Spekulation über Felder, die laut ADR/OQ-002 noch Source-System-
  Kontakt brauchen (`HNDL`, `okdn`, `projektleitung`, `contract_end_new`,
  `option_valid_until`, `index_rent`-Zeiträume) — als "Bedeutung noch nicht
  final geklärt" kennzeichnen, nicht selbst benennen oder umdeuten.
- Keinen Tenant-/Kunden-Vorbehalt in die externe Doku schreiben (z. B. "nur
  gegen `customer_mortensen` verifiziert") — das ist ein internes
  Rollout-Risiko (`v1_reviewed` ist global, nicht pro Kunde), keine
  API-Vertragsaussage. Gehört ins interne Projekt-Memory, nicht auf
  `docs.trassets.ai`.

## 7. Offene Entscheidung für den Autor

`budgets` und `tenants` sind live `v1_reviewed = true`, aber nicht
ADR-0003-konform (Abschnitt 5). Vor dem Schreiben der jeweiligen
Tabellenseite entscheiden: mit dem ausstehenden Fix synchronisieren (Doku
wartet auf `data-lake#602`/Tenants-Klärung) oder den aktuellen,
unvollständigen Stand ehrlich mit Hinweis-Box dokumentieren. Nicht
stillschweigend so schreiben, als wären beide Tabellen bereits vollständig
nach den in `v1/response-shape-conventions.mdx` beschriebenen Konventionen
gebaut.

## 8. Nachtrag 16.09.2026 (spät) — 9 weitere ADR-0003-PRs gemergt

Neue Runde Reshaping seit Abschnitt 1–7 geschrieben wurde, alle heute
gemergt (`data-lake` PRs #623–#631) und live gegen `customer_mortensen`
verifiziert (Zeilenzahlen vorher/nachher identisch, siehe jeweilige PR-
Beschreibung). **Nur 4 davon sind für Doku-Zwecke relevant** — die anderen
5 bewusst auslassen, siehe Abschnitt 8.2.

### 8.1 Relevant: die 4 bereits `v1_reviewed = true`-Tabellen bekamen zusätzliche Felder

Diese vier waren schon Teil von Abschnitt 2–4 dieses Handoffs — die
folgenden Änderungen kommen **zusätzlich** zu dem, was dort schon
beschrieben ist, nicht anstatt.

**Stakeholder → `tenants`** (PR #625)
- `contract_begin`/`contract_end` → `contract_period: {start, end}`
  (analog `properties.mandate_period`, asymmetrisches NULL toleriert).
- `contract_end_actual` **entfernt** — war reines ETL-Derivat
  (`LEAST(contract_end, contract_end_option)`), live 100 % verifiziert,
  aus `contract_end`/`contract_end_option` rekonstruierbar.
- `option_valid_until`-Sentinel (`2299-12-31`, 75/2121 Zeilen) und
  `contract_end_option` bleiben unverändert — weiterhin offene
  Fachklärung, wie in Abschnitt 4 beschrieben, nicht durch diese PR gelöst.
- Interner Workaround (PR #632, **keine externe Doku-Relevanz**): manche
  Kunden (`customer_showroom`) haben den Issue-#619-Rename
  (`floor_area_person_id` → `tenant_id`) in ihrer eigenen
  Anonymisierungs-Pipeline noch nicht nachgezogen. Die View ermittelt die
  Quellspalte jetzt zur Laufzeit — das nach außen sichtbare Feld
  `tenancy_id` bleibt in Name und Bedeutung für alle Kunden identisch,
  nichts an der Doku ändert sich dadurch.

**Operations → `projects`** (PR #629)
- `cost_center_id_name` (ETL-Concat `"<code> | <label>"`) **ersetzt**
  durch `cost_center: {code, label}`, aus dem Concat extrahiert.
- `project_begin_date`/`project_end_date` → `project_period: {start, end}`.
- `budget_from`/`budget_until` → `budget_period: {start, end}`.
- **Nicht in dieser PR gefixt, als bekannter Fehler dokumentieren oder
  ganz weglassen:** `ledger_account_nr` ist live zu 100 % identisch mit
  `cost_center_id` (beide aus derselben Quellspalte `p.kstst`) — ETL-
  Kopierfehler, kein eigenständiges Feld. Nicht als funktionierenden,
  eigenständigen "Ledger-Account"-Bezug beschreiben, bis ein eigenes
  Ticket das klärt (gleiche Fehlerklasse wie `accounts.accounting_entity`
  #616/`assets.afa_validity` #617).
- `to_hdr_id`/`request_hdr_id` bleiben weiterhin bewusst unverändert und
  referenziell ungeklärt (siehe Abschnitt 4) — durch diese PR nicht
  betroffen.

**Operations → `notifications`** (PR #628)
- `to_do_from`/`to_do_until` → `to_do_period: {start, end}`.
- `technical_object` (String, war 100 % Duplikat von `technical_object_id`)
  **entfernt** — `technical_object_id` bleibt die einzige ID-Spalte dafür.

**Property → `technical_objects`** (PR #627)
- `warranty_begin_date`/`warranty_end_date` → `warranty_period:
  {start, end}`. Sehr dünn befüllt (1/1250 Zeilen live) — beim Dokumentieren
  als selten genutztes Feld kennzeichnen, nicht als Regelfall darstellen.

### 8.2 Nicht relevant für diesen Doku-Zyklus — bewusst keine Seite anlegen

- **`contract_debits`** (PR #623, `debit_period: {start, end}` statt
  `date_begin`/`date_end`) und **`debit_diffs`**/`contract_debit_diffs`
  (PR #631, `debit_diff_value: {net, tax, gross}`): Code+RDS bereits
  umgestellt, aber `api_model.categories.v1_reviewed = false` für beide —
  noch nicht offiziell Teil des v1-Rollouts. Gleiche Regel wie in
  Abschnitt 6: keine Seite, auch nicht "coming soon".
- **`offers`** (PR #624, `offer_period: {start, end}`) und **`orders`**
  (PR #626, `ledger_account: {code, label}` + `runtime_period:
  {start, end}`): ebenfalls `v1_reviewed = false`. Für `orders` gilt
  zusätzlich weiterhin der in Abschnitt 6 genannte Ausschlussgrund
  (Issue #586, `vat_rate`-Zeilenduplikation, unverändert offen).
- **`index_rent`**: Code reshaped (PR #630, `validity_period`,
  `calculation_model: {code, label}`, `is_current`), aber die Tabelle ist
  **gar nicht** in `api_model.categories` registriert — kein live
  Endpunkt, unabhängig vom Reshaping-Stand nichts zu dokumentieren.

### 8.3 Sonstiges

- `api_model.categories.sample` (das JSON-Beispiel, das `api/main.py` für
  OpenAPI-Beispiele nutzt) ist für alle 4 Tabellen aus 8.1 aktuell leer —
  keine veralteten Beispielwerte, die vor dem Schreiben bereinigt werden
  müssten. Beispielwerte für die MDX-Seiten direkt aus der Live-API ziehen,
  nicht erfinden.
- Wie in Abschnitt 6 festgehalten: `v1_reviewed` ist global (nicht pro
  Kunde) — diese Runde wurde nur gegen `customer_mortensen` live
  verifiziert (Zeilenzahlen unverändert, Spalten wie beschrieben). Kein
  Grund für einen Kunden-Vorbehalt in der externen Doku, aber falls
  `customer_showroom`-Sync zum Zeitpunkt des Schreibens noch nicht
  abgeschlossen ist: das ist ein internes Rollout-Detail, keine
  API-Vertragsaussage.
