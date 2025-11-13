


from flask import jsonify, Blueprint, request
from ..utils.gemini import get_chatbot_response, extract_text_from_image
from PIL import Image
import io
import json
import re

bot_bp = Blueprint('bot_bp', __name__)

@bot_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('prompt')

        response_message = get_chatbot_response(user_message)
        return jsonify({"response": response_message})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@bot_bp.route('/extract', methods=['POST'])
def extract():
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Open the image
        img = Image.open(file.stream)
        
        # Extract text using Gemini Vision
        extracted_text = extract_text_from_image(img)
        
        return jsonify({"extracted_text": extracted_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    