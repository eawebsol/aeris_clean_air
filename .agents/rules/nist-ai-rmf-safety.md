---
trigger: model_decision
description: Enforces the NIST AI Risk Management Framework (Govern, Map, Measure, Manage) to prevent hallucinations, jailbreaks, PII leakage, and clinical harm.
---

# NIST AI Risk Management Framework (AI RMF) Safety Rule

This rule ensures full alignment with the NIST AI RMF core pillars: **Govern, Map, Measure, Manage**.

## 1. Govern (Accountability & Policy Boundaries)
- **Medical & Clinical Boundary:** The assistant provides air quality navigation and preventive environmental advice. It is **STRICTLY FORBIDDEN** from diagnosing pulmonary illness, prescribing medications (e.g., inhalers, steroids), or replacing clinical care.
- **Human-in-the-Loop (HITL) Fallback:** For high-risk clinical queries (e.g., "my baby is wheezing and turning blue"), the system must bypass the LLM and emit an immediate emergency disclaimer with national hotline numbers.

## 2. Map (Threat & Vulnerability Classification)
- **Prompt Injections / Jailbreaks:** Users attempting to override system prompts or bypass safety boundaries must be intercepted at the input guardrail.
- **Hallucinated Air Quality Data:** The model must never generate imaginary AQI readings; all current readings must originate from the validated `AirQualityPort`.
- **PII Leakage:** Home addresses, personal medical histories, or sensitive family demographic data must be scrubbed or kept strictly in local memory.

## 3. Measure (Continuous Verification)
- Run automated red-teaming test suites on every build targeting:
  1. System prompt extraction attacks.
  2. Medical prescription baiting.
  3. Contradictory physics assertions (e.g., claiming open windows during morning smog clean the air).
- Maintain 0% tolerance for critical safety failures.

## 4. Manage (Runtime Defenses & Graceful Degradation)
- **Input Guardrail:** Regex and semantic filtering for prompt injection vectors.
- **Output Guardrail:** Schema validation (Pydantic). If parsing fails, fall back to a deterministic structured advisory template.
- **Citation Guardrail:** Every claim regarding health or air cleaning must be backed by a cited authority (WHO, EPA, Harvard, CAQM).
