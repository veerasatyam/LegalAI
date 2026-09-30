import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from .entities import LEGAL_INDICATORS, LegalAction, HarmType
from ..utils.text_cleaner import TextCleaner

class ScenarioExtractor:
    """
    Extract structured legal meaning from user input
    """
    
    def __init__(self):
        self.cleaner = TextCleaner()
        self.legal_indicators = LEGAL_INDICATORS
        
    def extract(self, raw_input: str) -> Dict[str, Any]:
        """
        Main extraction method
        """
        # Clean and normalize
        cleaned = self.cleaner.clean(raw_input)
        normalized = self.cleaner.normalize_entities(cleaned)
        sentences = self.cleaner.extract_sentences(normalized)
        
        # Initialize structured data
        scenario = {
            'actors': self._extract_actors(normalized),
            'actions': self._extract_actions(normalized),
            'victim': self._extract_victim(normalized),
            'objects': self._extract_objects(normalized),
            'location': self._extract_location(normalized),
            'harm_types': self._classify_harm(normalized),
            'legal_categories': self._map_to_legal_categories(normalized),
            'intent_indicators': self._extract_intent(normalized),
            'urgency': self._assess_urgency(normalized),
            'witnesses': self._extract_witnesses(normalized),
            'evidence_mentioned': self._extract_evidence(normalized),
            'original_text': raw_input,
            'timestamp': datetime.now().isoformat()
        }
        
        return scenario
    
    def _extract_actors(self, text: str) -> List[str]:
        """Extract who did the action"""
        actors = []
        
        patterns = [
            r'(?:^|\s)([a-z]+(?: [a-z]+)?)(?=\s+(?:stopped|blocked|attacked|threatened|entered|took|pushed|hit))',
            r'(?:by\s+)([a-z]+(?: [a-z]+)?)',
            r'(?:from\s+)([a-z]+(?: [a-z]+)?)'
        ]
        
        # Check for group indicators
        if re.search(r'\b(?:group|people|they|them)\b', text):
            actors.append('group')
        
        # Known actor patterns
        if 'unknown_person' in text:
            actors.append('unknown_person')
        elif 'male_person' in text:
            actors.append('male_person')
        elif 'female_person' in text:
            actors.append('female_person')
        
        # If no actors found, default to unknown
        if not actors:
            actors.append('unknown_person(s)')
        
        return list(set(actors))  # Remove duplicates
    
    def _extract_actions(self, text: str) -> List[str]:
        """Extract actions performed"""
        actions = []
        
        # Common action verbs in legal context
        action_patterns = [
            r'\b(stopped|blocked|prevented|obstructed)\b',
            r'\b(attacked|hit|pushed|slapped|kicked|beat)\b',
            r'\b(threatened|intimidated|warned)\b',
            r'\b(entered|broke|trespassed)\b',
            r'\b(took|stole|snatched|grabbed)\b',
            r'\b(locked|trapped|confined|imprisoned)\b',
            r'\babused|insulted|shouted\b'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, text)
            actions.extend(matches)
        
        return list(set(actions))
    
    def _extract_victim(self, text: str) -> str:
        """Extract who was affected"""
        if re.search(r'\b(?:me|my|i|user|user\'s)\b', text):
            return 'user'
        elif re.search(r'\b(?:him|his)\b', text):
            return 'third_party_male'
        elif re.search(r'\b(?:her|hers)\b', text):
            return 'third_party_female'
        elif re.search(r'\b(?:them|their)\b', text):
            return 'third_party_group'
        else:
            return 'unspecified'
    
    def _extract_objects(self, text: str) -> List[str]:
        """Extract objects involved (vehicles, property, etc.)"""
        objects = []
        
        # Vehicle patterns
        if re.search(r'\b(?:bike|motorcycle|scooter)\b', text):
            objects.append('motorcycle')
        if re.search(r'\b(?:car|auto|taxi|vehicle)\b', text):
            objects.append('car')
        
        # Property patterns
        if re.search(r'\b(?:house|home|property|land)\b', text):
            objects.append('property')
        if re.search(r'\b(?:shop|store|business)\b', text):
            objects.append('commercial_property')
        
        # Document patterns
        if re.search(r'\b(?:document|paper|file|id|license)\b', text):
            objects.append('document')
        
        return list(set(objects))
    
    def _extract_location(self, text: str) -> str:
        """Extract where it happened"""
        location_patterns = {
            'public_road': r'\b(?:road|street|highway|traffic|intersection)\b',
            'private_property': r'\b(?:house|home|property|land|compound)\b',
            'public_place': r'\b(?:market|park|mall|public|crowd)\b',
            'workplace': r'\b(?:office|work|factory|site)\b'
        }
        
        for location, pattern in location_patterns.items():
            if re.search(pattern, text):
                return location
        
        return 'unspecified'
    
    def _classify_harm(self, text: str) -> List[str]:
        """Classify the type of harm"""
        harm_types = []
        
        harm_patterns = {
            'physical': r'\b(?:hit|pushed|slapped|kicked|attack|beat|hurt|injured|pain)\b',
            'psychological': r'\b(?:threaten|scared|afraid|fear|trauma|mental)\b',
            'property_damage': r'\b(?:broke|damage|destroy|vandalism)\b',
            'restriction_of_movement': r'\b(?:blocked|stopped|prevented|obstructed|locked|trapped)\b'
        }
        
        for harm_type, pattern in harm_patterns.items():
            if re.search(pattern, text):
                harm_types.append(harm_type)
        
        return harm_types
    
    def _map_to_legal_categories(self, text: str) -> List[str]:
        """Map scenario to potential legal categories"""
        categories = []
        
        for category, indicators in self.legal_indicators.items():
            for indicator in indicators:
                if indicator in text:
                    categories.append(category)
                    break
        
        return list(set(categories))
    
    def _extract_intent(self, text: str) -> List[str]:
        """Extract indicators of intent"""
        intent_indicators = []
        
        if re.search(r'\b(?:intentionally|deliberately|purposely|on purpose)\b', text):
            intent_indicators.append('explicit_intent')
        
        if re.search(r'\b(?:accidentally|mistake|unintentionally|by accident)\b', text):
            intent_indicators.append('lack_of_intent')
        
        if re.search(r'\b(?:angry|furious|enraged|shouting|abusing)\b', text):
            intent_indicators.append('emotional_state')
        
        return intent_indicators
    
    def _assess_urgency(self, text: str) -> str:
        """Assess how urgent the situation is"""
        urgency_indicators = {
            'high': r'\b(?:now|immediately|urgent|emergency|right now|at this moment|ongoing)\b',
            'medium': r'\b(?:today|just now|recently|few minutes|this hour)\b',
            'low': r'\b(?:yesterday|last week|few days|last month|some time ago)\b'
        }
        
        for urgency, pattern in urgency_indicators.items():
            if re.search(pattern, text):
                return urgency
        
        return 'medium'  # default
    
    def _extract_witnesses(self, text: str) -> List[str]:
        """Extract witness information"""
        witnesses = []
        
        if re.search(r'\b(?:witness|bystander|people saw|public|crowd)\b', text):
            witnesses.append('public_present')
        
        if re.search(r'\b(?:cctv|camera|recorded|video)\b', text):
            witnesses.append('cctv_available')
        
        return witnesses
    
    def _extract_evidence(self, text: str) -> List[str]:
        """Extract evidence mentioned"""
        evidence = []
        
        evidence_patterns = {
            'physical': r'\b(?:weapon|stick|knife|gun|stone)\b',
            'documentary': r'\b(?:document|paper|photo|picture|screenshot)\b',
            'digital': r'\b(?:cctv|video|recording|audio|phone)\b',
            'medical': r'\b(?:injury|wound|bleeding|hospital|doctor|treatment)\b'
        }
        
        for evidence_type, pattern in evidence_patterns.items():
            if re.search(pattern, text):
                evidence.append(evidence_type)
        
        return evidence