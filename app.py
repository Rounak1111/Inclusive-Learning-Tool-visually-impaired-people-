import os
import pdfplumber
from flask import Flask, render_template, request
import pyttsx3
import textwrap

app = Flask(__name__)

# Paths for output files
UPLOAD_FOLDER = "static/uploads"
OUTPUT_DIR = "static"
AUDIO_FILE_PATH = os.path.join(OUTPUT_DIR, "output_audio.mp3")
BRAILLE_FILE_PATH = os.path.join(OUTPUT_DIR, "output_braille.txt")

# Braille Mapping
braille_mapping = {
    "a": "⠁", "b": "⠃", "c": "⠉", "d": "⠙", "e": "⠑",
    "f": "⠋", "g": "⠛", "h": "⠓", "i": "⠊", "j": "⠚",
    "k": "⠅", "l": "⠇", "m": "⠍", "n": "⠝", "o": "⠕",
    "p": "⠏", "q": "⠟", "r": "⠗", "s": "⠎", "t": "⠞",
    "u": "⠥", "v": "⠧", "w": "⠺", "x": "⠭", "y": "⠽",
    "z": "⠵", " ": " ", ".": "⠲", ",": "⠂", "!": "⠖",
    "?": "⠦", "-": "⠤", "'": "⠄", "\"": "⠶", ":": "⠒",
}

# Ensure required folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_text_from_file(file):
    """Extracts text from a TXT or PDF file."""
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    
    if file.filename.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    
    elif file.filename.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    
    return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/convert_to_audio", methods=["POST"])
def convert_to_audio():
    text = request.form.get("text")
    file = request.files.get("file")

    if file and file.filename.endswith((".txt", ".pdf")):
        text = extract_text_from_file(file)

    if text and text.strip():
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 150)
            engine.save_to_file(text, AUDIO_FILE_PATH)
            engine.runAndWait()
            return f"Audio file saved! <a href='{AUDIO_FILE_PATH}' download>Download Audio</a>"
        except Exception as e:
            return f"Error in Text-to-Speech: {e}"
    
    return "No valid text provided."

@app.route("/convert_to_braille", methods=["POST"])
def convert_to_braille():
    text = request.form.get("text")
    file = request.files.get("file")

    if file and file.filename.endswith((".txt", ".pdf")):
        text = extract_text_from_file(file)

    if text and text.strip():
        try:
            braille_text = "".join(braille_mapping.get(char, "⠿") for char in text.lower())
            with open(BRAILLE_FILE_PATH, "w", encoding="utf-8") as file:
                file.write(textwrap.fill(braille_text, width=50))
            return f"Braille file saved! <a href='{BRAILLE_FILE_PATH}' download>Download Braille</a>"
        except Exception as e:
            return f"Error in Braille Conversion: {e}"
    
    return "No valid text provided."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

