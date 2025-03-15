from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from nacl.signing import SigningKey, VerifyKey
import os
import base64
import pandas as pd
import csv
from collections import Counter

# Load voter data from CSV
CSV_FILE = 'voters_list_updated.csv'
voter_data = pd.read_csv(CSV_FILE)

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

# Store votes in memory (for demonstration purposes)
votes = {}

# Database model for users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.String(10), unique=True, nullable=False)
    voter_card_number = db.Column(db.String(10), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

# Function to load candidates from CSV
def load_candidates():
    candidates = []
    csv_file = "candidates.csv"  # Make sure this file is in the same directory as evoting2.py
    try:
        with open(csv_file, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                candidates.append(row["Full Name"])  # Only store candidate names
    except Exception as e:
        print(f"Error loading candidates: {e}")
    return candidates

# Load candidates dynamically
CANDIDATES = load_candidates()

@app.route('/')
def index():
    return render_template('index.html', candidates=CANDIDATES)

@app.route('/vote', methods=['POST'])
def vote():

    # Get the JSON data from the request
    data = request.json

    # Check for required fields: national_id, candidate, email, public_key, and signature
    if not all(k in data for k in ('full_name', 'voter_id', 'voter_card_number', 'email', 'candidate', 'public_key', 'signature')):
        flash("Invalid request, missing fields.", "danger")
        return jsonify({"error": "Invalid request"}), 400

    full_name = data['full_name']
    voter_id = data['voter_id']
    voter_card_number = data['voter_card_number']
    email = data['email']
    candidate = data['candidate']

    # Validate voter against the CSV file
    voter = voter_data[(voter_data['Full Name'] == full_name) &
                       (voter_data['Voter ID'] == voter_id) &
                       (voter_data['Voter Card Number'] == voter_card_number) &
                       (voter_data['Email'] == email)]

    # Convert public_key and signature from string to bytes
    public_key = bytes(base64.b64decode(data['public_key']))
    signature = bytes(base64.b64decode(data['signature']))

    if voter.empty:
        flash("Voter details do not match our records.", "danger")
        return jsonify({"error": "Voter validation failed"}), 403
    
    # Check if the voter has already cast a vote
    if voter_id in votes:
        flash("You have already cast your vote. You cannot vote again.", "danger")
        return redirect(url_for('index'))

    # Store the vote
    votes[voter_id] = {
        'full_name': full_name,
        'voter_card_number': voter_card_number,
        'email': email,
        'candidate': candidate,
        'signature': data['signature'],
        'public_key': data['public_key']
    }
    
    # Send confirmation email
    send_confirmation_email(email, candidate)

    flash(f"Your vote for {candidate} has been recorded!", "success")
    # Redirect to the confirmation page with the candidate name
    return redirect(url_for('confirmation', candidate=candidate))

@app.route('/confirmation')
def confirmation():
    candidate = request.args.get('candidate', 'Unknown Candidate')
    return render_template('confirmation.html', candidate=candidate)


def send_confirmation_email(email, candidate):
    msg = Message("Vote Confirmation", recipients=[email])
    msg.body = f"Thank you for voting! You have voted for {candidate}."
    mail.send(msg)


@app.route('/voting_list', methods=['GET'])
def voting_list():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Verify votes before displaying them
    verified_votes = []
    for voter_id, vote_data in votes.items():
        full_name = vote_data.get('full_name', 'Unknown')
        voter_card_number = vote_data.get('voter_card_number', 'Unknown')
        email = vote_data.get('email', 'Unknown')
        candidate = vote_data.get('candidate', 'Unknown')
        
        message = f"{full_name}:{voter_id}:{voter_card_number}:{email}:{candidate}"

        # Properly decode Base64-encoded public key and signature
        public_key_bytes = base64.b64decode(vote_data['public_key'].encode())
        signature_bytes = base64.b64decode(vote_data['signature'].encode())

        try:
            verify_key = VerifyKey(public_key_bytes)
            verify_key.verify(message.encode(), signature_bytes)
            verified_votes.append(vote_data)
        except Exception as e:
            print(f"Verification failed for {voter_id}: {e}")
            continue

    # Count votes per candidate
    candidate_counts = Counter(vote["candidate"] for vote in verified_votes)

    # Convert verified votes list into a dictionary to match template expectations
    verified_votes_dict = {f"vote{i}": vote for i, vote in enumerate(verified_votes)}

    return render_template('voting_list.html', candidate_counts=candidate_counts,  votes=verified_votes_dict)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'admin':  # Replace with actual admin credentials
            session['logged_in'] = True
            return redirect(url_for('voting_list'))
        else:
            flash("Invalid credentials", "danger")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='10.17.4.21', port=6555)  # Allow access from any IP address