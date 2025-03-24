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

            rows = page.query_selector_all("table.fullview-news-outer tr")
            news_data = []
            for row in rows:
                time_cell = row.query_selector("td:nth-child(1)")
                title_cell = row.query_selector("td:nth-child(2) a")
                source_span = row.query_selector("td:nth-child(2) span")

                if title_cell and source_span:
                    time = time_cell.inner_text().strip() if time_cell else ""
                    title = title_cell.inner_text().strip()
                    link = title_cell.get_attribute("href")
                    source = source_span.inner_text().strip()
                    news_data.append({
                        "Zeit": time,
                        "Titel": f"[{title}]({link})",
                        "Quelle": source
                    })
            browser.close()
        return pd.DataFrame(news_data)
    except Exception as e:
        return f"Fehler beim Abrufen der Finviz News: {e}"

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

            rows = page.query_selector_all("table#earnings_announcements_earnings_table tr.odd, table#earnings_announcements_earnings_table tr.even")
            earnings_data = []
            for row in rows:
                cols = row.query_selector_all("th, td")
                if len(cols) >= 7:
                    earnings_data.append({
                        "Date": cols[0].inner_text().strip(),
                        "Period Ending": cols[1].inner_text().strip(),
                        "Estimate": cols[2].inner_text().strip(),
                        "Reported": cols[3].inner_text().strip(),
                        "Surprise": cols[4].inner_text().strip(),
                        "% Surprise": cols[5].inner_text().strip(),
                        "Time": cols[6].inner_text().strip(),
                    })
            browser.close()
        return pd.DataFrame(earnings_data)
    except Exception as e:
        return f"Fehler beim Abrufen der Zacks Earnings: {e}"

# Streamlit UI
st.title("📰 Finviz News & Zacks Earnings")

with st.form(key="ticker_form"):
    ticker = st.text_input("Ticker eingeben (z.B. AAPL):")
    submitted = st.form_submit_button("Daten abrufen")

if submitted and ticker:
    ticker = ticker.strip().upper()

    # Finviz
    st.subheader("🔹 Finviz News")
    finviz_data = scrape_finviz_news(ticker)
    if isinstance(finviz_data, pd.DataFrame) and not finviz_data.empty:
        st.dataframe(finviz_data)
    else:
        st.error(finviz_data)

    # Zacks
    st.subheader("🔹 Zacks Earnings Calendar")
    zacks_data = scrape_zacks_earnings(ticker)
    if isinstance(zacks_data, pd.DataFrame) and not zacks_data.empty:
        st.dataframe(zacks_data)
    else:
        st.error(zacks_data)
