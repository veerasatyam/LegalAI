import asyncio
import time
from typing import Dict, Any

from src.scenario_understanding.intent_classifier import IntentSafetyClassifier
from src.scenario_understanding.extractor import ScenarioExtractor
from src.legal_mapping.llm_pipeline import LLMLegalPipeline
from src.explanation_generator.response_builder import ResponseBuilder
from src.models.legal_schemas import Scenario

class CompleteLegalPipeline:
    """
    End-to-end Legal Awareness Pipeline:
    Step 1: User Input
    Step 2: Intent & Risk Classification (Safety Guardrail)
    Step 3: Scenario Understanding & Fact Extraction
    Step 4: Legal Element Mapping (Grok LLM)
    Step 5: FAISS Vector Retrieval (IPC Embeddings)
    Step 6: LLM Validation & Explanation Generator
    Step 7: Citations, Guidance & Statutory Disclaimer
    """
    
    def __init__(self):
        self.safety_classifier = IntentSafetyClassifier()
        self.extractor = ScenarioExtractor()
        self.legal_pipeline = LLMLegalPipeline()
        self.response_builder = ResponseBuilder()
    
    async def process(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input through entire pipeline
        """
        start_time = time.time()
        raw_text = (user_input or "").strip()
        
        # Step 2: Intent & Risk Classification
        intent = self.safety_classifier.classify(raw_text)
        if not intent.is_allowed:
            return {
                "status": "blocked",
                "is_safe": False,
                "summary": intent.reason,
                "legal_analysis": {
                    "applicable_sections": [],
                    "definitions": []
                },
                "risk_assessment": {
                    "level": "HIGH",
                    "reason": "Query screened as requesting evasion or unlawful assistance.",
                    "advice": "Please consult a licensed advocate for legal representation. We cannot assist in evading lawful processes."
                },
                "practical_guidance": {
                    "immediate_actions": [
                        "Consult a certified legal practitioner for formal representation",
                        "Cooperate with lawful official procedures"
                    ],
                    "legal_steps": [
                        "Obtain professional legal counsel"
                    ],
                    "evidence_to_collect": []
                },
                "warnings": [
                    "Smart Legal Aid is strictly an educational tool and will not provide advice for committing or escaping offences."
                ],
                "disclaimer": "This platform provides legal awareness for educational purposes and does not constitute legal advice.",
                "processing_time_ms": int((time.time() - start_time) * 1000),
                "original_input": raw_text
            }
        
        # Step 3: Extract structured scenario facts
        extracted = self.extractor.extract(raw_text)
        scenario = Scenario(**extracted)
        
        # Step 4 & 5: Legal mapping with Grok + FAISS
        legal_result = await self.legal_pipeline.process(scenario, raw_text)
        
        # Step 6 & 7: Generate explanations, practical guidance & citations
        response = self.response_builder.build_response(
            legal_result.matches,
            scenario
        )
        
        # Enrich metadata
        response["is_safe"] = True
        response["processing_time_ms"] = int((time.time() - start_time) * 1000)
        response["original_input"] = raw_text
        response["scenario_facts"] = {
            "actions": scenario.actions,
            "location": scenario.location,
            "harm_types": scenario.harm_types,
            "actors": scenario.actors
        }
        
        return response