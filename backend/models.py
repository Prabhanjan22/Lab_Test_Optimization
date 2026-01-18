from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class PatientProfile(BaseModel):
    name: str
    age: int
    gender: str

class SymptomInput(BaseModel):
    symptoms: List[str]

class LabTestParameter(BaseModel):
    name: str
    value: float
    unit: str
    reference_range: str
    is_abnormal: bool

class LabResult(BaseModel):
    test_name: str
    parameters: List[LabTestParameter]
    test_date: datetime

class RecommendedTest(BaseModel):
    test_name: str
    reason: str
    status: str = "recommended"

class SkippedTest(BaseModel):
    test_name: str
    reason: str

class Interpretation(BaseModel):
    patient_friendly: str
    clinician_summary: str

class Visit(BaseModel):
    visit_id: str
    date: datetime
    symptoms: List[str]
    recommended_tests: List[RecommendedTest] = []
    skipped_tests: List[SkippedTest] = []
    lab_results: List[LabResult] = []
    interpretations: Optional[Interpretation] = None

class PatientDocument(BaseModel):
    patient_id: str
    profile: PatientProfile
    visits: List[Visit] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class PatientRegistrationRequest(BaseModel):
    profile: PatientProfile
    symptoms: List[str]

class LabResultUploadRequest(BaseModel):
    patient_id: str
    visit_id: str
    lab_results: List[LabResult]
