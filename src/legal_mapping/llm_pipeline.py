import asyncio
import time
from typing import List
from src.models.legal_schemas import Scenario, LegalMappingResult, LegalMatch
from src.legal_mapping.hybrid_retriever import HybridRetriever
from src.legal_mapping.llm_validator import LLMValidator

class LLMLegalPipeline:
    """
    LLM-powered legal mapping pipeline
    """
    
    def __init__(self):
        self.retriever = HybridRetriever()
        self.validator = LLMValidator()
    
    async def process(self, scenario: Scenario, raw_input: str) -> LegalMappingResult:
        """
        Process scenario through LLM-powered pipeline
        """
        start_time = time.time()
        
        # Step 1: Hybrid retrieval (LLM + Vector)
        candidates, analysis = await self.retriever.retrieve(scenario, raw_input)
        
        # Step 2: Validate top candidates with LLM
        validation_tasks = []
        for section in candidates[:5]:  # Validate top 5
            task = self.validator.validate_match(scenario, section, raw_input)
            validation_tasks.append(task)
        
        validation_results = await asyncio.gather(*validation_tasks)
        
        # Step 3: Filter and sort
        valid_matches = [m for m in validation_results if m.relevance_score > 0.4]
        valid_matches.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Step 4: Ensure primary section from LLM is included
        if analysis.primary_section:
            # Check if it's already in matches
            present = any(m.section.section_number == analysis.primary_section for m in valid_matches)
            if not present:
                # Find and add it
                for section in candidates:
                    if section.section_number == analysis.primary_section:
                        match = await self.validator.validate_match(scenario, section, raw_input)
                        if match.relevance_score > 0.3:
                            valid_matches.insert(0, match)
                        break
        
        # Build result
        result = LegalMappingResult(
            scenario=scenario,
            matches=valid_matches[:5],  # Top 5
            total_sections_considered=len(candidates),
            processing_time_ms=int((time.time() - start_time) * 1000)
        )
        
        return result
    
    def format_output(self, result: LegalMappingResult) -> dict:
        """Format for API response"""
        output = {
            "scenario_summary": {
                "actions": result.scenario.actions,
                "location": result.scenario.location,
                "harm_types": result.scenario.harm_types
            },
            "applicable_sections": [],
            "disclaimer": "This AI-powered analysis is for informational purposes only. Consult a legal professional for advice.",
            "processing_time_ms": result.processing_time_ms
        }
        
        for match in result.matches:
            section_info = {
                "section": f"Section {match.section.section_number}",
                "title": match.section.title,
                "confidence": match.confidence,
                "relevance_score": round(match.relevance_score, 2),
                "why_applies": match.match_reasons[:3],
                "explanation": self._generate_explanation(match)
            }
            output["applicable_sections"].append(section_info)
        
        return output
    
    def _generate_explanation(self, match: LegalMatch) -> str:
        """Generate plain language explanation"""
        if match.match_reasons:
            return f"This may apply because: {'; '.join(match.match_reasons[:2])}"
        return f"Section {match.section.section_number} may be relevant to your situation."