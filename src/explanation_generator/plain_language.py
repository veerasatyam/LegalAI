from typing import Dict, Any, List
import re
from src.utils.legal_definitions import LEGAL_TERMS

class PlainLanguageTranslator:
    """
    Translates legal text into simple, understandable language
    """
    
    def __init__(self):
        self.legal_terms = LEGAL_TERMS
        
        # Common legal phrases and their plain equivalents
        self.phrase_mapping = {
            r'whoever wrongfully restrains': 'If someone illegally blocks or stops',
            r'shall be punished with imprisonment': 'can be sent to jail for',
            r'which may extend to': 'up to',
            r'or with fine': 'or have to pay a fine of',
            r'or with both': 'or both jail and fine',
            r'in the discretion of the court': 'the judge decides how much',
            r'cognizable offence': 'serious offense where police can arrest without warrant',
            r'non-cognizable': 'less serious - police need court order to arrest',
            r'against the will': 'without permission',
            r'without lawful justification': 'without any legal reason',
        }
    
    def translate_section(self, section_number: str, title: str, text: str) -> Dict[str, str]:
        """
        Translate an IPC section into plain language
        """
        # Clean the text
        clean_text = self._clean_text(text)
        
        # Apply phrase mappings
        plain_text = self._apply_phrase_mapping(clean_text)
        
        # Extract punishment info
        punishment = self._extract_punishment(text)
        
        # Determine what this section covers
        summary = self._generate_summary(section_number, title)
        
        return {
            "section": section_number,
            "title": title,
            "original": text[:200] + "..." if len(text) > 200 else text,
            "plain_meaning": plain_text,
            "summary": summary,
            "punishment": punishment
        }
    
    def _clean_text(self, text: str) -> str:
        """Remove legal formatting artifacts"""
        # Remove section numbers and brackets
        text = re.sub(r'^\d+\.\s*', '', text)
        text = re.sub(r'\[.*?\]', '', text)
        
        # Fix common abbreviations
        replacements = {
            'u/s': 'under section',
            'i.e.': 'that is',
            'e.g.': 'for example',
            'viz.': 'namely',
        }
        for abbr, full in replacements.items():
            text = text.replace(abbr, full)
        
        return text.strip()
    
    def _apply_phrase_mapping(self, text: str) -> str:
        """Replace legal phrases with plain language"""
        result = text
        for pattern, replacement in self.phrase_mapping.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        return result
    
    def _extract_punishment(self, text: str) -> Dict[str, Any]:
        """Extract punishment details from section text"""
        punishment = {
            "imprisonment": None,
            "fine": None,
            "both": False,
            "description": ""
        }
        
        # Look for imprisonment terms
        imprisonment_patterns = [
            r'imprisonment for a term which may extend to ([\w\s]+)',
            r'imprisonment of ([\w\s]+)',
            r' imprisonment (?:for|of) ([\w\s]+)'
        ]
        
        for pattern in imprisonment_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                punishment["imprisonment"] = match.group(1).strip()
                break
        
        # Look for fines
        fine_pattern = r'fine which may extend to ([\w\s,]+)'
        match = re.search(fine_pattern, text, re.IGNORECASE)
        if match:
            punishment["fine"] = match.group(1).strip()
        
        # Check if both apply
        if "or with both" in text.lower():
            punishment["both"] = True
        
        # Generate description
        if punishment["imprisonment"] and punishment["fine"]:
            punishment["description"] = f"Jail up to {punishment['imprisonment']} AND fine up to {punishment['fine']}"
        elif punishment["imprisonment"]:
            punishment["description"] = f"Jail up to {punishment['imprisonment']}"
        elif punishment["fine"]:
            punishment["description"] = f"Fine up to {punishment['fine']}"
        else:
            punishment["description"] = "Punishment as determined by court"
        
        return punishment
    
    def _generate_summary(self, section_number: str, title: str) -> str:
        """Generate a one-line summary of what the section covers"""
        # Common section summaries
        summaries = {
            "341": "This section deals with illegally blocking or stopping someone from moving freely.",
            "342": "This section covers wrongfully confining or imprisoning someone against their will.",
            "351": "This section defines what counts as assault (threatening gestures or actions).",
            "352": "This section covers using criminal force or assault without grave provocation.",
            "378": "This section defines theft - taking movable property without consent.",
            "383": "This section covers extortion - forcing someone to give property through threats.",
            "441": "This section defines criminal trespass - entering property without permission.",
            "447": "This section sets punishment for criminal trespass.",
            "503": "This section defines criminal intimidation - threatening someone with injury.",
            "506": "This section sets punishment for criminal intimidation.",
        }
        
        return summaries.get(section_number, f"This section explains {title.lower()}")