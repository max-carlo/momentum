import streamlit as st
from datetime import datetime
import yfinance as yf
from playwright.sync_api import sync_playwright

@st.cache_data
def get_earnings_data(ticker):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        url = f"https://www.earningswhispers.com/epsdetails/{ticker}"
        page.goto(url)

        def safe_extract(selector):
            try:
                return page.locator(selector).inner_text().strip()
            except:
                return "Nicht gefunden"

        data = {
            "earnings_date": safe_extract("#epsdetails .mbcontent .mainitem"),
            "earnings_surprise": safe_extract("#earnings .surprise"),
            "earnings_growth": safe_extract("#earnings .growth"),
            "revenue_surprise": safe_extract("#revenue .surprise"),
            "revenue_growth": safe_extract("#revenue .growth"),
        }
        return data

@st.cache_data
def get_short_ratio(ticker):
    t = yf.Ticker(ticker)
    info = t.info
    return info.get("shortRatio", "Nicht gefunden")

def parse_date(date_str):
    try:
        dt = datetime.strptime(date_str.replace("ET", "").strip(), "%A, %B %d, %Y at %I:%M %p")
        return dt.strftime("%d/%m/%y")
    except:
        return "Nicht gefunden"

def clean_text(text):
    phrases = ["Earnings Growth", "Revenue Growth", "Earnings Surprise"]
    for phrase in phrases:
        text = text.replace(phrase, "").strip()
    return text.replace(",", "").strip()

# Streamlit App UI
st.title("📈 Earnings Whisper Momentum")

ticker = st.text_input("Gib das Tickersymbol ein (z.B. AAPL):")

if ticker:
    st.info(f"Lade Earnings-Daten für **{ticker.upper()}**...")
    earnings_data = get_earnings_data(ticker)

    earnings_date = parse_date(data["earnings_date"])
    earnings_surprise = clean_text(data["earnings_surprise"])
    earnings_growth = clean_text(data["earnings_growth"])
    revenue_surprise = clean_text(data["revenue_surprise"])
    revenue_growth = clean_text(data["revenue_growth"])
    short_ratio = get_short_ratio(ticker)

    st.markdown(f"""
    **Ergebnisse für {ticker.upper()}**  
    📅 Earnings-Datum: `{earnings_date}`  
    📊 Earnings Surprise: `{earnings_surprise}`  
    📈 Earnings-Wachstum: `{earnings_growth}`  
    💵 Umsatz Überraschung: `{revenue_surprise}`  
    📈 Umsatzwachstum: `{revenue_growth}`  
    🩳 Short-Ratio: `{short_ratio}`
    """)
