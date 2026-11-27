"""
Vector Landmark Silhouettes for Indian States & Major Cities.
Provides lightweight, zero-dependency, ultra-crisp SVG architectural watermarks
modeled after famous heritage monuments (India Gate, Charminar, Gateway of India,
Vidhana Soudha, Victoria Memorial, Hawa Mahal, Taj Mahal, etc.)
Emitted as translucent silhouettes in the Hero AQI Card.
"""

from typing import Dict, Tuple
import base64
from pathlib import Path

LANDMARKS_DIR = Path(__file__).resolve().parent.parent.parent / "ui" / "assets" / "landmarks"

# Maps State or City -> PNG filename in src/ui/assets/landmarks/
LANDMARK_PNG_MAP: Dict[str, Tuple[str, str]] = {
    "Delhi": ("delhi.png", "India Gate & Red Fort"),
    "Delhi-NCR": ("delhi.png", "India Gate & Red Fort"),
    "Telangana": ("hyderabad.png", "Charminar, Hyderabad"),
    "Hyderabad": ("hyderabad.png", "Charminar, Hyderabad"),
    "Karnataka": ("bengaluru.png", "Vidhana Soudha, Bengaluru"),
    "Bengaluru": ("bengaluru.png", "Vidhana Soudha, Bengaluru"),
    "Mysuru": ("bengaluru.png", "Vidhana Soudha & Mysore Palace"),
    "Maharashtra": ("mumbai.png", "Gateway of India, Mumbai"),
    "Mumbai": ("mumbai.png", "Gateway of India, Mumbai"),
    "Pune": ("mumbai.png", "Gateway of India & Shaniwar Wada"),
    "Navi Mumbai": ("mumbai.png", "Gateway of India, Mumbai"),
    "Thane": ("mumbai.png", "Gateway of India, Mumbai"),
    "Uttar Pradesh": ("uttar_pradesh.png", "Taj Mahal, Uttar Pradesh"),
    "Noida": ("uttar_pradesh.png", "Taj Mahal, Uttar Pradesh"),
    "Ghaziabad": ("uttar_pradesh.png", "Taj Mahal, Uttar Pradesh"),
    "Lucknow": ("uttar_pradesh.png", "Taj Mahal & Rumi Darwaza"),
    "Kanpur": ("uttar_pradesh.png", "Taj Mahal, Uttar Pradesh"),
    "Agra": ("uttar_pradesh.png", "Taj Mahal, Agra"),
    "Varanasi": ("uttar_pradesh.png", "Taj Mahal & Varanasi Ghats"),
    "West Bengal": ("kolkata.png", "Victoria Memorial & Howrah Bridge"),
    "Kolkata": ("kolkata.png", "Victoria Memorial & Howrah Bridge"),
    "Howrah": ("kolkata.png", "Victoria Memorial & Howrah Bridge"),
    "Tamil Nadu": ("chennai.png", "Dravidian Temple Gopuram, Tamil Nadu"),
    "Chennai": ("chennai.png", "Dravidian Temple Gopuram, Chennai"),
    "Coimbatore": ("chennai.png", "Dravidian Temple Gopuram, Tamil Nadu"),
    "Madurai": ("chennai.png", "Meenakshi Temple Gopuram, Madurai"),
    "Rajasthan": ("jaipur.png", "Hawa Mahal, Jaipur"),
    "Jaipur": ("jaipur.png", "Hawa Mahal, Jaipur"),
    "Udaipur": ("jaipur.png", "Hawa Mahal & City Palace, Rajasthan"),
    "Jodhpur": ("jaipur.png", "Hawa Mahal & Mehrangarh, Rajasthan"),
    "Bihar": ("bihar.png", "Golghar & Mahabodhi Stupa, Bihar"),
    "Patna": ("bihar.png", "Golghar, Patna"),
    "Gaya": ("bihar.png", "Mahabodhi Temple, Gaya"),
    "Gujarat": ("gujarat.png", "Adalaj Stepwell & Sidi Saiyyed, Gujarat"),
    "Ahmedabad": ("gujarat.png", "Sidi Saiyyed & Stepwell, Ahmedabad"),
    "Surat": ("gujarat.png", "Adalaj Stepwell & Heritage, Gujarat"),
    "Vadodara": ("gujarat.png", "Laxmi Vilas & Stepwell, Gujarat"),
    "Punjab": ("punjab.png", "Golden Temple, Punjab"),
    "Amritsar": ("punjab.png", "Golden Temple, Amritsar"),
    "Ludhiana": ("punjab.png", "Golden Temple, Punjab"),
    "Jalandhar": ("punjab.png", "Golden Temple, Punjab"),
    "Patiala": ("punjab.png", "Golden Temple & Qila Mubarak, Punjab"),
    "Chandigarh (UT)": ("punjab.png", "Open Hand Monument, Chandigarh"),
    "Chandigarh": ("punjab.png", "Open Hand Monument, Chandigarh"),
    "Haryana": ("delhi.png", "NCR Heritage Skyline, Haryana"),
    "Gurugram": ("delhi.png", "Delhi-NCR Skyline, Gurugram"),
    "Faridabad": ("delhi.png", "Delhi-NCR Skyline, Faridabad"),
    "Madhya Pradesh": ("national_default.png", "Sanchi Stupa & Heritage, Madhya Pradesh"),
    "Bhopal": ("national_default.png", "Sanchi Stupa & Heritage, Bhopal"),
    "Indore": ("national_default.png", "Rajwada & Heritage Skyline, Indore"),
    "Odisha": ("national_default.png", "Konark & Kalinga Heritage, Odisha"),
    "Bhubaneswar": ("national_default.png", "Lingaraj & Kalinga Heritage, Bhubaneswar"),
    "Assam": ("national_default.png", "Kamakhya & Brahmaputra Heritage, Assam"),
    "Guwahati": ("national_default.png", "Kamakhya & Brahmaputra Heritage, Guwahati"),
    "Kerala": ("national_default.png", "Malabar Coastal Heritage, Kerala"),
    "Jammu & Kashmir": ("national_default.png", "Himalayan Heritage Skyline, J&K"),
}

