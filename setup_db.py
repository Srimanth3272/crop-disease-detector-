import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def setup_database():
    MONGO_URI = os.getenv("MONGO_URI")
    
    if not MONGO_URI:
        print("Error: MONGO_URI is not set in the .env file.")
        print("Please set it to your MongoDB Atlas Connection String.")
        return

    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client["smart_paddy"]
        collection = db["diseases"]
        
        # Load local JSON data
        json_path = os.path.join(os.path.dirname(__file__), "backend", "disease_info.json")
        with open(json_path, "r", encoding="utf-8") as f:
            disease_data = json.load(f)
            
        print(f"Loaded {len(disease_data)} diseases from local JSON.")
        
        # Transform and insert
        documents = []
        for disease_name, data in disease_data.items():
            # Add the disease name as an ID field
            doc = {"disease_id": disease_name}
            doc.update(data)
            documents.append(doc)
            
        # Clear existing data to prevent duplicates on rerun
        collection.delete_many({})
        
        # Insert new documents
        if documents:
            collection.insert_many(documents)
            print("Successfully uploaded data to MongoDB Cloud!")
        else:
            print("No data found to upload.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    print("Starting MongoDB Database Setup...")
    setup_database()
