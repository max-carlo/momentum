import streamlit as st
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

# --- Finviz News Scraper ---
def scrape_finviz_news(ticker="AAPL"):
    url = f"https://finviz.com/quote.ashx?t={ticker}&p=d"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/134.0.0.0 Safari/537.36"))
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            html = page.content()
        except Exception as e:
            browser.close()
            return f"Fehler beim Laden der Finviz-News: {e}"
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    news_rows = soup.select("table.fullview-news-outer tr")

    news_items = []
    for row in news_rows:
        time_cell = row.find("td", width="130")
        link_cell = row.find("a", class_="tab-link-news")
        source_span = row.find("span")
        if link_cell:
            time = time_cell.text.strip() if time_cell else ""
            title = link_cell.text.strip()
            href = link_cell["href"]
            source = source_span.text.strip("()") if source_span else ""
            item = f"**{time}** – [{title}]({href}) ({source})"
            news_items.append(item)
    return news_items

# --- Zacks Earnings Scraper ---
def scrape_zacks_earnings(ticker):
    url = f"https://www.zacks.com/stock/research/{ticker}/earnings-calendar"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/134.0.0.0 Safari/537.36"))
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("table#earnings_announcements_earnings_table", timeout=10000)
            rows = page.query_selector_all("tr.odd, tr.even")
            data = []
            for row in rows:
                cols = row.query_selector_all("th, td")
                if len(cols) >= 7:
                    data.append({
                        "Date": cols[0].inner_text().strip(),
                        "Period": cols[1].inner_text().strip(),
                        "Estimate": cols[2].inner_text().strip(),
                        "Reported": cols[3].inner_text().strip(),
                        "Surprise": cols[4].inner_text().strip(),
                        "% Surprise": cols[5].inner_text().strip(),
                        "Time": cols[6].inner_text().strip(),
                    })
        except Exception as e:
            browser.close()
            return f"Fehler beim Laden der Zacks-Daten: {e}"
        browser.close()
    return pd.DataFrame(data)

# --- Streamlit UI ---
st.title("📊 Aktien-Infos: Finviz News & Zacks Earnings")

with st.form("ticker_form"):
    ticker = st.text_input("Ticker eingeben (z. B. AAPL)", "")
    col1, col2 = st.columns(2)
    with col1:
        submitted_news = st.form_submit_button("📰 Finviz News abrufen")
    with col2:
        submitted_zacks = st.form_submit_button("📅 Zacks Earnings abrufen")

if submitted_news and ticker:
    news_list = scrape_finviz_news(ticker.strip().upper())
    if isinstance(news_list, list):
        st.markdown("### 📰 Finviz News")
        for item in news_list:
            st.markdown(f"- {item}")
    else:
        st.error(news_list)

if submitted_zacks and ticker:
    df = scrape_zacks_earnings(ticker.strip().upper())
    if isinstance(df, pd.DataFrame) and not df.empty:
        st.markdown("### 📅 Zacks Earnings Calendar")
        st.dataframe(df)
    else:
        st.error(df if isinstance(df, str) else "Keine Daten gefunden.")
