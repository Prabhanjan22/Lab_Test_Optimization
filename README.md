# Lab Test Optimization System

A simple, end-to-end system for optimizing lab test recommendations using rule-based logic and RAG (Retrieval Augmented Generation) for medical explanations.

## 🎯 Project Overview

This system helps reduce unnecessary lab tests by:
- Analyzing patient symptoms and recommending appropriate tests
- Checking past test history to avoid redundant testing
- Providing AI-generated explanations for recommendations
- Interpreting lab results with patient-friendly and clinical summaries

## 🏗️ System Architecture

```
┌─────────────────┐
│   Frontend      │
│  (HTML/CSS/JS)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI       │
│   Backend       │
└────────┬────────┘
         │
    ┌────┴────┬──────────────┐
    │         │              │
    ▼         ▼              ▼
┌────────┐ ┌──────┐  ┌──────────────┐
│MongoDB │ │ RAG  │  │ Recommendation│
│        │ │System│  │    Engine     │
└────────┘ └──┬───┘  └──────────────┘
              │
              ▼
       ┌──────────────┐
       │  Groq API   │
       │     API      │
       └──────────────┘
```

## 📁 Project Structure

```
labopti/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── database.py                # MongoDB connection
│   ├── models.py                  # Pydantic models
│   ├── rag_system.py              # RAG implementation
│   ├── recommendation_engine.py   # Test recommendation logic
│   ├── medical_guidelines.py      # Guidelines helper
│   └── requirements.txt           # Python dependencies
├── frontend/
│   ├── index.html                 # Web interface
│   ├── styles.css                 # Styling
│   └── script.js                  # Frontend logic
├── data/
│   └── guidelines.json            # Medical guidelines
├── .env.example                   # Environment template
└── README.md                      # This file
```

## 🚀 Setup Instructions

### Prerequisites

