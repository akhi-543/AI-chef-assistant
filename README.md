# AI Chef Assistant

## Overview
AI Chef Assistant is an AI-powered recipe generator and cooking assistant that helps users create personalized recipes based on available ingredients, cuisine preferences, and dietary restrictions. It integrates Google Gemini AI for recipe generation and the Edamam API for detailed nutritional analysis.

## Features
- **AI-Powered Recipe Generation**: Uses Google Gemini AI to create unique recipes.
- **Ingredient-Based Search**: Enter available ingredients, and get recipes instantly.
- **Dietary Restriction Support**: Customizes recipes based on dietary needs (vegetarian, gluten-free, keto, etc.).
- **Nutritional Analysis**: Fetches detailed macronutrient and calorie data using the Edamam API.
- **Interactive UI**: Built with Streamlit for a seamless user experience.
- **Data Visualization**: Uses Plotly to display nutritional breakdowns.

## Tech Stack
- **Frontend**: Streamlit (Python)
- **Backend**: Google Gemini AI
- **APIs**: Edamam Nutrition API
- **Libraries Used**:
  - `streamlit` (UI Framework)
  - `google.generativeai` (AI Model Integration)
  - `requests` (API Calls)
  - `json` (Data Handling)
  - `plotly.express` (Data Visualization)

## How It Works
1. **Enter Ingredients & Preferences**: Users input available ingredients and any dietary restrictions.
2. **AI Generates Recipe**: The system creates a detailed recipe with steps and tips.
3. **Nutritional Analysis**: The app fetches and displays nutrition details.
4. **Visualization**: Pie charts show nutrient distribution.

## Architechture
![Image](https://github.com/user-attachments/assets/82a4cf00-246d-481a-9d6e-5be98c955594)

## Future Enhancements
- **Voice Command Support** for hands-free interaction.
- **Grocery API Integration** to suggest missing ingredients.
- **Meal Planning Features** to generate multiple meals at once.
- **User Authentication** to save favorite recipes.

## Installation & Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/akhi-543/ai-chef-assistant.git
   cd ai-chef-assistant
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up API keys in Streamlit secrets:
   ```plaintext
   [secrets]
   GOOGLE_API_KEY = "your_google_api_key"
   EDAMAM_APP_ID = "your_edamam_app_id"
   EDAMAM_API_KEY = "your_edamam_api_key"
   ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Contributing
Feel free to fork this repository and create pull requests for improvements or bug fixes!

## License
This project is licensed under the MIT License.

## Acknowledgments
- **Google Gemini AI** for recipe generation.
- **Edamam API** for nutritional data.
- **Streamlit & Plotly** for the UI and data visualization.

---

⭐ **If you like this project, give it a star on GitHub!** ⭐

