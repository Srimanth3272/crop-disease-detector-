import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import sys

# Ensure backend module can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.inference import predict_image

app = Flask(__name__)
CORS(app)

import tempfile

# Vercel has a read-only file system, so we must use /tmp for uploads
if os.environ.get("VERCEL") == "1":
    app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
else:
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB max

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"error": "No image part"}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected image"}), 400
        
    if file:
        lang = request.form.get('lang', 'en')
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Get prediction using our inference module with language
            result = predict_image(filepath, lang=lang)
            
            # Clean up the file
            os.remove(filepath)
            
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Running on all interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)
