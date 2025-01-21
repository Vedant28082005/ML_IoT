from flask import Flask, request, jsonify
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import firebase_admin
from firebase_admin import credentials, firestore, db

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://dht-11-iot-92762-default-rtdb.asia-southeast1.firebasedatabase.app/'  # Replace with your RTDB URL
})

# Firestore client
firestore_db = firestore.client()

# Function to post sensor data to Firestore
def post_sensor_data_firestore(temperature, humidity):
    doc_ref = firestore_db.collection('sensor_data').document()
    doc_ref.set({
        'timestamp': firestore.SERVER_TIMESTAMP,
        'temperature': temperature,
        'humidity': humidity
    })
    print(f"Data posted to Firestore: Temperature={temperature}, Humidity={humidity}")

# Function to post sensor data to RTDB
def post_sensor_data_rtdb(classification_result):
    # Ensure classification_result is JSON serializable
    if isinstance(classification_result, np.ndarray):
        classification_result = classification_result.tolist()  # Convert NumPy array to list
    elif not isinstance(classification_result, (str, list, dict)):
        classification_result = str(classification_result)  # Convert other types to string

    ref = db.reference("/")
    db.reference("/sensor_data").set(classification_result)

    print(f"Data posted to RTDB: Classification={classification_result}")


# Initialize the scaler
scaler = StandardScaler()

# Example data for scaling (required for consistent scaling during prediction)
data = {
    'Temperature': [30, 22, 25, 18, 28, 24, 21, 19, 35, 32],
    'Humidity': [70, 80, 65, 90, 75, 85, 95, 60, 50, 55],
    'Weather': ['Sunny', 'Rainy', 'Sunny', 'Rainy', 'Sunny', 'Rainy', 'Rainy', 'Sunny', 'Sunny', 'Sunny']
}

df = pd.DataFrame(data)

# Map weather strings to numeric values
weather_mapping = {'Sunny': 0, 'Rainy': 1, 'Cloudy': 2}
df['Weather'] = df['Weather'].map(weather_mapping)

# Fit the scaler using the example data
scaler.fit(df[['Temperature', 'Humidity']])

# Load the pre-trained model
with open('weather_model.pkl', 'rb') as f:
    loaded_model = pickle.load(f)

# Initialize the Flask app
app = Flask(__name__)

@app.route('/predict', methods=['GET'])
def predict_weather():
    # Fetch query parameters from the URL
    temperature = request.args.get('temperature', type=float)
    humidity = request.args.get('humidity', type=float)

    # Check if both parameters are provided
    if temperature is None or humidity is None:
        return "Please provide both 'Temperature' and 'Humidity' as query parameters.", 400

    # Prepare and scale the input data
    input_data = np.array([[temperature, humidity]])
    scaled_data = scaler.transform(input_data)

    # Make a prediction
    prediction = loaded_model.predict(scaled_data)
    #classification_result = int(prediction[0])  # Convert prediction to an integer

    # Post data to Firestore and RTDB
    post_sensor_data_firestore(temperature, humidity)
    post_sensor_data_rtdb(prediction)

    # Return the result as plain text
    return f"Predicted Weather: {prediction}"

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
