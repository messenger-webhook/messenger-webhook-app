from selenium import webdriver
from selenium.webdriver.chrome.service import Service

service = Service("C:/Users/LENOVO/Desktop/bot netflix/chromedriver.exe")
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://www.google.com")
print("✅ Chrome lancé avec succès")
driver.quit()
