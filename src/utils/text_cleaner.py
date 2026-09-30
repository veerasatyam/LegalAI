import re
from typing import List

class TextCleaner:
    """Clean and normalize user input"""
    
    @staticmethod
    def clean(text: str) -> str:
        """Basic text cleaning"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\?\!,]', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        """Split into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def normalize_entities(text: str) -> str:
        """Normalize entity references"""
        # Replace "my" with "user's" for consistent processing
        text = re.sub(r'\bmy\b', "user's", text)
        text = re.sub(r'\bme\b', 'user', text)
        text = re.sub(r'\bi\b', 'user', text)
        
        # Replace common entity patterns
        replacements = {
            r'\bsomeone\b': 'unknown_person',
            r'\ba group of people\b': 'group',
            r'\bsome people\b': 'group',
            r'\bthey\b': 'unknown_person',
            r'\bhe\b': 'male_person',
            r'\bshe\b': 'female_person'
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text)
        
        return text