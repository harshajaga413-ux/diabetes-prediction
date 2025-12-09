import numpy as np
import pandas as pd
from flask import Flask, request, render_template, session, redirect, url_for
import pickle
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Needed for sessions (login). Change this to any random secret string.
app.secret_key = "change_this_to_any_random_secret_key"

# ---------------------------------------------------------------------
#  MODEL / PREDICTION LOGIC  (your original logic)
# ---------------------------------------------------------------------

# Train and save the improved model first
def train_and_save_model():
    # Import and preprocess data
    dataset = pd.read_csv('diabetes.csv')
    
    # Replace zero values with NaN and then fill with mean
    columns_to_process = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
    dataset[columns_to_process] = dataset[columns_to_process].replace(0, np.NaN)
    for column in columns_to_process:
        dataset[column].fillna(dataset[column].mean(), inplace=True)
    
    # Select all relevant features
    features = [
        'Glucose',
        'BloodPressure',
        'SkinThickness',
        'Insulin',
        'BMI',
        'DiabetesPedigreeFunction',
        'Age'
    ]
    X = dataset[features]
    y = dataset['Outcome']
    
    # Scale the features
    scaler = MinMaxScaler(feature_range=(0, 1))
    X_scaled = scaler.fit_transform(X)
    
    # Train KNN model
    knn = KNeighborsClassifier(n_neighbors=24, metric='minkowski', p=2)
    knn.fit(X_scaled, y)
    
    # Calculate accuracy
    accuracy = knn.score(X_scaled, y)
    
    return knn, scaler, features, accuracy

# Train model and get components
model, scaler, features, model_accuracy = train_and_save_model()

def get_feature_importance(input_values):
    """Calculate the relative importance of each feature's contribution"""
    scaled_input = scaler.transform([input_values])
    neighbors = model.kneighbors(scaled_input, return_distance=True)
    distances = neighbors[0][0]
    importance = 1 / (distances + 1e-10)  # Add small constant to avoid division by zero
    return importance / importance.sum()

# ---------------------------------------------------------------------
#  DIET RECOMMENDATION ENGINE (Rule-based AI)
# ---------------------------------------------------------------------

class DietRecommendationEngine:
    """Generate personalized diet plans based on user health profile"""
    
    def __init__(self):
        self.breakfast_options = {
            'veg': [
                'Oatmeal with berries and almonds (1 cup oats, 1/2 cup berries)',
                'Whole wheat toast with avocado and tomato (2 slices)',
                'Greek yogurt with granola and honey (1 cup yogurt)',
                'Vegetable omelet with spinach and mushrooms (3 eggs)',
                'Smoothie bowl with bananas, spinach, and chia seeds (1 banana)',
            ],
            'non_veg': [
                'Grilled chicken breast with brown rice and vegetables (150g chicken)',
                'Salmon omelet with whole wheat toast (100g salmon)',
                'Egg white scramble with turkey sausage (4 egg whites)',
                'Oatmeal with lean ground turkey and berries (150g turkey)',
                'Grilled fish with whole grain toast and vegetables (150g fish)',
            ]
        }
        
        self.lunch_options = {
            'veg': [
                'Chickpea salad with quinoa and olive oil dressing',
                'Lentil soup with mixed vegetables and brown rice',
                'Tofu stir-fry with broccoli, bell peppers, and brown rice',
                'Mediterranean vegetable plate with hummus and whole wheat pita',
                'Bean and vegetable curry with brown rice (low oil)',
            ],
            'non_veg': [
                'Grilled chicken breast with steamed broccoli and sweet potato (150g)',
                'Baked salmon with green beans and quinoa (150g)',
                'Lean ground turkey with whole wheat pasta and tomato sauce (150g)',
                'Grilled tilapia with brown rice and roasted vegetables (150g)',
                'Turkey meatballs with zucchini noodles and marinara sauce (150g)',
            ]
        }
        
        self.dinner_options = {
            'veg': [
                'Vegetable soup with lentils and whole grain bread',
                'Baked sweet potato with black beans and steamed broccoli',
                'Vegetable kebabs with brown rice and yogurt sauce',
                'Whole wheat pasta primavera with olive oil and vegetables',
                'Chickpea and vegetable curry with roti (low oil)',
            ],
            'non_veg': [
                'Grilled chicken breast with roasted vegetables and brown rice (150g)',
                'Baked white fish with asparagus and sweet potato (150g)',
                'Lean beef with broccoli and cauliflower rice (150g)',
                'Turkey and vegetable stir-fry with brown rice (150g)',
                'Grilled salmon with roasted Brussels sprouts and quinoa (150g)',
            ]
        }
        
        self.snacks = {
            'veg': [
                '🥕 Carrot sticks with hummus (1 medium carrot + 2 tbsp hummus)',
                '🥗 Apple with almond butter (1 apple + 1 tbsp almond butter)',
                '🥜 Mixed nuts (almonds, walnuts) - 30g',
                '🫘 Roasted chickpeas - 50g',
                '🥒 Cucumber slices with lemon and salt',
            ],
            'non_veg': [
                '🍗 Grilled chicken snack (50g grilled chicken breast)',
                '🥜 Mixed nuts and seeds - 30g',
                '🥛 Plain Greek yogurt - 150g',
                '🧀 Low-fat cheese with whole grain crackers',
                '🥚 Boiled eggs (2 eggs)',
            ]
        }
        
        self.restrictions = {
            'diabetic': [
                '❌ Avoid sugary drinks and sodas',
                '❌ Skip refined grains (white bread, white rice, pasta)',
                '❌ Avoid fried foods and excessive oils',
                '❌ Limit salt intake (max 2300mg/day)',
                '❌ Avoid processed meats and fast food',
                '❌ No alcohol or limit to minimal amounts',
                '❌ Avoid high-fat dairy products',
            ],
            'pre_diabetic': [
                '⚠️ Minimize sugary drinks and desserts',
                '⚠️ Reduce refined grain consumption',
                '⚠️ Limit fried foods and excess oil',
                '⚠️ Control portion sizes',
                '⚠️ Monitor sodium intake',
                '⚠️ Limit alcohol consumption',
                '⚠️ Avoid processed snacks',
            ],
            'normal': [
                '✓ Maintain balanced diet',
                '✓ Include whole grains and vegetables',
                '✓ Choose lean proteins',
                '✓ Limit added sugars',
                '✓ Stay hydrated',
                '✓ Regular physical activity recommended',
                '✓ Moderate portion sizes',
            ]
        }
    
    def calculate_water_intake(self, weight_kg):
        """Calculate recommended daily water intake based on weight"""
        # General rule: 30-35 ml per kg of body weight
        base_water = weight_kg * 30  # in ml
        liters = base_water / 1000
        glasses = int(liters / 0.25)  # Each glass is ~250ml
        return f"{liters:.1f} liters ({glasses} glasses of 250ml each)"
    
    def get_bmi_category(self, weight_kg, height_m):
        """Calculate BMI and return category"""
        bmi = weight_kg / (height_m ** 2)
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal Weight"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"
    
    def generate_plan(self, age, weight, height, diabetes_level, diet_type):
        """
        Generate personalized diet plan
        
        Args:
            age: Age in years
            weight: Weight in kg
            height: Height in meters
            diabetes_level: 'diabetic', 'pre_diabetic', or 'normal'
            diet_type: 'vegetarian' or 'non_vegetarian'
        """
        veg = 'veg' if diet_type == 'vegetarian' else 'non_veg'
        
        plan = {
            'profile': {
                'age': age,
                'weight': weight,
                'height': height,
                'diabetes_level': diabetes_level.replace('_', ' ').title(),
                'diet_type': diet_type.replace('_', ' ').title(),
            },
            'bmi_info': self.get_bmi_category(weight, height),
            'water_intake': self.calculate_water_intake(weight),
            'breakfast': self.breakfast_options[veg],
            'lunch': self.lunch_options[veg],
            'dinner': self.dinner_options[veg],
            'snacks': self.snacks[veg],
            'restrictions': self.restrictions[diabetes_level],
            'tips': [
                '🕐 Eat meals at regular times daily',
                '🍽️ Use smaller plates to control portions',
                '🥗 Eat vegetables first, then proteins, then carbs',
                '⏱️ Eat slowly and chew thoroughly (20+ minutes per meal)',
                '📊 Monitor your blood sugar before and after meals',
                '🏃 Exercise 30 minutes daily (walk, swim, cycle)',
                '😴 Get 7-8 hours of quality sleep',
                '💪 Consult with a nutritionist for personalized guidance',
            ]
        }
        
        return plan

