# Diabetes Prediction Application - Developer Documentation

## Project Overview

A comprehensive Flask-based diabetes prediction and health management application that combines machine learning prediction with wellness tracking features.

**Live URL:** http://127.0.0.1:5000 (when running locally)

---

## Architecture

### Technology Stack
- **Backend:** Flask 2.x, Python 3.8+
- **Frontend:** Jinja2 templates, HTML5, CSS3
- **Machine Learning:** scikit-learn (KNeighborsClassifier)
- **Data Processing:** Pandas, NumPy
- **Session Management:** Flask sessions
- **Data Storage:** In-memory dictionaries (development)

### Directory Structure
```
Diabetes-Prediction-master/
├── flask/
│   ├── app.py                    # Main Flask application
│   ├── diabetes.csv              # Training data
│   ├── improved_model.py         # Advanced ML features
│   ├── model.py                  # Basic ML model
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css         # Global styling
│   │   └── uploads/              # User uploads directory
│   └── templates/
│       ├── base.html             # Base template with navbar
│       ├── index.html            # Risk calculator
│       ├── bmi.html              # BMI calculator
│       ├── dashboard.html        # Main dashboard (15 features)
│       ├── diet_recommendation.html   # AI diet generator
│       ├── diet.html             # Diet plans
│       ├── symptoms_checker.html # Symptom analyzer
│       ├── food_search.html      # Food database search
│       ├── exercises.html        # Exercise recommendations
│       ├── precautions.html      # Diabetes precautions
│       ├── health_dashboard.html # Health score & stats (NEW)
│       ├── water_tracker.html    # Water intake logging (NEW)
│       ├── exercise_logger.html  # Workout logging (NEW)
│       ├── health_tips.html      # Wellness tips (NEW)
│       ├── faq.html              # FAQ database (NEW)
│       ├── lab_results.html      # Lab test tracker (NEW)
│       ├── login.html            # User authentication
│       └── register.html         # User registration
├── diabetes.ipynb                # Jupyter notebook analysis
├── requirements.txt              # Python dependencies
└── README.md                     # Project readme

```

---

## Core Features

### 1. Diabetes Risk Calculator
- **Route:** `/` (GET), `/predict` (POST)
- **Template:** `index.html`
- **ML Model:** KNeighborsClassifier (k=24)
- **Input Features:**
  - Glucose (0-200 mg/dL)
  - Blood Pressure (0-122 mmHg)
  - Skin Thickness (0-99 mm)
  - Insulin (0-846 mU/L)
  - BMI (0-67.1)
  - Diabetes Pedigree Function (0-2.42)
  - Age (21-81 years)
- **Outputs:**
  - Binary diagnosis: "Has Diabetes" / "Does Not Have Diabetes"
  - Risk probability (0-100%)
  - Risk stratification (Very Low → High)
  - Data quality warnings
  - Model accuracy display
  - Feature importance analysis

### 2. BMI Calculator
- **Route:** `/bmi` (GET/POST)
- **Template:** `bmi.html`
- **Features:**
  - Height input in centimeters
  - Weight in kilograms
  - Waist circumference optional
  - 9-category BMI classification
  - Age-adjusted recommendations
  - Abdominal fat assessment
  - Health risk visualization
  - Personalized advice

### 3. Symptoms Checker
- **Route:** `/symptoms` (GET/POST)
- **Template:** `symptoms_checker.html`
- **Features:**
  - 10 symptom options
  - Weighted scoring system
  - Risk level assessment (Low/Moderate/High)
  - Personalized recommendations
  - Emergency guidance
  - Professional consultation advice

### 4. AI Diet Recommendation Engine
- **Route:** `/diet-recommendation` (GET/POST)
- **Template:** `diet_recommendation.html`
- **Features:**
  - 5 diet types (High Protein, Low Carb, Balanced, Vegetarian, Diabetic)
  - 3 meals per recommendation
  - Snack suggestions
  - Water intake calculation
  - Restrictions handling
  - Health tips
  - Calorie estimates

### 5. Diet Plans Database
- **Route:** `/diet` (GET/POST)
- **Template:** `diet.html`
- **Features:**
  - Pre-defined diet plans
  - Meal options by category
  - Nutritional information
  - Preparation tips

### 6. Food Search Engine
- **Route:** `/food-search` (GET/POST)
- **Template:** `food_search.html`
- **Database:** ~50 foods with:
  - Glycemic Index (GI)
  - Sugar content
  - Alternative options
  - Health benefits
  - Calorie information

### 7. Exercise Recommendations
- **Route:** `/exercises` (GET)
- **Template:** `exercises.html`
- **Content:**
  - Recommended activities
  - Intensity guidelines
  - Duration suggestions
  - Benefits explanation

