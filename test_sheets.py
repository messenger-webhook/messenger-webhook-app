import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Autorisations Google
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Ouvre la feuille Google Sheets par son nom
sheet = client.open("abonnements").sheet1

# Récupère toutes les lignes
data = sheet.get_all_values()

# Affiche les données ligne par ligne
for i, row in enumerate(data, start=1):
    print(f"Ligne {i} : {row}")
