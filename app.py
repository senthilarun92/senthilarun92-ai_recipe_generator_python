from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from groq import Groq
import json
import re
import webbrowser
import threading

app = Flask(__name__)

CORS(app)

# =========================================
# GROQ API KEY
# =========================================

client = Groq(
    api_key="YOUR_GROQ_API_KEY"
)

# =========================================
# OPEN BROWSER
# =========================================

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")


# =========================================
# HOME PAGE
# =========================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================
# SUGGEST DISHES
# =========================================

@app.route("/suggest_dishes", methods=["POST"])
def suggest_dishes():

    try:

        data = request.get_json()

        ingredients = data.get("ingredients", "")
        cuisine = data.get("cuisine", "Any")
        diet = data.get("diet", "Any")
        language = data.get("language", "English")

        prompt = f"""
You are a professional chef AI.

Ingredients:
{ingredients}

Cuisine:
{cuisine}

Diet:
{diet}

Generate 5 recipe ideas.

IMPORTANT:
Return ONLY valid JSON.

Format:

{{
  "recipes": [
    {{
      "name": "Recipe Name",
      "description": "Short tasty description"
    }}
  ]
}}

Language:
{language}
"""

        completion = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.7,
            max_tokens=2000
        )

        result = completion.choices[0].message.content

        print("\nRAW DISH RESPONSE:\n")
        print(result)

        # CLEAN RESPONSE

        clean = re.sub(r"```json", "", result)
        clean = re.sub(r"```", "", clean)
        clean = clean.strip()

        # EXTRACT JSON

        start = clean.find("{")
        end = clean.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("No JSON object found")

        json_text = clean[start:end+1]

        recipes = json.loads(json_text)

        return jsonify(recipes)

    except Exception as e:

        print("SUGGEST ERROR:", str(e))

        return jsonify({
            "error": str(e)
        })


# =========================================
# GENERATE FULL RECIPE
# =========================================

@app.route("/generate_recipe", methods=["POST"])
def generate_recipe():

    try:

        data = request.get_json()

        dish_name = data.get("dish_name", "")
        language = data.get("language", "English")

        prompt = f"""
Generate a detailed recipe for:

{dish_name}

IMPORTANT:
Return ONLY valid JSON.

Format:

{{
  "recipe": {{

    "title": "Recipe Name",

    "description": "Recipe description",

    "prep_time": "15 mins",

    "cook_time": "30 mins",

    "servings": 2,

    "difficulty": "Easy",

    "nutrition": {{
      "calories": "350 kcal",
      "protein": "15g",
      "carbs": "40g",
      "fat": "10g"
    }},

    "ingredients": [
      "ingredient 1",
      "ingredient 2"
    ],

    "instructions": [
      "step 1",
      "step 2"
    ],

    "tips": "Chef tip",

    "similar": [
      "recipe 1",
      "recipe 2"
    ]

  }}
}}

Language:
{language}
"""

        completion = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.7,
            max_tokens=4000
        )

        result = completion.choices[0].message.content

        print("\nRAW RECIPE RESPONSE:\n")
        print(result)

        # CLEAN RESPONSE

        clean = re.sub(r"```json", "", result)
        clean = re.sub(r"```", "", clean)
        clean = clean.strip()

        # EXTRACT JSON

        start = clean.find("{")
        end = clean.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("No JSON object found")

        json_text = clean[start:end+1]

        recipe = json.loads(json_text)

        return jsonify(recipe)

    except Exception as e:

        print("RECIPE ERROR:", str(e))

        return jsonify({
            "error": str(e)
        })


# =========================================
# RUN APP
# =========================================

if __name__ == "__main__":

    threading.Timer(1.5, open_browser).start()

    app.run(
        debug=True,
        use_reloader=False
    )