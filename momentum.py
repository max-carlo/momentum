import streamlit as st
from playwright.sync_api import sync_playwright
import pandas as pd

def scrape_finviz_news(ticker):
    url = f"https://finviz.com/quote.ashx?t={ticker}&p=d"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/134.0.0.0 Safari/537.36"
            ))
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            news_rows = page.query_selector_all("table.fullview-news-outer tr")
            news = []
            for row in news_rows:
                cells = row.query_selector_all("td")
                if len(cells) == 2:
                    time = cells[0].inner_text().strip()
                    link = cells[1].query_selector("a")
                    if link:
                        title = link.inner_text().strip()
                        href = link.get_attribute("href")
                        source = cells[1].query_selector("span")
                        source_text = source.inner_text().strip("()") if source else ""
                        news.append((time, source_text, title, href))
            browser.close()
            return pd.DataFrame(news, columns=["Time", "Source", "Title", "URL"])
    except Exception as e:
        return f"Fehler beim Laden der Finviz-News: {e}"

def scrape_zacks_earnings(ticker):
    url = f"https://www.zacks.com/stock/research/{ticker}/earnings-calendar"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/134.0.0.0 Safari/537.36"
            ))
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            page.wait_for_selector("table#earnings_announcements_earnings_table", timeout=10000)
            table_html = page.inner_html("table#earnings_announcements_earnings_table")
            browser.close()
            df_list = pd.read_html(f"<table>{table_html}</table>")
            df = df_list[0] if df_list else pd.DataFrame()
            return df
    except Exception as e:
        return f"Fehler beim Laden der Zacks-Daten: {e}"

st.title("News & Earnings Scraper")

with st.form("ticker_form"):
    ticker = st.text_input("Ticker eingeben:").upper().strip()
    submitted = st.form_submit_button("Daten abrufen")

if submitted and ticker:
    # Finviz
    result_news = scrape_finviz_news(ticker)
    st.subheader("Finviz News")
    if isinstance(result_news, pd.DataFrame) and not result_news.empty:
        result_news["Title"] = result_news.apply(lambda row: f"[{row['Title']}]({row['URL']})", axis=1)
        st.dataframe(result_news[["Time", "Source", "Title"]])
    else:
        st.error(result_news if isinstance(result_news, str) else "Keine News gefunden.")

    # Zacks
    result_zacks = scrape_zacks_earnings(ticker)
    st.subheader("Zacks Earnings")
    if isinstance(result_zacks, pd.DataFrame) and not result_zacks.empty:
        st.dataframe(result_zacks)
    else:
        st.error(result_zacks if isinstance(result_zacks, str) else "Keine Earnings-Daten gefunden.")
