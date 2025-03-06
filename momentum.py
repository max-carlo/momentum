import re
from datetime import datetime

import yfinance as yf
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def remove_label_phrases(text):
    """
    Entfernt "Earnings Growth", "Revenue Growth", "Earnings Surprise"
    aus dem übergebenen Text - z. B. mit RegEx.
    """
    if text == "Nicht gefunden":
        return text

    # Groß-/Kleinschreibung ignorieren, Leerzeichen dahinter optional
    # \s* => beliebige Leerzeichen
    # Dann z.B. "Earnings Growth" => weg
    # "Earnings Surprise" => weg
    # "Revenue Growth" => weg

    # Du kannst sie nacheinander entfernen:
    text = re.sub(r"(?i)earnings growth\s*", "", text)   # "(?i)" -> case-insensitive
    text = re.sub(r"(?i)revenue growth\s*", "", text)
    text = re.sub(r"(?i)earnings surprise\s*", "", text)

    return text.strip()

def remove_commas(value):
    """
    Entfernt Kommas, z.B. "6,300.0%" -> "6300.0%".
    Falls "Nicht gefunden", bleibt es wie es ist.
    """
    if value == "Nicht gefunden":
        return value
    return value.replace(",", "")

def parse_date_to_ddmmyy(date_str):
    """
    Beispiel-Eingabe: "Wednesday, February 26, 2025 at 4:05 PM ET"
    Ausgabestring: "26/02/25"  (dd/mm/yy)
    """
    if date_str == "Nicht gefunden":
        return date_str

    # "Wednesday, February 26, 2025 at 4:05 PM ET"
    # => "Wednesday, February 26, 2025 4:05 PM"
    cleaned = date_str.replace(" at ", " ").replace(" ET", "")

    # "Wednesday, " entfernen
    if ", " in cleaned:
        parts = cleaned.split(", ", maxsplit=1)
        if len(parts) == 2:
            cleaned = parts[1]  # "February 26, 2025 4:05 PM"

    # parse
    try:
        dt = datetime.strptime(cleaned, "%B %d, %Y %I:%M %p")
        return dt.strftime("%d/%m/%y")  # "26/02/25"
    except:
        return date_str

def scrape_earnings_data_ew(ticker):
    """
    Ruft von https://www.earningswhispers.com/epsdetails/<ticker> folgende Felder ab:
      - #epsdate (z.B. "Wednesday, February 26, 2025 at 4:05 PM ET")
      - #earnings .surprise
      - #earnings .growth
      - #revenue .surprise
      - #revenue .growth

    Gibt Dictionary:
      {
        "earnings_date":  ...,
        "earnings_surprise":  ...,
        "earnings_growth":    ...,
        "revenue_surprise":   ...,
        "revenue_growth":     ...
      }
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    url = f"https://www.earningswhispers.com/epsdetails/{ticker}"
    driver.get(url)
    wait = WebDriverWait(driver, 15)

    data = {
        "earnings_date":      "Nicht gefunden",
        "earnings_surprise":  "Nicht gefunden",
        "earnings_growth":    "Nicht gefunden",
        "revenue_surprise":   "Nicht gefunden",
        "revenue_growth":     "Nicht gefunden",
    }

    try:
        # earnings_date
        try:
            el = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "#epsdate"))
            )
            data["earnings_date"] = el.text.strip()
        except:
            pass

        # earnings_surprise
        try:
            el = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "#earnings .surprise"))
            )
            data["earnings_surprise"] = el.text.strip()
        except:
            pass

        # earnings_growth
        try:
            el = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "#earnings .growth"))
            )
            data["earnings_growth"] = el.text.strip()
        except:
            pass

        # revenue_surprise
        try:
            el = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "#revenue .surprise"))
            )
            data["revenue_surprise"] = el.text.strip()
        except:
            pass

        # revenue_growth
        try:
            el = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "#revenue .growth"))
            )
            data["revenue_growth"] = el.text.strip()
        except:
            pass

    finally:
        driver.quit()

    return data

def get_short_ratio_yfinance(ticker):
    """
    Mit yfinance das shortRatio holen.
    Falls nicht vorhanden => "Nicht gefunden".
    """
    t = yf.Ticker(ticker)
    info = t.info
    sr = info.get("shortRatio", None)
    if sr is None:
        return "Nicht gefunden"
    return str(sr)

if __name__ == "__main__":
    # 1) Ticker eingeben
    user_ticker = input("Gib einen Ticker ein (z.B. MARA): ").strip().upper()

    # 2) Selenium -> Earnings Whispers
    ew_data = scrape_earnings_data_ew(user_ticker)

    # 3) Datum => dd/mm/yy
    date_ddmmyy = parse_date_to_ddmmyy(ew_data["earnings_date"])

    # 4) remove labels und Kommas
    #    => EG: "6300.0%", etc.
    eg_clean = remove_label_phrases( remove_commas(ew_data["earnings_growth"]) )
    rg_clean = remove_label_phrases( remove_commas(ew_data["revenue_growth"]) )
    es_clean = remove_label_phrases( remove_commas(ew_data["earnings_surprise"]) )

    # 5) short ratio
    sr_val = get_short_ratio_yfinance(user_ticker)

    # 6) Endformat:
    # <dd/mm/yy>
    # EG: 6300.0% / RG: 36.8%
    # ES: 1540.0%
    # SR: 2.3
    print(f"{date_ddmmyy}")
    print(f"EG: {eg_clean} / RG: {rg_clean}")
    print(f"ES: {es_clean}")
    print(f"SR: {sr_val}")
