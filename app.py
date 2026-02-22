import streamlit as st
import pickle
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# ─────────────────────────────────────────────
#  DATA
# ─────────────────────────────────────────────
hours = list(range(24))
registered = [12,6,4,3,4,18,70,155,185,130,108,112,118,105,112,122,178,192,155,108,84,62,42,22]
casual      = [4, 2,1,1,2, 6,12, 25, 42, 52, 58, 62, 65, 63, 60, 58, 48, 38, 28,22,16,10, 5]
months_label = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
total_rentals= [40200,22000,52000,72000,96000,115000,138000,135000,138000,104000,72000,25000]
avg_temp     = [4,5,9,15,19,24,27,26,21,15,9,5]

C = {
    'teal':'#14b8a6','cyan':'#38bdf8','purple':'#a78bfa',
    'orange':'#fb923c','green':'#4ade80',
    'grid':'rgba(255,255,255,0.04)','muted':'#3a5472','text':'#c8d6e8',
}

# ─────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────
def normalize_temperature(temp_celsius):
    """Convert Celsius temperature to normalized value (0-1 range)"""
    min_temp = -5
    max_temp = 40
    clipped_temp = np.clip(temp_celsius, min_temp, max_temp)
    normalized = (clipped_temp - min_temp) / (max_temp - min_temp)
    return normalized

def normalize_humidity(humidity_percent):
    """Convert humidity percentage (0-100) to normalized value (0-1 range)"""
    clipped_humidity = np.clip(humidity_percent, 0, 100)
    normalized = clipped_humidity / 100.0
    return normalized

def normalize_windspeed(windspeed_kmh):
    """Convert wind speed in km/h to normalized value (0-1 range)"""
    min_wind = 0
    max_wind = 50
    clipped_wind = np.clip(windspeed_kmh, min_wind, max_wind)
    normalized = (clipped_wind - min_wind) / (max_wind - min_wind)
    return normalized

def predict_for_hours(model, base_features, hours_range):
    """Generate predictions for a range of hours while keeping other features constant"""
    predictions = []
    for hour in hours_range:
        features = base_features.copy()
        features[8] = hour  # hour is at index 8
        pred_log = model.predict(features.reshape(1, -1))
        pred = int(max(0, np.expm1(pred_log)[0]))
        predictions.append(pred)
    return predictions

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Bike Rental AI",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  CUSTOM CSS (MINIMAL)
# ─────────────────────────────────────────────
st.markdown("""
<style>
.main-header {
    font-size: 1.65rem;
    font-weight: 800;
    color: #e2ecfb;
}
.nav-button {
    background: linear-gradient(145deg, #111827, #0f1c2e);
    border: 1px solid rgba(56,189,248,0.12);
    border-radius: 10px;
    padding: 12px 16px;
    margin: 4px 0;
    color: #5a7595;
    cursor: pointer;
    transition: all 0.2s;
}
.nav-button:hover {
    background: rgba(56,189,248,0.1);
    color: #c8d6e8;
}
.nav-button-active {
    background: rgba(56,189,248,0.15);
    color: #38bdf8;
    border-left: 3px solid #38bdf8;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SESSION STATE FOR NAVIGATION
# ─────────────────────────────────────────────
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

# ─────────────────────────────────────────────
#  CUSTOM SIDEBAR USING COLUMNS
# ─────────────────────────────────────────────
with st.container():
    cols = st.columns([1, 4])
    
    with cols[0]:
        st.markdown('<div class="main-header">🚲 Bike Rental AI</div>', unsafe_allow_html=True)
        
        # Custom navigation buttons
        nav_options = ["📊 Dashboard", "🌤 Weather", "🔮 Predict", "📈 Analytics"]
        
        for option in nav_options:
            # Extract the name without emoji for comparison
            option_name = option.split(" ")[1] if " " in option else option
            
            # Determine if this is the active page
            is_active = (option_name == st.session_state.page or 
                        (option_name == "Weather" and st.session_state.page == "Weather Forecast") or
                        (option_name == "Predict" and st.session_state.page == "Predict Demand"))
            
            # Create button with appropriate styling
            button_class = "nav-button-active" if is_active else "nav-button"
            
            if st.button(option, key=f"nav_{option}", use_container_width=True):
                if option == "📊 Dashboard":
                    st.session_state.page = "Dashboard"
                elif option == "🌤 Weather":
                    st.session_state.page = "Weather Forecast"
                elif option == "🔮 Predict":
                    st.session_state.page = "Predict Demand"
                elif option == "📈 Analytics":
                    st.session_state.page = "Analytics"
                st.rerun()
        
        # Model status
        st.markdown("""
        <div style="margin-top:30px;padding:14px 16px;background:rgba(20,184,166,0.05);border:1px solid rgba(20,184,166,0.13);border-radius:12px;">
            <div style="font-size:0.62rem;color:#1e3050;margin-bottom:8px;">MODEL STATUS</div>
            <div style="display:flex;align-items:center;gap:8px;">
                <span style="width:7px;height:7px;border-radius:50%;background:#22c55e;box-shadow:0 0 7px #22c55e;"></span>
                <span style="color:#7a91b0;font-size:0.81rem;">Active · Ready</span>
            </div>
            <div style="margin-top:8px;font-size:0.72rem;color:#1e3050;">Gradient Boosting · v1.0</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        # ─────────────────────────────────────────────
        #  PAGE CONTENT
        # ─────────────────────────────────────────────
        if st.session_state.page == "Dashboard":
            st.markdown('<div class="main-header">Bike Rental Dashboard</div>', unsafe_allow_html=True)
            st.markdown('<div style="color:#3a5472;margin-bottom:18px;">Historical analysis · 365 days · 8,760 hourly records</div>', unsafe_allow_html=True)
            
            # Simple placeholder content
            st.info("Dashboard content would go here")
            
        elif st.session_state.page == "Weather Forecast":
            st.markdown('<div class="main-header">Weather Forecast</div>', unsafe_allow_html=True)
            st.markdown('<div style="color:#3a5472;margin-bottom:22px;">7-day outlook and estimated impact on bike demand</div>', unsafe_allow_html=True)
            st.info("Weather forecast content would go here")
            
        elif st.session_state.page == "Predict Demand":
            st.markdown('<div class="main-header">Predict Demand</div>', unsafe_allow_html=True)
            st.markdown('<div style="color:#3a5472;margin-bottom:22px;">Enter conditions to forecast hourly bike rentals</div>', unsafe_allow_html=True)
            st.info("Prediction form would go here")
            
        elif st.session_state.page == "Analytics":
            st.markdown('<div class="main-header">Analytics</div>', unsafe_allow_html=True)
            st.markdown('<div style="color:#3a5472;margin-bottom:22px;">Deep dive into rental patterns and trends</div>', unsafe_allow_html=True)
            st.info("Analytics content would go here")
