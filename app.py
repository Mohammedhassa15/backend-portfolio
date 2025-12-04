from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from flask_cors import CORS

app = Flask(__name__)

CORS(app,  origins=["https://my-port-folio-three-psi.vercel.app/"])
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS", "mohammedhassan0041@gmail.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "zxxs prsc ubvk ffhv")

# Replace with your Gmail credentials
EMAIL_ADDRESS = "mohammedhassan0041@gmail.com"
EMAIL_PASSWORD = "zxxs prsc ubvk ffhv"

@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    try:
        # Prepare email
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Subject"] = f"New Contact Message from {name}"

        body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        msg.attach(MIMEText(body, "plain"))

        # Send email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
