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
