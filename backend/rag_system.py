from groq import Groq
import os
from dotenv import load_dotenv
from medical_guidelines import guidelines
from typing import List, Dict

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class RAGSystem:
    def __init__(self):
        pass
    
    def _retrieve_context(self, test_name: str, context_type: str = "general") -> str:
        test_info = guidelines.get_test_info(test_name)
        
        if not test_info:
            return f"No guideline information available for {test_name}"
        
        context = f"""
Test Name: {test_info.get('full_name', test_name)}
Description: {test_info.get('description', '')}
Indications: {test_info.get('indications', '')}
Interpretation Guide: {test_info.get('interpretation_guide', '')}
"""
        
        if context_type == "interpretation":
            ranges = test_info.get('normal_ranges', {})
            context += f"\nNormal Ranges: {ranges}"
        
        return context.strip()
    
    def explain_test_recommendation(self, test_name: str, symptoms: List[str], age: int, gender: str) -> str:
        context = self._retrieve_context(test_name, "general")
        
        symptom_reasoning = ""
        for symptom in symptoms:
            reasoning = guidelines.get_symptom_reasoning(symptom)
            if reasoning:
                symptom_reasoning += f"- {symptom}: {reasoning}\n"
        
        prompt = f"""
You are a medical assistant explaining lab test recommendations to patients.

CONTEXT FROM MEDICAL GUIDELINES:
{context}

SYMPTOM-BASED REASONING:
{symptom_reasoning}

PATIENT INFORMATION:
- Age: {age} years
- Gender: {gender}
- Symptoms: {', '.join(symptoms)}

Based STRICTLY on the provided context, explain in 2-3 sentences why {test_name} is recommended for this patient.
Use simple, patient-friendly language. Do not add information beyond the context provided.
"""
        
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a medical assistant explaining lab test recommendations to patients."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Unable to generate explanation: {str(e)}"
    
    def explain_test_skip(self, test_name: str, last_test_date: str, validity_days: int) -> str:
        context = self._retrieve_context(test_name, "general")
        
        prompt = f"""
You are a medical assistant explaining to a patient why a lab test can be skipped.

TEST INFORMATION:
{context}

PATIENT HISTORY:
- Last {test_name} was done on: {last_test_date}
- Test validity period: {validity_days} days
- Current recommendation: Skip this test

Explain in 2-3 sentences why this test can be skipped based on the recent test history.
Use simple, reassuring language. Mention that the previous test is still valid.
"""
        
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a medical assistant explaining to patients why lab tests can be skipped."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Test was recently done on {last_test_date} and is still valid for {validity_days} days."
    
    def interpret_lab_results(self, test_name: str, abnormal_parameters: List[Dict]) -> Dict[str, str]:
        context = self._retrieve_context(test_name, "interpretation")
        
        abnormal_summary = "\n".join([
            f"- {p['name']}: {p['value']} {p['unit']} (Normal: {p['reference_range']})"
            for p in abnormal_parameters
        ])
        
        patient_prompt = f"""
You are a medical assistant explaining lab results to a patient.

TEST INFORMATION:
{context}

ABNORMAL VALUES:
{abnormal_summary}

Provide a patient-friendly explanation (3-4 sentences) of what these abnormal values mean.
Use simple language, avoid medical jargon. Be reassuring but accurate.
Based STRICTLY on the provided context.
"""
        
        clinician_prompt = f"""
You are providing a technical summary for a clinician.

TEST INFORMATION:
{context}

ABNORMAL VALUES:
{abnormal_summary}

Provide a concise clinical summary (3-4 sentences) of the findings and their significance.
Use medical terminology. Suggest possible differential diagnoses if relevant.
Based STRICTLY on the provided context.
"""
        
        try:
            patient_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a medical assistant explaining lab results to patients in simple language."},
                    {"role": "user", "content": patient_prompt}
                ],
                temperature=0.3,
                max_tokens=600
            )
            
            clinician_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are providing technical medical summaries for clinicians."},
                    {"role": "user", "content": clinician_prompt}
                ],
                temperature=0.3,
                max_tokens=600
            )
            
            return {
                "patient_friendly": patient_response.choices[0].message.content.strip(),
                "clinician_summary": clinician_response.choices[0].message.content.strip()
            }
        except Exception as e:
            return {
                "patient_friendly": f"Some test values are outside the normal range. Please consult your doctor for detailed interpretation.",
                "clinician_summary": f"Error generating interpretation: {str(e)}"
            }
    
    def batch_explain_recommendations(self, tests: List[str], symptoms: List[str], age: int, gender: str) -> Dict[str, str]:
        explanations = {}
        for test in tests:
            explanations[test] = self.explain_test_recommendation(test, symptoms, age, gender)
        return explanations

rag_system = RAGSystem()
