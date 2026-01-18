from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from medical_guidelines import guidelines
from rag_system import rag_system
from database import find_patient

class RecommendationEngine:
    def __init__(self):
        self.guidelines = guidelines
    
    def _map_symptoms_to_tests(self, symptoms: List[str]) -> List[str]:
        candidate_tests = set()
        
        for symptom in symptoms:
            tests = self.guidelines.get_tests_for_symptom(symptom)
            candidate_tests.update(tests)
        
        return list(candidate_tests)
    
    def _add_age_specific_tests(self, tests: List[str], age: int) -> List[str]:
        age_specific = self.guidelines.get_age_specific_tests(age)
        
        combined = set(tests)
        combined.update(age_specific)
        
        return list(combined)
    
    def _get_last_test_date(self, patient_id: str, test_name: str) -> datetime | None:
        patient = find_patient(patient_id)
        
        if not patient or 'visits' not in patient:
            return None
        
        for visit in reversed(patient['visits']):
            if 'lab_results' in visit:
                for result in visit['lab_results']:
                    if result['test_name'] == test_name:
                        return datetime.fromisoformat(result['test_date']) if isinstance(result['test_date'], str) else result['test_date']
        
        return None
    
    def _is_test_still_valid(self, last_test_date: datetime, validity_days: int) -> bool:
        if not last_test_date:
            return False
        
        validity_period = timedelta(days=validity_days)
        return datetime.now() - last_test_date < validity_period
    
    def recommend_tests(
        self,
        patient_id: str,
        symptoms: List[str],
        age: int,
        gender: str
    ) -> Tuple[List[Dict], List[Dict]]:
        
        candidate_tests = self._map_symptoms_to_tests(symptoms)
        
        candidate_tests = self._add_age_specific_tests(candidate_tests, age)
        
        if not candidate_tests:
            candidate_tests = ["CBC"]
        
        recommended_tests = []
        skipped_tests = []
        
        for test_name in candidate_tests:
            last_test_date = self._get_last_test_date(patient_id, test_name)
            validity_days = self.guidelines.get_test_validity_days(test_name)
            
            if last_test_date and self._is_test_still_valid(last_test_date, validity_days):
                skip_reason = rag_system.explain_test_skip(
                    test_name,
                    last_test_date.strftime("%Y-%m-%d"),
                    validity_days
                )
                
                skipped_tests.append({
                    "test_name": test_name,
                    "reason": skip_reason,
                    "last_test_date": last_test_date.isoformat()
                })
            else:
                recommendation_reason = rag_system.explain_test_recommendation(
                    test_name,
                    symptoms,
                    age,
                    gender
                )
                
                recommended_tests.append({
                    "test_name": test_name,
                    "reason": recommendation_reason,
                    "status": "recommended"
                })
        
        return recommended_tests, skipped_tests
    
    def interpret_results(self, test_name: str, parameters: List[Dict]) -> Dict[str, str]:
        abnormal_params = [p for p in parameters if p.get('is_abnormal', False)]
        
        if not abnormal_params:
            return {
                "patient_friendly": "All test values are within normal range. This is a good result.",
                "clinician_summary": "All parameters within reference ranges. No abnormalities detected."
            }
        
        return rag_system.interpret_lab_results(test_name, abnormal_params)

recommendation_engine = RecommendationEngine()
