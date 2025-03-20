
import os
import base64
import hashlib
import csv
import pandas as pd
import json
import sys
from flask import Flask, request, render_template,jsonify, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from collections import Counter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///voting.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)

# Store votes in memory (for demonstration purposes)
votes = []  # ✅ Store votes in a list
used_voter_hashes = set()  # ✅ Keep track of used voter hashes


# Get the directory where the EXE or script is running
if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller EXE
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Define the path to the CSV file
CSV_FILE = os.path.join(base_dir, "voters_list_updated.csv")

# Check if the file exists
if not os.path.exists(CSV_FILE):
    raise FileNotFoundError(f"CSV file not found: {CSV_FILE}")

# Load voter data
voter_data = pd.read_csv(CSV_FILE)

print("CSV loaded successfully!")

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

# Serve the CSV file properly
@app.route('/voters_list_updated.csv')
def get_csv():
    return send_from_directory(base_dir, 'voters_list_updated.csv')  # Serve from base_dir

def base64_decode_safe(data):
    """Decodes base64 with padding correction."""
    data += "=" * ((4 - len(data) % 4) % 4)  # Fix padding issues
    return base64.b64decode(data)


@app.route('/vote', methods=['POST'])
def vote():
    #votes.clear()  # ✅ This will allow voting multiple times (FOR TESTING ONLY)

    try:
        data = request.json

        voter_id_hashed = data.get("voter_id_hashed")
        public_key = data.get("public_key")
        signature = data.get("signature")
        candidate = data.get("candidate")

        if not public_key or not signature or not candidate:
            return jsonify({"error": "Missing required vote fields."}), 400
        
        decoded_public_key = base64.b64decode(public_key)
        decoded_signature = base64.b64decode(signature)

        # Recalculate voter hash
        voter_hash = hashlib.sha256(decoded_public_key).hexdigest()  # ✅ Ensure raw bytes are hashed
        vote_data = json.dumps({"voter_hash": voter_hash, "candidate": candidate}, separators=(',', ':'))

        # ✅ Check if voter already voted
        if voter_id_hashed in used_voter_hashes:
            return jsonify({"message": "You have already voted!", "redirect": "/"}), 403

        used_voter_hashes.add(voter_id_hashed)  # ✅ Add to set to prevent multiple votes
        
        # Verify signature
        try:
            verify_key = VerifyKey(decoded_public_key)
            verify_key.verify(vote_data.encode(), decoded_signature)
            print("🔹 Signature Verified Successfully!")
        except BadSignatureError:
            print("❌ Signature verification failed!")
            return jsonify({"error": "Invalid signature. Vote rejected."}), 400

        # Store vote as a list entry instead of overwriting
        votes.append({"voter_hash": voter_hash, "candidate": candidate, "public_key": public_key, "signature": signature}) 

        return jsonify({"message": "Your vote has been recorded!", "redirect": f"/confirmation?candidate={candidate}"}), 200

    except Exception as e:
        print(f"❌ Internal Server Error: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/confirmation')
def confirmation():
    candidate = request.args.get('candidate', 'Unknown Candidate')
    return render_template('confirmation.html', candidate=candidate)

@app.route('/voting_list', methods=['GET'])
def voting_list():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    candidate_counts = Counter(vote["candidate"] for vote in votes)
    return render_template('voting_list.html', candidate_counts=candidate_counts, votes=votes)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.form.get('username') == 'admin' and request.form.get('password') == 'admin':
        session['logged_in'] = True
        return redirect(url_for('voting_list'))
    flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    host = input("Enter the IP address of the server: ")
    port = input("Enter the port number: ")
    app.run(host=host, port=port, ssl_context=('cert.pem', 'key.pem'))
