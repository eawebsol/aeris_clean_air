import unittest
import os
import sys

# Smoke tests to ensure all critical modules import and initialize without errors
class TestSmoke(unittest.TestCase):
    def test_imports_all_core_modules(self):
        """Smoke Test: Verify all primary packages and classes import cleanly."""
        try:
            from src.domain.models.schemas import AirQualityReading, WeatherForecast, IAQPlan
            from src.domain.constants.cpcb_stations import CPCB_STATIONS_HIERARCHY, STATION_CALIBRATED_DATA
            from src.domain.constants.impact_factors import EMISSION_FACTORS, IAQ_FACTORS
            from src.domain.services.physics_service import InversionPhysicsService, IAQService, ImpactCalculatorService
            from src.adapters.telemetry.hybrid_adapter import HybridAirQualityAdapter
            from src.adapters.llm.adapters import MockLLMAdapter, GeminiAdapter
            from src.guardrails.guardrails import InputGuardrail, OutputGuardrail
            from src.orchestration.orchestrator import SmogAssistantOrchestrator
        except Exception as e:
            self.fail(f"Smoke test import failed: {e}")

    def test_physics_service_smoke(self):
        """Smoke Test: Inversion, IAQ, and Impact calculations return expected bounds."""
        from src.domain.services.physics_service import InversionPhysicsService, IAQService, ImpactCalculatorService
        
        forecast = InversionPhysicsService.assess_inversion_risk(night_temp_c=6.0, wind_kmh=1.5, humidity_pct=88.0)
        self.assertTrue(forecast["is_inversion"])
        self.assertLess(forecast["mixing_height_m"], 100)

        iaq = IAQService.calculate_diy_purifier(room_sqft=300)
        self.assertGreater(iaq.cadr_required, 0)
        self.assertGreater(iaq.savings_inr, 0)

        impact = ImpactCalculatorService.calculate_wfh_impact(commute_km_roundtrip=24.0, commute_mode="petrol_car")
        self.assertGreater(impact['pm25_averted_grams'], 0)
        self.assertGreater(impact['co2_averted_kg'], 0)

    def test_orchestrator_smoke(self):
        """Smoke Test: Orchestrator initializes and handles a baseline query."""
        from src.adapters.telemetry.hybrid_adapter import HybridAirQualityAdapter
        from src.adapters.llm.adapters import MockLLMAdapter
        from src.orchestration.orchestrator import SmogAssistantOrchestrator

        adapter = HybridAirQualityAdapter(waqi_token="", datagov_api_key="")
        orchestrator = SmogAssistantOrchestrator(llm_adapter=MockLLMAdapter(), telemetry_adapter=adapter)
        res = orchestrator.handle_query("Daily routine advice", city="Delhi-NCR")
        self.assertIn("response", res)
        self.assertFalse(res["is_emergency"])

if __name__ == '__main__':
    unittest.main()
