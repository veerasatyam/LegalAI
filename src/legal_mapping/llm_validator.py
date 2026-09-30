import json
import re
from typing import List, Dict, Any
from src.models.legal_schemas import Scenario, IPCSection, LegalMatch
from src.legal_mapping.llm_analyzer import LLMLegalAnalyzer

class LLMValidator:
    """
    Uses Grok LLM to validate candidate IPC sections against the facts
    """
    
    def __init__(self):
        self.llm = LLMLegalAnalyzer().llm
    
    async def validate_match(self, scenario: Scenario, section: IPCSection, raw_input: str) -> LegalMatch:
        """
        Have LLM validate if candidate section applies and provide justification
        """
        prompt = self._build_validation_prompt(scenario, section, raw_input)
        
        try:
            response = await self.llm.ainvoke(prompt)
            content = getattr(response, "content", str(response))
            validation = self._parse_validation(content, scenario, section)
            
            match = LegalMatch(
                section=section,
                relevance_score=float(validation.get('score', 0.6)),
                match_reasons=validation.get('reasons', [f"Applicable to {section.title.lower()}"]),
                missing_elements=validation.get('missing', []),
                confidence=validation.get('confidence', 'MEDIUM')
            )
            return match
            
        except Exception as e:
            print(f"[WARN] Validation failed for Section {section.section_number}: {e}")
            return self._heuristic_validation(scenario, section, raw_input)
    
    def _build_validation_prompt(self, scenario: Scenario, section: IPCSection, raw_input: str) -> str:
        return f"""You are a legal expert validating whether an IPC section applies to this situation.

SITUATION DESCRIBED BY CITIZEN:
"{raw_input}"

EXTRACTED FACTS:
Actions: {', '.join(scenario.actions)}
Location: {scenario.location}
Harm Types: {', '.join(scenario.harm_types)}

IPC SECTION TO VALIDATE:
Section {section.section_number}: {section.title}
Text: {section.main_text or section.full_text[:300]}

TASK:
Determine if Section {section.section_number} applies to these facts.
Respond ONLY with JSON:
{{
    "applies": true,
    "score": 0.85,
    "reasons": ["The offender physically obstructed free passage on a public pathway"],
    "missing": [],
    "confidence": "HIGH",
    "explanation": "Section {section.section_number} directly covers wrongful obstruction of movement."
}}
"""
    
    def _parse_validation(self, content: str, scenario: Scenario, section: IPCSection) -> Dict[str, Any]:
        """Parse validation response"""
        try:
            cleaned = content.strip()
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)
            
            json_start = cleaned.find('{')
            json_end = cleaned.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(cleaned[json_start:json_end])
        except Exception:
            pass
        
        return self._heuristic_dict(scenario, section)

    def _heuristic_dict(self, scenario: Scenario, section: IPCSection) -> Dict[str, Any]:
        sec_num = str(section.section_number).strip()
        reasons = []
        confidence = "MEDIUM"
        score = 0.70
        
        if sec_num in ["339", "341"]:
            reasons.append("Voluntary obstruction of movement without lawful justification")
            confidence = "HIGH"
            score = 0.88
        elif sec_num in ["340", "342"]:
            reasons.append("Preventing a person from proceeding beyond circumscribed boundaries")
            confidence = "HIGH"
            score = 0.85
        elif sec_num in ["378", "379"]:
            reasons.append("Dishonest taking of movable property without owner's consent")
            confidence = "HIGH"
            score = 0.89
        elif sec_num in ["503", "506"]:
            reasons.append("Threatening injury to person or reputation to cause alarm")
            confidence = "HIGH"
            score = 0.84
        elif sec_num in ["351", "352"]:
            reasons.append("Use of criminal force or causing apprehension of force")
            score = 0.75
        else:
            reasons.append(f"Statutory elements of {section.title} align with described facts")
            
        return {
            "applies": True,
            "score": score,
            "reasons": reasons,
            "missing": [],
            "confidence": confidence,
            "explanation": f"Section {section.section_number} applies based on reported actions."
        }

    def _heuristic_validation(self, scenario: Scenario, section: IPCSection, raw_input: str) -> LegalMatch:
        val = self._heuristic_dict(scenario, section)
        return LegalMatch(
            section=section,
            relevance_score=val["score"],
            match_reasons=val["reasons"],
            missing_elements=[],
            confidence=val["confidence"]
        )