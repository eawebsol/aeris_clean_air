# Phased Implementation Roadmap

This roadmap defines the sequential, gate-governed execution plan for developing the Urban Smog & Clean Air Assistant. In accordance with `AGENTS.md`, no application feature code will precede the evaluation harness and domain contracts.

---

## Phase 1: Evaluation Harness & Golden Dataset (CRISP-ML Baseline)
- [ ] Create `evals/data/golden_eval_suite.jsonl` covering:
  - Predictive nocturnal inversion scenarios (Delhi, Patna, Kolkata).
  - Exposure minimization & WFH corporate justification requests.
  - DIY Corsi-Rosenthal calculations & Clean Room audits.
  - Adversarial injection & medical emergency test vectors.
- [ ] Implement `evals/eval_harness.py`:
  - Deterministic evaluation runner scoring faithfulness, relevance, schema validity, and safety pass-rate.
  - Set baseline gate enforcement.

---

## Phase 2: Domain Layer & Abstract Ports (SOLID Inversion)
- [ ] Define domain Pydantic schemas in `src/domain/models/`:
  - Telemetry entities (`AirQualityReading`, `WeatherForecast`, `InversionRisk`).
  - Household profiles (`FamilyProfile`, `VulnerabilityFlag`, `CommuteProfile`).
  - Advisory output schemas (`DailySmogRoutine`, `IAQAuditResult`, `ImpactLedger`).
- [ ] Define abstract port protocols in `src/domain/ports/`:
  - `LLMPort` (Text and Structured generation).
  - `AirQualityPort` (Current telemetry & nocturnal forecasts).
  - `MemoryPort` (Session context management).
- [ ] Implement pure, deterministic domain services in `src/domain/services/`:
  - `InversionService`: Nocturnal temperature drop, wind stagnation & boundary layer collapse physics.
  - `IAQService`: Corsi-Rosenthal box CADR sizing, room volume matching, and wet-mopping vs. sweeping logic.
  - `ImpactService`: Calculation of averted PM2.5/CO2 grams, WHO guideline comparisons, and World Bank economic health savings.

---

## Phase 3: Infrastructure Adapters & Orchestration
- [ ] Implement concrete adapters in `src/adapters/`:
  - `adapters/llm/gemini_adapter.py`: Production integration with Google Gemini API via structured schemas.
  - `adapters/llm/mock_adapter.py`: Offline deterministic mock for CI and evaluation benchmarking.
  - `adapters/telemetry/hybrid_aq_adapter.py`: Hybrid client querying live OpenAQ/WAQI API with automatic fallback to high-fidelity Delhi/Patna/Kolkata winter smog fixtures.
- [ ] Implement `src/orchestration/smog_orchestrator.py`:
  - Context assembly, domain service invocation, LLM synthesis, and fallback error handling.

---

## Phase 4: NIST AI RMF Guardrails & Safety Hardening
- [ ] Implement `src/guardrails/input_guardrail.py`:
  - Prompt injection detection, PII redactor, and clinical emergency bypass router.
- [ ] Implement `src/guardrails/output_guardrail.py`:
  - Pydantic schema validation, hallucinated value checks, and mandatory WHO/Harvard COGfx scientific citation enforcement.
- [ ] Run full test suite through `evals/test_eval_gates.py` and verify 100% safety pass rate and $\ge 0.92$ faithfulness.

---

## Phase 5: Editorial Presentation Layer & Demo Packaging
- [ ] Build the bespoke, human-crafted user interface in `src/ui/app.py`:
  - Clean typography, high-contrast atmospheric gauges, dual WHO vs. NAQI indicators.
  - Nocturnal Inversion Forecast banner with 1-Click WFH Request generator.
  - Interactive DIY Corsi-Rosenthal filter builder & bill-of-materials estimator.
  - Direct Impact Ledger displaying saved grams of PM2.5 and averted healthcare expenditure.
- [ ] Verify repository footprint:
  - Confirm repository size is strictly $< 10\text{ MB}$ (no build caches or heavy assets).
- [ ] Document setup instructions, architecture walkthrough, and scientific references in root `README.md`.