1. **Python 3.9+** installed
2. **MongoDB** installed and running locally
3. **Groq API Key** ([Get one free here](https://console.groq.com/))

### Step 1: Clone/Navigate to Project

```bash
cd n:\Projects\labopti
```

### Step 2: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=labopti
GROQ_API_KEY=your_actual_groq_api_key_here
```

### Step 4: Start MongoDB

Make sure MongoDB is running on your system:

```bash
# Windows
net start MongoDB

# Linux/Mac
sudo systemctl start mongod
```

### Step 5: Run Backend Server

```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

### Step 6: Open Frontend

Open `frontend/index.html` in your web browser, or serve it using a local server:

```bash
# Using Python
cd frontend
python -m http.server 8080
```

Then navigate to `http://localhost:8080`

## 📝 Usage Guide

### 1. Patient Registration & Symptom Input

- Enter patient name, age, and gender
- Input symptoms (comma-separated, e.g., "fever, fatigue, weakness")
- Click "Submit & Get Recommendations"

### 2. View Recommendations

The system will display:
- **Recommended Tests**: Tests that should be done based on symptoms
- **Skipped Tests**: Tests that were recently done and are still valid
- Each test includes an AI-generated explanation

### 3. Upload Lab Results

- Click "Upload Lab Results"
- Select the test from dropdown
- Enter parameter values
- System automatically detects abnormal values
- Click "Submit Lab Results"

### 4. View Interpretation

Two interpretations are generated:
- **Patient-Friendly**: Simple explanation in layman's terms
- **Clinician Summary**: Technical analysis for healthcare providers

## 🧠 How RAG Works

### RAG Workflow

1. **Retrieval**: System retrieves relevant medical guidelines from `guidelines.json`
2. **Augmentation**: Retrieved context is added to the LLM prompt
3.- ✅ RAG system using Groq LLaMA generates explanations using ONLY the provided context

### Prompt Templates

**Test Recommendation Explanation**:
```
Context: [Retrieved guideline text]
Patient: {age} years, {gender}, Symptoms: {symptoms}

Based strictly on the provided context, explain why {test_name} 
is recommended for this patient.
```

**Test Skip Explanation**:
```
Context: [Past test history]
Patient: {age} years, {gender}

Explain why {test_name} can be skipped based on recent test history.
```

**Lab Result Interpretation**:
```
Context: [Test guidelines]
Lab Results: [Abnormal values]

Provide:
1. Patient-friendly explanation
2. Clinician technical summary
```

## 🔧 Technical Details

### MongoDB Schema

**Collection**: `patients`

```json
{
  "patient_id": "uuid",
  "profile": {
    "name": "string",
    "age": "number",
    "gender": "string"
  },
  "visits": [
    {
      "visit_id": "uuid",
      "date": "datetime",
      "symptoms": ["symptom1", "symptom2"],
      "recommended_tests": [
        {
          "test_name": "string",
          "reason": "RAG-generated explanation",
          "status": "recommended"
        }
      ],
      "skipped_tests": [
        {
          "test_name": "string",
          "reason": "RAG-generated explanation"
        }
      ],
      "lab_results": [
        {
          "test_name": "string",
          "parameters": [
            {
              "name": "string",
              "value": "number",
              "unit": "string",
              "reference_range": "string",
              "is_abnormal": "boolean"
            }
          ],
          "test_date": "datetime"
        }
      ],
      "interpretations": {
        "patient_friendly": "string",
        "clinician_summary": "string"
      }
    }
  ]
}
```

### Recommendation Logic

```python
1. Map symptoms to candidate tests
2. Add age-specific tests (e.g., lipid profile for age > 40)
3. For each test:
   - Check last test date from patient history
   - Get test validity period (e.g., CBC valid for 90 days)
   - If test still valid → Skip with explanation
   - If test expired/never done → Recommend with explanation
4. Generate RAG-based explanations for all decisions
```

### Available Tests

- **CBC** (Complete Blood Count) - 90 days validity
- **CRP** (C-Reactive Protein) - 30 days validity
- **Blood Glucose** - 180 days validity
- **Lipid Profile** - 365 days validity
- **Thyroid Panel** (TSH, T3, T4) - 180 days validity
- **Liver Function Tests** - 90 days validity
- **Kidney Function Tests** - 90 days validity
- **Vitamin D** - 180 days validity

## 🧪 Testing the System

### Sample Test Case 1: New Patient with Fever

**Input**:
- Name: John Doe
- Age: 35
- Gender: Male
- Symptoms: fever, fatigue

**Expected Output**:
- Recommended: CBC, CRP
- Explanations based on fever and inflammation guidelines

### Sample Test Case 2: Repeat Visit

**Input**:
- Same patient revisits after 30 days
- Symptoms: fever, headache

**Expected Output**:
- Recommended: CRP (expired after 30 days)
- Skipped: CBC (still valid, done 30 days ago)
- Explanation: "Your CBC test from [date] is still valid for 60 more days..."

## 📚 API Endpoints

```
POST /api/patient/register
- Register new patient and get recommendations

POST /api/patient/new-visit/{patient_id}
- Create new visit for existing patient

POST /api/lab-results/upload
- Upload lab results and get interpretations

GET /api/patient/{patient_id}
- Get complete patient data

GET /api/patient/{patient_id}/visit/{visit_id}
- Get specific visit data
```

## 🎓 Academic Notes

### Key Features for Viva

1. **Simplicity**: Single database, clear architecture
2. **Explainability**: All decisions explained using RAG
3. **No Hallucinations**: LLM uses ONLY provided context
4. **Rule-Based**: Medical decisions made by rules, not AI
5. **Complete Workflow**: End-to-end patient journey tracking

### System Strengths

- Clear separation between rules (medical decisions) and AI (explanations)
- Complete audit trail in MongoDB
- No complex microservices or distributed systems
- Easy to understand and explain
- Follows medical best practices

### Limitations

- Single-user system (not multi-tenant)
- Simple rule-based logic (not ML-based predictions)
- Limited to predefined symptom-test mappings
- Requires manual guideline updates

## 🔒 Important Notes

- **Not for Production**: This is an academic/research project
- **Medical Disclaimer**: Not a substitute for professional medical advice
- **API Key**: Keep your Gemini API key secure
- **Data Privacy**: Patient data stored locally in MongoDB

## 🛠️ Troubleshooting

**MongoDB Connection Error**:
- Ensure MongoDB is running
- Check `MONGODB_URI` in `.env`

**API Key Error**:
- Verify Gemini API key in `.env`
- Check API quota/limits

**CORS Error**:
- Use a proper web server instead of file://
- Backend has CORS enabled for all origins

**No Recommendations**:
- Check if symptoms match predefined mappings
- Default recommendation is CBC if no matches

## 📞 Support

For questions or issues, refer to:
- MongoDB docs: https://docs.mongodb.com
- FastAPI docs: https://fastapi.tiangolo.com
- Gemini API docs: https://ai.google.dev

---

**Built for Academic Research | Lab Test Optimization System v1.0**
