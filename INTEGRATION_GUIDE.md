# ML Prediction API Integration Guide

This guide shows how to integrate the Disease Predictor ML API into your frontend application.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Disease Selection Flow](#disease-selection-flow)
3. [Symptom Loading](#symptom-loading)
4. [Making Predictions](#making-predictions)
5. [Displaying Results](#displaying-results)
6. [Error Handling](#error-handling)
7. [Complete Example](#complete-example)

---

## Quick Start

### Minimal Working Example

```html
<!DOCTYPE html>
<html>
<body>
  <select id="disease-select">
    <option value="">Select a disease</option>
  </select>
  
  <div id="symptoms"></div>
  
  <button onclick="predict()">Predict</button>
  <div id="results"></div>

  <script>
    let selectedSymptoms = [];

    // Load available diseases on page load
    async function loadDiseases() {
      const resp = await fetch('/api/diseases/list');
      const data = await resp.json();
      const select = document.getElementById('disease-select');
      
      data.diseases.forEach(disease => {
        const option = document.createElement('option');
        option.value = disease;
        option.text = disease.replace('_', ' ').toUpperCase();
        select.appendChild(option);
      });
    }

    // Load symptoms when disease is selected
    document.getElementById('disease-select').addEventListener('change', loadSymptoms);
    
    async function loadSymptoms(event) {
      const disease = event.target.value;
      if (!disease) return;
      
      const resp = await fetch(`/api/disease/${disease}/symptoms`);
      const data = await resp.json();
      
      const container = document.getElementById('symptoms');
      container.innerHTML = '';
      
      Object.entries(data.symptoms).forEach(([key, name]) => {
        const label = document.createElement('label');
        const input = document.createElement('input');
        input.type = 'checkbox';
        input.value = key;
        input.onchange = (e) => {
          if (e.target.checked) {
            selectedSymptoms.push(key);
          } else {
            selectedSymptoms = selectedSymptoms.filter(s => s !== key);
          }
        };
        label.appendChild(input);
        label.appendChild(document.createTextNode(name));
        container.appendChild(label);
      });
    }

    // Make prediction
    async function predict() {
      const disease = document.getElementById('disease-select').value;
      
      const resp = await fetch('/api/predict/disease', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          disease,
          symptoms: selectedSymptoms
        })
      });
      
      const data = await resp.json();
      const pred = data.prediction;
      
      document.getElementById('results').innerHTML = `
        <h3>${disease}</h3>
        <p>Probability: ${(pred.calibrated_probability * 100).toFixed(1)}%</p>
      `;
    }

    loadDiseases();
  </script>
</body>
</html>
```

---

## Disease Selection Flow

### 1. Load Available Diseases

When your page loads, fetch the list of available diseases:

```javascript
async function initializeDiseaseSelector() {
  try {
    const response = await fetch('/api/diseases/list');
    
    if (!response.ok) {
      console.error('Failed to load diseases');
      return;
    }
    
    const data = await response.json();
    
    if (data.success) {
      populateDiseaseDropdown(data.diseases);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

function populateDiseaseDropdown(diseases) {
  const select = document.getElementById('disease-select');
  
  diseases.forEach(disease => {
    const option = document.createElement('option');
    option.value = disease;
    option.textContent = disease.replace('_', ' ').toUpperCase();
    select.appendChild(option);
  });
}

// Run on page load
document.addEventListener('DOMContentLoaded', initializeDiseaseSelector);
```

---

## Symptom Loading

### 2. Load Symptoms for Selected Disease

When a disease is selected, load its symptoms dynamically:

```javascript
async function loadSymptoms(disease) {
  // Show loading state
  const container = document.getElementById('symptoms-container');
  container.innerHTML = '<p>Loading symptoms...</p>';
  
  try {
    const response = await fetch(`/api/disease/${disease}/symptoms`);
    const data = await response.json();
    
    if (!data.success) {
      container.innerHTML = `<p class="error">${data.error}</p>`;
      return;
    }
    
    renderSymptoms(data.symptoms);
    
  } catch (error) {
    console.error('Error loading symptoms:', error);
    container.innerHTML = '<p class="error">Failed to load symptoms</p>';
  }
}

function renderSymptoms(symptomsData) {
  const container = document.getElementById('symptoms-container');
  container.innerHTML = '';
  
  // symptomsData is an object: { "fever": "Fever", "cough": "Cough", ... }
  Object.entries(symptomsData).forEach(([symptomKey, symptomName]) => {
    const div = document.createElement('div');
    div.className = 'symptom-item';
    
    const input = document.createElement('input');
    input.type = 'checkbox';
    input.id = `symptom-${symptomKey}`;
    input.value = symptomKey;
    input.onchange = onSymptomToggle;
    
    const label = document.createElement('label');
    label.htmlFor = `symptom-${symptomKey}`;
    label.textContent = symptomName;
    
    div.appendChild(input);
    div.appendChild(label);
    container.appendChild(div);
  });
  
  updateSymptomCount();
}

// Track selected symptoms
let selectedSymptoms = [];

function onSymptomToggle(event) {
  const symptomKey = event.target.value;
  
  if (event.target.checked) {
    selectedSymptoms.push(symptomKey);
  } else {
    selectedSymptoms = selectedSymptoms.filter(s => s !== symptomKey);
  }
  
  updateSymptomCount();
}

function updateSymptomCount() {
  const count = selectedSymptoms.length;
  document.getElementById('symptom-count').textContent = 
    `${count} symptom${count !== 1 ? 's' : ''} selected`;
}
```

---

## Making Predictions

### 3. Send Prediction Request

Create a function to send selected symptoms and get predictions:

```javascript
async function predictDisease() {
  const disease = document.getElementById('disease-select').value;
  
  // Validate inputs
  if (!disease) {
    alert('Please select a disease');
    return;
  }
  
  if (selectedSymptoms.length === 0) {
    alert('Please select at least one symptom');
    return;
  }
  
  // Optional: Get demographic data
  const age = document.getElementById('age-input')?.value;
  const height = document.getElementById('height-input')?.value;
  const weight = document.getElementById('weight-input')?.value;
  
  // Show loading
  showLoading(true);
  
  try {
    const response = await fetch('/api/predict/disease', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        disease,
        symptoms: selectedSymptoms,
        age: age ? parseInt(age) : null,
        height: height ? parseInt(height) : null,
        weight: weight ? parseInt(weight) : null
      })
    });
    
    const data = await response.json();
    
    if (!response.ok || !data.success) {
      showError(data.error || 'Prediction failed');
      return;
    }
    
    displayPredictionResults(data.prediction);
    
  } catch (error) {
    console.error('Prediction error:', error);
    showError('Failed to connect to server');
  } finally {
    showLoading(false);
  }
}

function showLoading(isLoading) {
  const loader = document.getElementById('loading');
  if (loader) {
    loader.style.display = isLoading ? 'block' : 'none';
  }
}

function showError(message) {
  const errorDiv = document.getElementById('error-message');
  if (errorDiv) {
    errorDiv.style.display = 'block';
    errorDiv.textContent = `Error: ${message}`;
  }
}
```

---

## Displaying Results

### 4. Show Results to User

Format and display the prediction results:

```javascript
function displayPredictionResults(prediction) {
  const resultsDiv = document.getElementById('results-container');
  
  // Calculate risk level
  const probability = prediction.calibrated_probability;
  let riskLevel = 'Low';
  let riskColor = '#4CAF50'; // green
  
  if (probability >= 0.85) {
    riskLevel = 'Very High';
    riskColor = '#D32F2F'; // red
  } else if (probability >= 0.60) {
    riskLevel = 'High';
    riskColor = '#F57C00'; // orange
  } else if (probability >= 0.30) {
    riskLevel = 'Moderate';
    riskColor = '#FBC02D'; // yellow
  }
  
  // Build result HTML
  const html = `
    <div class="results-card">
      <h2>${prediction.disease.toUpperCase()}</h2>
      
      <div class="probability-display">
        <div class="probability-bar" style="background: ${riskColor}; width: ${probability * 100}%">
          ${(probability * 100).toFixed(1)}%
        </div>
      </div>
      
      <div class="risk-badge" style="background: ${riskColor}">
        ${riskLevel} Risk
      </div>
      
      <div class="details">
        <p><strong>Calibrated Probability:</strong> ${(probability * 100).toFixed(1)}%</p>
        <p><strong>Symptoms Matched:</strong> ${prediction.symptoms_matched || 0} of ${prediction.total_symptoms || 0}</p>
        
        ${prediction.bmi ? `
          <p><strong>BMI:</strong> ${prediction.bmi.toFixed(1)} (${prediction.bmi_category})</p>
        ` : ''}
      </div>
      
      <div class="disclaimer">
        <p><strong>⚠️ Disclaimer:</strong> This is an AI-based prediction for educational purposes only. 
        Please consult with a healthcare professional for accurate diagnosis and treatment.</p>
      </div>
    </div>
  `;
  
  resultsDiv.innerHTML = html;
  resultsDiv.style.display = 'block';
}
```

### 5. Get Multiple Disease Predictions

If you want to show top predictions for symptoms:

```javascript
async function predictMultipleDiseases() {
  if (selectedSymptoms.length === 0) {
    alert('Please select at least one symptom');
    return;
  }
  
  try {
    const response = await fetch('/api/predict/multiple', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        symptoms: selectedSymptoms,
        age: document.getElementById('age-input')?.value
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      displayMultiplePredictions(data.predictions);
    }
    
  } catch (error) {
    console.error('Error:', error);
  }
}

function displayMultiplePredictions(predictions) {
  const container = document.getElementById('top-diseases');
  
  let html = '<h3>Top Possible Conditions</h3><ol>';
  
  predictions.slice(0, 5).forEach((pred, index) => {
    const percent = (pred.calibrated_probability * 100).toFixed(1);
    html += `
      <li>
        <strong>${pred.disease}</strong>: ${percent}%
        <div style="width: 100%; background: #eee; border-radius: 3px;">
          <div style="width: ${percent}%; background: #4CAF50; height: 20px;"></div>
        </div>
      </li>
    `;
  });
  
  html += '</ol>';
  container.innerHTML = html;
}
```

---

## Error Handling

### 6. Comprehensive Error Handling

```javascript
async function safePredictDisease() {
  try {
    // Validate disease selection
    const disease = document.getElementById('disease-select').value;
    if (!disease) {
      throw new Error('Please select a disease');
    }
    
    // Validate symptoms
    if (selectedSymptoms.length === 0) {
      throw new Error('Please select at least one symptom');
    }
    
    // Validate age if provided
    const age = document.getElementById('age-input')?.value;
    if (age && (isNaN(age) || age < 1 || age > 120)) {
      throw new Error('Please enter a valid age between 1 and 120');
    }
    
    // Make prediction
    const response = await fetch('/api/predict/disease', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        disease,
        symptoms: selectedSymptoms,
        age: age ? parseInt(age) : null
      })
    });
    
    // Handle HTTP errors
    if (response.status === 429) {
      throw new Error('Too many requests. Please wait a moment.');
    }
    
    if (response.status === 404) {
      throw new Error('Disease not found in database');
    }
    
    if (response.status === 500) {
      throw new Error('Server error. Please try again later.');
    }
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    // Parse response
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.error || 'Prediction failed');
    }
    
    // Display results
    displayPredictionResults(data.prediction);
    
  } catch (error) {
    console.error('Prediction error:', error);
    showUserError(error.message);
  }
}

function showUserError(message) {
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error-banner';
  errorDiv.textContent = message;
  errorDiv.style.cssText = `
    background: #f44336;
    color: white;
    padding: 12px;
    border-radius: 4px;
    margin: 10px 0;
  `;
  
  const container = document.getElementById('results-container');
  container.innerHTML = '';
  container.parentNode.insertBefore(errorDiv, container);
}
```

---

## Complete Example

### Full Working Implementation

```html
<!DOCTYPE html>
<html>
<head>
  <title>Disease Prediction</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 600px;
      margin: 40px auto;
      padding: 20px;
    }
    
    .form-group {
      margin-bottom: 20px;
    }
    
    label {
      display: block;
      font-weight: bold;
      margin-bottom: 5px;
    }
    
    select, input {
      width: 100%;
      padding: 8px;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 14px;
    }
    
    button {
      background: #4CAF50;
      color: white;
      padding: 12px 24px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 16px;
    }
    
    button:hover {
      background: #45a049;
    }
    
    .symptom-item {
      margin: 10px 0;
    }
    
    .symptom-item input {
      width: auto;
      margin-right: 10px;
    }
    
    .results-card {
      background: #f5f5f5;
      padding: 20px;
      border-radius: 4px;
      margin-top: 20px;
    }
    
    .error {
      color: red;
      padding: 10px;
      background: #ffebee;
      border-radius: 4px;
    }
    
    #loading {
      display: none;
      text-align: center;
      padding: 20px;
    }
  </style>
</head>
<body>
  <h1>Disease Prediction Tool</h1>
  
  <div class="form-group">
    <label for="disease-select">Select Disease</label>
    <select id="disease-select">
      <option value="">-- Loading diseases --</option>
    </select>
  </div>
  
  <div class="form-group">
    <label>Symptoms</label>
    <div id="symptoms-container">Loading...</div>
    <p id="symptom-count">0 symptoms selected</p>
  </div>
  
  <div class="form-group">
    <label for="age-input">Age (optional)</label>
    <input type="number" id="age-input" min="1" max="120" placeholder="Enter age">
  </div>
  
  <div class="form-group">
    <label for="height-input">Height (cm, optional)</label>
    <input type="number" id="height-input" min="50" max="250" placeholder="Enter height">
  </div>
  
  <div class="form-group">
    <label for="weight-input">Weight (kg, optional)</label>
    <input type="number" id="weight-input" min="20" max="200" placeholder="Enter weight">
  </div>
  
  <button onclick="predictDisease()">Predict Disease</button>
  
  <div id="loading">⏳ Making prediction...</div>
  <div id="results-container"></div>

  <script>
    let selectedSymptoms = [];

    // Initialize on page load
    document.addEventListener('DOMContentLoaded', () => {
      loadDiseases();
      document.getElementById('disease-select').addEventListener('change', (e) => {
        if (e.target.value) {
          loadSymptoms(e.target.value);
        }
      });
    });

    async function loadDiseases() {
      const resp = await fetch('/api/diseases/list');
      const data = await resp.json();
      const select = document.getElementById('disease-select');
      select.innerHTML = '<option value="">-- Select a disease --</option>';
      
      data.diseases.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d;
        opt.text = d.toUpperCase();
        select.appendChild(opt);
      });
    }

    async function loadSymptoms(disease) {
      const container = document.getElementById('symptoms-container');
      container.innerHTML = '<p>Loading symptoms...</p>';
      selectedSymptoms = [];
      
      const resp = await fetch(`/api/disease/${disease}/symptoms`);
      const data = await resp.json();
      
      container.innerHTML = '';
      if (data.success) {
        Object.entries(data.symptoms).forEach(([key, name]) => {
          const div = document.createElement('div');
          div.className = 'symptom-item';
          
          const inp = document.createElement('input');
          inp.type = 'checkbox';
          inp.value = key;
          inp.onchange = (e) => {
            if (e.target.checked) selectedSymptoms.push(key);
            else selectedSymptoms = selectedSymptoms.filter(s => s !== key);
            updateCount();
          };
          
          const lbl = document.createElement('label');
          lbl.appendChild(inp);
          lbl.appendChild(document.createTextNode(name));
          
          div.appendChild(lbl);
          container.appendChild(div);
        });
      }
      updateCount();
    }

    function updateCount() {
      document.getElementById('symptom-count').textContent = 
        `${selectedSymptoms.length} symptoms selected`;
    }

    async function predictDisease() {
      const disease = document.getElementById('disease-select').value;
      
      if (!disease) {
        alert('Select a disease');
        return;
      }
      if (!selectedSymptoms.length) {
        alert('Select symptoms');
        return;
      }
      
      document.getElementById('loading').style.display = 'block';
      
      const resp = await fetch('/api/predict/disease', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          disease,
          symptoms: selectedSymptoms,
          age: document.getElementById('age-input').value || null,
          height: document.getElementById('height-input').value || null,
          weight: document.getElementById('weight-input').value || null
        })
      });
      
      const data = await resp.json();
      document.getElementById('loading').style.display = 'none';
      
      if (data.success) {
        const p = data.prediction;
        const prob = (p.calibrated_probability * 100).toFixed(1);
        document.getElementById('results-container').innerHTML = `
          <div class="results-card">
            <h2>${disease}</h2>
            <p>Probability: <strong>${prob}%</strong></p>
            <p>Symptoms matched: ${p.symptoms_matched}/${p.total_symptoms}</p>
            ${p.bmi ? `<p>BMI: ${p.bmi.toFixed(1)} (${p.bmi_category})</p>` : ''}
          </div>
        `;
      } else {
        document.getElementById('results-container').innerHTML = 
          `<div class="error">Error: ${data.error}</div>`;
      }
    }
  </script>
</body>
</html>
```

---

## Testing Your Integration

### Test with cURL

```bash
# Test symptom loading
curl "http://localhost:5000/api/disease/diabetes/symptoms"

# Test prediction
curl -X POST "http://localhost:5000/api/predict/disease" \
  -H "Content-Type: application/json" \
  -d '{
    "disease": "diabetes",
    "symptoms": ["increased_thirst", "frequent_urination"],
    "age": 45
  }'
```

### Test with Python

```python
import requests
import json

# Get symptoms
resp = requests.get('http://localhost:5000/api/disease/diabetes/symptoms')
print(resp.json())

# Make prediction
resp = requests.post(
  'http://localhost:5000/api/predict/disease',
  json={
    'disease': 'diabetes',
    'symptoms': ['increased_thirst', 'frequent_urination'],
    'age': 45
  }
)
print(resp.json())
```

---

## Next Steps

1. Copy code examples into your frontend
2. Test API endpoints with cURL or Postman
3. Implement error handling for your use case
4. Add styling to match your design
5. Test with various symptom combinations
6. Deploy and monitor performance

For more details, see [API_ENDPOINTS.md](API_ENDPOINTS.md)
