from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import os
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize the Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///voting.db'
app.config['SECRET_KEY'] = os.urandom(24)  # Secret key for session management
db = SQLAlchemy(app)

# Configure Flask-Mail for sending emails
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'evoting.py@gmail.com'
app.config['MAIL_PASSWORD'] = 'cvqw sjsg mfqy cdru'  # Use environment variables for sensitive data
app.config['MAIL_DEFAULT_SENDER'] = 'evoting.py@gmail.com'

# Initialize the Mail object
mail = Mail(app)

# Generate or retrieve a key for encryption and decryption
key = os.getenv('ENCRYPTION_KEY') or Fernet.generate_key()
cipher = Fernet(key)

# Database model for users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    national_id = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

# Store votes and voter keys in memory (for demonstration purposes)
votes = {}
voter_keys = {}
voter_private_keys = {}

# Define a list of candidates
CANDIDATES = [
    "Paul Kagame",
    "Sam Kutesa",
    "Modibo Keita",
    "Sarah Serem",
    "Amina Mohamed",
]

# Hardcoded admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'Hqwe99xc'

def generate_key_pair():
    """Generate a new RSA key pair."""
    key = RSA.generate(2048)
    return key, key.publickey()

def sign_message(private_key, message):
    """Sign a message with the private key."""
    hash_message = SHA256.new(message)
    signature = pkcs1_15.new(private_key).sign(hash_message)
    return signature

def verify_signature(public_key, message, signature):
    """Verify a signature with the public key."""
    hash_message = SHA256.new(message)
    try:
        pkcs1_15.new(public_key).verify(hash_message, signature)
        return True
    except (ValueError, TypeError):
        return False

@app.route('/')
def index():
    return render_template('index.html', candidates=CANDIDATES)


@app.route('/vote', methods=['POST'])
def vote():
    data = request.form
    app.logger.info(f"Received data: {data}")

    # Check for required fields: national_id and candidate
    if not all(k in data for k in ('national_id', 'candidate', 'email')):
        app.logger.error("Invalid request: Missing fields")
        return jsonify({"error": "Invalid request"}), 400

    national_id = data['national_id']  # Get the national ID from the form
    candidate = data['candidate'].encode()  # Get the candidate from the form
    email = data['email']  # Get the email from the form

    # Check if the voter has already cast a vote
    if national_id in votes:
        return jsonify({"error": "Voter has already cast a vote."}), 400

    # Sign the vote
    signature = sign_message(voter_private_keys[national_id], candidate)
    store_vote(national_id, candidate.decode(), signature)  # Store the vote using national_id
    send_confirmation_email(email, candidate.decode())  # Send confirmation email to the provided email

    return render_template('confirmation.html', candidate=candidate.decode())

def store_vote(national_id, candidate, signature):
    votes[national_id] = {
        'candidate': candidate,
        'signature': signature
    }

def send_confirmation_email(email, candidate):
    msg = Message("Vote Confirmation", recipients=[email], sender='evoting.py@gmail.com')
    msg.body = f"Thank you for voting! You have voted for {candidate}."
    
    try:
        mail.send(msg)
        app.logger.info(f"Confirmation email sent to {email}.")
    except Exception as e:
        app.logger.error(f"Failed to send email: {e}")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('voting_list'))
        else:
            flash("Invalid credentials", "danger")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/voting_list', methods=['GET'])
def voting_list():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    votes_data = {voter_id: {'candidate': vote_info['candidate'], 'signature': vote_info['signature']} for voter_id, vote_info in votes.items()}
    return render_template('voting_list.html', votes=votes_data)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=8080)