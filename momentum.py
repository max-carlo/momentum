import streamlit as st
from playwright.sync_api import sync_playwright
import pandas as pd

# --- Scraper-Funktion ---
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
        page.goto(url, wait_until="load", timeout=60000)

        # Dropdown auf 100 umstellen
        try:
            page.select_option('select[name="earnings_announcements_earnings_table_length"]', '100')
            page.wait_for_timeout(3000)
        except:
            pass  # falls Dropdown nicht existiert

        # Warte auf Tabelle
        page.wait_for_selector("table#earnings_announcements_earnings_table", timeout=10000)
        table_html = page.inner_html("table#earnings_announcements_earnings_table")
        browser.close()

    # Mit Pandas Tabelle parsen
    try:
        df_list = pd.read_html(f"<table>{table_html}</table>")
        df = df_list[0] if df_list else pd.DataFrame()
    except Exception as e:
        print(f"Fehler beim Parsen der Tabelle: {e}")
        df = pd.DataFrame()

    return df


# --- Streamlit App ---
st.title("📊 Zacks Earnings Calendar Scraper")

with st.form(key="ticker_form"):
    ticker = st.text_input("Ticker eingeben (z. B. AAPL):")
    submitted = st.form_submit_button("Daten abrufen")

if submitted and ticker:
    df = scrape_zacks_earnings(ticker.strip().upper())
    if df.empty:
        st.error("Keine Daten gefunden.")
    else:
        st.write(f"### Earnings Calendar für {ticker.upper()}")
        st.dataframe(df)
