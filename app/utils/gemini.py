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

season_index = {
    Wet: June – November
    Dry: December – May
}

reward_index_multiplier = {
   dry: 1.2,
   wet: 1  
}

Compute the user’s adjusted energy baseline using the rolling previously detected average of past consumption, 
multiplied by a seasonal factor (Sm: 0.9 for cool/rainy, 1.0–1.1 for transition, 1.2 for hot/dry).  
Recalibrate the baseline if the user saves ≥30% for 3 consecutive months, 
using the average of those 3 months × Sm, capped at ±20% monthly change. 
Only count energy savings ≥5% below the adjusted baseline as valid. Output the adjusted baseline (kWh), 
applied season factor, and a recalibration flag (true if triggered), each kWh saved is equivalent to 0.2 Token.



Return only a valid JSON object with the following keys:

{ 
  "baseline": number,                      
  "energy_saved": number,                   // baseline - current_usage
  "month": string,                          // current billing month
  "current_season": string,                  // e.g., "Winter", "Summer"(refer to the season_index)
  "rate_this_month": number,                // electricity rate (per kWh)
  "actual_consumption": number,             // total consumption in kWh
  "message": string                         // concise analysis including how the baseline was derived + energy-saving advice
  "Environmental_Impact": number,            // Equiv GHG Emissions in tons CO2
  "To_Offset_Emissions": number,             // trees needed to offset emissions
  "Token_reward": number,                    // tokens rewarded based on energy saved (energy_saved * reward_index_multiplier)
  "history": [                               
    {
      "month": string,
      "kwh_consumed": number
    }
  ]
}


Instructions:

1. For the "history" field: ONLY extract month and kwh_consumed from the chart/table visible in the bill image. 
   DO NOT include any other fields like billAmount, status, or tokensEarned.
   DO NOT invent or estimate data that is not visible in the image.
   If historical consumption data is not visible in the bill, return an empty array [].

2. Clearly explain how the baseline was obtained in the message field.

3. When estimating contextual effects (like weather or holidays), simulate a short reasoning process to make the explanation realistic.

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