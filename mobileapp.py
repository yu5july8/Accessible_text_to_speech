from flask import Flask, render_template, request, redirect, url_for
import os
import docx
from PyPDF2 import PdfReader
from fpdf import FPDF
import openai
import io
import uuid
from pdf2image import convert_from_path

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'docx', 'pdf', 'txt'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def parse_document(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    
    if file_path.endswith('.docx'):
        return parse_docx(file_path)
    elif file_path.endswith('.pdf'):
        return parse_pdf(file_path)
    elif file_path.endswith('.txt'):
        return parse_text(file_path)
    else:
        raise ValueError("Unsupported file type")

def parse_docx(file_path):
    doc = docx.Document(file_path)
    content = [para.text for para in doc.paragraphs]
    images = []  # Add code to extract images if needed
    return content, images

def parse_pdf(file_path):
    content = []
    reader = PdfReader(file_path)
    for page in reader.pages:
        content.append(page.extract_text())
    
    images = []
    pages = convert_from_path(file_path)
    for page_number, page_data in enumerate(pages):
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"page_{page_number + 1}.png")
        page_data.save(image_path, 'PNG')
        images.append(image_path)
    
    return content, images

def parse_text(file_path):
    with open(file_path, 'r') as file:
        content = file.readlines()
    return content, []

def generate_alt_text(images):
    alt_texts = []
    for image in images:
        alt_text = openai.Image.create(image=image)
        alt_texts.append(alt_text['data']['alt_text'])
    return alt_texts

def generate_accessible_pdf(content, images, alt_texts, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in content:
        pdf.cell(200, 10, txt=line, ln=True)
    for image, alt_text in zip(images, alt_texts):
        pdf.image(image, x=10, y=None, w=100)
        pdf.cell(200, 10, txt=alt_text, ln=True)
    pdf.output(output_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Process signup data here
        return redirect(url_for('home'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Process login data here
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = uuid.uuid4().hex + os.path.splitext(file.filename)[1]
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            content, images = parse_document(file_path)
            alt_texts = generate_alt_text(images)
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}.pdf")
            generate_accessible_pdf(content, images, alt_texts, output_path)
            return redirect(url_for('home'))
    return render_template('upload.html')

if __name__ == "__main__":
    app.run(debug=True)