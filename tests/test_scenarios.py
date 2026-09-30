import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

if sys.platform.startswith("win"):
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from src.scenario_understanding.extractor import ScenarioExtractor
from src.scenario_understanding.validator import ScenarioValidator
import json

def test_scenarios():
    extractor = ScenarioExtractor()
    validator = ScenarioValidator()
    
    test_inputs = [
        "Someone stopped my bike in the middle of the road",
        "A group of people blocked my house entrance and won't let me leave",
        "He pushed me and threatened to hit me",
        "They entered my house without permission and took my phone",
        "Someone snatched my chain at the market just now"
    ]
    
    results = []
    
    for i, input_text in enumerate(test_inputs, 1):
        print(f"\n{'='*50}")
        print(f"Test {i}: {input_text}")
        print('='*50)
        
        # Extract
        scenario = extractor.extract(input_text)
        
        # Validate
        is_valid, issues = validator.validate(scenario)
        suggestions = validator.suggest_improvement(scenario)
        
        # Print results
        print("\n📊 Extracted Scenario:")
        print(json.dumps(scenario, indent=2))
        
        print(f"\n✅ Valid: {is_valid}")
        if issues:
            print("\n⚠️ Issues:")
            for issue in issues:
                print(f"  - {issue}")
        
        if suggestions:
            print("\n💡 Suggestions:")
            for suggestion in suggestions:
                print(f"  - {suggestion}")
        
        results.append({
            'input': input_text,
            'scenario': scenario,
            'valid': is_valid,
            'issues': issues
        })
    
    return results

if __name__ == "__main__":
    results = test_scenarios()
    
    # Summary
    print("\n" + "="*50)
    print("📈 SUMMARY")
    print("="*50)
    valid_count = sum(1 for r in results if r['valid'])
    print(f"Total tests: {len(results)}")
    print(f"Fully valid: {valid_count}")
    print(f"Needs improvement: {len(results) - valid_count}")