


from flask import jsonify, Blueprint, request
from ..utils.gemini import get_chatbot_response

bot_bp = Blueprint('bot_bp', __name__)

@bot_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('prompt')

    response_message = get_chatbot_response(user_message)
    return jsonify({"response": response_message})