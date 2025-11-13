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

sysin = """
    You are an intelligent model that analyzes electricity bills to determine energy usage trends and establish a baseline for a saved energy tracker application.
You are provided with bill data (or extracted information from bill images) and should reason about patterns in electricity consumption.

Your task is to:

Analyze the past billing results detected from the provided bill image or data.

Establish a baseline for energy consumption by:

Calculating the average kWh usage from previous months.

Adjusting that average based on external contextual factors such as weather conditions, temperature, holidays, occupancy changes, or local events that typically influence energy use.

Optionally perform a conceptual search or reasoning step to infer how similar external factors (like seasonal heat or cold) may impact electricity demand in the current month.

Use this reasoning to explain how the baseline was derived.

Return only a valid JSON object with the following keys:

{
  "current_usage": number,                  // current month’s usage in kWh
  "energy_saved": number,                   // difference vs previous month in kWh
  "month": string,                          // current billing month
  "rate_this_month": number,                // electricity rate (per kWh)
  "actual_consumption": number,             // total consumption in kWh
  "baseline": number,                       // estimated baseline consumption based on historical + contextual data
  "message": string                         // concise analysis including how the baseline was derived + energy-saving advice
  "Environmental_Impact":                   // Equiv GHG Emissions
  "To_Offset_Emissions: number               // trees needed to offset emissions    
}


Instructions:

Clearly explain how the baseline was obtained in the message field (e.g., “Baseline derived from average usage of detected previous months adjusted for warmer weather and longer daytime hours.”).

When estimating contextual effects (like weather or holidays), simulate a short reasoning or search process to make the explanation realistic and informed.

Output JSON only, no extra text."""

def extract_text_from_image(image):
    """
    Extract text from an image using Gemini Vision API
    Args:
        image: PIL Image object
    Returns:
        dict: Extracted data as JSON object
    """
    try:
        # Convert PIL Image to bytes
        import io
        import json
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format or 'PNG')
        img_byte_arr.seek(0)
        
        # Use Gemini to extract text from image
        response = chat_service.client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[
                types.Part.from_bytes(
                    data=img_byte_arr.read(),
                    mime_type=f"image/{(image.format or 'png').lower()}",
                ),
            ],
            config=types.GenerateContentConfig(
                system_instruction=sysin,
                response_mime_type="application/json"
            )
        )
        
        # Parse and return JSON
        if response.text:
            return json.loads(response.text)
        else:
            raise Exception("Empty response from Gemini API")
    except Exception as e:
        raise Exception(f"Failed to extract text from image: {str(e)}")