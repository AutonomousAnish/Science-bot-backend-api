import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

# --- Configuration ---
# NOTE: Replace 'YOUR_ACTUAL_GEMINI_API_KEY_GOES_HERE' with your actual Gemini API Key
# IMPORTANT: You MUST set your key here!
API_KEY = "AIzaSyBXcai50ARh2vO-wQvZm2rXahBnPkjmNAo" 

# Define the unique placeholder used in the code
INITIAL_PLACEHOLDER = "YOUR_ACTUAL_GEMINI_API_KEY_GOES_HERE" 
FALLBACK_PLACEHOLDER = "FALLBACK_PLACEHOLDER"

# Ensure API Key is available
if not API_KEY or API_KEY == INITIAL_PLACEHOLDER:
    # This warning will now fire if the user misses the step above
    print("WARNING: GEMINI_API_KEY is missing or set to the default placeholder. The backend will fail.")
    # Attempt to use environment variable as a fallback
    API_KEY = os.environ.get("GEMINI_API_KEY", FALLBACK_PLACEHOLDER)

app = Flask(__name__)
# Enable CORS for all domains, allowing the frontend to connect
CORS(app)

# Initialize the Gemini Client
client = None
if API_KEY and API_KEY != INITIAL_PLACEHOLDER and API_KEY != FALLBACK_PLACEHOLDER:
    try:
        # The key is valid, proceed with initialization
        client = genai.Client(api_key=API_KEY)
        print("Gemini Client initialized successfully.")
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
else:
    print("FATAL: Gemini Client NOT initialized. Please ensure your API_KEY is correctly set in the code or environment.")

# System instruction for the model's persona
SYSTEM_INSTRUCTION_DEFAULT = (
    "You are an expert at teaching science to kids. Engage in conversations, explain concepts using analogies and examples, "
    "use humor, and suggest real-world experiments. Keep answers engaging and appropriate for a school-age audience."
)

@app.route('/generate', methods=['POST'])
def generate_content():
    if client is None:
        return jsonify({"error": "Gemini client failed to initialize due to missing API Key."}), 500

    try:
        # 1. Get the JSON data from the React frontend
        data = request.get_json()
        
        # 2. Extract the 'history' array. This array contains all messages.
        chat_history = data.get('history')

        if not chat_history:
            return jsonify({"error": "No chat history ('history' key) found in the request body."}), 400

        # 3. Configure and Call the Gemini API
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION_DEFAULT
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=chat_history, # Pass the entire history as contents
            config=config,
        )

        # 4. Return the model's response text to the frontend
        model_response = response.text

        # The frontend is expecting a key named 'response'
        return jsonify({"response": model_response})

    except Exception as e:
        print(f"An error occurred during content generation: {e}")
        # Return a 500 error if any other exception occurs
        return jsonify({"error": f"An internal server error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # Running on 127.0.0.1:5000 is required by the React frontend fetch call
    app.run(host='127.0.0.1', port=5000, debug=True)
