# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies
```bash
cd n:\Projects\labopti\backend
pip install -r requirements.txt
```

### Step 2: Configure API Key
1. Copy `.env.example` to `.env`
2. Add your Groq API key:
```
GROQ_API_KEY=your_key_here
```
Get a free API key at: https://console.groq.com/

### Step 3: Start MongoDB
```bash
# Windows
net start MongoDB

# Or if MongoDB is not installed, download from:
# https://www.mongodb.com/try/download/community
```

### Step 4: Run Backend
```bash
cd n:\Projects\labopti\backend
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
Connected to MongoDB: labopti
```

### Step 5: Open Frontend
Open `n:\Projects\labopti\frontend\index.html` in your browser

OR serve it properly:
```bash
cd n:\Projects\labopti\frontend
python -m http.server 8080
```
Then visit: http://localhost:8080

## 🧪 Test the System

### Example 1: Young Patient with Fever
1. Enter patient data:
   - Name: John Doe
   - Age: 28
   - Gender: Male
   - Symptoms: `fever, weakness`

2. Click "Submit & Get Recommendations"

3. Expected result: CBC and CRP recommended

### Example 2: Upload Lab Results
1. Click "Upload Lab Results"
2. Select "Complete Blood Count (CBC)"
3. Enter values:
   - hemoglobin: 11.5
   - wbc: 12500
   - platelets: 250000
4. Click "Submit Lab Results"
5. View AI-generated interpretations

## 📖 Full Documentation

See [README.md](file:///n:/Projects/labopti/README.md) for complete setup guide and technical details.

## ⚠️ Troubleshooting

**Can't connect to MongoDB?**
- Check if MongoDB is running: `mongod --version`
- Verify connection string in `.env`

- Ensure Groq API key is correct in `.env`
- Check API quota at https://console.groq.com

**CORS error?**
- Don't open HTML file directly (file://)
- Use Python HTTP server as shown above
