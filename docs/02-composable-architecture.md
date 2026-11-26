# Composable AI Architecture & SOLID System Design

## 1. High-Level Architecture Diagram

```mermaid
flowchart TD
    subgraph UI_Layer["Presentation Layer (Bespoke Streamlit Dashboard)"]
        UI["Modern Editorial UI\n(Zero 'Generic AI' Aesthetic, Custom Layout)"]
    end

    subgraph Guardrails_Layer["Security & Safety Boundary"]
        IG["Input Guardrail\n(Sanitization, PII Scrub, Jailbreak Defense)"]
        OG["Output Guardrail\n(Pydantic Schema Validation, Citation Verification)"]
    end

    subgraph Orchestration_Layer["Workflow & Orchestration Engine"]
        Orch["SmogAssistantOrchestrator\n(Context assembly, tool routing, fallback handling)"]
    end

    subgraph Domain_Layer["Pure Business & Physics Domain (Framework Agnostic)"]
        InvServ["InversionService\n(Boundary layer collapse, nocturnal radiative cooling)"]
        RoutServ["RoutineService\n(Exposure reduction, school & commute shift)"]
        IAQServ["IAQService\n(Corsi-Rosenthal CADR, clean room sealing)"]
        ImpServ["ImpactService\n(PM2.5 & CO2 averted, World Bank health cost savings)"]
    end

    subgraph Ports_Layer["Domain Ports (Abstract Contracts / Interfaces)"]
        LLMPort["«interface»\nLLMPort"]
        AQPort["«interface»\nAirQualityPort"]
        MemPort["«interface»\nMemoryPort"]
    end

    subgraph Adapters_Layer["Infrastructure Adapters (Concrete Implementations)"]
        GeminiAdapter["GeminiAdapter\n(Google Gemini API / Structured Outputs)"]
        MockLLMAdapter["MockLLMAdapter\n(Deterministic Offline & CI Testing)"]
        HybridAQAdapter["HybridAQAdapter\n(Live OpenAQ/WAQI + Offline High-Smog Fixtures)"]
        LocalMemAdapter["LocalMemoryAdapter\n(Stateful session storage)"]
    end

    UI --> IG
    IG --> Orch
    Orch --> Domain_Layer
    Domain_Layer --> Ports_Layer
    Ports_Layer <|.. GeminiAdapter
    Ports_Layer <|.. MockLLMAdapter
    Ports_Layer <|.. HybridAQAdapter
    Ports_Layer <|.. LocalMemAdapter
    Orch --> OG
    OG --> UI
```

---

## 2. Abstract Interface Contracts (SOLID Dependency Inversion)

All domain logic interacts exclusively with the following abstract ports. No direct imports of external vendor SDKs are permitted in the domain.

### 2.1 LLM Provider Interface (`LLMPort`)
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class LLMPort(ABC):
    """Abstract port for all Generative AI model providers."""

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        """Generate unstructured text completion with telemetry logging."""
        pass

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
    ) -> T:
        """Generate structured output validated against a Pydantic schema."""
        pass
```

### 2.2 Air Quality & Weather Telemetry Interface (`AirQualityPort`)
```python
from abc import ABC, abstractmethod
from typing import Optional
from domain.models.telemetry import AirQualityReading, WeatherForecast

class AirQualityPort(ABC):
    """Abstract port for meteorological and air quality telemetry."""

    @abstractmethod
    def get_current_reading(self, city_code: str) -> AirQualityReading:
        """Retrieve real-time or cached AQI, PM2.5, PM10, and gas concentrations."""
        pass

    @abstractmethod
    def get_nocturnal_forecast(self, city_code: str) -> WeatherForecast:
        """Retrieve overnight min temperature, wind speed, and inversion risk indicators."""
        pass
```

---

## 3. Repository Directory Structure

```
d:\hackathons\hack2skill\promptwars\
├── .agents/                               # Antigravity persistent agent rules
│   └── rules/
├── docs/                                  # Living architectural & governance docs
├── evals/                                 # Evaluation harness & benchmark suites
│   ├── data/                              # Golden datasets (JSONL)
│   └── test_eval_gates.py                 # Automated quantitative benchmark runner
├── src/
│   ├── domain/                            # PURE Domain layer (No external SDK dependencies)
│   │   ├── models/                        # Domain entities & Pydantic schemas
│   │   ├── ports/                         # Abstract interfaces (LLM, AQI, Memory)
│   │   ├── services/                      # Pure business logic (Physics, IAQ, Impact)
│   │   └── prompts/                       # Semantic versioned prompt templates
│   ├── adapters/                          # Concrete adapter implementations
│   │   ├── llm/                           # Gemini & Mock adapters
│   │   ├── telemetry/                     # OpenAQ/WAQI + offline fixtures
│   │   └── memory/                        # In-memory session store
│   ├── guardrails/                        # Input sanitizer & output validators
│   ├── orchestration/                     # Coordination & workflow engine
│   └── ui/                                # Polished, bespoke Streamlit UI
├── tests/                                 # Fast unit and contract tests
├── .gitignore                             # Enforcing < 10 MB repository constraint
├── README.md                              # Submission showcase & setup instructions
└── requirements.txt                       # Minimal pinned dependencies
```
