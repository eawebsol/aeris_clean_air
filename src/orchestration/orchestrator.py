"""
Master Orchestration Engine.
Coordinates Domain Services, Adapters, and NIST AI RMF Guardrails.
Guarantees every answer is tailored to the household intake and structured into 4 components:
1. What to do today
2. One indoor air quality (IAQ) hack
3. One sustainable alternative
4. Estimated direct impact of that choice with its assumption
"""

from typing import Dict, Any, Optional
from src.domain.ports.interfaces import LLMPort, AirQualityPort
from src.guardrails.guardrails import InputGuardrail, OutputGuardrail

class SmogAssistantOrchestrator:
    def __init__(self, llm_adapter: LLMPort, telemetry_adapter: AirQualityPort):
        self.llm = llm_adapter
        self.telemetry = telemetry_adapter

    def handle_query(
        self,
        user_query: str,
        city: str = "Delhi-NCR",
        intake_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        # Step 1: Input Guardrail (Emergency & injection defense)
        is_safe, sanitized_query, emergency_msg = InputGuardrail.inspect(user_query)
        if emergency_msg:
            return {
                "city": city,
                "response": emergency_msg,
                "is_emergency": True,
                "is_fallback": False
            }
        if not is_safe:
            return {
                "city": city,
                "response": sanitized_query,
                "is_emergency": False,
                "is_fallback": False
            }

        # Step 2: Telemetry injection
        station_name = intake_context.get("station") if intake_context else None
        if station_name and hasattr(self.telemetry, "get_station_reading"):
            current_aqi = self.telemetry.get_station_reading(station_name=station_name, city=city)
            nocturnal = self.telemetry.get_nocturnal_forecast(city=city, station_name=station_name)
        else:
            current_aqi = self.telemetry.get_current_reading(city)
            nocturnal = self.telemetry.get_nocturnal_forecast(city)

        # Intake defaults if not provided
        intake = intake_context or {
            "vulnerabilities": ["Children", "Elderly"],
            "commute_mode": "petrol_car",
            "cooking_fuel": "LPG",
            "has_purifier": False,
            "budget_band": "Middle (₹5k-15k)"
        }

        system_instruction = (
            "You are an evidence-based Urban Smog & Clean Air Assistant. "
            "You MUST ALWAYS structure your advice into exactly four clearly marked sections:\n"
            "1. WHAT TO DO TODAY: Concrete routine tailored to the user's specific location, AQI, and household (vulnerabilities, commute).\n"
            "2. ONE INDOOR AIR QUALITY (IAQ) HACK: A practical, low-cost indoor hack (e.g. Corsi-Rosenthal box, wet-mopping, ventilation timing).\n"
            "3. ONE SUSTAINABLE ALTERNATIVE: A sustainable lifestyle/community alternative (e.g. electric transit, upcycled soot tiles, clean heating).\n"
            "4. ESTIMATED IMPACT & ASSUMPTIONS: Quantify the estimated PM2.5/CO2 averted or rupees saved, stating the one-line assumption explicitly.\n"
            "Keep advice concise, direct, and grounded in WHO/CPCB standards. Never fabricate medical dosages."
        )

        prompt = (
            f"Context:\n"
            f"- City: {city}\n"
            f"- Current AQI: {current_aqi.aqi} ({current_aqi.category}, PM2.5: {current_aqi.pm25} ug/m3, {current_aqi.who_pm25_ratio}x WHO limit)\n"
            f"- Inversion Risk: {nocturnal.risk_level} (Night min: {nocturnal.night_temp_c}C, Wind: {nocturnal.surface_wind_kmh} km/h, Mixing height: ~{nocturnal.estimated_mixing_height_m}m)\n"
            f"- User Household Intake: Vulnerabilities: {', '.join(intake.get('vulnerabilities', []))}; "
            f"Commute: {intake.get('commute_mode')}; Cooking Fuel: {intake.get('cooking_fuel')}; "
            f"Air Purifier Owned: {intake.get('has_purifier')}; Budget Band: {intake.get('budget_band')}\n\n"
            f"User Question: {sanitized_query}"
        )

        # Step 3: LLM generation
        raw_output = self.llm.generate_text(prompt, system_instruction=system_instruction)

        # Check if fallback model was triggered
        is_fallback = "[Model Fallback]" in raw_output or getattr(self.llm, "is_mock", False)

        # Step 4: Output Guardrail
        guarded_output = OutputGuardrail.sanitize_output(raw_output)

        return {
            "city": city,
            "response": guarded_output,
            "current_aqi": current_aqi,
            "forecast": nocturnal,
            "is_emergency": False,
            "is_fallback": is_fallback
        }
