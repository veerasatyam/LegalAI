from typing import List, Dict, Any
from src.models.legal_schemas import LegalMatch, Scenario
from src.utils.legal_definitions import CRIME_SEVERITY

class RiskAnalyzer:
    """
    Analyzes legal risk and severity
    """
    
    def __init__(self):
        self.severity_levels = CRIME_SEVERITY
        
        # Section severity mapping
        self.section_severity = {
            "341": "low",      # Wrongful restraint
            "342": "medium",   # Wrongful confinement
            "352": "medium",   # Assault/force
            "353": "high",     # Assault on public servant
            "378": "medium",   # Theft
            "379": "medium",   # Punishment for theft
            "383": "high",     # Extortion
            "384": "high",     # Punishment for extortion
            "441": "low",      # Criminal trespass
            "447": "low",      # Punishment for trespass
            "503": "medium",   # Criminal intimidation
            "506": "high",     # Punishment for criminal intimidation
            "509": "medium",   # Word/gesture to insult modesty
        }
    
    def analyze(self, matches: List[LegalMatch], scenario: Scenario) -> Dict[str, Any]:
        """
        Analyze risk level and provide assessment
        """
        if not matches:
            return {
                "level": "unknown",
                "description": "Unable to assess risk level",
                "advice": "Consult a legal professional for proper assessment"
            }
        
        # Get highest severity from matches
        highest_severity = "low"
        primary_offense = None
        
        for match in matches[:3]:  # Check top 3 matches
            section = match.section.section_number
            severity = self.section_severity.get(section, "medium")
            
            if severity == "high":
                highest_severity = "high"
                primary_offense = match.section.title
                break
            elif severity == "medium" and highest_severity != "high":
                highest_severity = "medium"
                primary_offense = primary_offense or match.section.title
        
        # Get severity details
        severity_info = self.severity_levels.get(highest_severity, self.severity_levels["medium"])
        
        # Customize based on scenario
        analysis = {
            "level": highest_severity,
            "description": severity_info["description"],
            "primary_offense": primary_offense or "Multiple offenses",
            "advice": severity_info["advice"],
            "factors": self._get_risk_factors(matches, scenario)
        }
        
        return analysis
    
    def _get_risk_factors(self, matches: List[LegalMatch], scenario: Scenario) -> List[str]:
        """Identify factors that increase or decrease risk"""
        factors = []
        
        # Risk increasing factors
        if "weapon" in scenario.evidence_mentioned:
            factors.append("⚠️ Weapon involvement increases severity")
        
        if scenario.urgency == "high":
            factors.append("⚠️ Ongoing situation - immediate action needed")
        
        if any(m.section.section_number in ["353", "383", "506"] for m in matches):
            factors.append("⚠️ Non-bailable offense - bail may be difficult")
        
        if "public_servant" in str(scenario.actors):
            factors.append("⚠️ Offense against public servant - stricter treatment")
        
        # Risk decreasing factors
        if scenario.location == "private_property" and "341" in [m.section.section_number for m in matches]:
            factors.append("ℹ️ On private property - may affect applicability of public road offenses")
        
        if "lack_of_intent" in scenario.intent_indicators:
            factors.append("ℹ️ Lack of intent may reduce severity")
        
        if not factors:
            factors.append("ℹ️ Standard legal process applies")
        
        return factors