import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime

# === CONFIG GOOGLE SHEET ===
SPREADSHEET_ID = "1AagJA8u_ycvbZtqtV4qUf9My96ZtnEt8WTxOXGoD-j0"
WORKSHEET_NAME = "abonnements"

# Connexion Google Sheets
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(WORKSHEET_NAME)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("detach", True)
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def change_password(email, new_password):
    """Essaie de se connecter à Netflix avec email + mot de passe"""
    driver = setup_driver()
    try:
        driver.get("https://www.netflix.com/dz-fr/login")
        time.sleep(2)

        champ_email = driver.find_element(By.NAME, "userLoginId")
        champ_pass = driver.find_element(By.NAME, "password")

        champ_email.send_keys(email)
        champ_pass.send_keys(new_password)

        driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
        time.sleep(5)

        # Vérifier si connexion réussie (URL redirigée vers browse/profiles)
        if "browse" in driver.current_url or "profiles" in driver.current_url:
            driver.quit()
            return True
        else:
            driver.quit()
            return False
    except Exception as e:
        print(f"[ERROR] {email} -> {e}")
        try:
            driver.quit()
        except:
            pass
        return False

def main():
    # Lecture uniquement ligne 2 (après l’entête)
    row = sheet.row_values(2)

    email = row[2].strip() if len(row) > 2 else ""
    new_password = row[3].strip() if len(row) > 3 else ""
    today = datetime.now().strftime("%d/%m/%Y")

    if not email:
        sheet.update_cell(2, 13, "NO EMAIL")
        return
    if not new_password:
        sheet.update_cell(2, 13, "NO PASSWORD")
        return

    print(f"[PROCESS] Tentative login pour {email}")

    ok = change_password(email, new_password)

    if ok:
        sheet.update_cell(2, 12, today)     # col L = last_changed
        sheet.update_cell(2, 13, "OK")      # col M = status
        print(f"[SUCCESS] Connexion réussie avec {email}")
    else:
        sheet.update_cell(2, 13, "FAILED")
        print(f"[FAIL] Connexion échouée pour {email}")

if __name__ == "__main__":
    main()
