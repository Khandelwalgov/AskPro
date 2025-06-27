# parser_utils.py
import fitz  # PyMuPDF
import docx
import os

def extract_text_from_pdf(path):
    try:
        doc = fitz.open(path)
        text = ""
        for page in doc:
            text += page.get_text()
        print(text)
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {e}"

def extract_text_from_docx(path):
    try:
        doc = docx.Document(path)
        text = "\n".join([para.text for para in doc.paragraphs])
        print(text)
        return text.strip()
    except Exception as e:
        return f"Error reading DOCX: {e}"

def extract_text_from_txt(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        return f"Error reading TXT: {e}"

def extract_text(path, mimetype):
    if mimetype == "application/pdf":
        return extract_text_from_pdf(path)
    elif mimetype == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(path)
    elif mimetype == "text/plain":
        return extract_text_from_txt(path)
    else:
        return f"Unsupported MIME type: {mimetype}"
