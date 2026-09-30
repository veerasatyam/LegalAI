from typing import List, Dict, Any
from src.models.legal_schemas import LegalMatch, Scenario
from src.explanation_generator.plain_language import PlainLanguageTranslator
from src.explanation_generator.action_advisor import ActionAdvisor
from src.explanation_generator.risk_analyzer import RiskAnalyzer
from src.utils.legal_definitions import LEGAL_TERMS

class ResponseBuilder:
    """
    Builds complete, user-friendly legal response
    """
    
    def __init__(self):
        self.translator = PlainLanguageTranslator()
        self.action_advisor = ActionAdvisor()
        self.risk_analyzer = RiskAnalyzer()
        self.legal_terms = LEGAL_TERMS
    
    def build_response(self, matches: List[LegalMatch], scenario: Scenario) -> Dict[str, Any]:
        """
        Build complete response with explanations and actions
        """
        # Analyze risk
        risk = self.risk_analyzer.analyze(matches, scenario)
        
        # Get recommended actions
        actions = self.action_advisor.get_actions(matches, scenario)
        
        # Build response
        response = {
            "status": "success",
            "summary": self._build_summary(matches, scenario, risk),
            "legal_analysis": {
                "applicable_sections": [],
                "definitions": self._get_relevant_definitions(matches)
            },
            "practical_guidance": {
                "immediate_actions": actions["immediate"][:3],
                "legal_steps": actions["legal_steps"][:4],
                "evidence_to_collect": actions["evidence"]
            },
            "risk_assessment": risk,
            "warnings": actions["warnings"],
            "disclaimer": self._get_disclaimer(),
            "next_steps": self._prioritize_actions(actions, risk)
        }
        
        # Add explanations for each section
        for match in matches[:5]:  # Top 5 sections
            explanation = self._explain_section(match, scenario)
            response["legal_analysis"]["applicable_sections"].append(explanation)
        
        return response
    
    def _build_summary(self, matches: List[LegalMatch], scenario: Scenario, risk: Dict) -> str:
        """Build a one-paragraph summary"""
        if not matches:
            return "We couldn't identify specific IPC sections for your situation. Please consult a lawyer."
        
        primary = matches[0]
        section = primary.section.section_number
        
        summaries = {
            "341": "This appears to be a case of wrongful restraint - someone illegally blocked your movement.",
            "342": "This appears to be wrongful confinement - someone prevented you from leaving an area.",
            "352": "This appears to be an assault or use of criminal force against you.",
            "378": "This appears to be a theft - someone took your property without consent.",
            "383": "This appears to be extortion - someone threatened you to get property/money.",
            "441": "This appears to be criminal trespass - someone entered your property illegally.",
            "503": "This appears to be criminal intimidation - someone threatened to harm you.",
        }
        
        summary = summaries.get(section, f"Section {section} may apply to your situation.")
        summary += f" Risk level: {risk['level'].upper()}. {risk['advice']}"
        
        return summary
    
    def _explain_section(self, match: LegalMatch, scenario: Scenario) -> Dict[str, Any]:
        """Generate detailed explanation for a section"""
        section = match.section
        
        # Translate to plain language
        plain = self.translator.translate_section(
            section.section_number,
            section.title,
            section.full_text
        )
        
        explanation = {
            "section": f"Section {section.section_number}",
            "title": section.title,
            "plain_meaning": plain["plain_meaning"],
            "summary": plain["summary"],
            "punishment": plain["punishment"]["description"],
            "why_applies": match.match_reasons[:2],
            "confidence": match.confidence,
            "legal_details": {}
        }
        
        # Add legal details if available
        if hasattr(section, 'cognizable') and section.cognizable is not None:
            explanation["legal_details"]["cognizable"] = section.cognizable
            explanation["legal_details"]["bailable"] = getattr(section, 'bailable', None)
            explanation["legal_details"]["compoundable"] = getattr(section, 'compoundable', None)
        
        return explanation
    
    def _get_relevant_definitions(self, matches: List[LegalMatch]) -> List[Dict]:
        """Get definitions of legal terms relevant to this case"""
        definitions = []
        
        # Check which terms are relevant
        for match in matches:
            if hasattr(match.section, 'cognizable'):
                if match.section.cognizable and "cognizable" not in [d.get("term") for d in definitions]:
                    definitions.append({
                        "term": "cognizable",
                        "definition": self.legal_terms["cognizable"]["plain"],
                        "explanation": self.legal_terms["cognizable"]["explanation"]
                    })
                elif not match.section.cognizable and "non_cognizable" not in [d.get("term") for d in definitions]:
                    definitions.append({
                        "term": "non_cognizable",
                        "definition": self.legal_terms["non_cognizable"]["plain"],
                        "explanation": self.legal_terms["non_cognizable"]["explanation"]
                    })
        
        return definitions[:3]  # Limit to 3 terms
    
    def _prioritize_actions(self, actions: Dict, risk: Dict) -> List[str]:
        """Create prioritized next steps"""
        next_steps = []
        
        # Safety first
        if actions["immediate"]:
            next_steps.append(f"🚨 SAFETY: {actions['immediate'][0]}")
        
        # Medical if needed
        if any("medical" in step.lower() for step in actions["legal_steps"]):
            next_steps.append("🏥 MEDICAL: Get medical help/documentation")
        
        # Police complaint
        if risk["level"] in ["high", "medium"]:
            next_steps.append("👮 POLICE: File an FIR at nearest police station")
        else:
            next_steps.append("📋 COMPLAINT: Consider filing a complaint")
        
        # Evidence
        if actions["evidence"]:
            next_steps.append(f"📸 EVIDENCE: {actions['evidence'][0]}")
        
        # Legal advice
        if risk["level"] == "high":
            next_steps.append("⚖️ LAWYER: Consult a criminal lawyer immediately")
        
        return next_steps[:4]  # Top 4 priorities
    
    def _get_disclaimer(self) -> str:
        """Get legal disclaimer"""
        return """
⚠️ LEGAL DISCLAIMER: This information is for educational purposes only and does not constitute legal advice. 
Laws may have exceptions and interpretations vary by circumstances. Always consult a qualified lawyer 
for advice specific to your situation. The Indian Penal Code is complex and this tool may not capture 
all nuances of your case.
        """.strip()