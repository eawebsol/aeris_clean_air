import unittest
import concurrent.futures
import time
from src.adapters.telemetry.hybrid_adapter import HybridAirQualityAdapter
from src.adapters.llm.adapters import MockLLMAdapter
from src.orchestration.orchestrator import SmogAssistantOrchestrator
from src.domain.services.physics_service import InversionPhysicsService, IAQService, ImpactCalculatorService

class TestConcurrency(unittest.TestCase):
    def setUp(self):
        self.adapter = HybridAirQualityAdapter(waqi_token="", datagov_api_key="")
        self.orchestrator = SmogAssistantOrchestrator(
            llm_adapter=MockLLMAdapter(),
            telemetry_adapter=self.adapter
        )

    def test_concurrent_orchestrator_queries(self):
        """Concurrency Test: Run 50 concurrent simulated queries across multiple threads."""
        queries = [
            ("What should my family do tomorrow morning?", "Delhi-NCR"),
            ("How to make a DIY Corsi-Rosenthal box for 400 sqft?", "Patna"),
            ("Should we commute by metro or petrol car?", "Kanpur"),
            ("Severe asthma emergency advice", "Delhi-NCR"),
            ("Calculate WFH impact for 30 km commute", "Kolkata")
        ] * 10  # 50 total queries

        def execute_query(q_tuple):
            q, city = q_tuple
            start_t = time.perf_counter()
            res = self.orchestrator.handle_query(
                user_query=q,
                city=city,
                intake_context={"vulnerabilities": ["Children / Infants"], "commute_mode": "petrol_car"}
            )
            elapsed = time.perf_counter() - start_t
            return res, elapsed

        # Execute 50 concurrent workers
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(execute_query, q) for q in queries]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        self.assertEqual(len(results), 50)
        latencies = [r[1] for r in results]
        p95_latency = sorted(latencies)[int(0.95 * len(latencies))]

        print(f"\n[Concurrency Test] 50 Requests executed successfully.")
        print(f"Max Latency: {max(latencies)*1000:.2f} ms | p95 Latency: {p95_latency*1000:.2f} ms | Min Latency: {min(latencies)*1000:.2f} ms")
        self.assertLess(p95_latency, 0.5, "p95 latency should remain under 500ms for concurrent queries")

    def test_concurrent_physics_computations(self):
        """Concurrency Test: Run 200 parallel physics model evaluations."""
        def run_physics_batch(i):
            temp = 4.0 + (i % 20)
            wind = 0.5 + (i % 15) * 0.5
            hum = 50.0 + (i % 45)
            f = InversionPhysicsService.assess_inversion_risk(temp, wind, hum)
            iaq = IAQService.calculate_diy_purifier(room_sqft=100 + i * 2)
            wfh = ImpactCalculatorService.calculate_wfh_impact(commute_km_roundtrip=10.0 + i, commute_mode="petrol_car")
            return f, iaq, wfh

        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            futures = [executor.submit(run_physics_batch, i) for i in range(200)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        self.assertEqual(len(results), 200)

if __name__ == '__main__':
    unittest.main()
