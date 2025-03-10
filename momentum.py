import streamlit as st
import subprocess
import re
from datetime import datetime
import yfinance as yf
from playwright.sync_api import sync_playwright

# Explizit Chromium installieren
subprocess.run(["playwright", "install", "chromium"], check=True)

@st.cache_data
def get_earnings_data(ticker):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        url = f"https://www.earningswhispers.com/epsdetails/{ticker}"
        page.goto(url)

        def get_text(selector):
            try:
                return page.text_content(selector=selector).strip()
            # Oder sicherer mit Timeout:
            # return page.wait_for_selector(selector, timeout=5000).inner_text().strip()
        except:
            return "Nicht gefunden"

        data = {
            "earnings_date": page.locator("#epsdetails > div.edate").inner_text() if page.locator("#epsdetails > div.edate").is_visible() else "Nicht gefunden",
            "earnings_surprise": page.locator("#earnings .surprise").inner_text() if page.locator("#earnings .surprise").is_visible() else "Nicht gefunden",
            "earnings_growth": page.locator("#earnings .growth").inner_text() if page.locator("#earnings .growth").is_visible() else "Nicht gefunden",
            "revenue_surprise": page.locator("#revenue .surprise").inner_text() if page.locator("#revenue .surprise").is_visible() else "Nicht gefunden",
            "revenue_growth": page.locator("#revenue .growth").inner_text() if page.locator("#revenue .growth").is_visible() else "Nicht gefunden",
        }
        browser.close()
    return data

# Hier restlicher Streamlit-Code wie gehabt:
import streamlit as st
ticker = st.text_input("Gib den Ticker ein:")
if ticker:
    data = get_earnings_data(ticker)
    st.write(data)
