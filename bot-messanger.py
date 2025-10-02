from flask import Flask, request

app = Flask(__name__)

# ⚠️ DOIT être identique à celui mis dans Meta Developers
VERIFY_TOKEN = "bigoubigoubigou121212"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Facebook envoie hub.challenge et hub.verify_token
        token_sent = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if token_sent == VERIFY_TOKEN:
            return challenge, 200
        return "Token invalide", 403

    elif request.method == "POST":
        data = request.get_json()
        print("📩 Message reçu :", data)
        return "Message reçu", 200

if __name__ == "__main__":
    print("🚀 Bot Messenger en cours d'exécution...")
    app.run(host="0.0.0.0", port=5000)
