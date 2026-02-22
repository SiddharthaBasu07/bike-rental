import streamlit as st
import pickle
import numpy as np
import pandas as pd

# -----------------------------
# Load Trained Model
# -----------------------------
model = pickle.load(open("bike_model.pkl", "rb"))

st.title("🚲 Bike Rental Demand Prediction")
st.write("Enter details below to predict hourly bike rentals.")

# -----------------------------
# User Inputs
# -----------------------------

season = st.selectbox("Season (1=Spring, 2=Summer, 3=Fall, 4=Winter)", [1, 2, 3, 4])
holiday = st.selectbox("Holiday (0=No, 1=Yes)", [0, 1])
workingday = st.selectbox("Working Day (0=No, 1=Yes)", [0, 1])
weather = st.selectbox("Weather (1=Clear, 2=Mist, 3=Light Rain, 4=Heavy Rain)", [1, 2, 3, 4])

temp = st.number_input("Temperature (Celsius)", value=25.0)
atemp = st.number_input("Feels Like Temperature (Celsius)", value=27.0)
humidity = st.number_input("Humidity", value=60)
windspeed = st.number_input("Wind Speed", value=10.0)

year = st.selectbox("Year (0=2011, 1=2012)", [0, 1])
month = st.slider("Month", 1, 12, 6)
day = st.slider("Day", 1, 31, 15)
hour = st.slider("Hour", 0, 23, 12)
dayofweek = st.slider("Day of Week (0=Monday, 6=Sunday)", 0, 6, 3)

# -----------------------------
# Prediction
# -----------------------------

if st.button("Predict Demand"):

    # Create input dictionary
    input_dict = {
        'season': season,
        'holiday': holiday,
        'workingday': workingday,
        'weather': weather,
        'temp': temp,
        'atemp': atemp,
        'humidity': humidity,
        'windspeed': windspeed,
        'year': year,
        'month': month,
        'day': day,
        'hour': hour,
        'dayofweek': dayofweek
    }

    # Convert to DataFrame
    input_df = pd.DataFrame([input_dict])

    # Ensure column order EXACTLY matches training
    input_df = input_df.reindex(columns=model.feature_names_in_, fill_value=0)

    # Predict (model was trained on log1p)
    prediction_log = model.predict(input_df)

    # Reverse log transform
    prediction = np.expm1(prediction_log)

    st.success(f"🚲 Predicted Bike Rentals: {int(prediction[0])}")