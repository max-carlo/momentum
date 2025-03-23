import streamlit as st
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

# Finviz News Scraper
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

# Zacks Earnings Calendar Scraper
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
            return pd.DataFrame([["Fehler beim Laden der Zacks-Seite", "", "", "", "", "", ""]], columns=["Date", "Period", "Estimate", "Reported", "Surprise", "% Surprise", "Time"])
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", id="earnings_announcements_earnings_table")
    if not table:
        return pd.DataFrame([["Keine Tabelle gefunden", "", "", "", "", "", ""]], columns=["Date", "Period", "Estimate", "Reported", "Surprise", "% Surprise", "Time"])

    headers = [th.text.strip() for th in table.find_all("th")]
    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = tr.find_all(["th", "td"])
        if len(cells) == len(headers):
            rows.append([cell.text.strip() for cell in cells])

    df = pd.DataFrame(rows, columns=headers)
    return df.head(4)

# Streamlit UI
st.title("News & Earnings Scraper")

with st.form(key="form"):
    ticker = st.text_input("Ticker eingeben:")
    submitted = st.form_submit_button("Fetch Data")

if submitted and ticker:
    ticker = ticker.strip().upper()

    st.subheader(f"📰 Letzte Finviz News zu {ticker}")
    news = scrape_finviz_news(ticker)
    for time, title, url in news:
        st.markdown(f"- **{time}** – [{title}]({url})")

    st.subheader(f"📊 Zacks Earnings Calendar für {ticker}")
    df = scrape_zacks_earnings(ticker)
    st.dataframe(df)