# Initialize diet recommendation engine
diet_engine = DietRecommendationEngine()

# ---------------------------------------------------------------------
#  SYMPTOMS CHECKER ENGINE
# ---------------------------------------------------------------------

class SymptomsCheckerEngine:
    """Evaluate diabetes risk based on reported symptoms"""
    
    def __init__(self):
        # Symptom definitions with their diabetes risk contribution
        self.symptoms = {
            'frequent_urination': {
                'label': 'Frequent Urination',
                'description': 'Need to urinate more often than usual',
                'weight': 0.20,
                'emoji': '🚽'
            },
            'fatigue': {
                'label': 'Fatigue & Weakness',
                'description': 'Unusual tiredness and lack of energy',
                'weight': 0.18,
                'emoji': '😴'
            },
            'increased_thirst': {
                'label': 'Increased Thirst',
                'description': 'Drinking more water than usual',
                'weight': 0.20,
                'emoji': '🥤'
            },
            'blurred_vision': {
                'label': 'Blurred Vision',
                'description': 'Vision becomes blurry or unclear',
                'weight': 0.15,
                'emoji': '👁️'
            },
            'slow_healing': {
                'label': 'Slow Wound Healing',
                'description': 'Cuts and bruises take longer to heal',
                'weight': 0.12,
                'emoji': '🩹'
            },
            'numbness': {
                'label': 'Numbness/Tingling',
                'description': 'Tingling or numbness in hands/feet',
                'weight': 0.10,
                'emoji': '🤚'
            },
            'irritability': {
                'label': 'Mood Changes',
                'description': 'Increased irritability or mood swings',
                'weight': 0.08,
                'emoji': '😠'
            },
            'weight_loss': {
                'label': 'Unexplained Weight Loss',
                'description': 'Losing weight without trying',
                'weight': 0.15,
                'emoji': '⚖️'
            },
            'dark_skin': {
                'label': 'Dark Skin Patches',
                'description': 'Dark patches on skin (acanthosis nigricans)',
                'weight': 0.12,
                'emoji': '🖤'
            },
            'yeast_infections': {
                'label': 'Frequent Infections',
                'description': 'Frequent yeast or urinary infections',
                'weight': 0.10,
                'emoji': '🦠'
            }
        }
        
        self.recommendations = {
            'low': {
                'title': 'Low Risk',
                'color': '#28a745',
                'icon': '✅',
                'actions': [
                    '✓ Maintain current healthy lifestyle',
                    '✓ Continue regular exercise (30 min/day)',
                    '✓ Keep balanced diet with whole grains',
                    '✓ Stay hydrated (drink plenty of water)',
                    '✓ Get regular health check-ups annually',
                    '✓ Monitor your weight',
                ]
            },
            'moderate': {
                'title': 'Moderate Risk - Pre-Diabetic',
                'color': '#ffc107',
                'icon': '⚠️',
                'actions': [
                    '⚠️ Schedule a doctor\'s appointment soon',
                    '⚠️ Get a fasting glucose test done',
                    '⚠️ Start regular exercise (150 min/week)',
                    '⚠️ Reduce sugar and refined carbs intake',
                    '⚠️ Increase fiber in diet (vegetables, fruits)',
                    '⚠️ Manage stress with yoga or meditation',
                    '⚠️ Get 7-8 hours of sleep daily',
                    '⚠️ Monitor your weight and BMI',
                ]
            },
            'high': {
                'title': 'High Risk - Diabetes Likely',
                'color': '#dc3545',
                'icon': '🚨',
                'actions': [
                    '🚨 See your doctor immediately',
                    '🚨 Get blood glucose and HbA1c tests',
                    '🚨 Start structured diabetes education program',
                    '🚨 Begin prescribed medication if needed',
                    '🚨 Follow strict diet plan (consult nutritionist)',
                    '🚨 Exercise regularly (30-60 min/day)',
                    '🚨 Monitor blood sugar levels regularly',
                    '🚨 Get eye and foot check-ups',
                    '🚨 Keep regular doctor visits (every 3 months)',
                ]
            }
        }
    
    def calculate_risk(self, selected_symptoms):
        """
        Calculate diabetes risk based on selected symptoms
        
        Args:
            selected_symptoms: List of symptom keys
            
        Returns:
            Dict with risk level, probability, and recommendations
        """
        total_weight = 0
        selected_details = []
        
        for symptom_key in selected_symptoms:
            if symptom_key in self.symptoms:
                symptom = self.symptoms[symptom_key]
                total_weight += symptom['weight']
                selected_details.append({
                    'key': symptom_key,
                    'label': symptom['label'],
                    'emoji': symptom['emoji']
                })
        
        # Calculate probability (0-100%)
        probability = min(total_weight * 100, 100)
        
        # Determine risk level
        if probability < 25:
            risk_level = 'low'
        elif probability < 60:
            risk_level = 'moderate'
        else:
            risk_level = 'high'
        
        return {
            'probability': round(probability, 1),
            'risk_level': risk_level,
            'selected_symptoms': selected_details,
            'symptom_count': len(selected_symptoms),
            'recommendations': self.recommendations[risk_level],
            'all_symptoms': self.symptoms
        }

