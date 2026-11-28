---
trigger: model_decision
description: Enforces Composable AI Architecture and SOLID principles, maintaining strict separation between domain, ports, adapters, and UI.
---

# Composable AI Architecture & SOLID Principles Rule

This rule defines the directory boundaries, component responsibilities, and adapter contracts.

## 1. Directory Structure & Boundaries

```
src/
├── domain/                      # PURE Domain layer (No external SDK imports!)
│   ├── constants/               # Scientific factors, CPCB stations, landmarks, i18n
│   ├── models/                  # Domain entities & Pydantic schemas (schemas.py)
│   ├── ports/                   # Abstract base classes / Protocols (interfaces.py)
│   └── services/                # Pure physics & business logic (physics_service.py)
├── adapters/                    # Concrete implementations of domain ports
│   ├── llm/                     # Gemini multi-model cascade & mock adapter (adapters.py)
│   └── telemetry/               # 3-tier hybrid CPCB / WAQI / fixture adapter (hybrid_adapter.py)
├── orchestration/               # Master orchestrator connecting services & guardrails
├── guardrails/                  # NIST AI RMF input/output guardrails (guardrails.py)
└── ui/                          # Bespoke Streamlit dashboard & regional landmark silhouettes
```

## 2. SOLID Architectural Invariants
- **Single Responsibility Principle (SRP):**
  - Services calculate physics/impacts; adapters communicate with network APIs; guardrails validate; the orchestrator connects them.
- **Open/Closed Principle (OCP):**
  - Adding a new LLM provider (e.g., Anthropic, Groq, Ollama) requires only adding a new class implementing `LLMPort` without altering `services/` or `orchestration/`.
- **Liskov Substitution Principle (LSP):**
  - Mock adapters in `adapters/llm/mock_adapter.py` must pass the identical interface contract tests as `GeminiAdapter`.
- **Interface Segregation Principle (ISP):**
  - Clients should not depend on interfaces they do not use. Separate `EmbeddingPort` from `LLMPort`.
- **Dependency Inversion Principle (DIP):**
  - High-level modules must never depend on low-level modules. Both must depend on abstractions in `domain/ports/`.
