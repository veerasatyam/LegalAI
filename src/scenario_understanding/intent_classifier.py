import re
from typing import Tuple
from src.models.legal_schemas import IntentClassification

class IntentSafetyClassifier:
    """
    Step 2: Intent & Risk Classification
    Screens input to ensure the platform is used for legal awareness/rights understanding
    and blocks malicious inquiries seeking to evade law enforcement or commit offences.
    """
    
    BLOCKED_PATTERNS = [
        r'\b(?:how to|how can i|help me)\s+(?:escape|evade|flee|avoid)\s+(?:punishment|police|arrest|jail|custody|law)\b',
        r'\b(?:how to|how can i)\s+(?:hide|destroy|erase|delete|dispose)\s+(?:evidence|weapon|body|proof|cctv)\b',
        r'\b(?:how to|how can i)\s+(?:bribe|pay off)\s+(?:police|judge|officer)\b',
        r'\b(?:how to|how can i)\s+(?:commit|plan|execute)\s+(?:murder|theft|robbery|extortion|fraud|crime)\b',
        r'\b(?:how to get away with)\b',
        r'\b(?:tips to commit|ways to break the law)\b'
    ]
    
    def classify(self, text: str) -> IntentClassification:
        normalized = text.lower().strip()
        
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, normalized):
                return IntentClassification(
                    is_allowed=False,
                    intent_type="prohibited_evasion",
                    reason="This query appears to ask for assistance in evading legal consequences, destroying evidence, or committing an unlawful act. Smart Legal Aid is strictly an informational awareness platform and cannot assist in unlawful activities."
                )
                
        # Valid legal awareness query
        return IntentClassification(
            is_allowed=True,
            intent_type="incident_awareness",
            reason="Query is legitimate legal awareness inquiry."
        )