# Initialize symptoms checker engine
symptoms_engine = SymptomsCheckerEngine()

# ---------------------------------------------------------------------
#  FOOD SEARCH ENGINE (GI & Sugar Index)
# ---------------------------------------------------------------------

class FoodSearchEngine:
    """Search foods and provide GI index, sugar content, and alternatives"""
    
    def __init__(self):
        self.foods_database = {
            # Grains
            'white rice': {
                'name': 'White Rice',
                'gi': 73,
                'sugar_per_100g': 0.1,
                'category': 'High',
                'emoji': '🍚',
                'portion': '100g',
                'alternatives': ['brown rice', 'basmati rice', 'wild rice']
            },
            'brown rice': {
                'name': 'Brown Rice',
                'gi': 50,
                'sugar_per_100g': 0.2,
                'category': 'Medium',
                'emoji': '🍚',
                'portion': '100g',
                'alternatives': ['wild rice', 'quinoa', 'oats']
            },
            'basmati rice': {
                'name': 'Basmati Rice',
                'gi': 58,
                'sugar_per_100g': 0.1,
                'category': 'Medium',
                'emoji': '🍚',
                'portion': '100g',
                'alternatives': ['brown rice', 'wild rice', 'jasmine rice']
            },
            'white bread': {
                'name': 'White Bread',
                'gi': 75,
                'sugar_per_100g': 2.8,
                'category': 'High',
                'emoji': '🍞',
                'portion': '1 slice',
                'alternatives': ['whole wheat bread', 'multigrain bread', 'oat bread']
            },
            'whole wheat bread': {
                'name': 'Whole Wheat Bread',
                'gi': 51,
                'sugar_per_100g': 1.5,
                'category': 'Medium',
                'emoji': '🍞',
                'portion': '1 slice',
                'alternatives': ['multigrain bread', 'sourdough', 'rye bread']
            },
            'oats': {
                'name': 'Oats (rolled)',
                'gi': 51,
                'sugar_per_100g': 1.0,
                'category': 'Medium',
                'emoji': '🌾',
                'portion': '50g',
                'alternatives': ['steel-cut oats', 'oat bran', 'barley']
            },
            'pasta': {
                'name': 'Pasta (white)',
                'gi': 60,
                'sugar_per_100g': 2.0,
                'category': 'Medium',
                'emoji': '🍝',
                'portion': '100g cooked',
                'alternatives': ['whole wheat pasta', 'brown rice pasta', 'legume pasta']
            },
            'whole wheat pasta': {
                'name': 'Whole Wheat Pasta',
                'gi': 42,
                'sugar_per_100g': 1.2,
                'category': 'Low',
                'emoji': '🍝',
                'portion': '100g cooked',
                'alternatives': ['legume pasta', 'brown rice pasta', 'barley pasta']
            },
            
            # Fruits
            'watermelon': {
                'name': 'Watermelon',
                'gi': 72,
                'sugar_per_100g': 9.2,
                'category': 'High',
                'emoji': '🍉',
                'portion': '150g',
                'alternatives': ['strawberries', 'blueberries', 'peaches']
            },
            'banana': {
                'name': 'Banana',
                'gi': 62,
                'sugar_per_100g': 12.2,
                'category': 'Medium',
                'emoji': '🍌',
                'portion': '1 medium',
                'alternatives': ['apple', 'orange', 'berries']
            },
            'apple': {
                'name': 'Apple',
                'gi': 39,
                'sugar_per_100g': 10.4,
                'category': 'Low',
                'emoji': '🍎',
                'portion': '1 medium',
                'alternatives': ['pear', 'orange', 'berries']
            },
            'orange': {
                'name': 'Orange',
                'gi': 42,
                'sugar_per_100g': 9.3,
                'category': 'Low',
                'emoji': '🍊',
                'portion': '1 medium',
                'alternatives': ['apple', 'grapefruit', 'kiwi']
            },
            'strawberries': {
                'name': 'Strawberries',
                'gi': 40,
                'sugar_per_100g': 7.0,
                'category': 'Low',
                'emoji': '🍓',
                'portion': '150g',
                'alternatives': ['blueberries', 'raspberries', 'blackberries']
            },
            'blueberries': {
                'name': 'Blueberries',
                'gi': 53,
                'sugar_per_100g': 9.9,
                'category': 'Medium',
                'emoji': '🫐',
                'portion': '150g',
                'alternatives': ['strawberries', 'raspberries', 'blackberries']
            },
            
            # Vegetables
            'carrot': {
                'name': 'Carrot (raw)',
                'gi': 35,
                'sugar_per_100g': 4.7,
                'category': 'Low',
                'emoji': '🥕',
                'portion': '100g',
                'alternatives': ['celery', 'cucumber', 'bell pepper']
            },
            'potato': {
                'name': 'Potato (boiled)',
                'gi': 78,
                'sugar_per_100g': 1.3,
                'category': 'High',
                'emoji': '🥔',
                'portion': '150g',
                'alternatives': ['sweet potato', 'cauliflower', 'broccoli']
            },
            'sweet potato': {
                'name': 'Sweet Potato',
                'gi': 63,
                'sugar_per_100g': 4.2,
                'category': 'Medium',
                'emoji': '🍠',
                'portion': '100g',
                'alternatives': ['pumpkin', 'beetroot', 'turnip']
            },
            'pumpkin': {
                'name': 'Pumpkin',
                'gi': 75,
                'sugar_per_100g': 2.8,
                'category': 'High',
                'emoji': '🎃',
                'portion': '100g',
                'alternatives': ['sweet potato', 'butternut squash', 'zucchini']
            },
            'broccoli': {
                'name': 'Broccoli',
                'gi': 15,
                'sugar_per_100g': 1.7,
                'category': 'Low',
                'emoji': '🥦',
                'portion': '100g',
                'alternatives': ['cauliflower', 'cabbage', 'spinach']
            },
            'spinach': {
                'name': 'Spinach',
                'gi': 15,
                'sugar_per_100g': 0.4,
                'category': 'Low',
                'emoji': '🥬',
                'portion': '100g',
                'alternatives': ['kale', 'lettuce', 'arugula']
            },
            
            # Proteins
            'chicken': {
                'name': 'Chicken Breast (grilled)',
                'gi': 0,
                'sugar_per_100g': 0,
                'category': 'Low',
                'emoji': '🍗',
                'portion': '100g',
                'alternatives': ['turkey', 'fish', 'tofu']
            },
            'fish': {
                'name': 'Fish (salmon)',
                'gi': 0,
                'sugar_per_100g': 0,
                'category': 'Low',
                'emoji': '🐟',
                'portion': '100g',
                'alternatives': ['tuna', 'mackerel', 'cod']
            },
            'egg': {
                'name': 'Egg (boiled)',
                'gi': 0,
                'sugar_per_100g': 0.6,
                'category': 'Low',
                'emoji': '🥚',
                'portion': '1 large',
                'alternatives': ['tofu', 'lentils', 'chickpeas']
            },
            'tofu': {
                'name': 'Tofu',
                'gi': 15,
                'sugar_per_100g': 0.1,
                'category': 'Low',
                'emoji': '📦',
                'portion': '100g',
                'alternatives': ['tempeh', 'lentils', 'chickpeas']
            },
            
            # Legumes
            'lentils': {
                'name': 'Lentils (cooked)',
                'gi': 32,
                'sugar_per_100g': 1.1,
                'category': 'Low',
                'emoji': '🫘',
                'portion': '100g',
                'alternatives': ['chickpeas', 'black beans', 'kidney beans']
            },
            'chickpeas': {
                'name': 'Chickpeas',
                'gi': 28,
                'sugar_per_100g': 4.9,
                'category': 'Low',
                'emoji': '🫘',
                'portion': '100g',
                'alternatives': ['lentils', 'black beans', 'peas']
            },
            
            # Beverages & Sweets
            'orange juice': {
                'name': 'Orange Juice',
                'gi': 66,
                'sugar_per_100g': 9.3,
                'category': 'Medium',
                'emoji': '🧃',
                'portion': '200ml',
                'alternatives': ['water', 'herbal tea', 'vegetable juice']
            },
            'cola': {
                'name': 'Cola (regular)',
                'gi': 63,
                'sugar_per_100g': 10.6,
                'category': 'High',
                'emoji': '🥤',
                'portion': '200ml',
                'alternatives': ['water', 'tea', 'diet cola']
            },
            'milk': {
                'name': 'Milk (whole)',
                'gi': 31,
                'sugar_per_100g': 4.8,
                'category': 'Low',
                'emoji': '🥛',
                'portion': '200ml',
                'alternatives': ['almond milk', 'oat milk', 'coconut milk']
            },
            'honey': {
                'name': 'Honey',
                'gi': 58,
                'sugar_per_100g': 82.4,
                'category': 'Medium',
                'emoji': '🍯',
                'portion': '1 tbsp (20g)',
                'alternatives': ['stevia', 'maple syrup', 'agave']
            },
        }
    
    def search_food(self, query):
        """Search for food in database"""
        query = query.lower().strip()
        matches = []
        
        # Direct match
        if query in self.foods_database:
            matches.append(self.prepare_food_result(self.foods_database[query]))
        else:
            # Partial match
            for food_key, food_data in self.foods_database.items():
                if query in food_key or query in food_data['name'].lower():
                    matches.append(self.prepare_food_result(food_data))
        
        return matches if matches else None
    
    def prepare_food_result(self, food):
        """Prepare food data with alternatives details"""
        result = {
            'name': food['name'],
            'gi': food['gi'],
            'sugar_per_100g': food['sugar_per_100g'],
            'category': food['category'],
            'emoji': food['emoji'],
            'portion': food['portion'],
            'gi_status': self.get_gi_status(food['gi'])
        }
        
        # Add alternatives with their GI values
        result['alternatives'] = []
        for alt_key in food['alternatives']:
            if alt_key in self.foods_database:
                alt_food = self.foods_database[alt_key]
                result['alternatives'].append({
                    'name': alt_food['name'],
                    'gi': alt_food['gi'],
                    'category': alt_food['category'],
                    'emoji': alt_food['emoji']
                })
        
        return result
    
    def get_gi_status(self, gi_value):
        """Determine GI category"""
        if gi_value <= 55:
            return {'level': 'Low', 'color': '#28a745', 'emoji': '✅', 'advice': 'Good choice for diabetes'}
        elif gi_value <= 70:
            return {'level': 'Medium', 'color': '#ffc107', 'emoji': '⚠️', 'advice': 'Consume in moderation'}
        else:
            return {'level': 'High', 'color': '#dc3545', 'emoji': '❌', 'advice': 'Limit consumption or choose alternatives'}

