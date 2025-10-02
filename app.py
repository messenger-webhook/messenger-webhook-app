from flask import Flask, request

app = Flask(__name__)
VERIFY_TOKEN = "b370b63a6cafa7a144131c8c079aca96"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token_sent == VERIFY_TOKEN:
            return challenge, 200
        return "Invalid verification token", 403
    else:
        # Ici tu peux gérer les messages POST de Messenger
        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    # Render utilise le port fourni dans l'environnement
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
