const API_BASE_URL = 'http://localhost:8000';

let currentPatientId = '';
let currentVisitId = '';
let recommendedTests = [];

const testParameters = {
    'CBC': [
        { name: 'hemoglobin', unit: 'g/dL', normalRange: '13.5-17.5 (M), 12.0-15.5 (F)' },
        { name: 'wbc', unit: 'cells/mcL', normalRange: '4,000-11,000' },
        { name: 'platelets', unit: 'cells/mcL', normalRange: '150,000-400,000' }
    ],
    'CRP': [
        { name: 'crp', unit: 'mg/L', normalRange: '< 3.0' }
    ],
    'Blood_Glucose': [
        { name: 'glucose', unit: 'mg/dL', normalRange: '70-100 (fasting)' }
    ],
    'Lipid_Profile': [
        { name: 'total_cholesterol', unit: 'mg/dL', normalRange: '< 200' },
        { name: 'ldl', unit: 'mg/dL', normalRange: '< 100' },
        { name: 'hdl', unit: 'mg/dL', normalRange: '> 40 (M), > 50 (F)' },
        { name: 'triglycerides', unit: 'mg/dL', normalRange: '< 150' }
    ],
    'Thyroid_Panel': [
        { name: 'tsh', unit: 'mIU/L', normalRange: '0.4-4.0' },
        { name: 't3', unit: 'ng/dL', normalRange: '80-200' },
        { name: 't4', unit: 'mcg/dL', normalRange: '5.0-12.0' }
    ],
    'Liver_Function': [
        { name: 'alt', unit: 'U/L', normalRange: '7-56' },
        { name: 'ast', unit: 'U/L', normalRange: '10-40' },
        { name: 'bilirubin', unit: 'mg/dL', normalRange: '0.1-1.2' }
    ],
    'Kidney_Function': [
        { name: 'creatinine', unit: 'mg/dL', normalRange: '0.7-1.3 (M), 0.6-1.1 (F)' },
        { name: 'bun', unit: 'mg/dL', normalRange: '7-20' }
    ],
    'Vitamin_D': [
        { name: 'vitamin_d', unit: 'ng/mL', normalRange: '30-100' }
    ]
};

document.getElementById('patient-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('patient-name').value;
    const age = parseInt(document.getElementById('patient-age').value);
    const gender = document.getElementById('patient-gender').value;
    const symptomsText = document.getElementById('symptoms').value;

    const symptoms = symptomsText.split(',').map(s => s.trim().toLowerCase());

    const requestData = {
        profile: {
            name: name,
            age: age,
            gender: gender
        },
        symptoms: symptoms
    };

    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/api/patient/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error('Failed to register patient');
        }

        const data = await response.json();

        currentPatientId = data.patient_id;
        currentVisitId = data.visit_id;
        recommendedTests = data.recommended_tests;

        displayRecommendations(data);

        hideLoading();
        document.getElementById('registration-section').classList.add('hidden');
        document.getElementById('recommendations-section').classList.remove('hidden');

    } catch (error) {
        hideLoading();
        alert('Error: ' + error.message);
    }
});

function displayRecommendations(data) {
    document.getElementById('display-patient-id').textContent = data.patient_id;
    document.getElementById('display-visit-id').textContent = data.visit_id;

    const recommendedList = document.getElementById('recommended-tests-list');
    recommendedList.innerHTML = '';

    if (data.recommended_tests.length === 0) {
        recommendedList.innerHTML = '<p>No new tests recommended at this time.</p>';
    } else {
        data.recommended_tests.forEach(test => {
            const card = document.createElement('div');
            card.className = 'test-card';
            card.innerHTML = `
                <h4>${test.test_name}</h4>
                <p>${test.reason}</p>
            `;
            recommendedList.appendChild(card);
        });
    }

    if (data.skipped_tests && data.skipped_tests.length > 0) {
        document.getElementById('skipped-tests-container').classList.remove('hidden');
        const skippedList = document.getElementById('skipped-tests-list');
        skippedList.innerHTML = '';

        data.skipped_tests.forEach(test => {
            const card = document.createElement('div');
            card.className = 'test-card skipped-card';
            card.innerHTML = `
                <h4>${test.test_name}</h4>
                <p>${test.reason}</p>
            `;
            skippedList.appendChild(card);
        });
    }
}

