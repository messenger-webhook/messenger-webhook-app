import gspread
from google.oauth2.service_account import Credentials

# Nom du fichier Google Sheet et de la feuille
SPREADSHEET_NAME = "abonnements"
SHEET_NAME = "abonnements"

# Charger les credentials
creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)

client = gspread.authorize(creds)

try:
    # Ouvrir le fichier et la feuille
    sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)
    print("[SUCCESS] Connexion au fichier Google Sheets réussie ✅")

    # Lire les 2 premières lignes pour test
    rows = sheet.get_all_values()
    print("Premières lignes :")
    for row in rows[:2]:
        print(row)

except Exception as e:
    print("[ERROR]", e)
