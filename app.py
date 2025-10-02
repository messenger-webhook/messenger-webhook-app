from flask import Flask, request

app = Flask(__name__)

# ⚡️ Remplace ce token par le token que tu as défini dans Facebook
VERIFY_TOKEN = "b370b63a6cafa7a144131c8c079aca96"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Vérification du token pour Facebook
        token_sent = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token_sent == VERIFY_TOKEN:
            return challenge  # Renvoie le challenge en texte brut
        return "Token invalide", 403

    elif request.method == "POST":
        # Quand Facebook envoie un message ou événement
        data = request.get_json()
        print("Nouvel événement Messenger reçu :", data)
        # Ici tu peux traiter les messages ou les statuts
        return "OK", 200

if __name__ == "__main__":
    # Render utilisera son propre port, on met host 0.0.0.0 pour rendre accessible
    app.run(host="0.0.0.0", port=10000)
