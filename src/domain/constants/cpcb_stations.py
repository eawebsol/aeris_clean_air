"""
Comprehensive CPCB National Station Directory.
Enables true cascading filters: State -> City -> Station across all major Indian smog basins.
Sources: Central Pollution Control Board (CPCB) Continuous Ambient Air Quality Monitoring (CAAQM) Network.
"""

from typing import Dict, List, Any

# Cascading hierarchy: State -> City -> List of Stations
CPCB_STATIONS_HIERARCHY: Dict[str, Dict[str, List[str]]] = {
    "Delhi": {
        "Delhi-NCR": [
            "Alipur, Delhi - DPCC",
            "Anand Vihar, Delhi - DPCC",
            "Ashok Vihar, Delhi - DPCC",
            "Bawana, Delhi - DPCC",
            "Burari Crossing, Delhi - IMD",
            "Chandni Chowk, Delhi - IITM",
            "Dwarka-Sector 8, Delhi - DPCC",
            "IGI Airport (T3), Delhi - IMD",
            "ITO, Delhi - CPCB",
            "Jahangirpuri, Delhi - DPCC",
            "Lodhi Road, Delhi - IITM",
            "Major Dhyan Chand National Stadium, Delhi - DPCC",
            "Mandir Marg, Delhi - DPCC",
            "Mundka, Delhi - DPCC",
            "Narela, Delhi - DPCC",
            "Okhla Phase-2, Delhi - DPCC",
            "Patparganj, Delhi - DPCC",
            "Punjabi Bagh, Delhi - DPCC",
            "Pusa, Delhi - DPCC",
            "R K Puram, Delhi - DPCC",
            "Rohini, Delhi - DPCC",
            "Shadipur, Delhi - CPCB",
            "Sirifort, Delhi - CPCB",
            "Sonia Vihar, Delhi - DPCC",
            "Vivek Vihar, Delhi - DPCC",
            "Wazirpur, Delhi - DPCC"
        ]
    },
    "Bihar": {
        "Patna": [
            "DRM Office Danapur, Patna - BSPCB",
            "Govt. High School Shikarpur, Patna - BSPCB",
            "Muradpur, Patna - BSPCB",
            "Rajbansi Nagar, Patna - BSPCB",
            "Samanpura, Patna - BSPCB",
            "Planetarium Complex, Patna - BSPCB"
        ],
        "Gaya": [
            "Collectorate, Gaya - BSPCB",
            "Bodhigram, Gaya - BSPCB"
        ],
        "Muzaffarpur": [
            "Muzaffarpur Collectorate - BSPCB",
            "MIT Muzaffarpur - BSPCB"
        ]
    },
    "West Bengal": {
        "Kolkata": [
            "Victoria Memorial, Kolkata - WBPCB",
            "Rabindra Bharati University, Kolkata - WBPCB",
            "Ballygunge, Kolkata - WBPCB",
            "Jadavpur, Kolkata - WBPCB",
            "Fort William, Kolkata - WBPCB"
        ],
        "Howrah": [
            "Ghusuri, Howrah - WBPCB",
            "Padmapukur, Howrah - WBPCB"
        ]
    },
    "Uttar Pradesh": {
        "Noida": [
            "Sector-62, Noida - UPPCB",
            "Sector-1, Noida - UPPCB",
            "Sector-116, Noida - UPPCB",
            "Sector-125, Noida - UPPCB"
        ],
        "Ghaziabad": [
            "Indirapuram, Ghaziabad - UPPCB",
            "Loni, Ghaziabad - UPPCB",
            "Sanjay Nagar, Ghaziabad - UPPCB",
            "Vasundhara, Ghaziabad - UPPCB"
        ],
        "Lucknow": [
            "Lalbagh, Lucknow - UPPCB",
            "Talkatora District Industries Center, Lucknow - UPPCB",
            "Kendriya Vidyalaya, Lucknow - CPCB"
        ],
        "Kanpur": [
            "Nehru Nagar, Kanpur - UPPCB",
            "NSIT Kalyanpur, Kanpur - UPPCB"
        ]
    },
    "Haryana": {
        "Gurugram": [
            "Vikas Sadan, Gurugram - HSPCB",
            "Sector-51, Gurugram - HSPCB",
            "Teri Gram, Gurugram - HSPCB",
            "Gwal Pahari, Gurugram - IMD"
        ],
        "Faridabad": [
            "Sector-11, Faridabad - HSPCB",
            "Sector-16A, Faridabad - HSPCB",
            "Sector-30, Faridabad - HSPCB"
        ]
    },
    "Maharashtra": {
        "Mumbai": [
            "Bandra, Mumbai - MPCB",
            "Colaba, Mumbai - MPCB",
            "Kurla, Mumbai - MPCB",
            "Worli, Mumbai - MPCB",
            "BKC, Mumbai - MPCB"
        ],
        "Pune": [
            "Shivajinagar, Pune - MPCB",
            "Katraj, Pune - MPCB",
            "Hadapsar, Pune - MPCB"
        ]
    }
}

