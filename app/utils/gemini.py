from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

# Load environment variables once at module level
load_dotenv()

def get_chatbot_response(data):
    # Create a fresh client and chat for each request
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    chat = client.chats.create(
        model='gemini-2.5-flash-lite',
        config=types.GenerateContentConfig(
            system_instruction=[
                "You are a helpful assistant that helps people find information."
            ]
        ),
    )
    response = chat.send_message(message=data)
    
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

Compute the user’s adjusted energy baseline using the rolling previously detected average of past consumptions, 
Recalibrate the baseline if the user saves ≥30% for 3 consecutive months, 
using the average of those 3 months × Sm, capped at ±20% monthly change. 
Only count energy savings ≥5% below the adjusted baseline as valid. Output the adjusted baseline (kWh), 
applied season factor, and a recalibration flag (true if triggered).
Each kWh saved is equivalent to 0.2 Token & multiplied by a seasonal factor (get the multipliers from reward_index_multiplier).  



Return only a valid JSON object with the following keys:

{ 
  "baseline": number,                       // adjusted energy baseline
  "currentUsage": number,                   // consumption for the current billing cycle
  "energySaved": number,                    // baseline - currentUsage
  "sinagTokens": number,                    // total tokens rewarded based on energy saved
  "rate": number,                           // electricity rate (per kWh)
  "month": string,                          // current billing month
  "current_season": string,                 // e.g., "Wet", "Dry" (refer to the season_index)
  "message": string,                        // concise analysis including how the baseline was derived + energy-saving advice
  "Environmental_Impact": number,           // Equiv GHG Emissions in tons CO2
  "suggestion": string,                       // personalized energy-saving suggestion
  "To_Offset_Emissions": number,            // trees needed to offset emissions
  "saved_Percentage": number,              // percentage of energy saved this month
  "history": [                               
    {
      "month": string,
      "kWh_consumed": number,               // kwh consumed in that month
      "tokensEarned": number                // tokens earned that month based on savings
    }
  ]
}


Instructions:

1. For the "history" field: Extract month and kWh consumption from the chart/table visible in the bill image.
   - month: the month name or abbreviation
   - billAmount: calculate as (kwh_consumed × rate), rounded to 2 decimal places
   - tokensEarned: calculate tokens earned that month based on savings (use the energy_saved for that month × reward_index_multiplier)
   - status: set to "paid" for past months shown in the bill
   DO NOT invent or estimate data that is not visible in the image.
   If historical consumption data is not visible in the bill, return an empty array [].

2. Clearly explain how the baseline was obtained in the message field.

3. When estimating contextual effects (like weather or holidays), simulate a short reasoning process to make the explanation realistic.

4. Use camelCase for all JSON keys (e.g., currentUsage, energySaved, sinagTokens, billAmount, tokensEarned).

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
        
        # Create a fresh client for each request
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Use Gemini to extract text from image
        # For vision models, system instruction must be in contents, not config
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[
                sysin,  # System instruction as first content
                types.Part.from_bytes(
                    data=img_byte_arr.read(),
                    mime_type=f"image/{(image.format or 'png').lower()}",
                ),
            ],
            config=types.GenerateContentConfig(
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