# Initialize food search engine
food_search_engine = FoodSearchEngine()

# ---------------------------------------------------------------------
#  PERSISTENT USER CREDENTIAL STORAGE (using JSON file)
# ---------------------------------------------------------------------

# File to store user credentials
USERS_FILE = 'users_credentials.json'

def load_users():
    """Load users from JSON file. Create empty file if it doesn't exist."""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_users(users_dict):
    """Save users to JSON file."""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users_dict, f, indent=4)
    except IOError as e:
        print(f"Error saving users: {e}")

# Load users from file on startup
users = load_users()

# User health data storage (in-memory; replace with DB later)
# key = email, value = {predictions: [...], lab_results: [...], water_intake: [...], exercises: [...]}
user_health_data = {}

# Health tips database
health_tips = [
    "💧 Drink 8-10 glasses of water daily to stay hydrated and help regulate blood sugar",
    "🚴 Walk for 30 minutes daily - it helps improve insulin sensitivity",
    "🥗 Include fiber-rich foods in every meal to slow sugar absorption",
    "😴 Get 7-8 hours of quality sleep - poor sleep increases diabetes risk",
    "🧘 Practice 10 minutes of meditation daily to reduce stress and cortisol levels",
    "🥤 Replace sugary drinks with water, herbal tea, or unsweetened beverages",
    "🍎 Eat fruits with skin intact - they contain more fiber and nutrients",
    "⏱️ Eat slowly and chew thoroughly - aim for 20+ minutes per meal",
    "💪 Do strength training 2-3 times a week to build muscle and improve glucose control",
    "📊 Monitor your blood pressure regularly - target is below 130/80 mmHg",
]

