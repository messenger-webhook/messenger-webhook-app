import os
import imaplib
import email
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import time

# --- Charger variables d'environnement ---
load_dotenv()

IMAP_HOST = os.getenv("IMAP_HOST")
IMAP_PORT = int(os.getenv("IMAP_PORT"))
IMAP_USER = os.getenv("IMAP_USER")
IMAP_PASS = os.getenv("IMAP_PASS")
SHEET_NAME = os.getenv("SHEET_NAME")

# --- Connexion Google Sheet ---
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# --- Connexion Kuku (IMAP) ---
def get_latest_reset_link(mail_user, mail_pass):
    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    mail.login(mail_user, mail_pass)
    mail.select("INBOX")
    
    typ, data = mail.search(None, 'FROM', '"Netflix"')
    mail_ids = data[0].split()
    if not mail_ids:
        return None

    latest_email_id = mail_ids[-1]
    typ, data = mail.fetch(latest_email_id, '(RFC822)')
    raw_email = data[0][1]
    msg = email.message_from_bytes(raw_email)

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
    else:
        body = msg.get_payload(decode=True).decode()

    # Extraire le lien de reset
    match = re.search(r'https://www\.netflix\.com/.*?reset-password.*', body)
    return match.group(0) if match else None

# --- Générer nouveau mot de passe ---
def generate_new_password():
    import random, string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

# --- Modifier mot de passe via Selenium ---
def change_netflix_password(reset_link, new_password):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(reset_link)
    time.sleep(3)
    
    try:
        pw_field = driver.find_element(By.NAME, "newPassword")
        pw_field.send_keys(new_password)
        submit = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit.click()
        time.sleep(3)
        driver.quit()
        return True
    except Exception as e:
        driver.quit()
        return False

# --- Parcourir Sheet ---
today = datetime.today().strftime("%d/%m/%Y")

for i, row in enumerate(sheet.get_all_values()[1:], start=2):  # ignorer header
    fin_inscription = row[8].strip()
    email_compte = row[2].strip()
    
    if fin_inscription and fin_inscription <= today:
        print(f"Traitement du compte {email_compte}...")
        new_pass = generate_new_password()
        reset_link = get_latest_reset_link(IMAP_USER, IMAP_PASS)
        
        if reset_link:
            success = change_netflix_password(reset_link, new_pass)
            if success:
                sheet.update_cell(i, 4, new_pass)  # colonne 'texte' pour mdp
                sheet.update_cell(i, 9, today)  # mettre à jour date si besoin
                print(f"Mot de passe changé pour {email_compte}")
            else:
                sheet.update_cell(i, 9, "failed")
                print(f"Échec pour {email_compte}")
        else:
            sheet.update_cell(i, 9, "need_verification")
            print(f"Vérification nécessaire pour {email_compte}")
