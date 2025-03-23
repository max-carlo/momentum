import streamlit as st
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

def scrape_finviz_news(ticker="AAPL"):
    url = f"https://finviz.com/quote.ashx?t={ticker}&p=d"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/134.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            html = page.content()
        except Exception as e:
            browser.close()
            return f"Fehler beim Laden der Seite: {e}"

        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    news_rows = soup.select("table.fullview-news-outer tr")

    news_data = []
    for row in news_rows:
        time_cell = row.find("td", attrs={"align": "right"})
        link_cell = row.find("a", class_="tab-link-news")
        source_span = row.find("span")

        if time_cell and link_cell:
            time = time_cell.text.strip()
            title = link_cell.text.strip()
            href = link_cell["href"]
            source = source_span.text.strip("()") if source_span else ""

            news_data.append({
                "Time": time,
                "Title": title,
                "Source": source,
                "URL": href
            })

    return pd.DataFrame(news_data)

# Streamlit UI
st.title("Finviz News Scraper")

with st.form("ticker_form"):
    ticker = st.text_input("Ticker eingeben (z. B. AAPL)", "")
    submitted = st.form_submit_button("News abrufen")

if submitted and ticker:
    df = scrape_finviz_news(ticker.strip().upper())
    if isinstance(df, pd.DataFrame):
        st.dataframe(df)
    else:
        st.error(df)
