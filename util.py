import os
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader
import docx

load_dotenv(dotenv_path="api.env")
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise Exception("❌ GEMINI_API_KEY not found in environment.")

genai.configure(api_key=api_key)

def extract_text_from_file(file_path):
    """
    Extract text from a PDF, DOCX, or TXT file.
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    try:
        if file_extension == ".pdf":
            return extract_text_from_pdf(file_path)
        elif file_extension == ".docx":
            return extract_text_from_docx(file_path)
        elif file_extension == ".txt":
            return extract_text_from_txt(file_path)
        else:
            raise ValueError("Unsupported file format. Only PDF, DOCX, and TXT are supported.")
    except Exception as e:
        return f"Error extracting text: {e}"

def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file.
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF file: {e}")

def extract_text_from_docx(file_path):
    """
    Extract text from a DOCX file.
    """
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        raise Exception(f"Error reading DOCX file: {e}")

def extract_text_from_txt(file_path):
    """
    Extract text from a TXT file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"Error reading TXT file: {e}")

def send_to_gemini_api(content, model_name="models/gemini-2.0-flash", temperature=0.4):
    """
    Send the content (prompt or file text) to the Gemini API for processing.
    """
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(content)
        return response.text.strip()
    except Exception as e:
        return f"Gemini API error: {e}"