import streamlit as st
import yfinance as yf
from datetime import datetime
from playwright.sync_api import sync_playwright

@st.cache_resource
def install_playwright():
    import subprocess
    subprocess.run(["playwright", "install", "chromium"], check=True)

install_playwright = st.cache_resource(install_playwright)
install_playwright()

@st.cache_data
def get_earnings_data(ticker):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        url = f"https://www.earningswhispers.com/epsdetails/{ticker}"
        page.goto(url)
        earnings_data = {
            "earnings_date": page.text_content("#epsdetails") or "Nicht gefunden",
            "earnings_surprise": page.text_content("#earnings .surprise") or "Nicht gefunden",
            "earnings_growth": page.text_content("#earnings .growth") or "Nicht gefunden",
            "revenue_surprise": page.text_content("#revenue .surprise") or "Nicht gefunden",
            "revenue_growth": page.text_content("#revenue .growth") or "Nicht gefunden"
        }
        browser.close()
        return earnings_data

def parse_date(date_str):
    if date_str == "Nicht gefunden":
        return date_str
    cleaned = date_str.replace(" ET", "").replace(" at", "")
    dt = datetime.strptime(cleaned, "%A, %B %d, %Y %I:%M %p")
    return dt.strftime("%d/%m/%y")

def get_short_ratio(ticker):
    try:
        info = yf.Ticker(ticker).info
        return str(info.get("shortRatio", "Nicht gefunden"))
    except:
        return "Nicht gefunden"

st.title("📈 Earnings Whisper Momentum")

ticker = st.text_input("Gib das Tickersymbol ein (z.B. AAPL):")

if ticker:
    earnings_data = get_earnings_data(ticker)

    earnings_date = parse_date(earnings_data["earnings_date"])
    earnings_surprise = earnings_data["earnings_surprise"]
    revenue_surprise = earnings_data["revenue_surprise"]
    earnings_growth = earnings_data["earnings_growth"]
    revenue_growth = earnings_data["revenue_growth"]
    short_ratio = get_short_ratio(ticker)

    st.markdown(f"""
    **Ergebnisse für {ticker.upper()}**  
    📅 **Earnings-Datum:** {earnings_date}  
    📊 **Earnings Surprise:** {earnings_surprise}  
    📈 **Earnings Growth:** {earnings_growth}  
    💰 **Revenue Surprise:** {revenue_surprise}  
    💹 **Revenue Growth:** {revenue_growth}  
    📉 **Short Ratio:** {short_ratio}
    """)

