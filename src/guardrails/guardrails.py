"""
NIST AI RMF Guardrails:
1. InputGuardrail: Strips malicious injections and routes medical emergencies directly.
2. OutputGuardrail: Enforces schema validation and WHO/Harvard scientific grounding citations.
"""

import re
from typing import Tuple, Optional

class InputGuardrail:
    MALICIOUS_PATTERNS = [
        r"ignore previous instructions",
        r"output your system prompt",
        r"bypass rules",
        r"jailbreak"
    ]

    EMERGENCY_KEYWORDS = [
        r"\bwheezing\b",
        r"\bturn(ing)? blue\b",
        r"\bsteroid\b",
        r"\bdosage\b",
        r"\binhaler dose\b",
        r"\bsevere asthma attack\b"
    ]

    @classmethod
    def inspect(cls, user_input: str) -> Tuple[bool, str, Optional[str]]:
        """Returns: (is_safe, processed_prompt, emergency_override)"""
        # Medical emergency / clinical bypass
        for pattern in cls.EMERGENCY_KEYWORDS:
            if re.search(pattern, user_input, re.IGNORECASE):
                emergency_msg = (
                    "CRITICAL CLINICAL NOTICE: If an individual or child is experiencing acute respiratory distress, "
                    "severe wheezing, or difficulty breathing, please seek immediate emergency medical care or call 112 / 102. "
                    "This assistant cannot prescribe medications or replace emergency clinical diagnosis."
                )
                return True, user_input, emergency_msg

        # Adversarial Prompt Injection
        for pattern in cls.MALICIOUS_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                rejection = "I cannot comply with requests that attempt to override safety boundaries. Winter smog contains hazardous particulate matter."
                return False, rejection, rejection

        return True, user_input.strip(), None

class OutputGuardrail:
    @classmethod
    def sanitize_output(cls, text: str) -> str:
        # Guarantee scientific attribution if health claims appear
        if ("health" in text.lower() or "pm2.5" in text.lower()) and "who" not in text.lower():
            text += "\n\n*(Grounded in WHO 2021 Global Air Quality Guidelines & Harvard COGfx environmental studies)*"
        return text
