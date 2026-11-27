import unittest
import os
from src.domain.constants.cpcb_stations import CPCB_STATIONS_HIERARCHY, STATION_CALIBRATED_DATA
from src.domain.services.physics_service import InversionPhysicsService, IAQService, ImpactCalculatorService
from src.adapters.telemetry.hybrid_adapter import HybridAirQualityAdapter
from src.adapters.llm.adapters import MockLLMAdapter
from src.orchestration.orchestrator import SmogAssistantOrchestrator

class TestRegression(unittest.TestCase):
    def test_station_hierarchy_integrity(self):
        """Regression: Verify all cities in CPCB_STATIONS_HIERARCHY have valid stations."""
        for state, cities in CPCB_STATIONS_HIERARCHY.items():
            self.assertTrue(len(cities) > 0, f"State {state} has no cities")
            for city, stations in cities.items():
                self.assertTrue(len(stations) > 0, f"City {city} has no stations")

    def test_calibrated_stations_data_consistency(self):
        """Regression: Ensure station calibration dictionary contains valid schema."""
        required_keys = {"aqi", "pm25", "pm10"}
        for stn_name, data in STATION_CALIBRATED_DATA.items():
            missing = required_keys - set(data.keys())
            self.assertEqual(len(missing), 0, f"Station {stn_name} missing fields: {missing}")
            self.assertGreater(data["aqi"], 0)
            self.assertGreater(data["pm25"], 0)

    def test_commute_modes_regression(self):
        """Regression: Compare all commute modes and verify ordering and calculation integrity."""
        modes = ImpactCalculatorService.compare_commute_modes(km=15.0)
        self.assertEqual(len(modes), 6)
        mode_names = [m.mode for m in modes]
        self.assertIn("Electric Metro / Bus (Dedicated Lane)", mode_names)
        self.assertIn("Private Petrol Car (Rush Hour)", mode_names)
        self.assertIn("Bicycle (Severe Smog Penalty)", mode_names)
        
        # Verify EV metro has zero tailpipe PM2.5 exhaust
        metro = next(m for m in modes if "Electric Metro" in m.mode)
        self.assertEqual(metro.pm25_exhaust_grams, 0.0)

    def test_room_mass_balance_simulator(self):
        """Regression: Verify mass-balance indoor simulator physical calculations."""
        sim = ImpactCalculatorService.simulate_room_mass_balance(outdoor_pm25=300.0)
        self.assertEqual(len(sim), 4)
        self.assertEqual(sim[0]["pm25"], 300.0)
        self.assertLess(sim[1]["pm25"], 300.0)
        self.assertLess(sim[2]["pm25"], sim[1]["pm25"])
        self.assertLess(sim[3]["pm25"], sim[2]["pm25"])

    def test_community_multiplier(self):
        """Regression: Verify RWA/society scale multiplier."""
        single = ImpactCalculatorService.calculate_wfh_impact(24.0, "petrol_car")
        multi = ImpactCalculatorService.calculate_community_multiplier(single, 100)
        self.assertEqual(multi["scale"], 100)
        self.assertGreater(multi["total_pm25_kg_averted"], 0)
        self.assertGreater(multi["total_co2_tons_avoided"], 0)

    def test_impact_ledger_all_vehicles(self):
        """Regression: Verify impact calculation for all vehicle modes."""
        for mode in ["petrol_car", "diesel_car", "two_wheeler", "electric_vehicle_car", "electric_metro"]:
            impact = ImpactCalculatorService.calculate_wfh_impact(24.0, mode)
            self.assertIn("pm25_averted_grams", impact)
            self.assertIn("co2_averted_kg", impact)
            self.assertIn("avoided_healthcare_cost_inr", impact)
            self.assertIn("municipal_taxpayer_savings_inr", impact)

    def test_boundary_layer_physics_regression(self):
        """Regression: Verify severe inversion calculation edge cases."""
        # Extreme cold, dead calm, high humidity (Fog/Smog conditions)
        extreme = InversionPhysicsService.assess_inversion_risk(night_temp_c=3.0, wind_kmh=0.5, humidity_pct=95.0)
        self.assertTrue(extreme["is_inversion"])
        self.assertLess(extreme["mixing_height_m"], 100)
        self.assertEqual(extreme["severity"], "Severe Inversion Trap")

        # Warm, windy day (Dispersive conditions)
        dispersive = InversionPhysicsService.assess_inversion_risk(night_temp_c=25.0, wind_kmh=18.0, humidity_pct=40.0)
        self.assertFalse(dispersive["is_inversion"])
        self.assertGreater(dispersive["mixing_height_m"], 300)
        self.assertEqual(dispersive["severity"], "Moderate / Open Dispersion")

if __name__ == '__main__':
    unittest.main()
