import unittest
from src.adapters.telemetry.hybrid_adapter import HybridAirQualityAdapter
from src.adapters.llm.adapters import MockLLMAdapter
from src.orchestration.orchestrator import SmogAssistantOrchestrator

class TestZeroKeyFallback(unittest.TestCase):
    def test_mock_adapter_zero_crash(self):
        """Verify the entire application pipeline functions without any API keys or network."""
        # Force empty tokens
        adapter = HybridAirQualityAdapter(waqi_token="", datagov_api_key="")
        reading = adapter.get_current_reading("Kanpur")
        self.assertIsNotNone(reading)
        self.assertEqual(reading.city, "Kanpur")
        self.assertGreater(reading.aqi, 0)

        # Verify fallback station reading
        station_reading = adapter.get_station_reading("NSIT Kalyanpur, Kanpur - UPPCB", city="Kanpur")
        self.assertIsNotNone(station_reading)
        self.assertEqual(station_reading.city, "Kanpur")
        self.assertGreater(station_reading.aqi, 0)

        # Verify end-to-end orchestration with MockLLMAdapter
        orchestrator = SmogAssistantOrchestrator(
            llm_adapter=MockLLMAdapter(),
            telemetry_adapter=adapter
        )
        intake = {
            "vulnerabilities": ["Children / Infants"],
            "commute_mode": "petrol_car",
            "has_purifier": False
        }
        response = orchestrator.handle_query(
            user_query="Should my child go to school tomorrow?",
            city="Kanpur",
            intake_context=intake
        )
        self.assertIsNotNone(response)
        self.assertIn("response", response)
        advisory_text = response["response"]
        self.assertIn("WHAT TO DO TODAY", advisory_text.upper())
        self.assertIn("INDOOR AIR QUALITY", advisory_text.upper())
        self.assertIn("SUSTAINABLE ALTERNATIVE", advisory_text.upper())
        self.assertIn("ESTIMATED", advisory_text.upper())
        self.assertIn("WHO 2021", advisory_text)

if __name__ == '__main__':
    unittest.main()