# FAQ Database
faq_database = {
    'what_is_diabetes': {
        'question': 'What is diabetes?',
        'answer': 'Diabetes is a chronic condition where the body cannot properly regulate blood sugar levels. Type 1 occurs when the pancreas doesn\'t produce insulin. Type 2 occurs when the body becomes resistant to insulin.'
    },
    'prediabetes': {
        'question': 'What is pre-diabetes?',
        'answer': 'Pre-diabetes means your blood sugar levels are higher than normal but not yet in the diabetic range. It\'s a warning sign, but can often be reversed with lifestyle changes.'
    },
    'prevention': {
        'question': 'Can diabetes be prevented?',
        'answer': 'Yes! Type 2 diabetes can often be prevented or delayed through weight loss, regular exercise, healthy eating, and stress management. Early intervention is key.'
    },
    'diet': {
        'question': 'What should I eat if I have diabetes?',
        'answer': 'Focus on: whole grains, lean proteins, vegetables, fruits (in moderation), and healthy fats. Avoid: sugary drinks, processed foods, and excessive salt. Consult a dietitian for personalized advice.'
    },
    'exercise': {
        'question': 'How much exercise do I need?',
        'answer': 'Aim for at least 150 minutes of moderate-intensity aerobic exercise per week, plus strength training 2-3 times weekly. Even small amounts of activity are beneficial.'
    },
    'medication': {
        'question': 'Do I need medication?',
        'answer': 'Medication needs vary. Some can manage with lifestyle changes, others need medication. Your doctor will determine this based on your test results and health history.'
    },
    'monitoring': {
        'question': 'How often should I check blood sugar?',
        'answer': 'Frequency depends on your type and treatment. Type 1 typically checks multiple times daily. Type 2 may check 1-3 times daily or as recommended by doctor.'
    },
    'complications': {
        'question': 'What are diabetes complications?',
        'answer': 'Long-term complications include: heart disease, kidney disease, eye problems, nerve damage (neuropathy), and foot problems. Regular monitoring and management prevent these.'
    },
}

# ---------------------------------------------------------------------
#  ROOT + AUTH ROUTES
# ---------------------------------------------------------------------

@app.route("/")
def root():
    """Redirect to dashboard if logged in, otherwise to login."""
    if "user_email" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Basic validation
        if not name:
            error = "Name is required."
        elif not email or "@" not in email:
            error = "Valid email is required."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif password != confirm_password:
            error = "Passwords do not match."
        elif email in users:
            error = "Email already registered. Please login or use a different email."
        else:
            # Hash the password for security using PBKDF2 (compatible with all Python versions)
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            users[email] = {"name": name, "password": hashed_password}
            # Save users to file
            save_users(users)
            # After successful registration, go to login page
            return redirect(url_for("login"))

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = users.get(email)
        if not user:
            error = "Email not found. Please register first."
        elif not check_password_hash(user["password"], password):
            error = "Invalid email or password."
        else:
            # Save user in session
            session["user_email"] = email
            session["user_name"] = user["name"]
            return redirect(url_for("dashboard"))

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------------------------------------------------------------
#  DASHBOARD + FEATURE PAGES
# ---------------------------------------------------------------------

@app.route("/dashboard")
def dashboard():
    if "user_email" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")


@app.route("/precautions")
def precautions():
    if "user_email" not in session:
        return redirect(url_for("login"))
    return render_template("precautions.html")


@app.route("/diet")
def diet():
    if "user_email" not in session:
        return redirect(url_for("login"))
    return render_template("diet.html")


@app.route("/food-search", methods=['GET', 'POST'])
def food_search():
    if "user_email" not in session:
        return redirect(url_for("login"))
    
    results = None
    query = None
    error = None
    
    if request.method == 'POST':
        query = request.form.get('search', '').strip()
        
        if not query:
            error = "Please enter a food name to search"
        elif len(query) < 2:
            error = "Please enter at least 2 characters"
        else:
            results = food_search_engine.search_food(query)
            if not results:
                error = f"No foods found for '{query}'. Try: rice, bread, banana, carrot, chicken, etc."
    
    return render_template('food_search.html', 
                         results=results,
                         query=query,
                         error=error)


@app.route("/calculator")
def calculator():
    if "user_email" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")


@app.route("/exercises")
def exercises():
    if "user_email" not in session:
        return redirect(url_for("login"))
    return render_template("exercises.html")

