# Disease Predictor API Documentation

This document describes all available API endpoints for the Disease Predictor system. The API provides ML-based disease prediction, symptom analysis, and patient health assessment.

## Base URL

```
http://localhost:5000
http://yourserver.com (production)
```

## Authentication

Most endpoints do not require authentication. Doctor dashboard and patient dashboard endpoints may require session authentication.

---

## Core ML Prediction Endpoints

### 1. **Get Disease Symptoms**

Retrieve all symptoms associated with a specific disease.

**Endpoint:** `GET /api/disease/<disease>/symptoms`

**Parameters:**
- `disease` (string, path): Disease name (e.g., "diabetes", "hypertension")

**Response (200 OK):**
```json
{
  "success": true,
  "disease": "diabetes",
  "symptoms": {
    "increased_thirst": "Increased Thirst",
    "frequent_urination": "Frequent Urination",
    "extreme_hunger": "Extreme Hunger",
    "unexplained_weight_loss": "Unexplained Weight Loss"
  },
  "total_symptoms": 10
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "Disease 'invalid_disease' not found"
}
```

**Example:**
```bash
curl -X GET "http://localhost:5000/api/disease/diabetes/symptoms"
```

---

### 2. **Predict Disease Probability**

Make an ML-based prediction for a specific disease based on patient symptoms and demographic data.

**Endpoint:** `POST /api/predict/disease`

**Request Body:**
```json
{
  "disease": "diabetes",
  "symptoms": ["increased_thirst", "frequent_urination", "fatigue"],
  "age": 45,
  "height": 170,
  "weight": 75
}
```

**Parameters:**
- `disease` (string, required): Target disease name
- `symptoms` (array of strings, required): List of symptom keys
- `age` (integer, optional): Patient age (1-120)
- `height` (float, optional): Patient height in cm
- `weight` (float, optional): Patient weight in kg

**Response (200 OK):**
```json
{
  "success": true,
  "prediction": {
    "disease": "diabetes",
    "raw_probability": 0.82,
    "calibrated_probability": 0.78,
    "confidence_score": 0.75,
    "symptoms_matched": 3,
    "total_symptoms": 10,
    "bmi": 25.9,
    "bmi_category": "Overweight",
    "bayesian_prior": 0.15,
    "bayesian_likelihood": 0.75,
    "bayesian_posterior": 0.68
  }
}
```

**Response Fields:**
- `raw_probability`: Logistic regression score (0-1)
- `calibrated_probability`: Calibrated probability (0-1)
- `confidence_score`: Model confidence (0-1)
- `symptoms_matched`: Number of symptoms matched
- `total_symptoms`: Total symptoms for disease
- `bmi`: Body Mass Index (if height/weight provided)
- `bmi_category`: BMI classification
- `bayesian_*`: Bayesian analysis components

**Error Response (400):**
```json
{
  "success": false,
  "error": "Missing 'disease' parameter"
}
```

**Example:**
```bash
curl -X POST "http://localhost:5000/api/predict/disease" \
  -H "Content-Type: application/json" \
  -d '{
    "disease": "diabetes",
    "symptoms": ["increased_thirst", "frequent_urination"],
    "age": 45,
    "height": 170,
    "weight": 75
  }'
```

---

### 3. **Predict Multiple Diseases**

Get predictions for all available diseases based on patient symptoms.

**Endpoint:** `POST /api/predict/multiple`

**Request Body:**
```json
{
  "symptoms": ["fever", "cough", "fatigue"],
  "age": 30,
  "height": 170,
  "weight": 70
}
```

**Parameters:**
- `symptoms` (array of strings, required): List of symptom keys (minimum 1)
- `age` (integer, optional): Patient age
- `height` (float, optional): Patient height in cm
- `weight` (float, optional): Patient weight in kg

**Response (200 OK):**
```json
{
  "success": true,
  "predictions": [
    {
      "disease": "influenza",
      "raw_probability": 0.65,
      "calibrated_probability": 0.62,
      "confidence_score": 0.58
    },
    {
      "disease": "covid19",
      "raw_probability": 0.58,
      "calibrated_probability": 0.55,
      "confidence_score": 0.50
    }
  ],
  "total_predictions": 98,
  "top_disease": "influenza",
  "top_probability": 0.62,
  "symptoms_provided": 3
}
```

**Response Fields:**
- `predictions`: Array of disease predictions (top 10 shown)
- `total_predictions`: Total diseases in database
- `top_disease`: Disease with highest probability
- `top_probability`: Highest probability score
- `symptoms_provided`: Number of input symptoms

**Error Response (400):**
```json
{
  "success": false,
  "error": "'symptoms' must be a list"
}
```

**Example:**
```bash
curl -X POST "http://localhost:5000/api/predict/multiple" \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": ["fever", "cough"],
    "age": 30
  }'
```

---

### 4. **Get Available Diseases**

List all diseases available in the ML model.

**Endpoint:** `GET /api/diseases/list`

