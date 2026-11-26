from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Type, TypeVar
from pydantic import BaseModel
from src.domain.models.schemas import AirQualityReading, WeatherForecast

T = TypeVar("T", bound=BaseModel)

class LLMPort(ABC):
    """Abstract port for Generative AI providers."""
    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2
    ) -> str:
        pass

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.1
    ) -> T:
        pass

class AirQualityPort(ABC):
    """Abstract port for air quality and meteorological telemetry."""
    @abstractmethod
    def get_current_reading(self, city: str) -> AirQualityReading:
        pass

    @abstractmethod
    def get_station_reading(self, station_name: str, city: str = "Delhi-NCR") -> AirQualityReading:
        pass

    @abstractmethod
    def get_nocturnal_forecast(self, city: str, station_name: Optional[str] = None) -> WeatherForecast:
        pass
