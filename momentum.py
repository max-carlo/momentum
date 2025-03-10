import streamlit as st
import re
from datetime import datetime
import yfinance as yf
from playwright.sync_api import sync_playwright

# Hilfsfunktionen
def remove_labels(text):
    if text == "Nicht gefunden":
        return text
    return re.sub(r"(earnings growth|earnings surprise|revenue growth|revenue surprise)", "", text, flags=re.I).strip()

def remove_commas(value):
    return value.replace(",", "") if value != "Nicht gefunden" else value

def parse_date_to_ddmmyy(date_str):
    if date_str == "Nicht gefunden":
        return date_str
    date_str = re.sub(r"^[a-zA-Z]+,\s+", "", date_str)
    dt = datetime.strptime(date_str, "%B %d, %Y at %I:%M %p ET")
    return dt.strftime("%d/%m/%y")

@st.cache_data
def get_earnings_data(ticker):
    from playwright.sync_api import sync_playwright

    url = f"https://www.earningswhispers.com/epsdetails/{ticker}"

    with st.spinner('Hole Daten von Earnings Whispers...'):
        browser = sync_playwright().start().chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)

        def get_text(selector):
            try:
                page.wait_for_selector(selector, timeout=10000)
                return page.locator(selector=selector).inner_text().strip()
            except:
                return "Nicht gefunden"

        data = {
            "earnings_date": page.query_selector("#epsdate").inner_text().strip() if page.query_selector("#epsdetails #epsdate") else "Nicht gefunden",
            "earnings_surprise": page.inner_text("#earnings .surprise") if page.query_selector("#earnings .surprise") else "Nicht gefunden",
            "earnings_growth": page.inner_text("#earnings .growth") if page.query_selector("#earnings .growth") else "Nicht gefunden",
            "revenue_surprise": page.inner_text("#revenue .surprise") if page.query_selector("#revenue .surprise") else "Nicht gefunden",
            "revenue_growth": page.inner_text("#revenue .growth") if page.query_selector("#revenue .growth") else "Nicht gefunden"
        }

        browser.close()
    
    return data

def get_short_ratio_yfinance(ticker):
    t = yf.Ticker(ticker)
    info = t.info
    return str(info.get("shortRatio", "Nicht gefunden"))

# Hauptapp
def main():
    st.title("📊 Earnings Whispers & Yahoo Finance Data")
    ticker = st.text_input("Gib ein Aktienticker-Symbol ein (z.B. MAR)", value="AAPL").upper()

    if st.button("Daten abrufen"):
        data = get_earnings_data(ticker)

        earnings_date = parse_date_to_ddmmyy(data["earnings_date"])
        earnings_surprise = remove_commas(remove_labels(data["earnings_surprise"]))
        earnings_growth = remove_commas(remove_labels(data["earnings_growth"]))
        revenue_surprise = remove_commas(remove_labels(data["revenue_surprise"]))
        revenue_growth = remove_commas(remove_labels(data["revenue_growth"]))
        short_ratio = get_short_ratio_yfinance(ticker)

        st.subheader(f"Daten für {ticker.upper()}:")
        st.write(f"**Datum:** {earnings_date}")
        st.write(f"**Earnings Surprise:** {earnings_surprise}")
        st.write(f"**Earnings Growth:** {earnings_growth}")
        st.write(f"**Revenue Surprise:** {revenue_surprise}")
        st.write(f"**Revenue Growth:** {revenue_growth}")
        st.write(f"**Short Ratio:** {short_ratio}")

# App-Interface
st.title("📊 Earnings Whispers Datenabruf")
ticker = st.text_input("Ticker eingeben:", "AAPL").upper()

if st.button("Daten abrufen"):
    main(ticker)
