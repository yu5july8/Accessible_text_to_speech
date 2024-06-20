import docx
from PyPDF2 import PdfReader
from fpdf import FPDF
import openai
import io
import os
import uuid
from pdf2image import convert_from_path

# Function to handle document upload and parsing
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
    content = []
    images = []
    for para in doc.paragraphs:
        content.append(para.text)
    # Extract images if any (requires additional code)
    return content, images

def parse_pdf(file_path):
    # Extract text from PDF
    content = []
    reader = PdfReader(file_path)
    for page in reader.pages:
        content.append(page.extract_text())
    
    # Extract images from PDF
    images = []
    pages = convert_from_path(file_path)
    for page_number, page_data in enumerate(pages):
        image_path = f"page_{page_number + 1}.png"
        page_data.save(image_path, 'PNG')
        images.append(image_path)
    
    return content, images

def parse_text(file_path):
    with open(file_path, 'r') as file:
        content = file.readlines()
    return content, []

# Function to generate alt text using OpenAI
def generate_alt_text(images):
    alt_texts = []
    for image in images:
        # Convert image to text description
        alt_text = openai.Image.create(image=image)
        alt_texts.append(alt_text['data']['alt_text'])
    return alt_texts

# Function to tag and generate accessible PDF
def generate_accessible_pdf(content, images, alt_texts, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)  # Set the font before adding text
    # Add content and images with alt text
    for line in content:
        pdf.multi_cell(0, 10, line)
    # Additional tagging for accessibility
    pdf.output(output_path)

# Example usage
file_path = "/Users/yugoiwamoto/Desktop/project_x/example.pdf"
random_file_name = f"accessible_output_{uuid.uuid4()}.pdf"
output_path = random_file_name
try:
    content, images = parse_document(file_path)
    alt_texts = generate_alt_text(images)
    generate_accessible_pdf(content, images, alt_texts, output_path)
    print(f"Accessible PDF generated at {output_path}")
except Exception as e:
    print(f"Error: {e}")
