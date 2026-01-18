from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from models import (
    PatientRegistrationRequest,
    LabResultUploadRequest,
    Visit,
    RecommendedTest,
    SkippedTest,
    Interpretation
)
from database import (
    find_patient,
    insert_patient,
    add_visit_to_patient,
    update_patient,
    db_manager
)
from recommendation_engine import recommendation_engine
from datetime import datetime
import uuid

app = FastAPI(title="Lab Test Optimization System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    db_manager.connect()

@app.on_event("shutdown")
async def shutdown_event():
    db_manager.close()

@app.get("/")
async def root():
    return {"message": "Lab Test Optimization System API", "status": "running"}

@app.post("/api/patient/register")
async def register_patient_and_recommend(request: PatientRegistrationRequest):
    patient_id = str(uuid.uuid4())
    visit_id = str(uuid.uuid4())
    
    recommended_tests, skipped_tests = recommendation_engine.recommend_tests(
        patient_id=patient_id,
        symptoms=request.symptoms,
        age=request.profile.age,
        gender=request.profile.gender
    )
    
    visit = Visit(
        visit_id=visit_id,
        date=datetime.now(),
        symptoms=request.symptoms,
        recommended_tests=[RecommendedTest(**test) for test in recommended_tests],
        skipped_tests=[SkippedTest(**test) for test in skipped_tests]
    )
    
    patient_doc = {
        "patient_id": patient_id,
        "profile": request.profile.dict(),
        "visits": [visit.dict()],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    insert_patient(patient_doc)
    
    return {
        "patient_id": patient_id,
        "visit_id": visit_id,
        "recommended_tests": recommended_tests,
        "skipped_tests": skipped_tests
    }

@app.post("/api/patient/new-visit/{patient_id}")
async def create_new_visit(patient_id: str, symptoms: list[str]):
    patient = find_patient(patient_id)
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    visit_id = str(uuid.uuid4())
    
    recommended_tests, skipped_tests = recommendation_engine.recommend_tests(
        patient_id=patient_id,
        symptoms=symptoms,
        age=patient['profile']['age'],
        gender=patient['profile']['gender']
    )
    
    visit = Visit(
        visit_id=visit_id,
        date=datetime.now(),
        symptoms=symptoms,
        recommended_tests=[RecommendedTest(**test) for test in recommended_tests],
        skipped_tests=[SkippedTest(**test) for test in skipped_tests]
    )
    
    add_visit_to_patient(patient_id, visit.dict())
    
    return {
        "visit_id": visit_id,
        "recommended_tests": recommended_tests,
        "skipped_tests": skipped_tests
    }

@app.post("/api/lab-results/upload")
async def upload_lab_results(request: LabResultUploadRequest):
    patient = find_patient(request.patient_id)
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    visit_found = False
    for visit in patient.get('visits', []):
        if visit['visit_id'] == request.visit_id:
            visit_found = True
            break
    
    if not visit_found:
        raise HTTPException(status_code=404, detail="Visit not found")
    
    interpretations_dict = {}
    
    for lab_result in request.lab_results:
        interpretation = recommendation_engine.interpret_results(
            test_name=lab_result.test_name,
            parameters=[p.dict() for p in lab_result.parameters]
        )
        
        interpretations_dict[lab_result.test_name] = interpretation
    
    combined_interpretation = Interpretation(
        patient_friendly="\n\n".join([f"**{test}**: {interp['patient_friendly']}" for test, interp in interpretations_dict.items()]),
        clinician_summary="\n\n".join([f"**{test}**: {interp['clinician_summary']}" for test, interp in interpretations_dict.items()])
    )
    
    from pymongo import ReturnDocument
    collection = db_manager.get_collection("patients")
    
    updated_patient = collection.find_one_and_update(
        {"patient_id": request.patient_id, "visits.visit_id": request.visit_id},
        {
            "$set": {
                "visits.$.lab_results": [r.dict() for r in request.lab_results],
                "visits.$.interpretations": combined_interpretation.dict()
            }
        },
        return_document=ReturnDocument.AFTER
    )
    
    return {
        "message": "Lab results uploaded successfully",
        "interpretations": combined_interpretation
    }

@app.get("/api/patient/{patient_id}")
async def get_patient_data(patient_id: str):
    patient = find_patient(patient_id)
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient['_id'] = str(patient['_id'])
    
    return patient

@app.get("/api/patient/{patient_id}/visit/{visit_id}")
async def get_visit_data(patient_id: str, visit_id: str):
    patient = find_patient(patient_id)
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    for visit in patient.get('visits', []):
        if visit['visit_id'] == visit_id:
            return visit
    
    raise HTTPException(status_code=404, detail="Visit not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
