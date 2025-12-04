from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from resend import Resend

app = Flask(__name__)

# Allow your frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://my-port-folio-three-psi.vercel.app"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Load Resend API key
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
resend = Resend(api_key=RESEND_API_KEY)

@app.route("/api/contact-resend", methods=["POST", "OPTIONS"])
def contact_resend():
    if request.method == "OPTIONS":
        return jsonify({"message": "preflight ok"}), 200

    data = request.json
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    try:
        # Send with Resend
        resend.emails.send(
            from_="Portfolio Contact <onboarding@resend.dev>",
            to=["mohammedhassan0041@gmail.com"],  # your inbox
            subject=f"New Contact Message from {name}",
            html=f"""
                <h2>New Contact Form Submission</h2>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Message:</strong><br>{message}</p>
            """
        )

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("Resend Error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
