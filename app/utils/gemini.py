from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

class ChatConfig():
    def __init__(self):
        load_dotenv()
        self.client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        self.chat = self.client.chats.create(model='gemini-2.5-flash-lite',
                               config=types.GenerateContentConfig(
                                    system_instruction=[
                                        "You are a helpful assistant that helps people find information."
                                        ]
                                    ),
                                )

chat_service = ChatConfig()

def get_chatbot_response(data):
    # generate a chat instance from each request
    response = chat_service.chat.send_message(message=data)

    # Return the content of the chatbot message
    return response.text  