### 8. Precautions Guide
- **Route:** `/precautions` (GET)
- **Template:** `precautions.html`
- **Content:**
  - Essential precautions
  - Daily care tips
  - Emergency guidance
  - Medication reminders

### 9. Health Dashboard (NEW)
- **Route:** `/health-dashboard` (GET)
- **Template:** `health_dashboard.html`
- **Features:**
  - Health score (0-100)
  - Statistics aggregation
  - Quick action buttons
  - Recent activity tracking
  - User-specific data

### 10. Water Tracker (NEW)
- **Route:** `/log-water` (GET/POST)
- **Template:** `water_tracker.html`
- **Features:**
  - Daily water intake logging
  - Progress bar visualization
  - Quick preset buttons
  - Date-based aggregation
  - Hydration tips

### 11. Exercise Logger (NEW)
- **Route:** `/log-exercise` (GET/POST)
- **Template:** `exercise_logger.html`
- **Features:**
  - 9 exercise types
  - Duration tracking
  - 3 intensity levels
  - Auto calorie calculation
  - Recent exercises list
  - Exercise health tips

### 12. Health Tips Feed (NEW)
- **Route:** `/health-tips` (GET)
- **Template:** `health_tips.html`
- **Features:**
  - 10 curated health tips
  - 5 categories (Nutrition, Lifestyle, Exercise, Mental, Prevention)
  - Color-coded badges
  - Emoji-enhanced design

### 13. FAQ Database (NEW)
- **Route:** `/faq` (GET)
- **Template:** `faq.html`
- **Features:**
  - 8 Q&A items
  - Real-time search
  - Collapsible interface
  - Medical accuracy

### 14. Lab Results Tracker (NEW)
- **Route:** `/lab-results` (GET/POST)
- **Template:** `lab_results.html`
- **Features:**
  - 9 test types
  - Auto unit selection
  - Status indicators
  - Historical tracking
  - Reference ranges

---

## Data Models

### User Health Data Structure
```python
user_health_data = {
    'user@example.com': {
        'predictions': [
            {
                'glucose': 140,
                'blood_pressure': 90,
                'result': 'Has Diabetes',
                'probability': 0.85,
                'date': '2024-01-15'
            }
        ],
        'lab_results': [
            {
                'test': 'Fasting Blood Sugar',
                'result': 125,
                'unit': 'mg/dL',
                'normal_range': '< 100',
                'date': '2024-01-15'
            }
        ],
        'water_intake': [
            {
                'amount': 250,
                'date': '2024-01-15 09:00'
            }
        ],
        'exercises': [
            {
                'type': 'walking',
                'duration': 30,
                'intensity': 'moderate',
                'date': '2024-01-15 07:00',
                'calories_burned': 150
            }
        ],
        'health_score': 75
    }
}
```

---

## Key Classes & Functions

### Machine Learning Pipeline

#### `train_and_save_model()`
- Loads `diabetes.csv`
- Trains KNN classifier (k=24)
- Applies MinMaxScaler normalization
- Calculates model accuracy
- Returns: (model, scaler, accuracy)

#### `get_feature_importance(distances)`
- Calculates feature contribution
- Uses neighbor distances as weights
- Returns: importance scores per feature

#### `DietRecommendationEngine`
- Generates personalized meal plans
- 5 diet types
- 3 meals + snacks
- Water and calorie calculations

#### `SymptomsCheckerEngine`
- Analyzes selected symptoms
- Weighted scoring system
- Risk stratification
- Personalized recommendations

#### `FoodSearchEngine`
- ~50-food database
- GI index lookup
- Nutritional information
- Alternative suggestions

---

## Route Reference

### Authentication
| Route | Method | Purpose |
|-------|--------|---------|
| `/login` | GET/POST | User login |
| `/register` | GET/POST | User registration |
| `/logout` | GET | Session logout |

### Prediction & Assessment
| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Risk calculator display |
| `/predict` | POST | ML prediction processing |
| `/bmi` | GET/POST | BMI calculation |
| `/symptoms` | GET/POST | Symptom analysis |

### Information & Guidance
| Route | Method | Purpose |
|-------|--------|---------|
| `/diet-recommendation` | GET/POST | AI diet generator |
| `/diet` | GET/POST | Diet plans |
| `/food-search` | GET/POST | Food database |
| `/exercises` | GET | Exercise recommendations |
| `/precautions` | GET | Health precautions |
| `/health-tips` | GET | Wellness tips feed |
| `/faq` | GET | FAQ database |

