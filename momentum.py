import streamlit as st
import yfinance as yf
from datetime import datetime
from playwright.sync_api import sync_playwright
import re

@st.cache_resource
def install_playwright():
    import subprocess
    subprocess.run(["playwright", "install", "chromium"], check=True)

install_playwright()

@st.cache_data
def get_earnings_data(ticker):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page_url = f"https://www.earningswhispers.com/epsdetails/{ticker}"
        page = browser.new_page()
        page.goto(page_url)

        def safe_extract(selector):
            try:
                return page.locator(selector).inner_text().strip()
            except:
                return "Nicht gefunden"

        data = {
            "earnings_date": safe_extract("#epsdetails"),
            "earnings_surprise": safe_extract("#earnings .surprise"),
            "earnings_growth": safe_extract("#earnings .growth"),
            "revenue_surprise": safe_extract("#revenue .surprise"),
            "revenue_growth": safe_extract("#revenue .growth"),
        }
        browser.close()
        return data

def parse_date(date_str):
    if date_str == "Nicht gefunden":
        return date_str
    cleaned = re.sub(r'^\w+, ', '', date_str).replace(" at ", " ").replace(" ET", "")
    dt = datetime.strptime(cleaned, "%B %d, %Y %I:%M %p")
    return dt.strftime("%d/%m/%y")

def clean_text(text):
    phrases = ["Earnings Growth", "Revenue Growth", "Earnings Surprise"]
    for phrase in phrases:
        text = re.sub(fr"{phrase}", "", text, flags=re.I)
    return text.replace(",", "").strip()

@st.cache_data
def get_short_ratio(ticker):
    t = yf.Ticker(ticker)
    return str(t.info.get("shortRatio", "Nicht gefunden"))

# Streamlit App UI
st.title("📈 Earnings Whisper Momentum")

ticker = st.text_input("Gib das Tickersymbol ein (z.B. AAPL):")

if ticker:
    earnings_data = get_earnings_data(ticker)

    earnings_date = parse_date(earnings_data["earnings_date"])
    earnings_surprise = clean_text(earnings_data["earnings_surprise"])
    earnings_growth = clean_text(earnings_data["earnings_growth"])
    revenue_surprise = clean_text(earnings_data["revenue_surprise"])
    revenue_growth = clean_text(earnings_data["earnings_growth"])
    short_ratio = get_short_ratio(ticker)

    st.markdown(f"""
    **Ergebnisse für {ticker.upper()}**  
    📅 **Earnings-Datum:** {earnings_data["earnings_date"]}  
    📊 **Earnings Surprise:** {earnings_data["earnings_surprise"]}  
    📊 **Earnings Growth:** {earnings_data["earnings_growth"]}  
    💰 **Revenue Surprise:** {earnings_data["revenue_surprise"]}  
    🚀 **Revenue Growth:** {earnings_data["earnings_growth"]}  
    🩳 **Short-Ratio:** {short_ratio}
    """)

---

### 🚩 **Wichtig:**  
- Prüfe, ob deine Streamlit-App Zugriff auf externe Seiten (wie Earnings Whispers) erlaubt.
- Falls weiterhin Fehler auftauchen, teste zunächst lokal.

Jetzt sollte dein Eingabefenster wieder sichtbar sein und die App reibungslos laufen.
