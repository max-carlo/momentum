import streamlit as st
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType  # Angepasst: nutze jetzt webdriver_manager.utils

# Konfiguriere den WebDriver (Chrome/Chromium)
def get_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")
    # Falls nötig, passe hier den Pfad zu deinem Chromium-Binary an:
    # chrome_options.binary_location = "/usr/bin/chromium-browser"
    
    service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Beispiel-Funktion zum Scrapen der Earnings-Daten (Platzhalterwerte!)
def scrape_earnings_whispers(ticker):
    driver = get_driver()
    url = f"https://www.earningswhispers.com/stocks/{ticker}"
    driver.get(url)
    time.sleep(3)  # Warte, bis die Seite vollständig geladen ist
    
    # Hier kommt dein Scraping-Code, der die benötigten Daten extrahiert.
    # Im Folgenden werden Platzhalterwerte zurückgegeben:
    data = {
        "earnings_date": "26/02/25",         # Datum im Format dd/mm/yy
        "earnings_growth": "6300.0%",
        "revenue_growth": "36.8%",
        "earnings_surprise": "1540.0%",
        "short_ratio": "2.3"
    }
    
    driver.quit()
    return data

# Funktion zum Abfragen der Chromium-Version über subprocess
def show_chromium_version():
    try:
        output = subprocess.check_output(["chromium", "--version"])
        st.write("Chromium-Version:", output.decode().strip())
    except Exception as e:
        st.write("Fehler beim Aufruf von 'chromium --version':", e)

# Hauptfunktion der Streamlit-App
def main():
    st.title("Earnings Scraper & Chromium Version Checker")
    
    st.header("Earnings Scraper")
    ticker = st.text_input("Gib den Ticker ein:")
    if st.button("Daten abrufen"):
        if ticker:
            data = scrape_earnings_whispers(ticker.strip().upper())
            # Ausgabe im gewünschten Format (ohne erklärende Titel)
            st.write(f"{data['earnings_date']}")
            st.write(f"EG: {data['earnings_growth']} / RG: {data['revenue_growth']}")
            st.write(f"ES: {data['earnings_surprise']}")
            st.write(f"SR: {data['short_ratio']}")
        else:
            st.write("Bitte einen Ticker eingeben.")
    
    st.header("Chromium Version Check")
    if st.button("Chromium Version prüfen"):
        show_chromium_version()

if __name__ == "__main__":
    main()
