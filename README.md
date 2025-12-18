# Prototyp: Prüfplattform für KI-Systeme
**Workflow-basierter Open-Source-Prototyp**

## Überblick

Dieses Repository enthält den **Open-Source-Plattformprototyp zur Prüfung von KI-Systemen**, entwickelt im Rahmen des Projekts **MISSION KI**.

Die Prüfplattform ermöglicht die **automatisierte, reproduzierbare und nachvollziehbare Erzeugung technischer Evidenzen** mithilfe modularer, workflowbasierter Prüfungen. Zielgruppen sind:

- KI-Prüfer:innen und Auditierende
- Organisationen, die KI-Systeme prüfen oder Selbstprüfungen durchführen
- Entwickler:innen von KI-Prüfwerkzeugen
- Forschung, Standardisierung und Governance-Initiativen

Der veröffentlichte Code ist ein **Forschungs- und Konzeptprototyp**, der die technische Machbarkeit einer modularen Prüfplattform demonstriert.

## Motivation & Kontext

Vertrauenswürdige KI erfordert technische Evidenzen, die:

- nachvollziehbar,
- reproduzierbar,
- automatisiert erzeugbar und
- unabhängig validierbar

sind.

Im Rahmen von **MISSION KI** wurde ein technischer Prototyp entwickelt, der als **Backend einer zukünftigen Prüflandschaft** fungieren kann. Die Plattform unterstützt freiwillige, standardisierte KI-Prüfungen sowie die Integration von Qualitätstests in Entwicklungs- und Auslieferungsprozesse (CI/CD, MLOps).

## Architekturübersicht

Die Prüfplattform folgt einem **modularen, containerisierten und workflowbasierten Ansatz**.

Zentrale Komponenten:

- **Barebone** – Build- und Onboarding-Tool für neue Prüfwerkzeuge
- **Nodes** – Containerisierte Prüfwerkzeuge und Modellknoten
- **Orchestrator** – Ausführung und Steuerung von Prüfworkflows

## Repository-Struktur

- `barebone/` – Build-/Onboarding-Tool (inkl. Templates, Spezifikationsschema, CLI)
- `nodes/` – konkrete Prüfwerkzeuge und Beispiel-Modelle als containerisierte Knoten
- `orchestrator/` – Workflow-Ausführung (CWL), Templates, Beispiele, Hilfsskripte

## Barebone – Onboarding neuer Prüfwerkzeuge

Pfad: `barebone/`  
Detail-Doku: `barebone/README.md`

### Zusammenfassung (aus dem Detail-README)

Der **Barebone** unterstützt Tool-Entwickler:innen dabei, bestehende **Python-Prüfwerkzeuge** in plattformkompatible, containerisierte Knoten zu überführen.

- Konvertierung von Python-Funktionen in OCI-konforme Container (z. B. Docker)
- Werkzeug-/Funktionsbeschreibung über `spec.json` (maschinenlesbar)
- Unterstützte Schnittstellen:
  - Kommandozeile (empfohlen)
  - gRPC (experimentell)
- Automatische Generierung von:
  - Docker-Build-Kontexten
  - CWL-Tool-Deskriptoren (`*.cwl`)
- Template-/Beispiel-basierter Einstieg („copy & paste“)

➡️ Für Installation, Onboarding-Schritte und Beispiele siehe `barebone/README.md`.

## Nodes – Prüfwerkzeuge & Modellknoten

Pfad: `nodes/`

Nodes sind **ausführbare Prüfkomponenten**, die in Prüfworkflows kombiniert werden. Jede Node ist typischerweise:

- containerisiert,
- standardisiert aufrufbar (Ein-/Ausgaben per Dateien/URIs),
- unabhängig testbar,
- workflowfähig (z. B. via CWL-Toolbeschreibung).

### Enthaltene Beispiel-Nodes (aus den Detail-READMEs)

