# NIST AI Risk Management Framework (AI RMF) Risk Register

This document operationalizes the four core functions of the **NIST AI RMF 1.0**: **Govern, Map, Measure, and Manage**, specifically adapted for our Urban Smog & Clean Air Assistant.

---

## 1. Govern (Organizational Governance & Policies)

### 1.1 Scope & Intended Use Boundary
- **Intended Purpose:** Provide predictive meteorological alerts, exposure-reduction schedules, open-source indoor filtration guides (Corsi-Rosenthal), and quantifiable emission reduction alternatives for families and communities in severe smog zones (Delhi-NCR, Patna, Kolkata).
- **Prohibited / Out-of-Scope Uses:**
  - Clinical diagnosis of pulmonary diseases (asthma, COPD, bronchitis).
  - Medical prescribing (dosage of bronchodilators, steroids, or antihistamines).
  - Safety certification of commercial HVAC or industrial scrubbers.

### 1.2 Human-in-the-Loop (HITL) & Emergency Escalation
- If a user inputs symptoms indicating acute respiratory distress (e.g., cyanosis, severe shortness of breath, infant wheezing), the system triggers an emergency protocol:
  - Bypasses generative LLM processing entirely.
  - Returns a hardcoded, deterministic medical alert with emergency hotline numbers (e.g., India National Emergency 112 / Ambulance 102).

---

## 2. Map (Threat & Failure Mode Matrix)

| Threat / Risk Event | Category | Likelihood | Severity | Mitigation & Control Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **Hallucinated Air Quality Data** | Model Accuracy | Medium | High | **Ground-Truth Binding:** Model is never permitted to invent PM2.5 numbers; telemetry is strictly injected via `AirQualityPort` into structured prompt context. |
| **Medical / Clinical Advice Misinformation** | Safety / Clinical | Medium | Critical | **Hard Clinical Boundary Guardrail:** Regex and semantic filters intercept prescription or diagnostic queries with emergency disclaimers. |
| **Prompt Injection & Jailbreak Attacks** | Security | Medium | Medium | **Input Sanitizer:** Pre-processes user input, stripping delimiter injections and jailbreak templates before hitting orchestrator. |
| **Air Inequality Bias (Class Insensitivity)** | Fairness / Equity | High | Medium | **Accessible IAQ Alternatives:** Whenever commercial purifiers are referenced, the assistant is mandated to prioritize low-cost DIY Corsi-Rosenthal builds (~$35–$40). |
| **Meteorological Inversion Misprediction** | Model Reliability | Low | Medium | **Physics-Grounded Heuristics:** Inversion risk is calculated via deterministic boundary-layer physics (nocturnal radiative temperature drop + wind speed $< 5\text{ km/h}$) rather than probabilistic model guesses. |
| **External API Outage (OpenAQ/WAQI)** | Operational Resilience| Medium | Medium | **Hybrid Offline Fixtures:** Graceful fallback to verified historical winter smog profiles for Delhi, Patna, and Kolkata. |

---

## 3. Measure (Testing & Verification Metrics)

### 3.1 Golden Dataset & Red-Teaming Coverage
- A curated benchmark suite (`evals/data/golden_eval_suite.jsonl`) containing:
  - 20 Complex Routine Planning queries (vulnerable kids, elderly, shift work).
  - 15 DIY Indoor Air Quality technical queries (CADR calculation, MERV-13 filter setups).
  - 15 Adversarial injection and medical diagnosis queries.

### 3.2 Evaluation Thresholds (Release Gates)
- **Faithfulness Score:** $\ge 0.92$ (verified via automated cross-evaluation).
- **Injection Interception Rate:** $100\%$ pass on jailbreak prompts.
- **Medical Disclaimer Trigger Rate:** $100\%$ on simulated clinical emergency inputs.
- **Latency Target:** p95 under 2500 ms.

---

## 4. Manage (Runtime Defenses & UX Fallbacks)

### 4.1 Layered Defense Architecture
1. **Layer 1: Input Guardrail (`guardrails/input_guardrail.py`):**
   - Strips malicious control characters and detects adversarial intent.
   - Routes medical emergency keywords directly to emergency response templates.
2. **Layer 2: Domain Logic & Deterministic Physics (`domain/services/`):**
   - Calculations for CADR, nocturnal inversion probability, and carbon/PM2.5 metrics are computed in pure Python, not by the LLM.
3. **Layer 3: Output Guardrail (`guardrails/output_guardrail.py`):**
   - Validates completions against Pydantic schema contracts.
   - Enforces scientific citations (WHO, Harvard COGfx, EPA, CAQM).
   - If output fails schema validation, falls back to a deterministic structured emergency card.
