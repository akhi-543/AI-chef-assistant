import streamlit as st
import google.generativeai as genai
import json
from typing import Dict
import re
import requests
import json.decoder  
import plotly.express as px
if 'EDAMAM_APP_ID' not in st.secrets or 'EDAMAM_API_KEY' not in st.secrets:
    st.error("Please set your Edamam API credentials in Streamlit secrets!")
    st.stop()
if 'GOOGLE_API_KEY' not in st.secrets:
    st.error("Please set your Google API key in Streamlit secrets!")
    st.stop()

genai.configure(api_key=st.secrets['GOOGLE_API_KEY'])

# Initialize Gemini model
model = genai.GenerativeModel('gemini-pro')
def clean_ingredients(ingredients_list):
    """Enhance and clean the ingredients list for better API recognition."""
    cleaned_ingredients = []
    
    for ingredient in ingredients_list:
        cleaned_ingredient = str(ingredient).strip()
        
        # Example of cleaning vague ingredients
        if "chicken" in cleaned_ingredient.lower():
            cleaned_ingredient = "boneless chicken breast"
        if "salt" in cleaned_ingredient.lower():
            cleaned_ingredient = "table salt"
        if "sugar" in cleaned_ingredient.lower():
            cleaned_ingredient = "granulated sugar"
        if "flour" in cleaned_ingredient.lower():
            cleaned_ingredient = "all-purpose flour"
        
        # Add more cleaning logic as necessary based on common ingredients
        
        cleaned_ingredients.append(cleaned_ingredient)
    
    return cleaned_ingredients
