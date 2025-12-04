from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import sys

app = Flask(__name__)

# Allow the frontend origin(s) you expect. Add localhost for testing if needed.
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://my-port-folio-three-psi.vercel.app"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

RESEND_API_KEY = os.getenv("RESEND_API_KEY").strip()
FROM_EMAIL = os.getenv("FROM_EMAIL", "onboarding@resend.dev")   # change to your verified domain email
TO_EMAIL = os.getenv("TO_EMAIL", "mohammedhassan0041@gmail.com")


@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok", "message": "Backend running"}), 200


@app.route("/api/contact", methods=["POST", "OPTIONS"])
def contact():
    if request.method == "OPTIONS":
        return jsonify({"message": "preflight ok"}), 200

    data = request.get_json(silent=True) or {}
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    # Basic validation
    if not name or not email or not message:
        return jsonify({"status": "error", "message": "name, email and message are required"}), 400

    if not RESEND_API_KEY:
        # Clear diagnostic for logs so you don't have to read a stacktrace later
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

        # Log for debugging on Render
        print(f"resend status={response.status_code} body={response.text}", file=sys.stderr)

        if 200 <= response.status_code < 300:
            return jsonify({"status": "success"}), 200
        else:
            # Forward the upstream error message and status code
            return jsonify({
                "status": "error",
                "message": response.text
            }), max(response.status_code, 500)

    except Exception as e:
        print(f"exception sending email: {e}", file=sys.stderr)
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    # Bind to the port provided by Render (or default 5000 locally)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
