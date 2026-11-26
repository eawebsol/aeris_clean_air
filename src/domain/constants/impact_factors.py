"""
Attributed Environmental, Health, and Economic Impact Factors.
Every figure comes with a named scientific source and a one-line assumption.
All outputs derived from these constants are labeled as estimates.
"""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class ImpactFactor:
    value: float
    unit: str
    source: str
    assumption: str

# 1. Transport & Commute Emissions (Including EVs & Rush-Hour Traffic Density)
# Sources: CPCB, IIT Kanpur Comprehensive Air Quality Study, BEE, and DMRC
EMISSION_FACTORS = {
    "electric_vehicle_car_pm25_per_km": ImpactFactor(
        value=0.0,
        unit="g/km",
        source="Central Pollution Control Board (CPCB) Zero Tailpipe Baseline",
        assumption="Private Electric Vehicle (EV) produces zero street-level tailpipe exhaust"
    ),
    "electric_vehicle_car_co2_per_km": ImpactFactor(
        value=52.0,
        unit="g/km",
        source="CEA India Grid Emission Factor (Indirect Generation)",
        assumption="Battery EV charged from national grid averaging 0.71 kg CO2/kWh at 7.3 km/kWh efficiency"
    ),
    "petrol_car_pm25_per_km": ImpactFactor(
        value=0.035,
        unit="g/km",
        source="CPCB Vehicular Emission Load Guidelines",
        assumption="Tailpipe exhaust for BS-IV/BS-VI private petrol four-wheeler in urban stop-and-go traffic"
    ),
    "petrol_car_co2_per_km": ImpactFactor(
        value=170.0,
        unit="g/km",
        source="ICCT India Light-Duty Vehicle Fuel Economy Study",
        assumption="Average city fuel efficiency of 13.5 km/l under congested winter conditions"
    ),
    "diesel_car_pm25_per_km": ImpactFactor(
        value=0.085,
        unit="g/km",
        source="CPCB / Automotive Research Association of India (ARAI)",
        assumption="Older BS-IV urban diesel passenger vehicle without DPF regeneration in stop-and-go traffic"
    ),
    "diesel_car_co2_per_km": ImpactFactor(
        value=195.0,
        unit="g/km",
        source="ICCT India Passenger Transport Study",
        assumption="Average urban diesel consumption in stop-and-go rush-hour traffic"
    ),
    "two_wheeler_pm25_per_km": ImpactFactor(
        value=0.045,
        unit="g/km",
        source="CPCB Air Quality Assessment in Indian Cities",
        assumption="Four-stroke 100-150cc commuter motorcycle/scooter tailpipe exhaust"
    ),
    "two_wheeler_co2_per_km": ImpactFactor(
        value=48.0,
        unit="g/km",
        source="BEE Fuel Economy Baseline for Indian 2-Wheelers",
        assumption="Average city mileage of 45-50 km/l"
    ),
    "road_dust_resuspension_pm25_per_km": ImpactFactor(
        value=0.18,
        unit="g/km",
        source="IIT Kanpur Comprehensive Air Quality Study (Delhi-NCR)",
        assumption="Paved road dust resuspension triggered per vehicle kilometer traveled in dry winter conditions"
    ),
    "electric_metro_pm25_per_km": ImpactFactor(
        value=0.0,
        unit="g/km",
        source="Delhi Metro Rail Corporation (DMRC) Environmental Footprint",
        assumption="Zero tailpipe emissions at street-level breathing height"
    ),
    "electric_metro_co2_per_km": ImpactFactor(
        value=18.5,
        unit="g/km",
        source="Central Electricity Authority (CEA) Grid Emission Factor",
        assumption="Grid-averaged indirect emissions per passenger kilometer traveled on rapid transit"
    )
}

# 2. Rush-Hour Traffic Density & Corridors (IIT Kanpur / CRRI Model)
TRAFFIC_CORRIDOR_FACTORS = {
    "peak_hour_vehicle_density_per_km": ImpactFactor(
        value=3200.0,
        unit="vehicles/hour/arterial_corridor",
        source="Central Road Research Institute (CRRI) Delhi Arterial Road Study",
        assumption="Average peak morning rush-hour volume on major arterials (e.g. Ring Road, Outer Ring Road)"
    ),
    "wfh_corridor_pm25_reduction_pct_per_10k_wfh": ImpactFactor(
        value=6.8,
        unit="%",
        source="IIT Delhi Urban Mobility & Winter Inversion Stagnation Study",
        assumption="Estimated drop in micro-corridor tailpipe concentration per 10,000 tech/office workers shifting to WFH"
    ),
    "municipal_smog_mitigation_cost_per_kg_pm25_inr": ImpactFactor(
        value=4200.0,
        unit="INR/kg PM2.5",
        source="CAQM Emergency Anti-Smog Gun & Mechanical Sweeping Budget Allocation",
        assumption="Municipal cost of deployment for water-cannons, misting sprays, and mechanized dust sweepers per kg PM2.5 suppressed"
    )
}

