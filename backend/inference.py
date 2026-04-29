import os
import random
import time
import json
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

try:
    from pymongo import MongoClient
    MONGO_URI = os.getenv("MONGO_URI")
    if MONGO_URI:
        mongo_client = MongoClient(MONGO_URI)
        db = mongo_client["smart_paddy"]
        disease_collection = db["diseases"]
        USE_MONGO = True
        print("Connected to MongoDB Cloud!")
    else:
        USE_MONGO = False
        print("No MONGO_URI found, will fall back to local JSON.")
except ImportError:
    USE_MONGO = False
    print("pymongo not installed, falling back to local JSON.")

# Try importing tensorflow, but provide a mock fallback if not installed/configured properly

try:
    import tensorflow as tf
    import numpy as np
    from PIL import Image
    HAS_TF = True
except ImportError:
    HAS_TF = False

MODEL_PATH = "paddy_model.h5"
CLASSES = ["Leaf Blast", "Brown Spot", "Bacterial Leaf Blight", "Tungro Virus", "Healthy Leaf"]

def load_disease_info():
    try:
        with open(os.path.join(os.path.dirname(__file__), "disease_info.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading disease info: {e}")
        return {}

DISEASE_DB = load_disease_info()

# Attempt to load model
model = None
if HAS_TF and os.path.exists(MODEL_PATH):
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        print("Successfully loaded TensorFlow model.")
    except Exception as e:
        print(f"Failed to load model from {MODEL_PATH}: {e}")

def get_severity(confidence):
    if confidence > 0.90:
        return "High"
    elif confidence > 0.70:
        return "Medium"
    else:
        return "Low"

def predict_image(image_path, lang='en'):
    """
    Predicts the disease for the given image path.
    Uses the trained model if available, otherwise uses a mock prediction for testing UI.
    """
    # Load info
    
    if model is not None:
        # Real Inference
        try:
            img = Image.open(image_path).convert('RGB')
            img = img.resize((224, 224))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            predictions = model.predict(img_array)[0]
            max_index = np.argmax(predictions)
            disease_name = CLASSES[max_index]
            confidence = float(predictions[max_index])
        except Exception as e:
            print(f"Error during prediction: {e}")
            disease_name = "Error"
            confidence = 0.0
    else:
        # Mock Inference
        print("Model not found. Using MOCK inference.")
        time.sleep(1.5) # Simulate processing time
        disease_name = random.choice(CLASSES)
        confidence = round(random.uniform(0.70, 0.98), 2)
        
    # Fetch from MongoDB if available, otherwise fallback to local JSON DB
    db_entry = {}
    if USE_MONGO:
        try:
            mongo_doc = disease_collection.find_one({"disease_id": disease_name})
            if mongo_doc:
                db_entry = mongo_doc
        except Exception as e:
            print(f"MongoDB Error: {e}")
            db_entry = DISEASE_DB.get(disease_name, {})
    else:
        db_entry = DISEASE_DB.get(disease_name, {})
        
    info = db_entry.get(lang, db_entry.get('en', {}))
    
    severity = get_severity(confidence) if disease_name != "Healthy Leaf" else "None"
    
    return {
        "disease": info.get("disease_display", disease_name), # Localized name
        "confidence": confidence,
        "severity": severity,
        "cause": info.get("cause", "N/A"),
        "precautions": info.get("precautions", "N/A"),
        "fertilizers": info.get("fertilizers", "N/A"),
        "pesticides": info.get("pesticides", "N/A"),
        "organic": info.get("organic", "N/A")
    }
