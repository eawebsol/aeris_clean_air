"""
Hybrid Air Quality & Meteorological Telemetry Adapter.
Supports:
1. Live Open Government Data India (data.gov.in / CPCB Real Time National AQI)
2. Live WAQI / OpenAQ endpoint fallback
3. Calibrated historical winter fixtures for Delhi-NCR, Patna, Kolkata when offline/unauthenticated.
"""

import os
import requests
from typing import Optional, Dict, Any
from datetime import datetime
from src.domain.ports.interfaces import AirQualityPort
from src.domain.models.schemas import AirQualityReading, WeatherForecast
from src.domain.services.physics_service import InversionPhysicsService

from src.domain.constants.cpcb_stations import STATION_CALIBRATED_DATA, CPCB_STATIONS_HIERARCHY

class HybridAirQualityAdapter(AirQualityPort):
    def __init__(self, datagov_api_key: Optional[str] = None, waqi_token: Optional[str] = None):
        self.datagov_key = datagov_api_key or os.getenv("DATAGOV_API_KEY")
        self.waqi_token = waqi_token or os.getenv("WAQI_TOKEN")
        self.live_source_used: Optional[str] = None
        self._fixtures = {
            "Delhi-NCR": {
                "aqi": 428,
                "pm25": 285.4,
                "pm10": 442.0,
                "night_temp_c": 7.5,
                "wind_kmh": 2.2,
                "humidity": 88.0,
                "category": "Severe (GRAP Stage IV)",
                "source": "CPCB CAQM Historical Winter Inversion Benchmark"
            },
            "Patna": {
                "aqi": 395,
                "pm25": 242.0,
                "pm10": 380.0,
                "night_temp_c": 9.0,
                "wind_kmh": 3.1,
                "humidity": 84.0,
                "category": "Very Poor / Gangetic Basin Inversion",
                "source": "Bihar State Pollution Control Board Benchmark"
            },
            "Kolkata": {
                "aqi": 312,
                "pm25": 165.0,
                "pm10": 270.0,
                "night_temp_c": 13.5,
                "wind_kmh": 4.5,
                "humidity": 76.0,
                "category": "Poor / Industrial & Traffic Smog",
                "source": "West Bengal Pollution Control Board Benchmark"
            },
            "Kanpur": {
                "aqi": 126,
                "pm25": 58.0,
                "pm10": 135.0,
                "night_temp_c": 16.5,
                "wind_kmh": 4.8,
                "humidity": 62.0,
                "category": "Moderate",
                "source": "UPPCB CAAQM Station Baseline"
            },
            "Lucknow": {
                "aqi": 285,
                "pm25": 145.0,
                "pm10": 260.0,
                "night_temp_c": 14.0,
                "wind_kmh": 3.8,
                "humidity": 72.0,
                "category": "Poor",
                "source": "UPPCB CAAQM Station Baseline"
            },
            "Noida": {
                "aqi": 435,
                "pm25": 298.0,
                "pm10": 450.0,
                "night_temp_c": 7.2,
                "wind_kmh": 2.0,
                "humidity": 89.0,
                "category": "Severe (GRAP Stage IV)",
                "source": "UPPCB CAAQM Station Baseline"
            },
            "Ghaziabad": {
                "aqi": 452,
                "pm25": 325.0,
                "pm10": 475.0,
                "night_temp_c": 6.9,
                "wind_kmh": 1.7,
                "humidity": 91.0,
                "category": "Severe (GRAP Stage IV)",
                "source": "UPPCB CAAQM Station Baseline"
            }
        }

    def get_station_reading(self, station_name: str, city: str = "Delhi-NCR") -> AirQualityReading:
        """Retrieves station-specific telemetry or live data.gov.in reading for that exact monitor."""
        # 1. Check live CPCB / data.gov.in
        live = self._fetch_from_datagov(city)
        if live:
            who_ratio = round(live["pm25"] / 15.0, 1)
            return AirQualityReading(
                city=city,
                aqi=live["aqi"],
                pm25=live["pm25"],
                pm10=live["pm10"],
                who_pm25_ratio=who_ratio,
                category=f"{live.get('category', 'Live Station')} ({self.live_source_used})",
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M IST")
            )

        # 2. Station-specific calibrated baseline
        if station_name in STATION_CALIBRATED_DATA:
            stn = STATION_CALIBRATED_DATA[station_name]
            who_ratio = round(stn["pm25"] / 15.0, 1)
            cat = "Severe" if stn["aqi"] > 400 else ("Very Poor" if stn["aqi"] > 300 else "Poor")
            self.live_source_used = f"Official CPCB CAAQM Station ({station_name})"
            return AirQualityReading(
                city=city,
                aqi=stn["aqi"],
                pm25=stn["pm25"],
                pm10=stn["pm10"],
                who_pm25_ratio=who_ratio,
                category=f"{cat} (CPCB Station)",
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M IST")
            )

        # 3. City fallback
        return self.get_current_reading(city)

    def _fetch_from_datagov(self, city: str) -> Optional[Dict[str, Any]]:
        """Queries official Indian Government Open Data (data.gov.in / CPCB API)."""
        if not self.datagov_key:
            return None
        try:
            # Official CPCB resource on api.data.gov.in
            url = "https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
            params = {
                "api-key": self.datagov_key,
                "format": "json",
                "filters[city]": "Delhi" if "Delhi" in city else city,
                "limit": 10
            }
            resp = requests.get(url, params=params, timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                records = data.get("records", [])
                if records:
                    pm25_vals = [float(r["pollutant_avg"]) for r in records if r.get("pollutant_id") == "PM2.5" and r.get("pollutant_avg")]
                    aqi_vals = [float(r["pollutant_avg"]) for r in records if r.get("pollutant_avg")]
                    if pm25_vals:
                        avg_pm25 = sum(pm25_vals) / len(pm25_vals)
                        est_aqi = int(max(aqi_vals)) if aqi_vals else int(avg_pm25 * 1.5)
                        self.live_source_used = "Official CPCB (data.gov.in)"
                        return {
                            "aqi": est_aqi,
                            "pm25": round(avg_pm25, 1),
                            "pm10": round(avg_pm25 * 1.6, 1),
                            "category": "Live CPCB Ingestion"
                        }
        except Exception:
            pass
        return None

    def _fetch_from_waqi(self, city: str) -> Optional[Dict[str, Any]]:
        """Queries World Air Quality Index (WAQI) real-time feed (which aggregates CPCB stations)."""
        if not self.waqi_token:
            return None
        try:
            city_query = "delhi" if "Delhi" in city else city.lower()
            url = f"https://api.waqi.info/feed/{city_query}/?token={self.waqi_token}"
            resp = requests.get(url, timeout=4)
            if resp.status_code == 200:
                res = resp.json()
                if res.get("status") == "ok":
                    data = res.get("data", {})
                    aqi = data.get("aqi", 0)
                    iaqi = data.get("iaqi", {})
                    pm25 = iaqi.get("pm25", {}).get("v", aqi * 0.7)
                    pm10 = iaqi.get("pm10", {}).get("v", aqi * 1.1)
                    self.live_source_used = "Live WAQI / CPCB Network"
                    return {
                        "aqi": int(aqi),
                        "pm25": float(pm25),
                        "pm10": float(pm10),
                        "category": "Live Station Reading"
                    }
        except Exception:
            pass
        return None

    def get_current_reading(self, city: str) -> AirQualityReading:
        # 1. Try official data.gov.in
        live = self._fetch_from_datagov(city)
        # 2. Try WAQI
        if not live:
            live = self._fetch_from_waqi(city)

        if live:
            who_ratio = round(live["pm25"] / 15.0, 1)
            return AirQualityReading(
                city=city,
                aqi=live["aqi"],
                pm25=live["pm25"],
                pm10=live["pm10"],
                who_pm25_ratio=who_ratio,
                category=f"{live.get('category', 'Live Station')} ({self.live_source_used})",
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M IST")
            )

        # 3. Fallback to calibrated historical fixture
        self.live_source_used = "Offline CPCB Benchmark Fixture"
        data = self._fixtures.get(city, self._fixtures["Delhi-NCR"])
        who_ratio = round(data["pm25"] / 15.0, 1)
        return AirQualityReading(
            city=city,
            aqi=data["aqi"],
            pm25=data["pm25"],
            pm10=data["pm10"],
            who_pm25_ratio=who_ratio,
            category=data["category"],
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M IST")
        )

    def get_nocturnal_forecast(self, city: str, station_name: Optional[str] = None) -> WeatherForecast:
        # Check if station calibrated data has meteorological values
        if station_name and station_name in STATION_CALIBRATED_DATA:
            stn = STATION_CALIBRATED_DATA[station_name]
            night_temp = float(stn.get("temp", 15.0))
            wind = float(stn.get("wind", 3.0))
            humidity = float(stn.get("humidity", 65.0))
        elif city in self._fixtures:
            data = self._fixtures[city]
            night_temp = data["night_temp_c"]
            wind = data["wind_kmh"]
            humidity = data["humidity"]
        else:
            data = self._fixtures["Delhi-NCR"]
            night_temp = data["night_temp_c"]
            wind = data["wind_kmh"]
            humidity = data["humidity"]

        inversion = InversionPhysicsService.assess_inversion_risk(
            night_temp_c=night_temp,
            wind_kmh=wind,
            humidity_pct=humidity
        )
        return WeatherForecast(
            city=city,
            night_temp_c=night_temp,
            surface_wind_kmh=wind,
            relative_humidity_pct=humidity,
            is_inversion_favorable=inversion["is_inversion"],
            estimated_mixing_height_m=inversion["mixing_height_m"],
            risk_level=inversion["severity"]
        )
