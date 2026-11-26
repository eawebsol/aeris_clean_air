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
│   ├── models/                  # Domain entities, Pydantic data schemas
│   ├── ports/                   # Abstract base classes / Protocols (Interfaces)
│   │   ├── llm_port.py          # Abstract LLM provider interface
│   │   ├── air_quality_port.py  # Abstract telemetry / AQI provider interface
│   │   └── memory_port.py       # Abstract session / conversation store
│   ├── services/                # Pure business logic
│   │   ├── inversion_service.py # Nocturnal temperature drop & smog physics
│   │   ├── routine_service.py   # Daily planner & exposure optimization
│   │   ├── iaq_service.py       # DIY Corsi-Rosenthal & Clean Room calculations
│   │   └── impact_service.py    # PM2.5, CO2, and health cost savings calculator
│   └── prompts/                 # Versioned prompt templates
├── adapters/                    # Concrete implementations of domain ports
│   ├── llm/                     # Google Gemini adapter, mock adapter for CI/evals
│   ├── telemetry/               # Hybrid OpenAQ/WAQI API client + local fixture fallback
│   └── memory/                  # In-memory / local session state
├── orchestration/               # Multi-step workflows, tool dispatchers, agent graphs
├── guardrails/                  # Input validation, output schema enforcement, PII filter
├── ui/                          # User interface (Bespoke Streamlit dashboard with polished CSS)
└── evals/                       # Evaluation harness, golden test suites, benchmark scripts
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
