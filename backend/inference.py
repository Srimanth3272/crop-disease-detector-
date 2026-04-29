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
CLASSES = [
    "Leaf Blast", "Brown Spot", "Bacterial Leaf Blight", "Tungro Virus", "Healthy Leaf",
    "Sheath Blight", "Sheath Rot", "False Smut", "Stem Rot", "Bakanae Disease",
    "Narrow Brown Leaf Spot", "Khaira Disease", "Grassy Stunt Virus", "Ragged Stunt Virus", "Udbatta Disease"
]

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

def is_paddy_leaf(image_path):
    """
    Stricter heuristic check to see if an image is a plant leaf using HSV color space.
    Filters out non-plant images (documents, faces, objects) based on color distribution.
    """
    try:
        from PIL import Image
        import numpy as np
        
        img = Image.open(image_path).convert('HSV')
        img.thumbnail((150, 150)) # Speed up processing
        img_array = np.array(img)
        
        # In Pillow HSV: H is 0-255, S is 0-255, V is 0-255
        H = img_array[:, :, 0]
        S = img_array[:, :, 1]
        V = img_array[:, :, 2]
        
        # 1. Reject if the image is mostly grayscale/white/black (low saturation)
        mean_saturation = np.mean(S)
        if mean_saturation < 40: # Documents like Aadhaar have very low average saturation
            return False
            
        # 2. Count "Plant Colored" pixels (Green, Yellow, Brown) with decent saturation
        # Green Hue in PIL (0-255): approx 40 to 120
        # Yellow/Brown Hue: approx 10 to 40
        # Saturation must be > 40 to avoid considering grey as colored
        # Value must be > 30 to avoid black
        
        is_plant_color = ((H > 10) & (H < 130)) & (S > 40) & (V > 30)
        
        plant_ratio = np.sum(is_plant_color) / (img_array.shape[0] * img_array.shape[1])
        
        # A leaf close-up should have a significant amount of plant colors.
        # Require at least 20% of the image to be distinctly plant-colored.
        if plant_ratio < 0.20:
            return False
            
        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return True # Fallback to True if processing fails

def predict_image(image_path, lang='en'):
    """
    Predicts the disease for the given image path.
    Uses the trained model if available, otherwise uses a mock prediction for testing UI.
    """
    # First, validate if the image is actually a leaf
    if not is_paddy_leaf(image_path):
        error_msg = "The uploaded image does not appear to be a plant leaf."
        prec_msg = "Please upload a clear image of a paddy leaf to get accurate disease predictions."
        
        if lang == 'te':
            error_msg = "అప్‌లోడ్ చేసిన చిత్రం మొక్క ఆకులా కనిపించడం లేదు. (Aadhaar/Documents not allowed)"
            prec_msg = "ఖచ్చితమైన అంచనాల కోసం దయచేసి వరి ఆకు యొక్క స్పష్టమైన చిత్రాన్ని అప్‌లోడ్ చేయండి."
            
        return {
            "disease": "Invalid Image / చెల్లని చిత్రం" if lang == 'te' else "Invalid Image",
            "confidence": 0.0,
            "severity": "None",
            "cause": error_msg,
            "precautions": prec_msg,
            "fertilizers": "-",
            "pesticides": "-",
            "organic": "-"
        }
        
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
