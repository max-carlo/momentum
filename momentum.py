import re
from datetime import datetime

import streamlit as st
import yfinance as yf

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_driver():
    """
    Erzeugt einen Headless-Chrome-WebDriver mit Pfaden,
    wie sie auf (z.B.) Streamlit Cloud via packages.txt üblich sind.
    Passen Sie Pfade ggf. an Ihren Server an.
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")
    chrome_options.binary_location = "/usr/bin/chromium-browser"
    driver = webdriver.Chrome("/usr/bin/chromedriver", options=chrome_options)
    return driver

def scrape_earnings_whispers(ticker: str):
    """
    Ruft von https://www.earningswhispers.com/epsdetails/<ticker> die Earnings-Daten ab:
       - Earnings-Datum (#epsdate)
       - Earnings Growth (#earnings .growth)
       - Earnings Surprise (#earnings .surprise)
       - Revenue Growth (#revenue .growth)
       - Revenue Surprise (#revenue .surprise)
    Gibt ein dict zurück, oder "Nicht gefunden" falls nicht identifizierbar
    """
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
        # 1) Earnings Date
        try:
            el = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#epsdate")))
            data["earnings_date"] = el.text.strip()
        except:
            pass

        # 2) Earnings Growth
        try:
            el = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#earnings .growth")))
            data["earnings_growth"] = el.text.strip()
        except:
            pass

        # 3) Earnings Surprise
        try:
            el = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#earnings .surprise")))
            data["earnings_surprise"] = el.text.strip()
        except:
            pass

        # 4) Revenue Growth
        try:
            el = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#revenue .growth")))
            data["revenue_growth"] = el.text.strip()
        except:
            pass

        # 5) Revenue Surprise
        try:
            el = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#revenue .surprise")))
            data["revenue_surprise"] = el.text.strip()
        except:
            pass

    finally:
        driver.quit()

    return data

def parse_earnings_date_to_ddmmyy(date_str: str) -> str:
    """
    Bsp: "Wednesday, February 26, 2025 at 4:05 PM ET" => "26/02/25"
    """
    if "Nicht gefunden" in date_str:
        return date_str

    # " at " und " ET" entfernen
    tmp = date_str.replace(" at ", " ").replace(" ET", "")
    # Wochentag+Komma raus:
    # z.B. "Wednesday, February 26, 2025 4:05 PM" => "February 26, 2025 4:05 PM"
    if ", " in tmp:
        parts = tmp.split(", ", maxsplit=1)
        if len(parts) == 2:
            tmp = parts[1]

    # z.B. "February 26, 2025 4:05 PM"
    # => datetime
    fmts = ["%B %d, %Y %I:%M %p", "%B %d, %Y"]  # evtl. fallback
    for f in fmts:
        try:
            dt = datetime.strptime(tmp, f)
            return dt.strftime("%d/%m/%y")
        except:
            pass

    return date_str  # Fallback

def remove_label_phrases(text: str) -> str:
    """
    Entfernt "Earnings Growth", "Revenue Growth", "Earnings Surprise" etc. (case-insensitive)
    """
    if "Nicht gefunden" in text:
        return text
    text = re.sub(r"(?i)earnings growth", "", text)
    text = re.sub(r"(?i)revenue growth", "", text)
    text = re.sub(r"(?i)earnings surprise", "", text)
    return text.strip()

def remove_commas(text: str) -> str:
    """
    "6,300.0%" => "6300.0%"
    """
    if "Nicht gefunden" in text:
        return text
    return text.replace(",", "")

def get_short_ratio_via_yfinance(ticker: str) -> str:
    """
    Ruft per yfinance das Feld shortRatio ab (float).
    """
    t = yf.Ticker(ticker)
    info = t.info
    sr = info.get("shortRatio", None)
    if sr is None:
        return "Nicht gefunden"
    return str(sr)

def main():
    st.title("Earnings & Short Ratio via Selenium + yfinance")

    ticker = st.text_input("Gib einen Ticker ein (z.B. MARA)")

    if st.button("Los!"):
        if not ticker.strip():
            st.warning("Bitte einen Ticker eingeben.")
            return

        # 1) Earnings data scrapen
        st.write("**Scraping** Earnings Whispers ... bitte warten.")
        ew = scrape_earnings_whispers(ticker.strip().upper())

        # 2) Fields bearbeiten
        date_ddmmyy = parse_earnings_date_to_ddmmyy(ew["earnings_date"])

        eg = remove_label_phrases(remove_commas(ew["earnings_growth"]))
        rg = remove_label_phrases(remove_commas(ew["revenue_growth"]))
        es = remove_label_phrases(remove_commas(ew["earnings_surprise"]))
        # Falls du revenue surprise benötigst: remove_label_phrases(remove_commas(ew["revenue_surprise"]))

        # 3) Short Ratio
        st.write("Hole Short Ratio von yfinance ...")
        sr = get_short_ratio_via_yfinance(ticker.strip().upper())

        # 4) Format
        # 26/02/25
        # EG: 6300.0% / RG: 36.8%
        # ES: 1540.0%
        # SR: 2.3
        # => ohne "Earnings Growth" etc., nur EG, RG, ES, SR

        result = f"""
{date_ddmmyy}
EG: {eg} / RG: {rg}
ES: {es}
SR: {sr}
""".strip()

        st.subheader("Ergebnis")
        st.code(result, language="text")


if __name__ == "__main__":
    main()
