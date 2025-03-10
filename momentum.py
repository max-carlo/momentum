import streamlit as st
from playwright.sync_api import sync_playwright
import yfinance as yf
from datetime import datetime

@st.cache_data
def get_earnings_data(ticker):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()

        url = f"https://www.earningswhispers.com/epsdetails/{ticker}"
        page.goto(url, timeout=60000)

        # Hilfsfunktion für sichere Extraktion
        def safe_extract(selector):
            try:
                return page.locator(selector).text_content().strip()
            except:
                return "Nicht gefunden"

        data = {
            "earnings_date": "Nicht gefunden",
            "earnings_surprise": "Nicht gefunden",
            "earnings_growth": "Nicht gefunden",
            "revenue_surprise": "Nicht gefunden",
            "revenue_growth": "Nicht gefunden",
        }

        # Daten extrahieren mit korrektem try-except
        try:
            data["earnings_date"] = safe_extract(page, "#epsdetails > div.edate")
        except:
            pass

        try:
            data["earnings_surprise"] = safe_extract(page, "#earnings .surprise")
        except:
            pass

        try:
            data["earnings_growth"] = safe_extract(page, "#earnings .growth")
        except:
            pass

        try:
            data["revenue_surprise"] = safe_extract(page, "#revenue .surprise")
        except:
            pass

        try:
            data["revenue_growth"] = safe_extract(page, "#revenue .growth")
        except:
            pass

        browser.close()

        return data

# Hilfsfunktion, um Text sicher auszulesen
def safe_extract(page, selector):
    try:
        if page.locator(selector).is_visible():
            return page.locator(selector).inner_text().strip()
        else:
            return "Nicht gefunden"
    except:
        return "Nicht gefunden"
