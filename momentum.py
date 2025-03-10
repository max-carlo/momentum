import re
from datetime import datetime
import streamlit as st
import yfinance as yf

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")

    # Falls du die Chromium-Binary manuell setzen willst:
    # chrome_options.binary_location = "/usr/bin/chromium"

    # Ab Selenium 4.6:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_earnings_whispers(ticker: str):
    url = f"https://www.earningswhispers.com/epsdetails/{ticker}"
    driver = get_driver()
    driver.get(url)
    wait = WebDriverWait(driver, 15)

    data = {
        "earnings_date": "Nicht gefunden",
        "earnings_growth": "Nicht gefunden",
        "earnings_surprise": "Nicht gefunden",
        "revenue_growth": "Nicht gefunden",
        "revenue_surprise": "Nicht gefunden",
    }
    try:
        # Beispiel: hole via CSS-Selektor #epsdate
        el = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#epsdate")))
        data["earnings_date"] = el.text.strip()
        # etc. ...
    except Exception as e:
        st.error(f"Fehler beim Scrapen: {e}")
    finally:
        driver.quit()

    return data

# ... Restlicher Code analog, YFinance-Aufruf, Formatierung usw. ...

def main():
    st.title("Earnings & Short Ratio via Selenium + webdriver-manager + yfinance")

    ticker = st.text_input("Gib einen Ticker ein (z.B. MARA)")

    if st.button("Ausführen"):
        if not ticker.strip():
            st.warning("Bitte einen Ticker eingeben.")
            return

        # Selenium:
        ew = scrape_earnings_whispers(ticker.strip().upper())
        # yfinance:
        # short_ratio = ...
        # Ausgabe ...

if __name__ == "__main__":
    main()




import streamlit as st
import subprocess

def show_chromium_version():
    try:
        output = subprocess.check_output(["chromium", "--version"])
        st.write("Chromium-Version:", output.decode().strip())
    except Exception as e:
        st.write("Fehler beim Aufruf von chromium --version:", e)

def main():
    st.title("Chromium Version Check")
    if st.button("Check Chromium"):
        show_chromium_version()

if __name__ == "__main__":
    main()




import streamlit as st
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

def show_chromium_version():
    try:
        output = subprocess.check_output(["chromium", "--version"])
        st.write("Chromium-Version:", output.decode().strip())
    except Exception as e:
        st.write("Fehler beim Aufruf von chromium --version:", e)

def get_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # 1) Versuch mit auto-erkennung von Chromium:
    service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())

    # ODER 2) Explizit mit version="120.0.6099.0" probieren, wenn der auto-Mode streikt:
    #
    # service = Service(ChromeDriverManager(
    #       version="120.0.6099.0",
    #       chrome_type=ChromeType.CHROMIUM
    # ).install())

    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver





import streamlit as st
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
# Optional: Weitere Importe, z. B. für yfinance oder BeautifulSoup, falls benötigt
# import yfinance as yf

# Funktion, die den WebDriver konfiguriert und zurückgibt
def get_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")
    # Falls nötig: Passe den Binary-Pfad an, falls dein System-Chromium an einem anderen Ort liegt.
    # chrome_options.binary_location = "/usr/bin/chromium-browser"

    # Der webdriver-manager sorgt nun automatisch für den passenden ChromeDriver
    service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Beispiel-Funktion zum Scrapen von Earnings-Daten (hier mit Platzhalterwerten)
def scrape_earnings_whispers(ticker):
    driver = get_driver()
    # Beispiel-URL – passe diese ggf. an die korrekte URL deiner Zielseite an
    url = f"https://www.earningswhispers.com/stocks/{ticker}"
    driver.get(url)
    # Kurze Wartezeit, damit die Seite vollständig laden kann
    time.sleep(3)
    
    # Hier folgt dein Code zum Extrahieren der gewünschten Daten,
    # z.B. mit driver.find_element(...) oder BeautifulSoup.
    # Im Folgenden verwenden wir Platzhalterwerte:
    data = {
        "earnings_date": "26/02/25",
        "earnings_growth": "6300.0%",
        "revenue_growth": "36.8%",
        "earnings_surprise": "1540.0%",
        "short_ratio": "2.3"
    }
    driver.quit()
    return data

# Hauptfunktion der App
def main():
    st.title("Earnings Scraper Demo")
    ticker = st.text_input("Gib den Ticker ein:")
    
    if st.button("Daten abrufen"):
        if ticker:
            data = scrape_earnings_whispers(ticker.strip().upper())
            # Ausgabe im gewünschten Format (ohne Titeltext, nur EG, RG usw.)
            st.write(f"{data['earnings_date']}")
            st.write(f"EG: {data['earnings_growth']} / RG: {data['revenue_growth']}")
            st.write(f"ES: {data['earnings_surprise']}")
            st.write(f"SR: {data['short_ratio']}")
        else:
            st.write("Bitte einen Ticker eingeben.")

if __name__ == "__main__":
    main()