def fetch_nutritional_info(ingredients_list):
    """Fetch detailed nutritional information from Edamam API."""
    url = "https://api.edamam.com/api/nutrition-details"
    headers = {"Content-Type": "application/json"}
    
    # Clean the ingredients list before sending to the API
    ingredients_list = clean_ingredients(ingredients_list)
    
    # Ensure ingredients are strings
    ingredients_list = [str(ingredient) for ingredient in ingredients_list]
    
    payload = {
        "title": "Generated Recipe",
        "ingr": ingredients_list
    }
    
    response = requests.post(
        f"{url}?app_id={st.secrets['EDAMAM_APP_ID']}&app_key={st.secrets['EDAMAM_API_KEY']}",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching nutrition data: {response.status_code} - {response.text}")
        return None
    

def generate_recipe_prompt(ingredients: str, cuisine_type: str, dietary_restrictions: str) -> str:
    """Generate a prompt for the recipe generation."""
    return f"""Create a detailed recipe based on these parameters:
    Ingredients available: {ingredients}
    Cuisine type: {cuisine_type}
    Dietary restrictions: {dietary_restrictions}

    Please provide the recipe in this JSON format:
    {{
        "name": "Recipe Name",
        "description": "Brief description",
        "servings": "Number of servings",
        "prep_time": "Preparation time",
        "cook_time": "Cooking time",
        "ingredients": ["list", "of", "ingredients", "with", "measurements"],
        "instructions": ["Step 1", "Step 2", "etc"],
        "tips": ["Helpful tip 1", "Helpful tip 2"],
        "nutrition": {{
            "calories": "per serving",
            "protein": "in grams",
            "carbs": "in grams",
            "fat": "in grams"
        }}
    }}
    Please ensure the response is valid JSON format."""

def get_ai_cooking_advice(question: str) -> str:
    """Get AI-powered cooking advice using Gemini."""
    prompt = f"""As an expert chef, provide helpful advice for this cooking question:
    Question: {question}
    
    Please provide detailed, practical advice that would be helpful for home cooks."""

    response = model.generate_content(prompt)
    return response.text

def generate_ai_recipe(ingredients: str, cuisine_type: str, dietary_restrictions: str) -> Dict:
    """Generate a recipe using Gemini AI."""
    try:
        prompt = generate_recipe_prompt(ingredients, cuisine_type, dietary_restrictions)
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        recipe_str = response.text.strip()
        if recipe_str.startswith("```json"):
            recipe_str = recipe_str[7:-3]
        
        # Remove any non-JSON content
        recipe_str = re.sub(r'[^\x00-\x7F]+', '', recipe_str)
        
        # Attempt JSON parsing
        try:
            recipe = json.loads(recipe_str)
        except json.decoder.JSONDecodeError as e:
            st.error(f"JSON decoding error: {str(e)}. Attempting to fix the response.")
            st.write(recipe_str)  # Display raw JSON for debugging
            return None
        
        # Fetch detailed nutritional info
        detailed_nutrition = fetch_nutritional_info(recipe['ingredients'])
        if detailed_nutrition:
            recipe['nutrition']['detailed'] = detailed_nutrition['totalNutrients']
        
        return recipe
    
    except Exception as e:
        st.error(f"Error generating recipe: {str(e)}")
        return None
def calculate_daily_values(nutrients):
    daily_values = {
        "Protein": 50,    # grams
        "Carbs": 275,     # grams
        "Fat": 78,        # grams
        "Fiber": 28,      # grams
        "Sugars": 50,     # grams
        "Saturated Fat": 20,  # grams
    }
    
    percent_values = {
        key: (nutrients[key] / daily_values[key]) * 100 for key in nutrients if key in daily_values
    }
    return percent_values

def display_recipe(recipe: Dict):
    st.success(f"📝 Generated Recipe: {recipe['name']}")
    st.write(f"*{recipe['description']}*")
    
    # Recipe details
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Servings", recipe['servings'])
    with col2:
        st.metric("Prep Time", recipe['prep_time'])
    with col3:
        st.metric("Cook Time", recipe['cook_time'])
    
    with st.expander("📋 Ingredients", expanded=True):
        for ingredient in recipe['ingredients']:
            st.write(f"• {ingredient}")
    
    with st.expander("👩‍🍳 Instructions", expanded=True):
        for i, instruction in enumerate(recipe['instructions'], 1):
            st.write(f"{i}. {instruction}")
    
    with st.expander("💡 Cooking Tips"):
        for tip in recipe['tips']:
            st.write(f"• {tip}")
    
    # Display nutrition information
    with st.expander("🥗 Nutrition Information"):
        nutrition = recipe['nutrition']
        st.write(f"**Calories**: {nutrition['calories']} kcal")
        st.write(f"**Protein**: {nutrition['protein']} g")
        st.write(f"**Carbs**: {nutrition['carbs']} g")
        st.write(f"**Fat**: {nutrition['fat']} g")

        # Get detailed nutrition data if available
        if 'detailed' in nutrition:
            nutrients = {
                "Protein": nutrition['detailed']['PROCNT']['quantity'],
                "Carbs": nutrition['detailed']['CHOCDF']['quantity'],
                "Fat": nutrition['detailed']['FAT']['quantity'],
                "Fiber": nutrition['detailed'].get('FIBTG', {}).get('quantity', 0),
                "Sugars": nutrition['detailed'].get('SUGAR', {}).get('quantity', 0),
                "Saturated Fat": nutrition['detailed'].get('FASAT', {}).get('quantity', 0)
            }
            
            # Interactive filter for nutrients
            selected_nutrients = st.multiselect(
                "Select Nutrients to Display",
                list(nutrients.keys()),
                default=list(nutrients.keys())
            )
            
            # Filter the nutrients based on selection
            filtered_nutrients = {k: nutrients[k] for k in selected_nutrients}
            
            # Display Pie Chart
            if filtered_nutrients:
                fig = px.pie(
                    values=filtered_nutrients.values(),
                    names=filtered_nutrients.keys(),
                    title="Selected Nutritional Breakdown",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig)
            
            # Calculate and display % Daily Values
            daily_percent = calculate_daily_values(filtered_nutrients)
            st.write("### % Daily Values")
            for nutrient, value in daily_percent.items():
                st.write(f"{nutrient}: {value:.1f}%")


def main():
    st.set_page_config(
        page_title="AI Chef Assistant",
        page_icon="👩‍🍳",
        layout="wide"
    )
    
    st.title("👩‍🍳 AI Chef Assistant")
    st.caption("Powered by Google Gemini")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Recipe Generator", "Cooking Advice"])
    
    if page == "Recipe Generator":
        st.header("AI Recipe Generator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            ingredients = st.text_area(
                "What ingredients do you have?",
                placeholder="e.g., chicken breast, potatoes, olive oil, garlic",
                help="List your available ingredients"
            )
            
            cuisine_type = st.selectbox(
                "What type of cuisine would you like?",
                ["Italian", "Indian", "Chinese", "Japanese", "Mexican", "Mediterranean", "American", "Thai"]
            )
        
        with col2:
            dietary_restrictions = st.text_area(
                "Any dietary restrictions or preferences?",
                placeholder="e.g., vegetarian, gluten-free, low-carb",
                help="Specify any dietary restrictions or preferences"
            )
        
        if st.button("Generate Recipe", type="primary"):
            if ingredients:
                with st.spinner("👩‍🍳 Chef is thinking..."):
                    recipe = generate_ai_recipe(ingredients, cuisine_type, dietary_restrictions)
                if recipe:
                    display_recipe(recipe)
            else:
                st.warning("Please enter some ingredients!")
    
    else:  # Cooking Advice page
        st.header("AI Cooking Advice")
        
        question = st.text_input(
            "Ask any cooking question",
            placeholder="e.g., How do I perfectly sear a steak?",
            help="Ask about techniques, timing, temperature, or any cooking-related question"
        )
        
        if question:
            with st.spinner("Getting expert advice..."):
                advice = get_ai_cooking_advice(question)
                st.info(advice)
        
        # Common cooking questions
        with st.expander("Common Cooking Questions"):
            if st.button("How to keep herbs fresh?"):
                with st.spinner("Getting advice..."):
                    st.write(get_ai_cooking_advice("How to keep herbs fresh?"))
            
            if st.button("Best way to sharpen knives?"):
                with st.spinner("Getting advice..."):
                    st.write(get_ai_cooking_advice("What's the best way to sharpen kitchen knives?"))

if __name__ == "__main__":
    main()