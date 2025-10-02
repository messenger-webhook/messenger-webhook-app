from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "b370b63a6cafa7a144131c8c079aca96"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        token_sent = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token_sent == VERIFY_TOKEN:
            return challenge
        return "Invalid verification token"
    elif request.method == "POST":
        data = request.get_json()
        print(data)  # Pour tester les messages reçus
        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
