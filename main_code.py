import docx
import PyPDF2
from fpdf import FPDF
import openai
import io

# Function to handle document upload and parsing
def parse_document(file_path):
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
    # Use PyPDF2 or pdfplumber to extract text and images
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
    # Add content and images with alt text
    for line in content:
        pdf.multi_cell(0, 10, line)
    # Additional tagging for accessibility
    pdf.output(output_path)

# Example usage
file_path = "example.docx"
output_path = "accessible_output.pdf"
content, images = parse_document(file_path)
alt_texts = generate_alt_text(images)
generate_accessible_pdf(content, images, alt_texts, output_path)