**Scikit-learn Metriken**  
Pfad: `nodes/scikit-metrics-tool/`  
Detail-Doku: `nodes/scikit-metrics-tool/README.md`  
Kurzbeschreibung: Metriken aus `sklearn.metrics` für Klassifikation/Regression (z. B. Accuracy, Precision, Recall, F1, ROC AUC, MCC, MSE). Fokus: Verlässlichkeit.

**IBM AI Fairness 360**  
Pfad: `nodes/aif360/`  
Detail-Doku: `nodes/aif360/README.md`  
Kurzbeschreibung: Fairness-/Bias-Metriken (z. B. Statistical Parity Difference, Disparate Impact, Consistency). Fokus: Nicht-Diskriminierung.

**Uncertainty Toolbox**  
Pfad: `nodes/uncertainty-toolbox-metrics/`  
Detail-Doku: `nodes/uncertainty-toolbox-metrics/README.md`  
Kurzbeschreibung: Unsicherheits- und Kalibrationsmetriken (z. B. ECE/MACE/NLL/CRPS). Fokus: Unsicherheit & Kalibration.

**Beispiel-Modellknoten**  
Pfad: `nodes/scikit-logreg-model/`  
Detail-Doku: `nodes/scikit-logreg-model/README.md`  
Kurzbeschreibung: Referenzmodell als Node (z. B. Logistic Regression) zur Demonstration von Modellknoten in Workflows.

➡️ Details zu Inputs/Outputs, Container-Run, Beispielen und Testdaten siehe die jeweiligen Unter-READMEs.

## Orchestrator – Ausführung von Prüfworkflows

Pfad: `orchestrator/`  
Detail-Doku: `orchestrator/README.md`

### Zusammenfassung (aus dem Detail-README)

Der **Orchestrator** führt Prüfworkflows als **Multi-Container-Anwendungen** aus und sorgt dafür, dass Knoten in der richtigen Reihenfolge laufen und Datenabhängigkeiten eingehalten werden.

- Workflow-Spezifikation: **Common Workflow Language (CWL)**
- Ausführung typischerweise mit `cwltool`
- Unterstützt sequenzielle und parallele Ausführung
- Portabel über lokale Rechner, Server und (je nach Setup) Cloud-Umgebungen
- Enthält Workflow-Templates und Beispiel-Workflows
- Optional/experimentell: gRPC-basierte Ausführung einfacher Szenarien

➡️ Details zu Workflow-Templates, Beispielaufrufen und Setup siehe `orchestrator/README.md`.

## Prüfworkflows (Konzept)

Ein **Prüfworkflow** beschreibt formal:

- welche Prüfkomponenten ausgeführt werden,
- in welcher Reihenfolge,
- mit welchen Ein- und Ausgaben.

Eigenschaften:

- DAG (gerichteter azyklischer Graph)
- reproduzierbar durch containerisierte Ausführung
- versionierbar durch Workflow-/Tool-Spezifikationen
- CI/CD- und MLOps-tauglich (CLI-ausführbar)

Typische Workflows:

- Modell + Testdaten → Inferenz → Metrikberechnung
- Vorhersagen + sensitive Attribute → Fairnessmetriken
- Regressionsvorhersagen + Unsicherheiten → Kalibrationsmetriken
- Regressionstests über Modellversionen hinweg

## Status des Projekts

**Forschungs- und Prototypstatus**

- kein produktives System
- keine API-Stabilitätsgarantie
- Fokus auf Architektur, Konzepte und technische Machbarkeit

Geeignet für:

- Forschung & Pilotprojekte
- Tool-Entwicklung und -Integration
- Standardisierungs- und Governance-Kontexte

## Weiterentwicklung

Mögliche nächste Schritte:

- API-Anbindung an Prüfoberflächen
- Ausbau eines Prüfwerkzeug-Katalogs
- Persistente Ergebnis- und Metadatenverwaltung
- Governance-/Rollenmodelle
- Erweiterungen für regulatorische Anforderungen (z. B. EU AI Act)
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
