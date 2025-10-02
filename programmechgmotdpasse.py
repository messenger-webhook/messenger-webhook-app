import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import string
from datetime import datetime
import imaplib
import email
import os
from dotenv import load_dotenv

# === CONFIG ===
load_dotenv()
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
CLIENT = gspread.authorize(CREDS)

SPREADSHEET = CLIENT.open("bot netflix")   # Nom du fichier
SHEET = SPREADSHEET.sheet1                 # Première feuille

IMAP_HOST = os.getenv("IMAP_HOST")
IMAP_PORT = int(os.getenv("IMAP_PORT", 993))

# === UTILS ===
def generer_mdp(longueur=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(longueur))

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("detach", True)
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def lire_mail_reset(user, password):
    """Cherche le lien reset Netflix dans la boîte IMAP"""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(user, password)
        mail.select("inbox")
        typ, data = mail.search(None, '(FROM "info@account.netflix.com")')
        if data[0]:
            latest = data[0].split()[-1]
            typ, msg_data = mail.fetch(latest, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        body = part.get_payload(decode=True).decode()
                        # recherche du lien reset
                        for line in body.split():
                            if "netflix.com/password" in line:
                                return line
            else:
                body = msg.get_payload(decode=True).decode()
                for line in body.split():
                    if "netflix.com/password" in line:
                        return line
        return None
    except Exception as e:
        print(f"[FAIL] IMAP login {user}: {e}")
        return None

# === TRAITEMENT ===
rows = SHEET.get_all_values()

for i, row in enumerate(rows[1:], start=2):  # saute l’entête
    nom = row[0]
    email_netflix = row[2]    # colonne C
    fin = row[8]              # colonne I
    inbox_user = row[14]      # colonne O (inbox)
    new_password = generer_mdp()
    today = datetime.now().strftime("%d/%m/%Y")

    print(f"[PROCESS] {nom} — fin {fin}")

    try:
        # === 1. lancer reset sur Netflix
        driver = setup_driver()
        driver.get("https://www.netflix.com/dz-en/passwordreset")
        time.sleep(2)

        champ_email = driver.find_element(By.NAME, "email")
        champ_email.send_keys(email_netflix)

        bouton = driver.find_element(By.CSS_SELECTOR, "button[type=submit]")
        bouton.click()
        print(f"[INFO] Reset demandé pour {email_netflix}")

        time.sleep(10)  # attendre réception mail

        # === 2. lire le mail inbox
        inbox_pass = os.getenv("IMAP_PASS")  # mot de passe dans .env
        reset_link = lire_mail_reset(inbox_user, inbox_pass)

        if reset_link:
            print(f"[INFO] Lien reset trouvé: {reset_link}")
            driver.get(reset_link)
            time.sleep(3)

            champ1 = driver.find_element(By.NAME, "password")
            champ2 = driver.find_element(By.NAME, "passwordConfirm")

            champ1.send_keys(new_password)
            champ2.send_keys(new_password)

            driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
            time.sleep(5)

            # === mise à jour Google Sheet
            SHEET.update_cell(i, 11, new_password)  # col K
            SHEET.update_cell(i, 12, today)         # col L
            SHEET.update_cell(i, 13, "OK")          # col M
            print(f"[SUCCESS] Mot de passe changé pour {email_netflix}")
        else:
            SHEET.update_cell(i, 13, "MAIL NOT FOUND")
            print(f"[FAIL] Aucun mail de reset pour {email_netflix}")

        driver.quit()

    except Exception as e:
        SHEET.update_cell(i, 13, f"ERROR: {str(e)[:50]}")
        print(f"[FAIL] Erreur {email_netflix}: {e}")
        try:
            driver.quit()
        except:
            pass
