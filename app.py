from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import sys

app = Flask(__name__)

# Full CORS rules — includes OPTIONS preflight, GET (for health), POST
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://my-port-folio-three-psi.vercel.app"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
TO_EMAIL = os.getenv("TO_EMAIL", "mohammedhassan0041@gmail.com")


@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok", "message": "Backend running"}), 200


# Health endpoint for uptime monitor (Render Free Tier fix)
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "alive"}), 200


@app.route("/api/contact", methods=["POST", "OPTIONS"])
def contact():
    # Crucial for CORS preflight on Render
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json(silent=True) or {}
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    if not name or not email or not message:
        return jsonify({"status": "error", "message": "name, email and message are required"}), 400

    if not RESEND_API_KEY:
        msg = "RESEND_API_KEY not set in environment"
        print(msg, file=sys.stderr)
        return jsonify({"status": "error", "message": msg}), 500

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
            },
            timeout=10
        )

        print(f"resend status={response.status_code} body={response.text}", file=sys.stderr)

        if response.ok:
            return jsonify({"status": "success"}), 200

        return jsonify({
            "status": "error",
            "message": response.text
        }), max(response.status_code, 500)

    except Exception as e:
        print(f"exception sending email: {e}", file=sys.stderr)
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
