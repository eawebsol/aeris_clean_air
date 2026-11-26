---
trigger: model_decision
description: Enforces CRISP-ML(Q) lifecycle discipline, dataset/prompt versioning, and quantitative evaluation gates.
---

# CRISP-ML(Q) Lifecycle Governance Rule

This rule enforces the CRISP-ML(Q) standard across all data exploration, prompt engineering, and model deployment decisions.

## 1. Business & Data Understanding Phase
- All algorithmic recommendations must trace back to scientifically validated thresholds:
  - **WHO Global Air Quality Guidelines 2021** (Annual PM2.5: $5\,\mu\text{g/m}^3$, 24-hour PM2.5: $15\,\mu\text{g/m}^3$).
  - **Diurnal Radiation Inversion Physics** (Boundary layer collapse linked to nocturnal temperature drops and surface wind $< 5\text{ km/h}$).
  - **Indian National Air Quality Index (NAQI) & CAQM GRAP** Stages (Stage I: AQI 201–300, Stage II: 301–400, Stage III: 401–450, Stage IV: $>450$).
- Target Primary Metropolitan Basins:
  1. **Delhi-NCR** (Severe seasonal inversion & transboundary biomass/vehicle smog).
  2. **Patna / Bihar Gangetic Basin** (Chronic high PM2.5 persistence and high population density).
  3. **Kolkata** (Severe winter vehicular and industrial stagnation).

## 2. Data & Prompt Versioning
- **Datasets:** Evaluation sets (`evals/data/`) must be versioned deterministically (e.g., `golden_dataset_v1.jsonl`). Synthetic and cached real OpenAQ/WAQI telemetry must follow explicit schemas.
- **Prompts:** Production prompts must be stored in external configuration files under `domain/prompts/` with semantic versioning (`v1.0.0`). Never hardcode prompt strings directly inside application business logic.

## 3. Quantitative Evaluation Gates
Before any prompt modification, model upgrade, or pipeline release, the evaluation harness must confirm:
- **Groundedness / Faithfulness:** $\ge 0.90$ (Answers must cite authoritative sources without fabricating air quality metrics).
- **Answer Relevance:** $\ge 0.88$ against the golden evaluation set.
- **Safety / Toxicity Pass Rate:** $100\%$ on adversarial injection and medical diagnostic queries.
- **Latency Budget (p95):** $\le 2500\text{ ms}$ for core advisory flows.
- **Cost per Interaction:** Tracked and kept within budget constraints.
