import streamlit as st
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

# 📌 Finviz News Scraper
def scrape_finviz_news(ticker):
    url = f"https://finviz.com/quote.ashx?t={ticker}&p=d"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/134.0.0.0 Safari/537.36"
        ))
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            html = page.content()
        except Exception as e:
            browser.close()
            return [f"Fehler beim Laden der Finviz-Seite: {e}"]
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table.fullview-news-outer tr")

    news_items = []
    for row in rows:
        time_cell = row.find("td", width="130")
        link_tag = row.find("a", class_="tab-link-news")
        source = row.find("span")
        if time_cell and link_tag and source:
            time = time_cell.text.strip()
            title = link_tag.text.strip()
            url = link_tag["href"]
            news_items.append((time, title, url))

    return news_items[:5]  # Top 5 News

# 📌 Zacks Earnings Calendar Scraper
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
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            html = page.content()
        except Exception as e:
            browser.close()
            return pd.DataFrame([["Fehler beim Laden der Zacks-Seite", "", "", "", "", "", ""]],
                                columns=["Date", "Period", "Estimate", "Reported", "Surprise", "% Surprise", "Time"])
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table#earnings_announcements_earnings_table tr.odd, table#earnings_announcements_earnings_table tr.even")

    if not rows:
        return pd.DataFrame([["Keine Datenzeilen gefunden", "", "", "", "", "", ""]],
                            columns=["Date", "Period", "Estimate", "Reported", "Surprise", "% Surprise", "Time"])

    data = []
    for row in rows[:4]:  # nur die ersten 4 Zeilen
        cells = row.find_all(["th", "td"])
        if len(cells) == 7:
            data.append([c.text.strip() for c in cells])

    df = pd.DataFrame(data, columns=["Date", "Period", "Estimate", "Reported", "Surprise", "% Surprise", "Time"])
    return df

# 🧼 Streamlit UI
st.title("Finviz & Zacks Scraper")

with st.form(key="form"):
    ticker = st.text_input("Ticker eingeben:")
    finviz_btn = st.form_submit_button("Finviz News abrufen")
    zacks_btn = st.form_submit_button("Zacks Earnings abrufen")

if finviz_btn and ticker:
    st.subheader(f"📰 Letzte Finviz News zu {ticker.upper()}")
    news = scrape_finviz_news(ticker.strip().upper())
    if isinstance(news, list):
        for time, title, url in news:
            st.markdown(f"- **{time}** – [{title}]({url})")
    else:
        st.error(news)

if zacks_btn and ticker:
    st.subheader(f"📊 Zacks Earnings Calendar für {ticker.upper()}")
    df = scrape_zacks_earnings(ticker.strip().upper())
    st.dataframe(df)