# ---------------------------------------------------------------------
#  PREDICTION ROUTE (your original logic)
# ---------------------------------------------------------------------

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get values from the form
        input_values = []
        for feature in features:
            value = float(request.form.get(feature, 0))
            input_values.append(value)

        # Validate inputs are within reasonable ranges
        glucose = input_values[0]
        blood_pressure = input_values[1]
        skin_thickness = input_values[2]
        insulin = input_values[3]
        bmi = input_values[4]
        dpf = input_values[5]
        age = input_values[6]
        
        # Check for zero values (often indicate missing data)
        zero_count = sum(1 for i, val in enumerate(input_values) if val == 0 and i > 0)
        data_quality_warning = ""
        if zero_count >= 3:
            data_quality_warning = "⚠️ Multiple zero values detected. Some measurements may be missing. Results may be less accurate."
        
        # Scale the input
        scaled_input = scaler.transform([input_values])
        
        # Get prediction and probability
        prediction = model.predict(scaled_input)
        probability = model.predict_proba(scaled_input)[0]
        confidence = probability[1] if prediction[0] == 1 else probability[0]
        
        # Get feature importance
        importance = get_feature_importance(input_values)
        
        # Create feature contribution analysis with normal ranges
        feature_analysis = []
        feature_ranges = {
            'Glucose': {'min': 70, 'max': 100, 'unit': 'mg/dL', 'normal': 'Normal fasting: 70-100'},
            'BloodPressure': {'min': 90, 'max': 120, 'unit': 'mmHg', 'normal': 'Normal: <120/80'},
            'SkinThickness': {'min': 10, 'max': 40, 'unit': 'mm', 'normal': 'Typical: 15-35'},
            'Insulin': {'min': 0, 'max': 30, 'unit': 'mIU/L', 'normal': 'Normal: 0-25'},
            'BMI': {'min': 18.5, 'max': 24.9, 'unit': 'kg/m²', 'normal': 'Healthy: 18.5-24.9'},
            'DiabetesPedigreeFunction': {'min': 0, 'max': 1.0, 'unit': '', 'normal': 'Genetic risk factor'},
            'Age': {'min': 0, 'max': 120, 'unit': 'years', 'normal': 'Age factor'}
        }
        
        for i, feature in enumerate(features):
            value = input_values[i]
            range_info = feature_ranges.get(feature, {})
            is_abnormal = False
            status = "Normal"
            
            if feature in feature_ranges:
                min_val = range_info['min']
                max_val = range_info['max']
                if feature != 'DiabetesPedigreeFunction' and feature != 'Age':
                    if value < min_val:
                        is_abnormal = True
                        status = f"Low (normal: {min_val}-{max_val})"
                    elif value > max_val:
                        is_abnormal = True
                        status = f"High (normal: {min_val}-{max_val})"
            
            feature_analysis.append({
                'name': feature,
                'value': round(value, 1),
                'unit': range_info.get('unit', ''),
                'importance': f"{importance[i]*100:.1f}%",
                'is_abnormal': is_abnormal,
                'status': status
            })
        
        # Sort features by importance
        feature_analysis.sort(
            key=lambda x: float(x['importance'].strip('%')),
            reverse=True
        )
        
        # Risk stratification
        risk_level = "Low Risk"
        risk_color = "green"
        risk_details = "Your risk indicators suggest low diabetes risk. Maintain healthy habits."
        
        if prediction[0] == 1:
            if confidence >= 0.8:
                risk_level = "High Risk"
                risk_color = "red"
                risk_details = "High probability of diabetes. Consult a healthcare provider immediately."
            elif confidence >= 0.6:
                risk_level = "Moderate-High Risk"
                risk_color = "orange"
                risk_details = "Significant risk indicators present. Schedule a medical checkup."
            else:
                risk_level = "Moderate Risk"
                risk_color = "yellow"
                risk_details = "Some risk factors detected. Monitor your health closely."
        else:
            if confidence >= 0.85:
                risk_level = "Very Low Risk"
                risk_color = "darkgreen"
                risk_details = "Excellent indicators. Continue your healthy lifestyle."
            elif confidence >= 0.7:
                risk_level = "Low Risk"
                risk_color = "green"
                risk_details = "Good health indicators. Stay active and eat well."
        
        result = (
            "Has Diabetes"
            if prediction[0] == 1
            else "Does Not Have Diabetes"
        )
        
        # Show precautions if diabetes is detected
        show_precautions = prediction[0] == 1
        
        return render_template(
            'index.html',
            prediction=result,
            confidence=f"{confidence*100:.1f}%",
            feature_analysis=feature_analysis,
            show_precautions=show_precautions,
            risk_level=risk_level,
            risk_color=risk_color,
            risk_details=risk_details,
            data_quality_warning=data_quality_warning,
            probability_class1=f"{probability[1]*100:.1f}%",
            probability_class0=f"{probability[0]*100:.1f}%",
            model_accuracy=f"{model_accuracy*100:.2f}%"
        )
                             
    except Exception as e:
        return render_template(
            'index.html',
            prediction="Error in prediction. Please check your input values.",
            error=str(e)
        )


# -----
#  DIET RECOMMENDATION ROUTE
# -----

@app.route('/diet-recommendation', methods=['GET', 'POST'])
def diet_recommendation():
    if request.method == 'POST':
        try:
            age = int(request.form.get('age', 30))
            weight = int(request.form.get('weight', 70))
            height_cm = float(request.form.get('height', 170))
            height_m = height_cm / 100  # Convert cm to meters
            diabetes_level = request.form.get('diabetes_level', 'normal')
            diet_type = request.form.get('diet_type', 'vegetarian')
            
            # Validate inputs
            if age < 1 or age > 120 or weight < 20 or weight > 200 or height_cm < 100 or height_cm > 250:
                return render_template('diet_recommendation.html', 
                                     error="Please enter valid health metrics")
            
            # Generate diet plan (convert height back to meters for calculation)
            diet_plan = diet_engine.generate_plan(age, weight, height_m, diabetes_level, diet_type)
            
            return render_template('diet_recommendation.html', 
                                 plan=diet_plan,
                                 show_plan=True)
        
        except Exception as e:
            return render_template('diet_recommendation.html', 
                                 error=f"Error generating plan: {str(e)}")
    
    return render_template('diet_recommendation.html')


# -----
#  SYMPTOMS CHECKER ROUTE
# -----

