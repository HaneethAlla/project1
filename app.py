from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_session import Session
from werkzeug.utils import secure_filename
import os
from llm import process_file
from util import extract_text_from_file, send_to_gemini_api
from markdown import markdown

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensure uploads folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('project.html')

@app.route('/set_api_key', methods=['POST'])
def set_api_key():
    data = request.get_json()
    api_key = data.get('api_key')

    if not api_key:
        return jsonify({"error": "No API key provided"}), 400

    # Store the API key in the session
    session['api_key'] = api_key
    return jsonify({"message": "API key saved successfully!"})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Extract text from the uploaded file
        extracted_text = extract_text_from_file(file_path)
        if extracted_text.startswith("Error"):
            return jsonify({"error": extracted_text}), 500

        # Get the temperature value from the form
        temperature = float(request.form.get("temperature", 0.4))  # Default to 0.4 if not provided

        # Send extracted text to Gemini API
        gemini_response = send_to_gemini_api(extracted_text, temperature=temperature)

        # Convert response to HTML using markdown
        formatted_response = markdown(gemini_response)

        # Render the summary page with the response
        return render_template('summary.html', filename=filename, result=formatted_response)

    return jsonify({"error": "Unsupported file type"}), 400

@app.route('/summary')
def summary():
    filename = request.args.get('filename')
    result = request.args.get('result')  # Summary passed here
    return render_template('summary.html', filename=filename, result=result)

@app.route('/process_prompt', methods=['POST'])
def process_prompt():
    data = request.get_json()
    prompt = data.get('prompt')
    model = data.get('model', 'gemini-2.0-flash')  # Default to Gemini 2.0 Flash
    temperature = data.get('temperature', 0.4)  # Default to 0.4

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # Call the AI model to process the prompt
    try:
        response = process_file(prompt, is_file=False, temperature=temperature, model_name=model)
    except Exception as e:
        return jsonify({"error": f"Error processing prompt: {e}"}), 500

    # Return the response as JSON
    return jsonify({"result": response})

if __name__ == '__main__':
    app.run(debug=True)