# Maps (State or City) -> (Landmark Name, SVG Path Data, viewBox width, height)
# All silhouettes are drawn as filled monochromatic vector contours with bottom alignment
LANDMARK_CATALOG: Dict[str, Tuple[str, str, int, int]] = {
    # Delhi: India Gate + Red Fort battlements
    "Delhi": (
        "India Gate & Red Fort",
        "M0 120 L0 110 L15 110 L15 105 L25 105 L25 110 L40 110 L40 90 L50 90 L50 110 L70 110 "
        "L70 45 L65 45 L65 40 L75 35 L85 35 L85 20 L95 20 L95 10 L105 10 L105 20 L115 20 L115 35 "
        "L125 35 L135 40 L135 45 L130 45 L130 110 L150 110 L150 90 L160 90 L160 110 L175 110 L175 105 "
        "L185 105 L185 110 L200 110 L200 120 Z "
        "M85 110 L85 70 Q100 55 115 70 L115 110 Z",
        200, 120
    ),
    # Telangana / Hyderabad: Charminar (4 minarets with grand arches)
    "Telangana": (
        "Charminar, Hyderabad",
        "M10 120 L10 25 L16 15 L22 25 L22 45 L32 45 L32 55 L42 55 L42 35 L50 35 L50 120 "
        "M150 120 L150 35 L158 35 L158 55 L168 55 L168 45 L178 45 L178 25 L184 15 L190 25 L190 120 "
        "M42 45 L158 45 L158 50 L42 50 Z "
        "M50 120 L50 85 Q100 45 150 85 L150 120 Z "
        "M75 45 L75 25 Q100 10 125 25 L125 45 Z",
        200, 120
    ),
    "Hyderabad": (
        "Charminar, Hyderabad",
        "M10 120 L10 25 L16 15 L22 25 L22 45 L32 45 L32 55 L42 55 L42 35 L50 35 L50 120 "
        "M150 120 L150 35 L158 35 L158 55 L168 55 L168 45 L178 45 L178 25 L184 15 L190 25 L190 120 "
        "M42 45 L158 45 L158 50 L42 50 Z "
        "M50 120 L50 85 Q100 45 150 85 L150 120 Z "
        "M75 45 L75 25 Q100 10 125 25 L125 45 Z",
        200, 120
    ),
    # Maharashtra / Mumbai: Gateway of India
    "Maharashtra": (
        "Gateway of India, Mumbai",
        "M15 120 L15 65 L25 50 L35 50 L35 65 L45 65 L45 35 L55 35 L55 120 "
        "M145 120 L145 35 L155 35 L155 65 L165 65 L165 50 L175 50 L185 65 L185 120 "
        "M45 40 L155 40 L155 46 L45 46 Z "
        "M55 120 L55 80 Q100 48 145 80 L145 120 Z "
        "M80 40 L80 20 Q100 12 120 20 L120 40 Z",
        200, 120
    ),
    "Mumbai": (
        "Gateway of India, Mumbai",
        "M15 120 L15 65 L25 50 L35 50 L35 65 L45 65 L45 35 L55 35 L55 120 "
        "M145 120 L145 35 L155 35 L155 65 L165 65 L165 50 L175 50 L185 65 L185 120 "
        "M45 40 L155 40 L155 46 L45 46 Z "
        "M55 120 L55 80 Q100 48 145 80 L145 120 Z "
        "M80 40 L80 20 Q100 12 120 20 L120 40 Z",
        200, 120
    ),
    # Karnataka / Bengaluru: Vidhana Soudha central dome & columns
    "Karnataka": (
        "Vidhana Soudha, Bengaluru",
        "M0 120 L0 80 L30 80 L30 90 L50 90 L50 80 L70 80 L70 50 L85 50 L85 30 Q100 12 115 30 L115 50 "
        "L130 50 L130 80 L150 80 L150 90 L170 90 L170 80 L200 80 L200 120 Z "
        "M92 30 L92 18 L108 18 L108 30 Z M98 18 L98 6 L102 6 L102 18 Z",
        200, 120
    ),
    "Bengaluru": (
        "Vidhana Soudha, Bengaluru",
        "M0 120 L0 80 L30 80 L30 90 L50 90 L50 80 L70 80 L70 50 L85 50 L85 30 Q100 12 115 30 L115 50 "
        "L130 50 L130 80 L150 80 L150 90 L170 90 L170 80 L200 80 L200 120 Z "
        "M92 30 L92 18 L108 18 L108 30 Z M98 18 L98 6 L102 6 L102 18 Z",
        200, 120
    ),
    # Uttar Pradesh / Agra / Lucknow: Taj Mahal dome & minarets
    "Uttar Pradesh": (
        "Taj Mahal, Agra",
        "M15 120 L18 35 L22 25 L26 35 L29 120 M171 120 L174 35 L178 25 L182 35 L185 120 "
        "M45 120 L45 70 L65 70 L65 60 Q100 15 135 60 L135 70 L155 70 L155 120 Z "
        "M97 25 L97 10 L103 10 L103 25 Z "
        "M75 120 L75 85 Q100 60 125 85 L125 120 Z",
        200, 120
    ),
    # West Bengal / Kolkata: Victoria Memorial & Howrah Bridge
    "West Bengal": (
        "Victoria Memorial, Kolkata",
        "M10 120 L10 90 L35 90 L35 70 Q50 50 65 70 L65 90 L75 90 L75 60 Q100 20 125 60 L125 90 "
        "L135 90 L135 70 Q150 50 165 70 L165 90 L190 90 L190 120 Z "
        "M96 30 L96 15 L104 15 L104 30 Z",
        200, 120
    ),
    "Kolkata": (
        "Victoria Memorial, Kolkata",
        "M10 120 L10 90 L35 90 L35 70 Q50 50 65 70 L65 90 L75 90 L75 60 Q100 20 125 60 L125 90 "
        "L135 90 L135 70 Q150 50 165 70 L165 90 L190 90 L190 120 Z "
        "M96 30 L96 15 L104 15 L104 30 Z",
        200, 120
    ),
    # Tamil Nadu / Chennai: Shore Temple & Dravidian Gopuram
    "Tamil Nadu": (
        "Dravidian Gopuram, Tamil Nadu",
        "M25 120 L50 120 L60 100 L68 82 L74 65 L78 50 L82 35 L86 20 L114 20 L118 35 L122 50 "
        "L126 65 L132 82 L140 100 L150 120 L175 120 Z "
        "M88 20 Q100 8 112 20 Z "
        "M85 120 L85 95 Q100 82 115 95 L115 120 Z",
        200, 120
    ),
    "Chennai": (
        "Dravidian Gopuram, Tamil Nadu",
        "M25 120 L50 120 L60 100 L68 82 L74 65 L78 50 L82 35 L86 20 L114 20 L118 35 L122 50 "
        "L126 65 L132 82 L140 100 L150 120 L175 120 Z "
        "M88 20 Q100 8 112 20 Z "
        "M85 120 L85 95 Q100 82 115 95 L115 120 Z",
        200, 120
    ),
    # Rajasthan / Jaipur: Hawa Mahal jharokhas
    "Rajasthan": (
        "Hawa Mahal, Jaipur",
        "M20 120 L35 120 L38 95 L48 95 L50 75 L62 75 L65 55 L78 55 L82 35 L90 35 L90 20 "
        "L110 20 L110 35 L118 35 L122 55 L135 55 L138 75 L150 75 L152 95 L162 95 L165 120 L180 120 Z "
        "M96 20 Q100 8 104 20 Z",
        200, 120
    ),
    "Jaipur": (
        "Hawa Mahal, Jaipur",
        "M20 120 L35 120 L38 95 L48 95 L50 75 L62 75 L65 55 L78 55 L82 35 L90 35 L90 20 "
        "L110 20 L110 35 L118 35 L122 55 L135 55 L138 75 L150 75 L152 95 L162 95 L165 120 L180 120 Z "
        "M96 20 Q100 8 104 20 Z",
        200, 120
    ),
    # Bihar / Patna: Golghar granary dome
    "Bihar": (
        "Golghar, Patna",
        "M20 120 L35 120 Q100 25 165 120 L180 120 Z "
        "M94 36 L94 22 L106 22 L106 36 Z M97 22 L100 12 L103 22 Z",
        200, 120
    ),
    # Gujarat / Ahmedabad: Sidi Saiyyed & Adalaj stepwell arches
    "Gujarat": (
        "Adalaj Stepwell Arches, Gujarat",
        "M15 120 L15 65 L40 65 L40 120 M40 65 L40 45 L75 45 L75 120 M75 45 L75 30 L125 30 L125 120 "
        "M125 45 L125 120 M125 45 L160 45 L160 120 M160 65 L160 120 M160 65 L185 65 L185 120 "
        "M85 120 L85 60 Q100 40 115 60 L115 120 Z",
        200, 120
    ),
    # Punjab / Chandigarh: Golden Temple & Open Hand
    "Punjab": (
        "Golden Temple & Open Hand, Punjab",
        "M20 120 L20 85 L45 85 L45 65 Q60 50 75 65 L75 85 L85 85 L85 55 Q100 25 115 55 L115 85 "
        "L125 85 L125 65 Q140 50 155 65 L155 85 L180 85 L180 120 Z M97 35 L97 18 L103 18 L103 35 Z",
        200, 120
    ),
    "Chandigarh (UT)": (
        "Open Hand Monument, Chandigarh",
        "M50 120 L50 80 L75 80 L75 50 L85 50 L85 25 L95 25 L95 10 L105 10 L105 25 L115 25 L115 50 "
        "L125 50 L125 80 L150 80 L150 120 Z",
        200, 120
    ),
    # Default National Monument (Ashoka Stambh / Sarnath Lions & Gateway)
    "National": (
        "National Heritage Monument",
        "M30 120 L30 85 L50 85 L50 65 L70 65 L70 45 L85 45 L85 25 L95 25 L95 10 L105 10 L105 25 "
        "L115 25 L115 45 L130 45 L130 65 L150 65 L150 85 L170 85 L170 120 Z "
        "M85 120 L85 75 Q100 60 115 75 L115 120 Z",
        200, 120
    )
}


