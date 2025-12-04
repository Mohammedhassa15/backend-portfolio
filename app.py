from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)

CORS(app, resources={
    r"/api/*": {
        "origins": ["https://my-port-folio-three-psi.vercel.app"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = "onboarding@resend.dev"   # change to your verified domain email
TO_EMAIL = "mohammedhassan0041@gmail.com"

@app.route("/api/contact", methods=["POST", "OPTIONS"])
def contact():
    if request.method == "OPTIONS":
        return jsonify({"message": "preflight ok"}), 200

    data = request.json
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    payload = {
        "from": f"Portfolio Contact <{FROM_EMAIL}>",
        "to": [TO_EMAIL],
        "subject": f"New Message From {name}",
        "text": f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
    }

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            json=payload,
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            }
        )

        if response.status_code == 200 or response.status_code == 202:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({
                "status": "error",
                "message": response.text
            }), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
