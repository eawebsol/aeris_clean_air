from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class CityCode(str, Enum):
    DELHI = "Delhi-NCR"
    PATNA = "Patna"
    KOLKATA = "Kolkata"

class AirQualityReading(BaseModel):
    city: str
    aqi: int
    pm25: float = Field(..., description="PM2.5 concentration in ug/m3")
    pm10: float = Field(..., description="PM10 concentration in ug/m3")
    who_pm25_ratio: float = Field(..., description="Ratio over WHO 24-hr guideline (15 ug/m3)")
    category: str
    timestamp: str

class WeatherForecast(BaseModel):
    city: str
    night_temp_c: float
    surface_wind_kmh: float
    relative_humidity_pct: float
    is_inversion_favorable: bool
    estimated_mixing_height_m: int
    risk_level: str

class CommuteComparison(BaseModel):
    mode: str
    travel_time_min: int
    pm25_exposure_score: str
    co2_grams: float
    pm25_exhaust_grams: float

class IAQPlan(BaseModel):
    room_sqft: int
    cadr_required: int
    diy_fan_size_inches: int
    merv_rating: str
    est_cost_inr: float
    commercial_hepa_cost_inr: float
    savings_inr: float
    instructions: List[str]

class DirectImpactLedger(BaseModel):
    pm25_averted_grams: float
    co2_averted_kg: float
    avoided_healthcare_cost_inr: float
    who_protective_factor: str