def get_landmark_svg(state: str, city: str, is_dark: bool = False, opacity: float = 0.16) -> str:
    """
    Returns an image or SVG watermark snippet positioned in the background of the hero card.
    Checks src/ui/assets/landmarks/ for a custom PNG first (e.g., delhi.png), falling back to SVG.
    """
    png_file, png_label = LANDMARK_PNG_MAP.get(
        city,
        LANDMARK_PNG_MAP.get(state, ("national_default.png", "National Heritage Monument"))
    )
    png_path = LANDMARKS_DIR / png_file

    if png_path.exists():
        b64_data = base64.b64encode(png_path.read_bytes()).decode("ascii")
        # White silhouette PNG: keep white on dark Severe card, invert to dark slate on light pastel cards
        img_filter = "none" if is_dark else "invert(1) brightness(0.15)"
        img_opacity = 0.22 if is_dark else 0.11

        return (
            f'<div class="landmark-watermark" style="position:absolute; left:18%; right:30%; bottom:0; '
            f'height:185px; pointer-events:none; z-index:0; overflow:hidden; display:flex; '
            f'align-items:flex-end; justify-content:center;">'
            f'<img src="data:image/png;base64,{b64_data}" alt="{png_label}" '
            f'style="max-height:100%; max-width:100%; width:auto; height:auto; object-fit:contain; '
            f'object-position:bottom center; opacity:{img_opacity}; filter:{img_filter};" />'
            f'</div>'
            f'<div style="position:absolute; right:18px; bottom:6px; font-size:0.66rem; font-weight:800; '
            f'letter-spacing:0.04em; text-transform:uppercase; color:{"rgba(255,255,255,0.55)" if is_dark else "rgba(15,23,42,0.42)"}; '
            f'pointer-events:none; z-index:1;">'
            f'🏛️ {png_label}'
            f'</div>'
        )

    key = city if city in LANDMARK_CATALOG else (state if state in LANDMARK_CATALOG else "National")
    landmark_name, path_data, vb_w, vb_h = LANDMARK_CATALOG[key]

    fill_color = "#ffffff" if is_dark else "#0f172a"
    effective_opacity = 0.22 if is_dark else 0.13

    svg_markup = (
        f'<div class="landmark-watermark" style="position:absolute; left:22%; right:32%; bottom:0; height:145px; '
        f'pointer-events:none; z-index:0; overflow:hidden; display:flex; '
        f'align-items:flex-end; justify-content:center;">'
        f'<svg viewBox="0 0 {vb_w} {vb_h}" preserveAspectRatio="xMidYMax meet" '
        f'style="height:100%; width:100%; fill:{fill_color}; opacity:{effective_opacity};">'
        f'<title>{landmark_name}</title>'
        f'<path d="{path_data}" />'
        f'</svg>'
        f'</div>'
        f'<div style="position:absolute; right:18px; bottom:6px; font-size:0.66rem; font-weight:800; '
        f'letter-spacing:0.04em; text-transform:uppercase; color:{"rgba(255,255,255,0.55)" if is_dark else "rgba(15,23,42,0.42)"}; '
        f'pointer-events:none; z-index:1;">'
        f'🏛️ {landmark_name}'
        f'</div>'
    )
    return svg_markup
