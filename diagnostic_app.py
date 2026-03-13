import streamlit as st
import pickle
import os
import glob

st.set_page_config(page_title="Model Test", page_icon="🔧")

st.title("🔧 Model Diagnostic Tool")

st.write(f"**Current directory:** {os.getcwd()}")

# List all files
st.subheader("📁 Files in directory")
files = os.listdir('.')
pkl_files = [f for f in files if f.endswith('.pkl')]

if pkl_files:
    st.success(f"Found {len(pkl_files)} .pkl files:")
    for f in pkl_files:
        size = os.path.getsize(f) / (1024*1024)
        st.write(f"- {f} ({size:.2f} MB)")
else:
    st.error("No .pkl files found!")

# Try loading models
st.subheader("🔄 Loading models")

model_files = {
    'bike_model_gradientboosting.pkl': 'Gradient Boosting',
    'bike_model_randomforest.pkl': 'Random Forest',
    'bike_model_xgboost.pkl': 'XGBoost',
    'bike_model_catboost.pkl': 'CatBoost',
}

loaded_models = []

for filename, display_name in model_files.items():
    if os.path.exists(filename):
        try:
            with open(filename, 'rb') as f:
                model = pickle.load(f)
            st.success(f"✅ {display_name} - Loaded successfully")
            loaded_models.append(display_name)
        except Exception as e:
            st.error(f"❌ {display_name} - Failed to load: {e}")
    else:
        st.warning(f"⚠️ {display_name} - File not found: {filename}")

if loaded_models:
    st.subheader("✅ Available models")
    st.write(f"Loaded: {', '.join(loaded_models)}")
else:
    st.error("❌ No models could be loaded!")

st.info("If models are missing, run: python retrain_models.py")