@app.route('/symptoms-checker', methods=['GET', 'POST'])
def symptoms_checker():
    if request.method == 'POST':
        try:
            # Get selected symptoms from form
            selected_symptoms = request.form.getlist('symptoms')
            
            if not selected_symptoms:
                return render_template('symptoms_checker.html',
                                     all_symptoms=symptoms_engine.symptoms,
                                     error="Please select at least one symptom")
            
            # Calculate risk
            result = symptoms_engine.calculate_risk(selected_symptoms)
            
            return render_template('symptoms_checker.html',
                                 all_symptoms=symptoms_engine.symptoms,
                                 result=result,
                                 show_result=True)
        
        except Exception as e:
            return render_template('symptoms_checker.html',
                                 all_symptoms=symptoms_engine.symptoms,
                                 error=f"Error: {str(e)}")
    
    return render_template('symptoms_checker.html',
                         all_symptoms=symptoms_engine.symptoms)


@app.route('/bmi', methods=['GET', 'POST'])
def bmi():
    if "user_email" not in session:
        return redirect(url_for("login"))

    result = None
    error = None

    if request.method == 'POST':
        try:
            weight = float(request.form.get('weight', 70))
            height_cm = float(request.form.get('height', 170))
            age = int(request.form.get('age', 30))
            waist_input = request.form.get('waist', '').strip()
            waist_cm = float(waist_input) if waist_input else 0  # Handle empty waist
            gender = request.form.get('gender', 'other')

            if weight <= 0 or height_cm <= 0 or age <= 0:
                error = "Please enter positive numbers."
            else:
                height_m = height_cm / 100.0
                bmi_value = weight / (height_m ** 2)
                bmi_rounded = round(bmi_value, 1)
                
                # Ideal weight range (BMI 18.5-24.9)
                ideal_min = 18.5 * (height_m ** 2)
                ideal_max = 24.9 * (height_m ** 2)
                weight_diff = weight - ideal_max if weight > ideal_max else ideal_min - weight if weight < ideal_min else 0
                
                # BMI Category and Risk
                if bmi_value < 16:
                    category = "Severe Underweight"
                    risk_level = "High"
                    color = "#ff6b6b"
                    emoji = "⚠️"
                elif bmi_value < 18.5:
                    category = "Underweight"
                    risk_level = "Moderate"
                    color = "#ffa94d"
                    emoji = "⚠️"
                elif bmi_value < 25:
                    category = "Normal Weight"
                    risk_level = "Low"
                    color = "#51cf66"
                    emoji = "✅"
                elif bmi_value < 27:
                    category = "Overweight (Mild)"
                    risk_level = "Low-Moderate"
                    color = "#ffd43b"
                    emoji = "⚠️"
                elif bmi_value < 30:
                    category = "Overweight"
                    risk_level = "Moderate"
                    color = "#ffa94d"
                    emoji = "⚠️"
                elif bmi_value < 35:
                    category = "Obesity (Class I)"
                    risk_level = "High"
                    color = "#ff922b"
                    emoji = "⚠️"
                elif bmi_value < 40:
                    category = "Obesity (Class II)"
                    risk_level = "Very High"
                    color = "#ff6b6b"
                    emoji = "🚨"
                else:
                    category = "Obesity (Class III - Severe)"
                    risk_level = "Critical"
                    color = "#c92a2a"
                    emoji = "🚨"
                
                # Abdominal obesity assessment (waist circumference)
                abdominal_risk = None
                if waist_cm > 0:
                    if gender == 'male':
                        if waist_cm > 102:
                            abdominal_risk = "High (Increased abdominal fat - health risk)"
                        elif waist_cm > 94:
                            abdominal_risk = "Moderate (Elevated abdominal fat)"
                        else:
                            abdominal_risk = "Low (Healthy waist circumference)"
                    else:  # female
                        if waist_cm > 88:
                            abdominal_risk = "High (Increased abdominal fat - health risk)"
                        elif waist_cm > 80:
                            abdominal_risk = "Moderate (Elevated abdominal fat)"
                        else:
                            abdominal_risk = "Low (Healthy waist circumference)"
                
                # Age-adjusted recommendations
                if age < 18:
                    age_note = "As a young person, focus on building healthy habits now for long-term wellness."
                elif age < 40:
                    age_note = "Your age is a good time to establish or improve fitness and nutrition habits."
                elif age < 60:
                    age_note = "Monitor your weight carefully; preventive care is crucial at this stage."
                else:
                    age_note = "Regular health monitoring and medical consultation are especially important."
                
                # Health risks
                health_risks = []
                if bmi_value < 18.5:
                    health_risks = ["Malnutrition", "Weak immune system", "Low bone density", "Anemia risk"]
                elif bmi_value < 25:
                    health_risks = []
                elif bmi_value < 30:
                    health_risks = ["Early-stage metabolic issues", "Increased blood pressure risk"]
                elif bmi_value < 35:
                    health_risks = ["Type 2 Diabetes risk", "Heart disease risk", "Sleep apnea", "Hypertension", "Joint stress"]
                else:
                    health_risks = ["Severe Type 2 Diabetes risk", "Severe Heart disease risk", "Sleep apnea", "Severe Hypertension", "Reduced mobility"]
                
                # Personalized recommendations
                recommendations = []
                
                if bmi_value < 18.5:
                    recommendations = [
                        "🍎 Increase calorie intake with nutrient-dense foods (nuts, avocados, whole grains)",
                        "💪 Start strength training to build muscle mass",
                        "🏥 Consult a doctor to rule out underlying health conditions",
                        "🥗 Eat 5-6 small meals per day for better calorie absorption"
                    ]
                elif bmi_value < 25:
                    recommendations = [
                        "✅ Maintain current weight with balanced diet",
                        "🏃 Continue 150 min/week of moderate exercise",
                        "🥗 Eat plenty of vegetables, fruits, and whole grains",
                        "💧 Drink 8-10 glasses of water daily"
                    ]
                elif bmi_value < 30:
                    recommendations = [
                        "🎯 Aim to lose 5-10% of body weight over 6 months",
                        f"⚖️ Target weight: {round(ideal_max, 1)} kg (for normal BMI)",
                        "🚴 Exercise 30-45 min, 5 days/week (cardio + strength)",
                        "🥗 Reduce sugary drinks and processed foods",
                        "📊 Monitor weight weekly"
                    ]
                else:
                    recommendations = [
                        "🎯 Consult a healthcare provider and dietitian for a structured plan",
                        f"⚖️ Target weight: {round(ideal_max, 1)} kg (gradual loss of 0.5-1 kg/week)",
                        "🚴 Start with light activity (walking 20-30 min/day)",
                        "🥗 Follow a low-calorie, nutrient-dense diet",
                        "📊 Medical monitoring for comorbidities (diabetes, hypertension)",
                        "💊 Consider medical interventions if lifestyle changes don't work"
                    ]
                
                result = {
                    'bmi': bmi_rounded,
                    'category': category,
                    'risk_level': risk_level,
                    'color': color,
                    'emoji': emoji,
                    'weight': weight,
                    'height_cm': height_cm,
                    'age': age,
                    'waist_cm': waist_cm,
                    'gender': gender,
                    'ideal_min': round(ideal_min, 1),
                    'ideal_max': round(ideal_max, 1),
                    'weight_diff': round(abs(weight_diff), 1),
                    'weight_status': 'Loss' if weight > ideal_max else 'Gain' if weight < ideal_min else 'Maintain',
                    'abdominal_risk': abdominal_risk,
                    'age_note': age_note,
                    'health_risks': health_risks,
                    'recommendations': recommendations
                }

        except Exception as e:
            error = f"Error calculating BMI: {str(e)}"

    return render_template('bmi.html', result=result, error=error)