**Response (200 OK):**
```json
{
  "success": true,
  "diseases": [
    "diabetes",
    "hypertension",
    "covid19",
    "heart_disease",
    "influenza",
    ...
  ],
  "total_diseases": 98
}
```

**Example:**
```bash
curl -X GET "http://localhost:5000/api/diseases/list"
```

---

## Legacy Endpoints (Home.html Format)

These endpoints maintain backward compatibility with existing frontend implementations.

### **Get ML Symptoms (Legacy)**

**Endpoint:** `GET /api/ml/symptoms/<disease>`

Returns symptoms in format compatible with home.html dashboard.

**Response:**
```json
{
  "success": true,
  "symptoms": [
    {"key": "fever", "name": "Fever"},
    {"key": "cough", "name": "Cough"}
  ]
}
```

---

### **Make Prediction (Legacy)**

**Endpoint:** `POST /api/ml/predict`

Returns predictions in legacy format with Bayesian analysis.

**Request Body:**
```json
{
  "disease": "diabetes",
  "symptoms": ["increased_thirst", "frequent_urination"],
  "age": 45,
  "height_cm": 170,
  "weight_kg": 75
}
```

**Response:**
```json
{
  "success": true,
  "disease": "diabetes",
  "ml_prediction": {
    "raw_probability": 55.0,
    "calibrated_probability": 52.8,
    "missing_symptoms": [
      {"name": "Extreme Hunger", "weight": 0.75},
      {"name": "Blurred Vision", "weight": 0.70}
    ]
  },
  "bayesian_analysis": {
    "prior": 15.5,
    "likelihood": 75.2,
    "posterior": 68.3
  },
  "risk_assessment": {
    "level": "Moderate",
    "color": "warning",
    "description": "Based on 2 selected symptoms..."
  }
}
```

---

## Common Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": "Missing required parameter"
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": "Disease 'xyz' not found"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Prediction failed"
}
```

---

## Usage Examples

### Example 1: Simple Symptom-Based Prediction

```javascript
// JavaScript/Frontend
async function predictDisease() {
  const response = await fetch('/api/predict/disease', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      disease: 'diabetes',
      symptoms: ['increased_thirst', 'frequent_urination'],
      age: 45
    })
  });

  const data = await response.json();
  
  if (data.success) {
    const pred = data.prediction;
    console.log(`Probability: ${(pred.calibrated_probability * 100).toFixed(1)}%`);
    console.log(`Risk Level: ${pred.risk_level || 'Low'}`);
  }
}
```

### Example 2: Get All Predictions for Symptoms

```javascript
async function getTopDiseases() {
  const symptoms = ['fever', 'cough', 'fatigue'];
  
  const response = await fetch('/api/predict/multiple', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symptoms })
  });

  const data = await response.json();
  
  if (data.success) {
    data.predictions.forEach((pred, i) => {
      console.log(`${i+1}. ${pred.disease}: ${(pred.calibrated_probability*100).toFixed(1)}%`);
    });
  }
}
```

### Example 3: Build Dynamic Symptom Selector

```javascript
async function loadDiseaseSymptoms(disease) {
  const response = await fetch(`/api/disease/${disease}/symptoms`);
  const data = await response.json();
  
  if (data.success) {
    const symptoms = data.symptoms;
    
    // Build checkbox UI
    Object.entries(symptoms).forEach(([key, name]) => {
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.value = key;
      checkbox.label = name;
      // ... add to DOM
    });
  }
}
```

---

## Data Formats

### Symptom Keys

Symptoms are referenced by lowercase, underscore-separated keys:
- `increased_thirst`
- `frequent_urination`
- `blurred_vision`
- `chest_pain`
- `shortness_breath`

Full display names are returned by the API.

### Probability Interpretation

All probability scores are on a **0-1 scale** (where 1 = 100%):

- **0.00 - 0.30**: Low risk
- **0.30 - 0.60**: Moderate risk
- **0.60 - 0.85**: High risk
- **0.85 - 1.00**: Very high risk

---

## Rate Limiting

The API implements rate limiting:
- **10 requests per 30 seconds** per IP address
- Exceeding this limit returns a **429 Too Many Requests** response

---

## Performance Notes

- **Symptom loading**: ~10-50ms
- **Single disease prediction**: ~50-100ms
- **Multiple disease prediction**: ~1-2 seconds (98 diseases)
- **Predictions are cached** for identical requests within 5 minutes

---

## Future Improvements

- [ ] Add authentication for personalized predictions
- [ ] Include medical imaging analysis (eyes/skin)
- [ ] Real-time model retraining with patient feedback
- [ ] Confidence intervals for predictions
- [ ] Support for PDF report generation via API
- [ ] WebSocket support for real-time analytics

---

## Support

For API issues or feature requests:
- GitHub Issues: https://github.com/sudheerxdev/Disease-predictor-v2
- Email: sudheer@example.com
- Status Page: http://localhost:5000/health
