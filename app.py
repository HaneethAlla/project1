from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_session import Session
from werkzeug.utils import secure_filename
import os
from llm import process_file
from util import extract_text_from_file, send_to_gemini_api
from markdown import markdown

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('project.html')

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

        extracted_text = extract_text_from_file(file_path)
        if extracted_text.startswith("Error"):
            return jsonify({"error": extracted_text}), 500

        extracted_text_file = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}_extracted.txt")
        with open(extracted_text_file, 'w', encoding='utf-8') as f:
            f.write(extracted_text)

        prompt = request.form.get("prompt", "You are an AI assistant. Summarize the following document in a clear, concise, and structured format.")

        formatted_prompt = send_to_gemini_api(prompt, temperature=0.4)

        gemini_response = send_to_gemini_api(f"{formatted_prompt}\n\n{extracted_text}")

        formatted_response = markdown(gemini_response)

        return render_template('summary.html', filename=filename, result=formatted_response)

    return jsonify({"error": "Unsupported file type"}), 400

@app.route('/summary')
def summary():
    filename = request.args.get('filename')
    result = request.args.get('result')  
    return render_template('summary.html', filename=filename, result=result)

@app.route('/process_prompt', methods=['POST'])
def process_prompt():
    data = request.get_json()
    prompt = data.get('prompt')
    model = data.get('model', 'gemini-2.0-flash') 
    temperature = data.get('temperature', 0.4) 

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        response = process_file(prompt, is_file=False, temperature=temperature, model_name=model)
    except Exception as e:
        return jsonify({"error": f"Error processing prompt: {e}"}), 500

    return jsonify({"result": response})

if __name__ == '__main__':
    app.run(debug=True)
