import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Charger les identifiants depuis le fichier .env
load_dotenv()
KUKU_USER = os.getenv("KUKU_USER")
KUKU_PASS = os.getenv("KUKU_PASS")

# URLs Kuku (connexion + boîte de réception FR)
LOGIN_URL = "https://m.kuku.lu/fr.php"
INBOX_URL = "https://m.kuku.lu/recv.php"

# Créer une session persistante
session = requests.Session()

def login_kuku():
    print(f"🔐 Tentative de connexion avec {KUKU_USER} ...")
    payload = {
        "si": KUKU_USER,   # champ pseudo (si = screen id)
        "pw": KUKU_PASS,   # mot de passe
        "submit": "Login"
    }

    res = session.post(LOGIN_URL, data=payload)
    print(f"📡 Code HTTP: {res.status_code}")

    if "Boîte de réception" in res.text or "recv.php" in res.url:
        print("✅ Connexion réussie !")
        return True
    else:
        print("❌ Connexion échouée, identifiants probablement incorrects")
        return False

def fetch_inbox():
    print("📥 Récupération des mails ...")
    res = session.get(INBOX_URL)
    print(f"📡 Inbox status: {res.status_code}")

    # Sauvegarder HTML complet pour analyse
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(res.text)
    print("✅ inbox.html sauvegardé (ouvre-le dans ton navigateur)")

    # Petit aperçu console
    soup = BeautifulSoup(res.text, "html.parser")
    mails = soup.find_all("div")
    print(f"📩 Nombre d’éléments <div> trouvés : {len(mails)}")
    print("--- Aperçu brut du texte ---")
    print(soup.get_text()[:500])  # seulement les 500 premiers caractères

if __name__ == "__main__":
    if login_kuku():
        fetch_inbox()
