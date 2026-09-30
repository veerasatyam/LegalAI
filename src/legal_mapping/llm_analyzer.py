import re
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import Config
from src.models.legal_schemas import Scenario

class LegalAnalysis(BaseModel):
    """Structured output from LLM"""
    relevant_sections: List[str] = Field(description="List of IPC section numbers that might apply")
    primary_section: Optional[str] = Field(description="Most applicable section number")
    legal_elements: Dict[str, bool] = Field(default_factory=dict, description="Whether each legal element is present")
    missing_elements: List[str] = Field(default_factory=list, description="Elements needed but not clearly present")
    search_queries: List[str] = Field(default_factory=list, description="Search queries to find relevant sections")
    reasoning: str = Field(default="", description="Brief reasoning for section selection")
    confidence: str = Field(default="MEDIUM", description="HIGH/MEDIUM/LOW")

class LLMLegalAnalyzer:
    """
    Uses Grok LLM to analyze scenarios and identify relevant IPC sections
    """
    
    def __init__(self):
        self.llm = Config.get_llm()
        self.section_knowledge = self._load_section_knowledge()
    
    def _load_section_knowledge(self) -> str:
        return """
        Key IPC Sections Reference:
        - Section 341: Wrongful restraint (voluntarily obstructing a person so as to prevent proceeding in any direction)
        - Section 342: Wrongful confinement (wrongfully restraining in such a manner as to prevent proceeding beyond certain circumscribing limits)
        - Section 351: Assault (making gesture or preparation causing apprehension of criminal force)
        - Section 352: Punishment for assault or criminal force
        - Section 378: Theft (dishonestly taking movable property out of possession of any person without consent)
        - Section 379: Punishment for theft
        - Section 383: Extortion (intentionally putting in fear of injury to deliver property)
        - Section 425: Mischief (causing wrongful loss or damage to property)
        - Section 441: Criminal trespass (entering into or upon property in possession of another to commit offence)
        - Section 503: Criminal intimidation (threatening another with injury to person, reputation or property)
        - Section 506: Punishment for criminal intimidation
        - Section 509: Word, gesture or act intended to insult the modesty of a woman
        """
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=4))
    async def analyze(self, scenario: Scenario, raw_input: str) -> LegalAnalysis:
        """
        Use Grok LLM to analyze scenario and identify relevant sections
        """
        prompt = self._build_analysis_prompt(scenario, raw_input)
        
        try:
            response = await self.llm.ainvoke(prompt)
            content = getattr(response, "content", str(response))
            analysis = self._parse_llm_response(content, scenario)
            return analysis
        except Exception as e:
            print(f"[WARN] LLM analysis failed: {e}. Utilizing structured heuristic analyzer.")
            return self._heuristic_analysis(scenario, raw_input)
    
    def _build_analysis_prompt(self, scenario: Scenario, raw_input: str) -> str:
        return f"""You are a legal expert specializing in the Indian Penal Code (IPC). 
Analyze this real-life scenario and identify which IPC sections might apply.

USER'S INCIDENT DESCRIPTION:
"{raw_input}"

EXTRACTED FACTS:
- Actions: {', '.join(scenario.actions) if scenario.actions else 'None clearly stated'}
- Location: {scenario.location or 'Unspecified'}
- Harm Types: {', '.join(scenario.harm_types) if scenario.harm_types else 'None detected'}
- Objects involved: {', '.join(scenario.objects) if scenario.objects else 'None'}
- Intent indicators: {', '.join(scenario.intent_indicators) if scenario.intent_indicators else 'None'}

{self.section_knowledge}

TASK:
1. Identify 1 to 4 IPC section numbers that most directly apply to these facts.
2. Formulate 2-3 specific legal search queries for our IPC database.
3. Check key ingredients and note any missing elements.
4. Provide plain-language legal reasoning.

Respond ONLY with valid JSON in this exact structure:
{{
    "relevant_sections": ["341", "506"],
    "primary_section": "341",
    "legal_elements": {{
        "wrongful_obstruction": true,
        "threat_of_injury": true
    }},
    "missing_elements": [],
    "search_queries": [
        "wrongful restraint blocking road bike",
        "punishment for criminal intimidation"
    ],
    "reasoning": "Blocking passage on a road constitutes wrongful restraint under Section 339/341 IPC.",
    "confidence": "HIGH"
}}
"""
    
    def _parse_llm_response(self, content: str, scenario: Optional[Scenario] = None) -> LegalAnalysis:
        """Parse LLM response into structured format"""
        try:
            cleaned = content.strip()
            # Remove markdown code blocks if present
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)
            
            json_start = cleaned.find('{')
            json_end = cleaned.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = cleaned[json_start:json_end]
                data = json.loads(json_str)
                return LegalAnalysis(**data)
            
            return self._heuristic_analysis(scenario, content)
        except Exception as e:
            print(f"[WARN] Error parsing LLM response: {e}")
            return self._heuristic_analysis(scenario, content)
            
    def _heuristic_analysis(self, scenario: Optional[Scenario], text: str) -> LegalAnalysis:
        """High-accuracy fallback heuristic when LLM API is unavailable or parsing fails"""
        combined = ((scenario.original_text if scenario else "") + " " + text).lower()
        sections = []
        queries = []
        
        # Wrongful restraint
        if any(w in combined for w in ["stop", "block", "obstruct", "bike", "road", "passage", "path", "prevent"]):
            sections.extend(["339", "341"])
            queries.append("wrongful restraint voluntarily obstructs")
            
        # Confinement
        if any(w in combined for w in ["lock", "room", "house", "confine", "trap", "let me out", "can't leave"]):
            sections.extend(["340", "342"])
            queries.append("wrongful confinement prevent beyond circumscribing limits")
            
        # Theft
        if any(w in combined for w in ["steal", "stole", "theft", "snatch", "took my", "stolen", "phone", "jewelry", "wallet"]):
            sections.extend(["378", "379"])
            queries.append("theft dishonestly take movable property")
            
        # Extortion
        if any(w in combined for w in ["pay them", "give money", "demand money", "extort"]):
            sections.extend(["383", "384"])
            queries.append("extortion put in fear of injury")
            
        # Intimidation / Threats
        if any(w in combined for w in ["threat", "kill you", "harm", "beat you", "warning"]):
            sections.extend(["503", "506"])
            queries.append("criminal intimidation threat of injury")
            
        # Assault / Force
        if any(w in combined for w in ["hit", "push", "pushed", "slap", "beat", "collar", "attack"]):
            sections.extend(["351", "352"])
            queries.append("assault criminal force")
            
        # Criminal Trespass
        if any(w in combined for w in ["entered my house", "trespass", "broke into", "without permission"]):
            sections.extend(["441", "447"])
            queries.append("criminal trespass entry into property")
            
        # Damage to property / Mischief
        if any(w in combined for w in ["damage", "stone", "broke my car", "destroy", "vandal"]):
            sections.extend(["425", "426"])
            queries.append("mischief causing damage to property")
            
        # Deduplicate
        seen = set()
        dedup_sections = [s for s in sections if not (s in seen or seen.add(s))]
        if not dedup_sections:
            dedup_sections = ["341"]
            queries = ["wrongful restraint public road"]
            
        return LegalAnalysis(
            relevant_sections=dedup_sections,
            primary_section=dedup_sections[0],
            legal_elements={"incident_identified": True},
            missing_elements=[],
            search_queries=queries or [combined[:60]],
            reasoning=f"Matched statutory elements for IPC section(s): {', '.join(dedup_sections)}.",
            confidence="MEDIUM" if len(dedup_sections) > 1 else "HIGH"
        )