function showLabUploadSection() {
    document.getElementById('recommendations-section').classList.add('hidden');
    document.getElementById('lab-upload-section').classList.remove('hidden');
}

function backToRecommendations() {
    document.getElementById('lab-upload-section').classList.add('hidden');
    document.getElementById('recommendations-section').classList.remove('hidden');
}

document.getElementById('test-select').addEventListener('change', (e) => {
    const testName = e.target.value;
    const container = document.getElementById('parameters-input-container');

    if (!testName) {
        container.innerHTML = '';
        return;
    }

    const parameters = testParameters[testName];

    container.innerHTML = '<h3>Enter Test Results</h3>';

    parameters.forEach((param, index) => {
        const paramDiv = document.createElement('div');
        paramDiv.className = 'parameter-input';
        paramDiv.innerHTML = `
            <div class="parameter-row">
                <div class="form-group">
                    <label>${param.name}</label>
                    <input type="text" value="${param.name}" disabled>
                </div>
                <div class="form-group">
                    <label>Value</label>
                    <input type="number" step="0.01" id="param-value-${index}" required>
                </div>
                <div class="form-group">
                    <label>Unit</label>
                    <input type="text" value="${param.unit}" disabled>
                </div>
                <div class="form-group">
                    <label>Normal Range</label>
                    <input type="text" value="${param.normalRange}" disabled>
                </div>
            </div>
        `;
        container.appendChild(paramDiv);
    });
});

async function submitLabResults() {
    const testName = document.getElementById('test-select').value;

    if (!testName) {
        alert('Please select a test');
        return;
    }

    const parameters = testParameters[testName];
    const labParameters = [];

    for (let i = 0; i < parameters.length; i++) {
        const valueInput = document.getElementById(`param-value-${i}`);
        const value = parseFloat(valueInput.value);

        if (isNaN(value)) {
            alert(`Please enter a valid value for ${parameters[i].name}`);
            return;
        }

        const isAbnormal = checkIfAbnormal(parameters[i].name, value, parameters[i].normalRange);

        labParameters.push({
            name: parameters[i].name,
            value: value,
            unit: parameters[i].unit,
            reference_range: parameters[i].normalRange,
            is_abnormal: isAbnormal
        });
    }

    const requestData = {
        patient_id: currentPatientId,
        visit_id: currentVisitId,
        lab_results: [{
            test_name: testName,
            parameters: labParameters,
            test_date: new Date().toISOString()
        }]
    };

    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/api/lab-results/upload`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error('Failed to upload lab results');
        }

        const data = await response.json();

        displayInterpretations(data.interpretations);

        hideLoading();
        document.getElementById('lab-upload-section').classList.add('hidden');
        document.getElementById('interpretation-section').classList.remove('hidden');

    } catch (error) {
        hideLoading();
        alert('Error: ' + error.message);
    }
}

function checkIfAbnormal(paramName, value, normalRange) {
    const rangeText = normalRange.toLowerCase();

    if (rangeText.includes('<')) {
        const threshold = parseFloat(rangeText.replace(/[^0-9.]/g, ''));
        return value >= threshold;
    }

    if (rangeText.includes('>')) {
        const threshold = parseFloat(rangeText.replace(/[^0-9.]/g, ''));
        return value <= threshold;
    }

    const numbers = rangeText.match(/[\d.]+/g);
    if (numbers && numbers.length >= 2) {
        const min = parseFloat(numbers[0]);
        const max = parseFloat(numbers[1]);
        return value < min || value > max;
    }

    return false;
}

function displayInterpretations(interpretations) {
    document.getElementById('patient-interpretation').innerHTML =
        interpretations.patient_friendly.replace(/\*\*/g, '<br><strong>').replace(/\n\n/g, '<br><br>');

    document.getElementById('clinician-interpretation').innerHTML =
        interpretations.clinician_summary.replace(/\*\*/g, '<br><strong>').replace(/\n\n/g, '<br><br>');
}

function resetForm() {
    document.getElementById('patient-form').reset();
    document.getElementById('registration-section').classList.remove('hidden');
    document.getElementById('recommendations-section').classList.add('hidden');
    document.getElementById('lab-upload-section').classList.add('hidden');
    document.getElementById('interpretation-section').classList.add('hidden');

    currentPatientId = '';
    currentVisitId = '';
    recommendedTests = [];
}

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}
