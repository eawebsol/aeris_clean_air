# Workspace Invariants & Engineering Baseline (PromptWars Challenge 6)

This repository hosts an enterprise-grade, evidence-based GenAI assistant designed to help families and communities navigate severe winter smog and urban air pollution. All contributors and AI agents MUST adhere to these non-negotiable architectural, lifecycle, and safety invariants.

---

## 1. Non-Negotiable Engineering Invariants

### Invariant 1: No Feature Code Without Spec & Evals
- **Gate:** No domain logic, pipeline code, or user-facing endpoint may be committed or merged without:
  1. An approved specification in `docs/`.
  2. Baseline unit tests covering domain edge cases.
  3. Quantitative evaluation benchmarks (faithfulness, relevance, safety) in `evals/` executed against the golden dataset.

### Invariant 2: Strict Dependency Inversion (SOLID)
- **Decoupled Providers:** Core domain entities and use-cases (`domain/`) must **NEVER** import or invoke concrete SDKs directly (e.g., `google.generativeai`, `openai`, `qdrant_client`, `chromadb`).
- **Abstract Contracts:** All model inferences, embeddings, vector retrievals, and air quality telemetry must be accessed strictly through abstract interfaces/protocols defined in `domain/ports/` and implemented under `adapters/`.
- Changing an LLM provider or vector engine must require **zero modifications** to business logic.

### Invariant 3: Production-Grade Observability at Every AI Boundary
- Every call crossing an AI or external API boundary must emit structured logs containing:
  - Correlation ID / Request ID.
  - Token consumption (prompt, completion, total).
  - Latency (p50, p95).
  - Model identifier and temperature.
  - Guardrail validation status (input and output check outcomes).
- Unstructured `print()` statements are strictly forbidden in production modules.

### Invariant 4: Strict Schema Validation & Graceful Fallbacks
- All generative AI completions must be constrained and validated via strict schemas (Pydantic / Structured Outputs).
- If a model output fails validation or hallucinates out-of-domain advice, the system must trigger a deterministic, rule-based fallback without throwing unhandled exceptions to the user.

### Invariant 5: Repository Footprint Constraint
- In strict adherence to Hack2skill competition rules, the **entire Git repository size must remain strictly under 10 MB**.
- All virtual environments (`.venv`), temporary model caches, large raw datasets, and build artifacts must be excluded via `.gitignore`.

---

## 2. Framework Alignments
1. **Lifecycle Discipline:** Governed by `.agents/rules/crisp-ml-lifecycle.md` (CRISP-ML(Q)).
2. **Structural Boundaries:** Governed by `.agents/rules/composable-solid-architecture.md`.
3. **Safety & Risk Governance:** Governed by `.agents/rules/nist-ai-rmf-safety.md` (NIST AI RMF).
