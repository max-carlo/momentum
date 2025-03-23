import pandas as pd
import streamlit as st
from playwright.sync_api import sync_playwright

def scrape_zacks_earnings(ticker):
    url = f"https://www.zacks.com/stock/research/{ticker}/earnings-calendar"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/134.0.0.0 Safari/537.36"
        ))
        page = context.new_page()

        try:
            page.goto(url, wait_until="networkidle", timeout=90000)
            page.wait_for_selector("table#earnings_announcements_earnings_table", timeout=20000)
            table_html = page.inner_html("table#earnings_announcements_earnings_table")
        except Exception as e:
            browser.close()
            return f"Fehler beim Laden der Seite: {e}"

        browser.close()

    try:
        df_list = pd.read_html(f"<table>{table_html}</table>")
        df = df_list[0] if df_list else pd.DataFrame()
    except Exception as e:
        return f"Fehler beim Parsen der Tabelle: {e}"

    return df

# Streamlit UI
st.title("Zacks Earnings Scraper")

ticker = st.text_input("Ticker eingeben:")
if st.button("Lade Zacks Earnings"):
    result = scrape_zacks_earnings(ticker.strip().upper())
    if isinstance(result, str):
        st.error(result)
    else:
        st.write("### Earnings Calendar")
        st.dataframe(result)