### Health Tracking
| Route | Method | Purpose |
|-------|--------|---------|
| `/health-dashboard` | GET | Overall health view |
| `/log-water` | GET/POST | Water intake logging |
| `/log-exercise` | GET/POST | Workout logging |
| `/lab-results` | GET/POST | Lab test tracking |

### Dashboard
| Route | Method | Purpose |
|-------|--------|---------|
| `/dashboard` | GET | Main feature hub |

---

## Styling & Frontend

### CSS Classes
- `.page` - Main page container
- `.card-dashboard` - Dashboard feature cards
- `.headline` - Page titles
- `.subtitle-main` - Subtitle text
- `.form-group` - Form field wrapper
- `.btn-outline` - Outline buttons
- `.card-icon-circle` - Icon containers
- `.progress-bar` - Progress indicators
- `.status-badge` - Status indicators
- `.gradient-bg` - Gradient backgrounds

### Color Palette
- **Primary Blue:** #0b74ff
- **Dark Text:** #111827
- **Light Gray:** #f9fafb, #f3f4f6
- **Success Green:** #28a745, #d4edda
- **Warning Yellow:** #ffc107, #fef3c7
- **Danger Red:** #dc3545, #fee2e2
- **Info Cyan:** #17a2b8

### Responsive Design
- Mobile-first approach
- CSS Grid for layouts
- Flexbox for components
- Media queries for breakpoints
- Touch-friendly button sizes (min 44px)

---

## Running the Application

### Prerequisites
```bash
pip install -r requirements.txt
```

### Start Server
```bash
cd flask
python app.py
```

### Access Application
- Local: http://127.0.0.1:5000
- Network: http://YOUR_IP:5000

### Debug Mode
- Automatically enabled in development
- Debugger PIN displayed in console
- Hot reload on file changes

---

## Testing

### Syntax Validation
```bash
python -m py_compile flask/app.py
```

### Template Rendering
- Check browser console for JS errors
- Verify all links load correctly
- Test form submissions

### Data Validation
- Test with edge case inputs
- Verify error handling
- Check negative number rejection

---

## Development Best Practices

### Code Organization
1. **Imports** at top of file
2. **Constants** and configs
3. **Data structures**
4. **Utility functions**
5. **Route handlers**
6. **Main block** at bottom

### Security Considerations
- ✅ Session-based authentication
- ✅ Input validation
- ✅ SQL injection prevention (no DB used)
- ⚠️ TODO: Add CSRF protection
- ⚠️ TODO: Implement rate limiting
- ⚠️ TODO: Add HTTPS in production

### Performance Tips
- Cache model after loading
- Use list comprehensions
- Lazy load large datasets
- Minimize database queries (when DB added)

---

## Future Enhancements

### Short Term
1. Add password hashing
2. Implement CSRF tokens
3. Add rate limiting
4. Create API endpoints
5. Add unit tests

### Medium Term
1. SQLite database integration
2. User profile customization
3. Medication tracker
4. Trend analysis charts
5. Email notifications

### Long Term
1. Mobile app (React Native)
2. Cloud deployment (Heroku/AWS)
3. Advanced ML models
4. Wearable device integration
5. Community features

---

## Troubleshooting

### Common Issues

**Port 5000 already in use**
```bash
# Use different port
python -c "app.run(port=5001)"
```

**Module not found**
```bash
pip install -r requirements.txt
```

**Template not rendering**
- Check template path in templates/ folder
- Verify function name matches route
- Check for Jinja2 syntax errors

**Data not persisting**
- Currently using in-memory storage
- Data resets on server restart
- Implement database for persistence

---

## API Response Examples

### Risk Prediction Response
```json
{
    "result": "Has Diabetes",
    "probability": 0.85,
    "risk_level": "Moderate-High",
    "confidence": "High",
    "accuracy": 77.34,
    "features": [
        {
            "name": "Glucose",
            "value": 150,
            "importance": 0.35,
            "normal_range": "70-100 mg/dL",
            "status": "High"
        }
    ]
}
```

### Health Score Response
```json
{
    "health_score": 75,
    "breakdown": {
        "base": 50,
        "lab_results": 10,
        "exercises": 20,
        "hydration": 15
    },
    "stats": {
        "predictions": 5,
        "lab_results": 3,
        "exercises": 12,
        "water_intake": 2250
    }
}
```

---

## Contact & Support

For bug reports or feature requests, please document:
1. Steps to reproduce
2. Expected vs actual behavior
3. Error messages (if any)
4. Python/Flask version
5. Operating system

---

**Version:** 2.0 - Health Tracking Edition  
**Last Updated:** 2024  
**Maintainer:** Development Team  
**License:** Open Source
