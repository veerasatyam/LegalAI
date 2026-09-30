from typing import List, Dict, Any
from src.models.legal_schemas import LegalMatch, Scenario

class ActionAdvisor:
    """
    Recommends practical next steps based on legal situation
    """
    
    def __init__(self):
        self.action_templates = {
            "immediate": {
                "341": [
                    "Note down vehicle numbers of people blocking you",
                    "Record video of the obstruction if safe",
                    "Call police control room (100) if you feel threatened"
                ],
                "342": [
                    "Try to call or message someone for help",
                    "Note down names/descriptions of people confining you",
                    "Dial 100 if you have phone access",
                    "Make noise to attract attention if in public place"
                ],
                "352": [
                    "Move to a safe location if possible",
                    "Take photos of any injuries",
                    "Note down witness details",
                    "Report to nearest police station"
                ],
                "378": [
                    "Do not confront the thief if alone",
                    "Note down description of person",
                    "Check for CCTV cameras in area",
                    "File complaint immediately"
                ],
                "default": [
                    "Ensure your immediate safety",
                    "Move to a safe location",
                    "Call emergency services if needed (100)"
                ]
            },
            "legal": {
                "file_complaint": [
                    "Visit the nearest police station",
                    "Carry ID proof and incident details",
                    "Ask for a copy of your complaint (FIR if registered)",
                    "Note down the complaint number"
                ],
                "gather_evidence": [
                    "Take photos/videos of the scene",
                    "Collect contact details of witnesses",
                    "Preserve any physical evidence",
                    "Save WhatsApp messages or call logs if relevant"
                ],
                "medical": [
                    "Get medical examination done",
                    "Keep all medical reports",
                    "Take photos of injuries",
                    "Get doctor's certificate"
                ],
                "lawyer": [
                    "Consult a criminal lawyer",
                    "Keep all documents ready",
                    "Don't sign anything without legal advice",
                    "Discuss bail options if arrested"
                ]
            }
        }
        
        # Section to recommended actions mapping
        self.section_actions = {
            "341": ["file_complaint", "gather_evidence"],
            "342": ["file_complaint", "lawyer", "gather_evidence"],
            "352": ["medical", "file_complaint", "gather_evidence"],
            "378": ["file_complaint", "gather_evidence"],
            "383": ["file_complaint", "lawyer", "gather_evidence"],
            "441": ["file_complaint", "gather_evidence"],
            "447": ["file_complaint", "gather_evidence"],
            "503": ["file_complaint", "gather_evidence", "lawyer"],
            "506": ["file_complaint", "lawyer", "gather_evidence"]
        }
    
    def get_actions(self, matches: List[LegalMatch], scenario: Scenario) -> Dict[str, List[str]]:
        """
        Generate recommended actions based on matches
        """
        actions = {
            "immediate": [],
            "legal_steps": [],
            "evidence": [],
            "warnings": []
        }
        
        # Get all applicable section numbers
        sections = [m.section.section_number for m in matches if m.confidence != "LOW"]
        
        if not sections:
            # Provide general advice
            actions["immediate"] = self.action_templates["immediate"]["default"]
            actions["legal_steps"] = ["Consider consulting a lawyer for proper advice"]
            return actions
        
        # Add immediate actions for primary sections
        primary_section = sections[0] if sections else "default"
        if primary_section in self.action_templates["immediate"]:
            actions["immediate"].extend(self.action_templates["immediate"][primary_section])
        else:
            actions["immediate"].extend(self.action_templates["immediate"]["default"])
        
        # Add legal steps based on sections
        legal_steps = set()
        for section in sections:
            if section in self.section_actions:
                for step in self.section_actions[section]:
                    legal_steps.add(step)
        
        for step in legal_steps:
            if step in self.action_templates["legal"]:
                actions["legal_steps"].extend(self.action_templates["legal"][step])
        
        # Add evidence recommendations based on scenario
        actions["evidence"] = self._get_evidence_tips(scenario)
        
        # Add warnings based on severity
        actions["warnings"] = self._get_warnings(matches)
        
        # Remove duplicates
        actions["immediate"] = list(dict.fromkeys(actions["immediate"]))
        actions["legal_steps"] = list(dict.fromkeys(actions["legal_steps"]))
        
        return actions
    
    def _get_evidence_tips(self, scenario: Scenario) -> List[str]:
        """Generate evidence recommendations based on scenario"""
        evidence = []
        
        if "physical" in scenario.harm_types:
            evidence.extend([
                "Take photos of injuries immediately",
                "Get medical examination done within 24 hours",
                "Keep all medical reports and bills"
            ])
        
        if "property_damage" in scenario.harm_types:
            evidence.extend([
                "Take photos/videos of damaged property",
                "Keep repair estimates or bills",
                "Note down any witnesses"
            ])
        
        if scenario.location == "public_road":
            evidence.extend([
                "Check for CCTV cameras in the area",
                "Note down nearby shop names for witnesses",
                "Take photos of the exact location"
            ])
        
        if scenario.witnesses:
            evidence.extend([
                "Get contact details of all witnesses",
                "Ask witnesses to note down what they saw",
                "Request CCTV footage from nearby shops"
            ])
        
        if not evidence:
            evidence = [
                "Note down everything you remember",
                "Save any messages or call logs related to incident",
                "Take photos of the location/scene"
            ]
        
        return evidence[:5]  # Limit to top 5
    
    def _get_warnings(self, matches: List[LegalMatch]) -> List[str]:
        """Generate warnings based on legal severity"""
        warnings = []
        
        for match in matches:
            if hasattr(match.section, 'cognizable') and match.section.cognizable:
                warnings.append("⚠️ This is a cognizable offense - police can arrest without warrant")
            
            if hasattr(match.section, 'bailable') and not match.section.bailable:
                warnings.append("⚠️ This is a non-bailable offense - getting bail may require court order")
        
        return list(dict.fromkeys(warnings))  # Remove duplicates