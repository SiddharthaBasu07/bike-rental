import pickle
import os

print("Testing model loading...")
models = [
    'bike_model_gradientboosting.pkl',
    'bike_model_randomforest.pkl',
    'bike_model_xgboost.pkl',
    'bike_model_catboost.pkl'
]

for model_file in models:
    if os.path.exists(model_file):
        try:
            with open(model_file, 'rb') as f:
                model = pickle.load(f)
            print(f"✅ {model_file} - Loaded successfully")
        except Exception as e:
            print(f"❌ {model_file} - Failed to load: {e}")
    else:
        print(f"❌ {model_file} - File not found")
