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

sysin = """You are a model that analyzes electricity bills and creates a baseline for saved energy tracker applications.
    based on the past results of the bill image provided, create a baseline for energy consumption.
    Get the baseline by analyzing the average consumption from the bill image provided, and at the same time also take into account the weather, holidays, and other factors that may affect energy consumption.
    and other important external factors that affects the consumption and the user, and from this create a rough estimation of baseline for energy consumption.

    Return a JSON object with the following keys:
    current_usage: number (the current usage in kWh)
    energy_saved: number (the energy saved in kWh compared to last month)
    month: string (the month of the bill)
    rate_this_month: number (the rate for this month in kWh)
    actual_consumption: number (the actual consumption in kWh)
    message: string (a brief analysis of the bill + tips to save energy)
    baseline: number (the baseline energy consumption in kWh)"""

def extract_text_from_image(image):
    """
    Extract text from an image using Gemini Vision API
    Args:
        image: PIL Image object
    Returns:
        str: Extracted text from the image
    """
    try:
        # Convert PIL Image to bytes
        import io
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format or 'PNG')
        img_byte_arr.seek(0)
        
        # Use Gemini to extract text from image
        response = chat_service.client.models.generate_content(
            model='gemini-2.0-flash-lite',
            contents=[
                types.Part.from_bytes(
                    data=img_byte_arr.read(),
                    mime_type=f"image/{(image.format or 'png').lower()}",
                ),
            ],
            config=types.GenerateContentConfig(
                system_instruction=sysin
            )
        )
        
        return response.text
    except Exception as e:
        raise Exception(f"Failed to extract text from image: {str(e)}")