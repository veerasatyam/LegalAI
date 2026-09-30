import re
import json
from pathlib import Path
from typing import List, Dict, Any

class IPCStructurer:
    def __init__(self):
        self.sections = []
        
    def parse_sections(self, pages: List[Dict]) -> List[Dict]:
        """
        Convert raw PDF pages into structured IPC sections.
        This regex looks for section patterns like "341." or "341-A."
        """
        full_text = "\n".join([page['text'] for page in pages])
        
        # Pattern: Section number (with optional letter) followed by title
        section_pattern = r'(\d+[A-Z]?\.?)\s+([A-Z][^\.]+\.?)—(.*?)(?=\n\d+[A-Z]?\.?\s+[A-Z]|$)'
        
        matches = re.findall(section_pattern, full_text, re.DOTALL)
        
        for match in matches:
            section_num = match[0].rstrip('.')
            title = match[1].strip()
            content = match[2].strip()
            
            # Further split content into main text and illustrations
            illustration_split = re.split(r'Illustration[s]?:', content)
            main_text = illustration_split[0].strip()
            illustrations = illustration_split[1].strip() if len(illustration_split) > 1 else ""
            
            section = {
                'section_number': section_num,
                'title': title,
                'full_text': f"{title}—{main_text}",
                'main_text': main_text,
                'illustrations': illustrations,
                'source': 'Indian Penal Code, 1860',
                'last_updated': None  # You can add date if available
            }
            
            self.sections.append(section)
        
        return self.sections
    
    def validate_sections(self) -> List[Dict]:
        """Basic validation to ensure we parsed correctly"""
        validated = []
        for section in self.sections:
            # Check if section has required fields
            if all(k in section for k in ['section_number', 'title', 'full_text']):
                # Additional validation: section number should be numeric or alphanumeric
                if re.match(r'^\d+[A-Z]?$', section['section_number']):
                    validated.append(section)
        
        return validated
    
    def save_to_json(self, output_path: str):
        """Save structured sections to JSON"""
        validated = self.validate_sections()
        
        output = {
            'metadata': {
                'source': 'Indian Penal Code, 1860',
                'total_sections': len(validated),
                'version': '1.0'
            },
            'sections': validated
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(validated)} sections to {output_path}")
        return output_path