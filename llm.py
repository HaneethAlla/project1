import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="api.env")
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise Exception("❌ GEMINI_API_KEY not found in environment.")

genai.configure(api_key=api_key)

available_models = genai.list_models()
print("Available models:")
for model in available_models:
    print(f"- {model.name} (supported methods: {model.supported_generation_methods})")

model_name = "models/gemini-2.0-flash"  
model = genai.GenerativeModel(model_name)

def process_file(input_data, is_file=True, model_name="gemini-2.0-flash"):
    try:
        if is_file:
            with open(input_data, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = input_data 
    except Exception as e:
        return f"Error reading input: {e}"

    prompt = f"Summarize the following content:\n\n{content}"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini API error: {e}"
