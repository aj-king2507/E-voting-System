# **E-Voting System 🗳️**

## **📌 Project Overview**
The **E-Voting System** is a secure and transparent online voting platform built with **Python, Flask, and SQLAlchemy**. It ensures **anonymity, verification, and integrity** in digital elections by utilizing cryptographic techniques. The system supports **voter authentication, encrypted voting, digital signatures, and real-time vote tallying** while ensuring a secure and seamless voting experience.

---

## **🚀 Features**
### **🔐 Security Measures**
- **Public Key Cryptography (NaCl/TweetNaCl)** for vote security.
- **Voter Anonymity**: Each vote is hashed and cannot be linked to an individual voter.
- **Digital Signature Verification**: Votes are signed using the voter's public key and verified before counting.
- **Admin Authentication**: Only authorized admins can access voting results.
- **Session-Based Authentication**: Secure login/logout functionality.
- **Email Confirmation**: Voters receive an email confirmation after voting.
- **Immutable Vote Records**: Votes are stored securely in an in-memory structure to prevent tampering.

### **🎯 Functional Features**
- **User Registration & Authentication** via a login system.
- **Candidate Selection Interface** dynamically generated from `candidates.csv`.
- **Vote Encryption & Verification** using cryptographic keys.
- **Secure Vote Storage** to prevent unauthorized modifications.
- **Admin Panel for Viewing Vote Counts** securely.
- **Error Handling & Flash Messages** for user-friendly notifications.

---

## **📦 Dependencies**
The following libraries are required for the project:
```sh
Flask
Flask-SQLAlchemy
pandas
pynacl
base64
hashlib
json
csv
os
sys
emailjs
```
To install all dependencies, run the following command:
```sh
pip install Flask Flask-SQLAlchemy pandas pynacl emailjs
```
The following libraries are required for the project:
```sh
Flask
Flask-SQLAlchemy
pandas
nacl
base64
hashlib
json
csv
os
sys
EmailJS
```

## **🛠️ Installation & Setup**

### **1️⃣ Running the Executable (Recommended)**
⚠️ Note: The directory containing evoting.exe must also include cert.pem, key.pem, and the CSV files (candidates.csv and voters_list_updated.csv) for the application to run properly.
If you are using Windows, you can run the application directly using the provided executable file:
```sh
evoting.exe
```
You will be prompted to enter the **IP address** and **port number** where the server should run.

### **2️⃣ Clone the Repository (For Development)**
```sh
git clone https://github.com/aj-king2507/E-voting-System.git
cd E-voting-System
```

### **3️⃣ Install Dependencies**
Ensure you have **Python 3** installed, then install the required packages:
```sh
pip install -r requirements.txt
```

### **4️⃣ Required Files**
Ensure the following files are present in the working directory:
- `evoting.exe` (for Windows users)
- `evoting.py` (for Python execution)
- `candidates.csv` (Candidate list)
- `voters_list_updated.csv` (Voter list)
- `cert.pem` & `key.pem` (SSL certificates for secure connections)
- `EmailJS.txt` (Email configuration)

### **5️⃣ Set Up the Database**
The system uses **SQLite** as the database. To initialize it, run:
```sh
python -c "from evoting import db; db.create_all()"
```

### **6️⃣ Start the Server Locally (For Python Users)**
Run the Flask application:
```sh
python evoting.py
```
You will be prompted to enter the **IP address** and **port number** before the server starts.

Then, open **https://<entered-ip>:<entered-port>/** in your browser to access the voting system.

---

## **🌐 Running the Server on a Remote IP**
If you want to deploy the server on a remote machine and access it from other devices, run Flask with:
```sh
python evoting.py
```
When prompted, enter `0.0.0.0` as the IP address and any port of your choice.

This makes the server accessible over the network using your machine’s IP address.

### **⚠️ Note on Crypto.subtle & HTTP Restrictions**
The `crypto.subtle` API **only works over HTTPS or localhost**, meaning:
- It will **not** work if accessed using `http://your-remote-ip:6555/`.
- It **requires a secure HTTPS connection** to function remotely.

### **How to Fix This?**
1. **Use a Reverse Proxy with HTTPS (Recommended)**
   - Set up **Nginx** as a reverse proxy to serve your Flask app over HTTPS.
   - Obtain a free SSL certificate using **Let's Encrypt**.
   
2. **Use a Secure Tunnel (Alternative for Testing)**
   - Services like [ngrok](https://ngrok.com/) allow you to create an HTTPS tunnel:
     ```sh
     ngrok http 6555
     ```
   - This will provide an HTTPS URL that works with `crypto.subtle`.

---

## **🖥️ Usage Guide**
1. **User Login:** Voters log in via the `/` route.
2. **Vote Submission:** Voters select a candidate and submit their vote.
3. **Vote Encryption:** Each vote is cryptographically signed and verified.
4. **Admin Login:** Admin logs in via `/login` to view vote results.
5. **Voting List:** Admin can access `/voting_list` to see vote counts and verified votes.
6. **Confirmation Email:** Voters receive an email after submitting their vote.

---

## **🛠️ Troubleshooting & FAQs**
### **1️⃣ Error: `sqlite3.OperationalError: unable to open database file`**
- Make sure the database file exists in the correct location.
- Run `python -c "from evoting import db; db.create_all()"`.

### **2️⃣ Admin Can't Access Voting List?**
- Ensure you log in via `/login` with the correct admin credentials (`admin/admin`).
- Check if `session['logged_in']` is set correctly.

### **3️⃣ Email Confirmation Not Sending?**
- Verify your **EmailJS** configuration in `index.html`.
- Make sure the API key in `emailjs.init("KETXkj4v7fICTN4e_")` is correct.

### **4️⃣ `crypto.subtle` Not Working on Remote IP?**
- **Solution**: Use HTTPS via **Nginx + Let's Encrypt** or **ngrok**.
- `crypto.subtle` requires a **secure HTTPS connection** to work properly.

---

## **🤝 Contribution Guidelines**
1. **Fork the repository**.
2. **Create a feature branch**: `git checkout -b feature-name`.
3. **Make changes and commit**: `git commit -m "Added new feature"`.
4. **Push to GitHub**: `git push origin feature-name`.
5. **Submit a Pull Request** for review.

---

## **📜 License**
This project is licensed under the **MIT License** – feel free to modify and share!

---

## **📧 Contact & Support**
For questions or issues, contact [aj-king2507](https://github.com/aj-king2507) or open an issue on GitHub.

**🚀 Happy Voting! 🗳️**

