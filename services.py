import google.generativeai as genai
import os
import re
import json
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash')

# auto description
async def generate_menu_details(name: str, ingredients: list):
    ingredients_str = ", ".join(ingredients)
    
    prompt = f"""
    You are a professional Michelin Star Chef.
    Menu item: "{name}" made from: "{ingredients_str}".
    
    Task:
    1. Write appetizing description (max 1 sentence).
    2. Estimate calories (integer).

    Return JSON only:
    {{
        "description": "...",
        "calories": 150
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        if result_text.startswith("```"):
            result_text = result_text.replace("```json", "").replace("```", "")
            
        return json.loads(result_text)
    except Exception as e:
        return {"description": "Delicious homemade dish (AI unavailable).", "calories": 0}

#Allergan & health scanner
async def analyze_health(name: str, ingredients: list):
    ingredients_str = ", ".join(ingredients)
    
    prompt = f"""
    Analyze this menu item: "{name}" made from: "{ingredients_str}".
    
    Act as a Nutritionist. Return JSON only:
    1. allergens: List of common allergens found (e.g. Peanuts, Seafood, Gluten, Dairy). If none, empty list [].
    2. diet_labels: List of diets suitable (e.g. Vegan, Keto, Halal, High Protein).
    3. health_score: Integer 1-10 (10 is healthiest).
    4. advice: 1 short sentence advice.

    Format:
    {{
        "allergens": ["..."],
        "diet_labels": ["..."],
        "health_score": 8,
        "advice": "..."
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "")
        return json.loads(text)
    except Exception as e:
        return {
            "allergens": [], 
            "diet_labels": [], 
            "health_score": 5, 
            "advice": "Data kesehatan tidak tersedia saat ini."
        }


async def calculate_burn_activity(name: str, calories: int):
    prompt = f"""
    I have a food item: "{name}" which is approximately {calories} calories.
    
    Act as a Personal Trainer. 
    Calculate how long (in minutes) a person needs to do these exercises to burn those {calories} calories:
    1. Running (Lari)
    2. Cycling (Sepeda)
    3. Swimming (Renang)
    
    Return JSON format only:
    {{
        "exercises": [
            {{ "activity": "Running", "duration": "XX mins", "intensity": "Medium" }},
            {{ "activity": "Cycling", "duration": "XX mins", "intensity": "Low" }},
            {{ "activity": "Swimming", "duration": "XX mins", "intensity": "High" }}
        ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "")
        return json.loads(text)
    except Exception as e:
        print(f"❌ ERROR GEMINI BURN CALORIES: {e}")
        print(f"📄 TEXT DARI AI: {text if 'text' in locals() else 'Kosong'}")
        return {
            "exercises": [
                {"activity": "Jalan Kaki", "duration": "60 mins", "intensity": "Low"}
            ]
        }