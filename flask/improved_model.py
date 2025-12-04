import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
import pickle

# Import and preprocess data
dataset = pd.read_csv('diabetes.csv')

# Replace zero values with NaN and then fill with mean
columns_to_process = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
dataset[columns_to_process] = dataset[columns_to_process].replace(0, np.NaN)
for column in columns_to_process:
    dataset[column].fillna(dataset[column].mean(), inplace=True)

# Select all relevant features
features = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
X = dataset[features]
y = dataset['Outcome']

# Scale the features
scaler = MinMaxScaler(feature_range=(0, 1))
X_scaled = scaler.fit_transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=features)

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.20, random_state=42, stratify=dataset['Outcome'])

# Train KNN model
knn = KNeighborsClassifier(n_neighbors=24, metric='minkowski', p=2)
knn.fit(X_train, y_train)

# Save both the model and the scaler
model_data = {
    'model': knn,
    'scaler': scaler,
    'features': features
}

with open('improved_model.pkl', 'wb') as f:
    pickle.dump(model_data, f)

# Print model accuracy
print(f"Model accuracy: {knn.score(X_test, y_test) * 100:.2f}%")