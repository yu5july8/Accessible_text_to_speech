from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
import uuid
import docx
from PyPDF2 import PdfReader
from fpdf import FPDF
from pdf2image import convert_from_path
import openai
import stripe
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with your actual secret key
db = SQLAlchemy(app)

# Ensure the uploads and processed directories exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
if not os.path.exists(app.config['PROCESSED_FOLDER']):
    os.makedirs(app.config['PROCESSED_FOLDER'])

# OpenAI API key (replace 'your_openai_api_key' with your actual key)
openai.api_key = 'your_openai_api_key'

# Stripe API keys
stripe.api_key = 'your_stripe_secret_key'  # Replace with your actual Stripe secret key
stripe_public_key = 'your_stripe_public_key'  # Replace with your actual Stripe public key

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_subscribed = db.Column(db.Boolean, default=False)
    page_count = db.Column(db.Integer, default=0)
    stripe_customer_id = db.Column(db.String(150), nullable=True)
    stripe_subscription_id = db.Column(db.String(150), nullable=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        new_user = User(first_name=data['first_name'], last_name=data['last_name'], email=data['email'], password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        return redirect(url_for('home'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(email=data['email']).first()
        if user and user.password == data['password']:
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            return jsonify({'message': 'Log-in failed'}), 400
    return render_template('login.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/subscription')
def subscription():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('subscription.html', stripe_public_key=stripe_public_key)

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 403

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        # Create Stripe customer if not exists
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(email=user.email)
            user.stripe_customer_id = customer.id
            db.session.commit()

        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer=user.stripe_customer_id,
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'DocTune Monthly Subscription',
                        },
                        'unit_amount': 20,
                        'recurring': {
                            'interval': 'month',
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=url_for('subscription_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('subscription_cancel', _external=True),
        )
        return jsonify({'sessionId': checkout_session['id']})
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/subscription-success')
def subscription_success():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    session_id = request.args.get('session_id')
    checkout_session = stripe.checkout.Session.retrieve(session_id)

    user = User.query.get(session['user_id'])
    user.is_subscribed = True
    user.stripe_subscription_id = checkout_session['subscription']
    db.session.commit()

    return render_template('subscription_success.html')

@app.route('/subscription-cancel')
def subscription_cancel():
    return render_template('subscription_cancel.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user.is_subscribed and user.page_count >= 20:
        return jsonify({'error': 'Page limit exceeded. Please subscribe for unlimited access.'}), 403
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file:
            filename = uuid.uuid4().hex + os.path.splitext(file.filename)[1]
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            # Process the uploaded document
            processed_content = process_document(file_path)
            tagged_content = auto_tag_content(processed_content)
            processed_filename = save_processed_document(tagged_content)
            session['processed_file'] = processed_filename
            # Update user's page count
            page_count = len(processed_content['text'])
            user.page_count += page_count
            db.session.commit()
            return redirect(url_for('processing'))
    return render_template('upload.html')

@app.route('/processing')
def processing():
    # Simulate processing for demonstration purposes
    import time
    time.sleep(5)
    return redirect(url_for('download'))

@app.route('/download')
def download():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('download.html')

@app.route('/download_processed_document')
def download_processed_document():
    if 'user_id' not in session or 'processed_file' not in session:
        return redirect(url_for('login'))
    return send_from_directory(app.config['PROCESSED_FOLDER'], session['processed_file'], as_attachment=True)

def process_document(file_path):
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
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            img = rel.target_part.blob
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], uuid.uuid4().hex + '.png')
            with open(img_path, 'wb') as img_file:
                img_file.write(img)
            images.append(img_path)
    return {'text': content, 'images': images}

def parse_pdf(file_path):
    content = []
    images = []
    reader = PdfReader(file_path)
    for page in reader.pages:
        content.append(page.extract_text())
    pages = convert_from_path(file_path)
    for page_number, page_data in enumerate(pages):
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], f"page_{page_number + 1}.png")
        page_data.save(img_path, 'PNG')
        images.append(img_path)
    return {'text': content, 'images': images}

def parse_text(file_path):
    with open(file_path, 'r') as file:
        content = file.readlines()
    return {'text': content, 'images': []}

def generate_alt_text(image_paths):
    alt_texts = []
    for image_path in image_paths:
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
            response = openai.Image.create(image=img_data)
            alt_text = response['data']['alt_text']
            alt_texts.append(alt_text)
    return alt_texts

def auto_tag_content(content):
    tagged_content = []
    for text in content['text']:
        tagged_content.append(f"<p>{text}</p>")
    alt_texts = generate_alt_text(content['images'])
    for img_path, alt_text in zip(content['images'], alt_texts):
        tagged_content.append(f'<img src="{img_path}" alt="{alt_text}"/>')
    return tagged_content

def save_processed_document(tagged_content):
    processed_filename = uuid.uuid4().hex + '.html'
    processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
    with open(processed_path, 'w') as file:
        file.write('\n'.join(tagged_content))
    return processed_filename

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)