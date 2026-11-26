# CRISP-DM / CRISP-ML(Q) Project Charter: Urban Smog & Clean Air Assistant

## 1. Business Understanding & Problem Definition

### 1.1 Problem Statement
During winter months in urban centers across northern and eastern India (most acutely in **Delhi-NCR, Patna/Gangetic Basin, and Kolkata**), nocturnal radiation inversions trap hazardous particulate matter ($\text{PM}_{2.5}$, $\text{PM}_{10}$) and toxic gases near the ground. Morning mixing heights collapse to under 100 meters, exposing millions of citizens to air quality indices (AQI) exceeding 400–500 ($25\times$ to $35\times$ higher than the 2021 WHO 24-hour limit of $15\,\mu\text{g/m}^3$).

Families face three critical problems:
1. **Reactive Awareness:** Citizens only notice smog *after* arriving at work or school, missing the opportunity to shift commutes or initiate remote work the evening before.
2. **Air Inequality & Indoor Vulnerability:** Commercial air purifiers ($200–$500) are economically out of reach for most households, while unvented heating, incense, and dry sweeping compound indoor toxicity.
3. **Lack of Actionable Agency:** Citizens feel helpless because existing apps provide abstract AQI numbers without quantifying the direct health, economic, or emission benefits of their everyday decisions.

### 1.2 Target User Personas
- **The Urban Corporate Commuter (IT/ITES & Knowledge Workers):** Needs early evening alerts to trigger WFH approvals and route adjustments before morning rush hour.
- **The Sensitive Household Guardian (Parents with Infants / Caregivers for Elderly & Asthmatics):** Requires actionable indoor air quality hacks, safe room creation, and clear clinical boundary warnings.
- **The Community Action Champion (Neighborhood RWA Leader / Student Activist):** Coordinates carpooling, monitors open burning, and promotes sustainable materials (e.g., upcycled soot tiles).

---

## 2. McKinsey 5-Layer Success Metrics

| Layer | Metric Name | Baseline / Industry Standard | Project Target | Measurement Method |
| :--- | :--- | :--- | :--- | :--- |
| **1. Technical Performance** | Groundedness & Faithfulness | 0.70 (Generic LLM) | **$\ge 0.92$** | Automated Ragas / LLM-as-a-judge against golden dataset |
| | E2E Latency (p95) | 4500 ms | **$\le 2500$ ms** | Telemetry logs at orchestration boundary |
| | Quantitative Schema Accuracy | 80% | **$100\%$** | Pydantic validation pass rate |
| **2. User Experience & Adoption** | Bespoke Design Trust Score | Low (Generic AI vibe) | **High Quality (Editorial UI)** | Custom typography, zero markdown dumps, zero generic chatbot fluff |
| | Predictive Lead Time | 0 hrs (Morning reactive) | **$\ge 10$ hrs** (Issued at 8:30 PM previous evening) | Nocturnal inversion alert timestamp verification |
| **3. Operational KPIs** | Clean Room Setup Feasibility | Expensive ($300+) | **Sub-$40 (DIY Corsi-Rosenthal)** | Bill-of-materials pricing calculator for local Indian hardware |
| | Modal Shift Route Accuracy | Vague advice | **EV Sub-lane & Metro comparative route metrics** | Calculated fuel, travel time, and exposure delta |
| **4. Strategic Outcomes** | Harvard COGfx Productivity Integration | Absent in existing apps | **Cognitive drop risk alerts mapped to indoor PM2.5** | Rule-based cognitive impairment risk mapping |
| | Scientific Standards Alignment | Local NAQI only | **Side-by-side WHO 2021 Threshold comparison** | Dual-gauge indicator ($\mu\text{g/m}^3$ vs. WHO $15\,\mu\text{g/m}^3$ limit) |
| **5. Financial / Health ROI** | Avoided Medical Burden | Unquantified | **₹3,000–₹6,000 / family / winter in avoided sick days & care** | World Bank $8.1T global air pollution cost model adaptation |

---

## 3. Data Inventory & Engineering Strategy

### 3.1 Data Sources (Hybrid Architecture)
- **Live Ambient Telemetry:** OpenAQ API and WAQI API for ground-truth ambient PM2.5, PM10, temperature, wind speed, and humidity across Delhi-NCR, Patna, and Kolkata.
- **Offline Deterministic Fallbacks & Fixtures:** Deterministic JSON fixtures modeling high-inversion winter smog scenarios (e.g., December cold-wave night with 2 km/h wind and 7°C nocturnal drop) for offline testing, evals, and disconnected hackathon demos.
- **Curated Knowledge Repositories (Domain Corpus):**
  - Corsi-Rosenthal Foundation technical specifications and CADR formulas.
  - CAQM Delhi GRAP Framework guidelines (Stages I–IV).
  - Harvard T.H. Chan COGfx indoor air and cognitive function findings.
  - World Bank and Health Effects Institute (State of Global Air) economic impact coefficients.

### 3.2 Ingestion & Indexing Strategy
- Compact, in-memory structured vector store or deterministic BM25 / schema-based retrieval.
- Strict repository size constraint: The entire codebase, documentation, and evaluation assets must strictly stay **under 10 MB** to comply with Hack2skill competition rules.

---

## 4. Quantitative Evaluation Gates

Before advancing between implementation phases, the solution must pass these quantitative gates:
1. **Safety Gate:** Zero tolerance ($0\%$) for clinical prescription generation or unhandled prompt injections.
2. **Faithfulness Gate:** $\ge 0.90$ groundedness score across 50 golden test cases.
3. **Nocturnal Inversion Accuracy Gate:** Correctly flags radiation inversion risk on all validated historical winter smog test fixtures.
4. **Latency Gate:** p95 latency under 2.5 seconds on CPU.