# Station specific calibrated baselines
STATION_CALIBRATED_DATA: Dict[str, Dict[str, Any]] = {
    "Alipur, Delhi - DPCC": {"aqi": 428, "pm25": 285.4, "pm10": 442.0, "temp": 7.5, "wind": 2.2, "humidity": 88},
    "Anand Vihar, Delhi - DPCC": {"aqi": 465, "pm25": 340.2, "pm10": 490.0, "temp": 7.0, "wind": 1.8, "humidity": 92},
    "Bawana, Delhi - DPCC": {"aqi": 445, "pm25": 310.0, "pm10": 460.0, "temp": 6.8, "wind": 1.9, "humidity": 90},
    "ITO, Delhi - CPCB": {"aqi": 415, "pm25": 270.0, "pm10": 410.0, "temp": 8.0, "wind": 2.5, "humidity": 85},
    "R K Puram, Delhi - DPCC": {"aqi": 420, "pm25": 280.0, "pm10": 430.0, "temp": 7.6, "wind": 2.1, "humidity": 87},
    "DRM Office Danapur, Patna - BSPCB": {"aqi": 395, "pm25": 242.0, "pm10": 380.0, "temp": 9.0, "wind": 3.1, "humidity": 84},
    "Victoria Memorial, Kolkata - WBPCB": {"aqi": 312, "pm25": 165.0, "pm10": 270.0, "temp": 13.5, "wind": 4.5, "humidity": 76},
    "Sector-62, Noida - UPPCB": {"aqi": 435, "pm25": 298.0, "pm10": 450.0, "temp": 7.2, "wind": 2.0, "humidity": 89},
    "Indirapuram, Ghaziabad - UPPCB": {"aqi": 452, "pm25": 325.0, "pm10": 475.0, "temp": 6.9, "wind": 1.7, "humidity": 91},
    "Vikas Sadan, Gurugram - HSPCB": {"aqi": 418, "pm25": 275.0, "pm10": 425.0, "temp": 7.8, "wind": 2.3, "humidity": 86},
    "Bandra, Mumbai - MPCB": {"aqi": 185, "pm25": 78.0, "pm10": 135.0, "temp": 22.0, "wind": 8.5, "humidity": 68},
    "NSIT Kalyanpur, Kanpur - UPPCB": {"aqi": 114, "pm25": 48.0, "pm10": 114.0, "temp": 16.5, "wind": 4.8, "humidity": 62},
    "Nehru Nagar, Kanpur - UPPCB": {"aqi": 117, "pm25": 52.0, "pm10": 117.0, "temp": 16.2, "wind": 4.5, "humidity": 64},
    "Lalbagh, Lucknow - UPPCB": {"aqi": 285, "pm25": 145.0, "pm10": 260.0, "temp": 14.0, "wind": 3.8, "humidity": 72}
}
