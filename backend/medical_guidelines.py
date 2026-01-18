import json
from typing import Dict, List, Optional

class MedicalGuidelines:
    def __init__(self, guidelines_path: str = "../data/guidelines.json"):
        with open(guidelines_path, 'r') as f:
            self.guidelines = json.load(f)
    
    def get_test_info(self, test_name: str) -> Optional[Dict]:
        return self.guidelines.get("tests", {}).get(test_name)
    
    def get_test_validity_days(self, test_name: str) -> int:
        test_info = self.get_test_info(test_name)
        return test_info.get("validity_days", 90) if test_info else 90
    
    def get_tests_for_symptom(self, symptom: str) -> List[str]:
        symptom_lower = symptom.lower()
        symptom_data = self.guidelines.get("symptom_mappings", {}).get(symptom_lower, {})
        return symptom_data.get("tests", [])
    
    def get_symptom_reasoning(self, symptom: str) -> str:
        symptom_lower = symptom.lower()
        symptom_data = self.guidelines.get("symptom_mappings", {}).get(symptom_lower, {})
        return symptom_data.get("reasoning", "")
    
    def get_age_specific_tests(self, age: int) -> List[str]:
        additional_tests = []
        if age >= 50:
            age_data = self.guidelines.get("age_specific_recommendations", {}).get("above_50", {})
            additional_tests = age_data.get("additional_tests", [])
        elif age >= 40:
            age_data = self.guidelines.get("age_specific_recommendations", {}).get("above_40", {})
            additional_tests = age_data.get("additional_tests", [])
        return additional_tests
    
    def get_normal_range(self, test_name: str, parameter: str, gender: Optional[str] = None) -> str:
        test_info = self.get_test_info(test_name)
        if not test_info:
            return "No reference range available"
        
        ranges = test_info.get("normal_ranges", {})
        param_range = ranges.get(parameter, "")
        
        if isinstance(param_range, dict) and gender:
            return param_range.get(gender.lower(), "")
        return param_range if isinstance(param_range, str) else ""
    
    def get_test_interpretation_guide(self, test_name: str) -> str:
        test_info = self.get_test_info(test_name)
        return test_info.get("interpretation_guide", "") if test_info else ""
    
    def get_all_test_names(self) -> List[str]:
        return list(self.guidelines.get("tests", {}).keys())

guidelines = MedicalGuidelines()
