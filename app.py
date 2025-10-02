from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Ton token de vérification que tu as mis sur Messenger
VERIFY_TOKEN = "b370b63a6cafa7a144131c8c079aca96"

# Route pour la validation du webhook
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    # Récupère les paramètres envoyés par Messenger
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    mode = request.args.get("hub.mode")

    if mode == "subscribe" and token_sent == VERIFY_TOKEN:
        return challenge, 200  # Renvoie le challenge si le token est correct
    return "Invalid verification token", 403

# Route pour recevoir les messages
@app.route('/webhook', methods=['POST'])
def receive_message():
    data = request.get_json()
    print("Message reçu:", data)  # Affiche dans les logs Render
    return jsonify(status="ok"), 200

if __name__ == "__main__":
    # Render définit automatiquement le port via la variable d'environnement PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
