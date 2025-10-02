import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# === CONFIG GOOGLE SHEETS ===
SHEET_ID = "1d0ZgkEtohd-ZnrPtLmd2y-wtJc6zCF7PzDEe9qriMYM"
SHEET_NAME = "base1"
JSON_KEYFILE = "service.json"  # ton fichier de clé service account

# Connexion Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEYFILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# Charger les données
data = sheet.get_all_records()
df = pd.DataFrame(data)

# ✅ Corriger cellules fusionnées (remplissage vers le bas)
df = df.ffill()

# === SELENIUM : Fonction changement mot de passe Netflix ===
def change_netflix_password(driver, email, old_password, new_password):
    try:
        driver.get("https://www.netflix.com/login")

        # Email
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "userLoginId"))
        ).send_keys(email)

        # Ancien mot de passe
        driver.find_element(By.NAME, "password").send_keys(old_password)

        # Bouton Se connecter
        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        login_btn.click()

        # Attente profil
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.profile-icon"))
        )

        # Aller dans paramètres du compte
        driver.get("https://www.netflix.com/YourAccount")

        # Cliquer changer mot de passe
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Changer de mot de passe"))
        ).click()

        # Champs
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "currentPassword"))
        ).send_keys(old_password)

        driver.find_element(By.NAME, "newPassword").send_keys(new_password)
        driver.find_element(By.NAME, "confirmNewPassword").send_keys(new_password)

        # Valider
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)

        return True, f"Mot de passe changé pour {email}"

    except Exception as e:
        return False, f"Erreur avec {email}: {e}"

# === MAIN ===
if __name__ == "__main__":
    driver = webdriver.Chrome()

    for index, row in df.iterrows():
        email = row["email"]  # Col A
        old_password = row["mot de passe"]  # Col B
        new_password = old_password[:3] + "123"  # exemple : modif du mot de passe

        success, message = change_netflix_password(driver, email, old_password, new_password)
        print(message)

    driver.quit()
