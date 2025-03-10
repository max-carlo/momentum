import streamlit as st
import re
from datetime import datetime
import yfinance as yf
from playwright.sync_api import sync_playwright

# Hilfsfunktionen
def remove_labels(value):
    if value == "Nicht gefunden":
        return value
    patterns = ["earnings growth", "earnings surprise", "revenue surprise", "revenue growth"]
    for pattern in patterns:
        value = re.sub(pattern, "", value, flags=re.IGNORECASE)
    return value.strip()

def remove_commas(value):
    return value.replace(",", "") if value != "Nicht gefunden" else value

def parse_date_to_ddmmyy(date_str):
    if date_str == "Nicht gefunden":
        return date_str
    date_str = re.sub(r"^[a-zA-Z]+,\s+", "", date_str)
    try:
        dt = datetime.strptime(date_str, "%B %d, %Y at %I:%M %p ET")
        return dt.strftime("%d/%m/%y")
    except:
        return "Nicht gefunden"

# Daten von Earnings Whispers abrufen
@st.cache_data
def get_earnings_data(ticker):
    url = f"https://www.earningswhispers.com/epsdetails/{ticker}"
    data = {
        "earnings_date": "Nicht gefunden",
        "earnings_surprise": "Nicht gefunden",
        "earnings_growth": "Nicht gefunden",
        "revenue_surprise": "Nicht gefunden",
        "revenue_growth": "Nicht gefunden"
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)

        try:
            data["earnings_date"] = page.text_content("#epsdetails #epsdate") or "Nicht gefunden"
            data["earnings_surprise"] = page.text_content("#earnings .surprise") or "Nicht gefunden"
            data["earnings_growth"] = page.text_content("#earnings .growth") or "Nicht gefunden"
            data["revenue_surprise"] = page.text_content("#revenue .surprise") or "Nicht gefunden"
            data["revenue_growth"] = page.text_content("#revenue .growth") or "Nicht gefunden"
        except:
            pass

    return data

def get_short_ratio_yfinance(ticker):
    t = yf.Ticker(ticker)
    info = t.info
    return str(info.get("shortRatio", "Nicht gefunden"))

# Streamlit-App-Startpunkt
st.title("Earnings Whispers Datenabruf")

ticker = st.text_input("Gib das Ticker-Symbol ein:", value="AAPL").upper()

if st.button("Daten abrufen"):
    with st.spinner('Lade Daten...'):
        data = get_earnings_data(ticker)

        earnings_date = parse_date_to_ddmmyy(data["earnings_date"])
        earnings_surprise = remove_commas(remove_labels(data["earnings_surprise"]))
        earnings_growth = remove_commas(remove_labels(data["earnings_growth"]))
        revenue_surprise = remove_commas(remove_labels(data["revenue_surprise"]))
        revenue_growth = remove_commas(remove_labels(data["revenue_growth"]))
        short_ratio = get_short_ratio_yfinance(ticker)

        st.subheader(f"Daten für: {ticker}")
        st.write(f"**Earnings Datum:** {earnings_date}")
        st.write(f"**Earnings Surprise:** {earnings_surprise}")
        st.write(f"**Earnings Growth:** {earnings_growth}")
        st.write(f"**Revenue Surprise:** {revenue_surprise}")
        st.write(f"**Revenue Growth:** {revenue_growth}")
        st.write(f"**Short Ratio:** {short_ratio}")
