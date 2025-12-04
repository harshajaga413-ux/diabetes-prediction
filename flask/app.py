import numpy as np
import pandas as pd
from flask import Flask, request, render_template, session, redirect, url_for
import pickle
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler

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
    
    return knn, scaler, features

# Train model and get components
model, scaler, features = train_and_save_model()

def get_feature_importance(input_values):
    """Calculate the relative importance of each feature's contribution"""
    scaled_input = scaler.transform([input_values])
    neighbors = model.kneighbors(scaled_input, return_distance=True)
    distances = neighbors[0][0]
    importance = 1 / (distances + 1e-10)  # Add small constant to avoid division by zero
    return importance / importance.sum()

# ---------------------------------------------------------------------
#  SIMPLE IN-MEMORY USER STORE (demo only – replace with DB later)
# ---------------------------------------------------------------------

# key = email, value = {"name": ..., "password": ...}
users = {}

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
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Basic validation
        if not name or not email or not password or len(password) < 6:
            return render_template("register.html")

        if email in users:
            # Email already registered
            return render_template("register.html")

        users[email] = {"name": name, "password": password}
        # After successful registration, go to login page
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = users.get(email)
        if not user or user["password"] != password:
            # Invalid credentials – re-render login
            return render_template("login.html")

        # Save user in session
        session["user_email"] = email
        session["user_name"] = user["name"]
        return redirect(url_for("dashboard"))

    return render_template("login.html")


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


@app.route("/sugar-levels")
def sugar_levels():
    if "user_email" not in session:
        return redirect(url_for("login"))
    return render_template("sugar_levels.html")


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

        # Scale the input
        scaled_input = scaler.transform([input_values])
        
        # Get prediction and probability
        prediction = model.predict(scaled_input)
        probability = model.predict_proba(scaled_input)[0]
        confidence = probability[1] if prediction[0] == 1 else probability[0]
        
        # Get feature importance
        importance = get_feature_importance(input_values)
        
        # Create feature contribution analysis
        feature_analysis = []
        for i, feature in enumerate(features):
            feature_analysis.append({
                'name': feature,
                'value': input_values[i],
                'importance': f"{importance[i]*100:.1f}%"
            })
        
        # Sort features by importance
        feature_analysis.sort(
            key=lambda x: float(x['importance'].strip('%')),
            reverse=True
        )
        
        result = (
            "High risk of diabetes - Please consult a doctor"
            if prediction[0] == 1
            else "Low risk of diabetes"
        )
        
        return render_template(
            'index.html',
            prediction=result,
            confidence=f"{confidence*100:.1f}%",
            feature_analysis=feature_analysis
        )
                             
    except Exception as e:
        return render_template(
            'index.html',
            prediction="Error in prediction. Please check your input values.",
            error=str(e)
        )


if __name__ == "__main__":
    app.run(debug=True)