# -----
#  HEALTH TRACKING & WELLNESS FEATURES
# -----

@app.route('/health-dashboard')
def health_dashboard():
    if "user_email" not in session:
        return redirect(url_for("login"))
    
    email = session["user_email"]
    if email not in user_health_data:
        user_health_data[email] = {
            'predictions': [],
            'lab_results': [],
            'water_intake': [],
            'exercises': [],
            'health_score': 0
        }
    
    health_data = user_health_data[email]
    
    # Calculate health score (0-100)
    health_score = 50  # Base score
    if health_data['lab_results']:
        health_score += 10
    if len(health_data['exercises']) >= 3:
        health_score += 20
    if health_data['water_intake']:
        avg_water = sum([w['amount'] for w in health_data['water_intake']]) / len(health_data['water_intake'])
        if avg_water >= 8:
            health_score += 15
    
    health_score = min(health_score, 100)
    
    return render_template('health_dashboard.html',
                         health_data=health_data,
                         health_score=int(health_score),
                         predictions_count=len(health_data['predictions']),
                         last_prediction=health_data['predictions'][-1] if health_data['predictions'] else None)


@app.route('/log-water', methods=['GET', 'POST'])
def log_water():
    if "user_email" not in session:
        return redirect(url_for("login"))
    
    email = session["user_email"]
    message = None
    
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 250))
            if email not in user_health_data:
                user_health_data[email] = {'water_intake': [], 'predictions': [], 'lab_results': [], 'exercises': [], 'health_score': 0}
            
            user_health_data[email]['water_intake'].append({
                'amount': amount,
                'date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')
            })
            message = f"✅ Logged {amount}ml of water!"
        except Exception as e:
            message = f"❌ Error: {str(e)}"
    
    # Calculate today's water intake
    today_water = 0
    if email in user_health_data:
        today = pd.Timestamp.now().strftime('%Y-%m-%d')
        today_water = sum([w['amount'] for w in user_health_data[email]['water_intake'] if w['date'].startswith(today)])
    
    return render_template('water_tracker.html', message=message, today_water=today_water)


@app.route('/log-exercise', methods=['GET', 'POST'])
def log_exercise():
    if "user_email" not in session:
        return redirect(url_for("login"))
    
    email = session["user_email"]
    message = None
    
    if request.method == 'POST':
        try:
            exercise_type = request.form.get('exercise_type', 'walking')
            duration = int(request.form.get('duration', 30))
            intensity = request.form.get('intensity', 'moderate')
            
            if email not in user_health_data:
                user_health_data[email] = {'exercises': [], 'predictions': [], 'lab_results': [], 'water_intake': [], 'health_score': 0}
            
            user_health_data[email]['exercises'].append({
                'type': exercise_type,
                'duration': duration,
                'intensity': intensity,
                'date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'),
                'calories_burned': duration * {'light': 3, 'moderate': 5, 'vigorous': 8}.get(intensity, 5)
            })
            message = f"✅ Logged {duration} min of {exercise_type}!"
        except Exception as e:
            message = f"❌ Error: {str(e)}"
    
    exercises_list = []
    if email in user_health_data:
        exercises_list = user_health_data[email]['exercises'][-10:]  # Last 10
    
    return render_template('exercise_logger.html', message=message, exercises=exercises_list)


@app.route('/health-tips')
def health_tips_route():
    if "user_email" not in session:
        return redirect(url_for("login"))
    
    return render_template('health_tips.html', tips=health_tips)


@app.route('/faq')
def faq():
    if "user_email" not in session:
        return redirect(url_for("login"))
    
    return render_template('faq.html', faq_data=faq_database)


@app.route('/lab-results', methods=['GET', 'POST'])
def lab_results():
    if "user_email" not in session:
        return redirect(url_for("login"))
    
    email = session["user_email"]
    message = None
    
    if request.method == 'POST':
        try:
            test_name = request.form.get('test_name', '')
            result = request.form.get('result', '')
            unit = request.form.get('unit', '')
            normal_range = request.form.get('normal_range', '')
            
            if email not in user_health_data:
                user_health_data[email] = {'lab_results': [], 'predictions': [], 'water_intake': [], 'exercises': [], 'health_score': 0}
            
            user_health_data[email]['lab_results'].append({
                'test': test_name,
                'result': float(result),
                'unit': unit,
                'normal_range': normal_range,
                'date': pd.Timestamp.now().strftime('%Y-%m-%d')
            })
            message = f"✅ Lab result recorded: {test_name} = {result} {unit}"
        except Exception as e:
            message = f"❌ Error: {str(e)}"
    
    lab_results_list = []
    if email in user_health_data:
        lab_results_list = user_health_data[email]['lab_results']
    
    return render_template('lab_results.html', message=message, results=lab_results_list)


if __name__ == "__main__":
    app.run(debug=True)
