import streamlit as st
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
import pandas as pd

st.title("Ticker Scraper (Finviz + Zacks)")

ticker = st.text_input("Ticker eingeben:")


# --------- FINVIZ SCRAPER (bewährter Code) ----------
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
            return f"Fehler beim Laden der Finviz-Seite: {e}"

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


# --------- ZACKS SCRAPER ----------
def scrape_zacks_earnings(ticker):
    url = f"https://www.zacks.com/stock/research/{ticker}/earnings-calendar"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=90000)

            rows = page.query_selector_all("tr.odd, tr.even")
            if not rows:
                raise Exception("Keine .odd/.even Tabellenzeilen gefunden.")

            data = []
            for row in rows:
                cells = row.query_selector_all("th, td")
                if len(cells) >= 7:
                    try:
                        date = cells[0].inner_text()
                        period = cells[1].inner_text()
                        estimate = cells[2].inner_text()
                        reported = cells[3].inner_text()
                        surprise = cells[4].inner_text()
                        surprise_percent = cells[5].inner_text()
                        time = cells[6].inner_text()
                        data.append({
                            "Date": date,
                            "Period": period,
                            "Estimate": estimate,
                            "Reported": reported,
                            "Surprise": surprise,
                            "% Surprise": surprise_percent,
                            "Time": time
                        })
                    except:
                        continue
            browser.close()
            return pd.DataFrame(data)
    except PlaywrightTimeoutError as e:
        return f"Fehler beim Laden der Zacks-Daten: {e}"
    except Exception as e:
        return f"Allgemeiner Fehler bei Zacks-Daten: {e}"


# --------- BUTTONS ----------
col1, col2 = st.columns(2)

with col1:
    if st.button("🔍 Finviz News laden") and ticker:
        st.subheader("📢 Finviz News")
        news = scrape_finviz_news(ticker.strip().upper())
        if isinstance(news, list):
            for item in news:
                st.markdown(f"- {item}")
        else:
            st.error(news)

with col2:
    if st.button("📊 Zacks Earnings laden") and ticker:
        st.subheader("📈 Zacks Earnings")
        earnings = scrape_zacks_earnings(ticker.strip().upper())
        if isinstance(earnings, pd.DataFrame):
            st.dataframe(earnings)
        else:
            st.error(earnings)