# 3. Sustainable Building Materials: Prevention vs. Conventional Brick Kilns
SUSTAINABLE_MATERIAL_FACTORS = {
    "red_clay_brick_kiln_pm25_per_sqft": ImpactFactor(
        value=38.0,
        unit="g PM2.5/sqft",
        source="CPCB Brick Kiln Emission Audit & CSE India Clean Brick Initiative",
        assumption="Traditional fixed-chimney bull's trench kiln burning low-grade coal/biomass per standard brick unit"
    ),
    "upcycled_soot_tile_pm25_sequestered_per_sqft": ImpactFactor(
        value=42.5,
        unit="g PM2.5/sqft",
        source="Carbon Craft Design / Technical Sequestration Audit",
        assumption="Captured industrial/diesel particulate carbon permanently bound inside hydraulic-pressed architectural tile"
    )
}

# 4. Indoor Air Quality & Filtration Economics (Grassroots Innovations & Lab Benchmarks)
IAQ_FACTORS = {
    "project_vayu_filter_cost_inr": ImpactFactor(
        value=140.0,
        unit="INR",
        source="Project Vayu (Krish Aggarwal & Samarth Meattle, Delhi Students / Diana Award 2026)",
        assumption="Electrostatic fan bonnet attaching to standard classroom/table fan; traps 90% PM2.5 in closed 200 sq ft room"
    ),
    "filtair_exhaust_cost_inr": ImpactFactor(
        value=2500.0,
        unit="INR",
        source="FiltAir (Aarkin Soni, Delhi Teen Innovation)",
        assumption="Cardboard enclosure + pre-filter + true HEPA filter powered by high-static exhaust fan"
    ),
    "diy_cadr_per_box_fan": ImpactFactor(
        value=240.0,
        unit="CFM",
        source="UC Davis / Corsi-Rosenthal Foundation Lab Sizing Tests",
        assumption="20-inch box fan running on medium speed with four 2-inch MERV-13 pleated filters"
    ),
    "commercial_hepa_cost_inr": ImpactFactor(
        value=16500.0,
        unit="INR",
        source="Consumer Market Pricing Benchmark (Delhi/Patna 2025-2026)",
        assumption="Retail price of branded HEPA room purifier for 300-350 sq ft coverage"
    ),
    "diy_box_fan_cost_inr": ImpactFactor(
        value=1450.0,
        unit="INR",
        source="IndiaMART / Local Hardware Wholesale Index (Delhi/Kolkata)",
        assumption="Standard 20-inch 3-speed domestic box or shroud fan"
    ),
    "diy_merv13_filters_cost_inr": ImpactFactor(
        value=1800.0,
        unit="INR",
        source="HVAC Filter Supply Pricing Benchmark",
        assumption="Set of four 20x20x1 or 20x20x2 inch MERV-13 / ISO ePM1 replacement pleats"
    ),
    "diy_tape_shroud_cost_inr": ImpactFactor(
        value=200.0,
        unit="INR",
        source="Local Hardware Estimate",
        assumption="One roll heavy-duty duct tape plus fan shipping box repurposed as base and shroud"
    )
}

# 5. Health & Economic Valuation
HEALTH_ECONOMIC_FACTORS = {
    "outpatient_cost_per_acute_respiratory_event_inr": ImpactFactor(
        value=1850.0,
        unit="INR",
        source="World Bank South Asia Air Quality Health Burden & AIIMS Cost Studies",
        assumption="Average out-of-pocket spend per acute winter bronchospasm (clinic visit + bronchodilator/oral meds + travel)"
    ),
    "who_pm25_24hr_limit": ImpactFactor(
        value=15.0,
        unit="ug/m3",
        source="WHO Global Air Quality Guidelines 2021 Update",
        assumption="Health-protective 24-hour mean concentration threshold to avoid severe respiratory inflammation"
    )
}
