# Phased Implementation Roadmap & Verification Gates

This roadmap defines the sequential, gate-governed execution plan for developing the Urban Smog & Clean Air Assistant. In accordance with `AGENTS.md`, all implementation phases are verified by automated tests and quantitative evaluation gates.

---

## Phase 1: Evaluation Harness & Golden Dataset (CRISP-ML Baseline) — [COMPLETED]
- [x] Create `evals/data/golden_eval_suite.jsonl` covering:
  - Predictive nocturnal inversion scenarios (Delhi-NCR, Patna, Kolkata).
  - Exposure minimization & WFH corporate justification requests.
  - DIY Corsi-Rosenthal calculations & Clean Room audits.
  - Adversarial injection & medical emergency test vectors.
- [x] Implement `evals/test_eval_gates.py`:
  - Deterministic evaluation runner scoring faithfulness, relevance, schema validity, and safety pass-rate.
  - **Outcome:** Gate PASSED (100% Safety, 100% Faithfulness, p95 Latency 0.22 ms).

---

## Phase 2: Domain Layer & Abstract Ports (SOLID Inversion) — [COMPLETED]
- [x] Define domain Pydantic schemas in `src/domain/models/schemas.py`:
  - Telemetry entities (`AirQualityReading`, `WeatherForecast`).
  - Household profiles and consultation intake contexts.
  - Advisory output schemas (`CommuteComparison`, `IAQPlan`, `DirectImpactLedger`).
- [x] Define abstract port protocols in `src/domain/ports/interfaces.py`:
  - `LLMPort` (`generate_text`, `generate_structured`).
  - `AirQualityPort` (`get_current_reading`, `get_station_reading`, `get_nocturnal_forecast`).
- [x] Implement pure, deterministic domain services in `src/domain/services/physics_service.py`:
  - `InversionPhysicsService`: Nocturnal temperature drop, wind stagnation & boundary layer collapse physics, Berkeley Earth cigarette equivalence.
  - `IAQService`: Corsi-Rosenthal box CADR sizing ($CADR = \frac{V \times 4.5}{60}$), room volume matching, and attributed bill of materials.
  - `ImpactCalculatorService`: Calculation of averted PM2.5/CO2 grams, WHO guideline comparisons, and World Bank economic health savings.
- [x] Establish attributed domain constants in `src/domain/constants/`:
  - `cpcb_stations.py`: 35+ continuous CPCB monitoring stations across 12 Indian states/cities.
  - `impact_factors.py`: Emission factors, traffic corridor density, and sustainable materials.
  - `landmark_silhouettes.py`: Regional architectural landmark silhouettes.
  - `localization.py`: Bilingual English & Hindi translations.

---

## Phase 3: Infrastructure Adapters & Orchestration — [COMPLETED]
- [x] Implement concrete adapters in `src/adapters/`:
  - `src/adapters/llm/adapters.py`:
    - `GeminiAdapter`: Multi-model cascade (`gemini-2.5-flash` $\to$ `gemini-2.0-flash` $\to$ `gemini-1.5-flash` $\to$ `MockLLMAdapter`).
    - `MockLLMAdapter`: 100% deterministic offline mock for zero-key evaluation and CI testing.
  - `src/adapters/telemetry/hybrid_adapter.py`:
    - `HybridAirQualityAdapter`: 3-tier resilient client querying live `data.gov.in` CPCB API $\to$ WAQI/OpenAQ $\to$ calibrated historical winter fixtures.
- [x] Implement `src/orchestration/orchestrator.py`:
  - `SmogAssistantOrchestrator`: Context assembly, domain service invocation, LLM synthesis with 4 mandatory advisory sections, and fallback error handling.

---

## Phase 4: NIST AI RMF Guardrails & Safety Hardening — [COMPLETED]
- [x] Implement `src/guardrails/guardrails.py`:
  - `InputGuardrail`: Prompt injection detection and clinical emergency bypass router (112 / 102 medical escalations).
  - `OutputGuardrail`: Schema validation and mandatory WHO 2021 & Harvard COGfx scientific citation enforcement.
- [x] Run full automated test suites:
  - 17/17 tests passing across `tests/qa/` (smoke, regression, 50-request concurrency) and `tests/security/` (guardrail injection, zero-key fallback, secret leak scan).
  - Verified 100% safety pass rate and 100% faithfulness on `evals/test_eval_gates.py`.

---

## Phase 5: Editorial Presentation Layer & Demo Packaging — [COMPLETED]
- [x] Build the bespoke, human-crafted user interface in `src/ui/app.py`:
  - Clean atmospheric typography, glassmorphic decision cards, and high-contrast telemetry indicators.
  - Nocturnal Inversion Forecast banner with 1-Click Corporate WFH Request generator.
  - Interactive DIY Corsi-Rosenthal filter builder & bill-of-materials estimator.
  - Direct Impact Ledger displaying saved grams of PM2.5, avoided healthcare expenditure, and collective RWA community multiplier.
  - Single-click floating dock scroll-spy navigation (`Live AQI`, `Diurnal`, `AI Consult`, `Tools & Data`, `4-Pillar Plan`).
  - 12 regional heritage landmark silhouette illustrations adapted to local AQI tiers.
- [x] Verify repository footprint constraint:
  - Compressed all 12 landmark illustrations to 192 KB total.
  - Tracked file size: **0.52 MB**.
  - Total git repository footprint: **~2.7 MB** (well under the strict Hack2skill **10.0 MB** limit).
- [x] Document setup instructions, architecture walkthrough, and scientific references in root `README.md` and `docs/`.
