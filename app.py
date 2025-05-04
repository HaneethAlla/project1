from flask import Flask, render_template, request, redirect, url_for
import os

# Import your function from llm.py
from llm import process_file
from app import process_file  # Import the function only

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure uploads folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('project.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    # Save file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # 🔁 Call your backend function here
    dummy_response = process_file(filepath)

    # Pass result to summary page
    return redirect(url_for('summary', filename=file.filename, result=dummy_response))

@app.route('/summary')
def summary():
    filename = request.args.get('filename')
    result = request.args.get('result')  # dummy response passed here
    return render_template('summary.html', filename=filename, result=result)

if __name__ == '__main__':
    app.run(debug=True)
