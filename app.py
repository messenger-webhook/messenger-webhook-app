from flask import Flask, request
import os

app = Flask(__name__)

# Ton token exact défini dans Messenger
VERIFY_TOKEN = "b370b63a6cafa7a144131c8c079aca96"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Vérification du token
        token_sent = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token_sent == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Token invalide", 403
    elif request.method == "POST":
        # Ici tu recevras les messages
        data = request.get_json()
        print("Message reçu:", data)
        return "OK", 200

if __name__ == "__main__":
    # Render fournit le PORT via une variable d'environnement
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
