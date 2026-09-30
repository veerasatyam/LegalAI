from typing import Dict, Any, List, Tuple

class ScenarioValidator:
    """
    Validate extracted scenario data
    """
    
    def __init__(self):
        self.required_fields = [
            'actors', 'actions', 'victim', 'location',
            'harm_types', 'legal_categories'
        ]
    
    def validate(self, scenario: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate scenario and return issues
        """
        issues = []
        
        # Check required fields
        for field in self.required_fields:
            if field not in scenario:
                issues.append(f"Missing required field: {field}")
            elif field in ['actors', 'actions', 'harm_types', 'legal_categories']:
                if not scenario[field]:  # Empty list
                    issues.append(f"No {field} detected")
        
        # Specific validations
        if scenario['actors'] == ['unknown_person(s)'] and not scenario['actions']:
            issues.append("No clear actors or actions identified")
        
        if scenario['legal_categories'] and not scenario['harm_types']:
            issues.append("Legal categories present but no harm types classified")
        
        # Urgency check
        if scenario['urgency'] == 'high' and not scenario.get('evidence_mentioned'):
            issues.append("High urgency but no evidence mentioned - recommend immediate action")
        
        return len(issues) == 0, issues
    
    def suggest_improvement(self, scenario: Dict[str, Any]) -> List[str]:
        """
        Suggest what information is missing
        """
        suggestions = []
        
        if not scenario['actions']:
            suggestions.append("What exactly did they do?")
        
        if scenario['location'] == 'unspecified':
            suggestions.append("Where did this happen? (public road, private property, etc.)")
        
        if not scenario['legal_categories']:
            suggestions.append("Try to describe what happened in more detail")
        
        if not scenario.get('witnesses'):
            suggestions.append("Were there any witnesses or CCTV?")
        
        return suggestions