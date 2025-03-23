import streamlit as st
import pandas as pd
from playwright.sync_api import sync_playwright

def scrape_finviz_news(ticker):
    url = f"https://finviz.com/quote.ashx?t={ticker}&p=d"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            rows = page.query_selector_all("table.fullview-news-outer tr")
            news_data = []
            for row in rows:
                cells = row.query_selector_all("td")
                if len(cells) == 2:
                    time = cells[0].inner_text().strip()
                    link_tag = cells[1].query_selector("a")
                    source_tag = cells[1].query_selector("span")
                    if link_tag and source_tag:
                        title = link_tag.inner_text().strip()
                        link = link_tag.get_attribute("href")
                        source = source_tag.inner_text().strip("()")
                        news_data.append({"Zeit": time, "Titel": f"[{title}]({link})", "Quelle": source})
        except Exception as e:
            return pd.DataFrame([{"Fehler": f"{e}"}])
        browser.close()
    return pd.DataFrame(news_data)

def scrape_zacks_earnings(ticker):
    url = f"https://www.zacks.com/stock/research/{ticker}/earnings-calendar"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            rows = page.query_selector_all("tr.even, tr.odd")
            data = []
            for row in rows:
                cols = row.query_selector_all("th, td")
                if len(cols) >= 7:
                    data.append({
                        "Datum": cols[0].inner_text().strip(),
                        "Periode": cols[1].inner_text().strip(),
                        "Schätzung": cols[2].inner_text().strip(),
                        "Bericht": cols[3].inner_text().strip(),
                        "Überraschung": cols[4].inner_text().strip(),
                        "% Überraschung": cols[5].inner_text().strip(),
                        "Zeitpunkt": cols[6].inner_text().strip(),
                    })
        except Exception as e:
            return pd.DataFrame([{"Fehler": f"{e}"}])
        browser.close()
    return pd.DataFrame(data)

# Streamlit UI
st.title("Finviz News & Zacks Earnings")

with st.form("ticker_form"):
    ticker = st.text_input("Ticker eingeben:").upper().strip()
    submitted = st.form_submit_button("Daten abrufen")

if submitted and ticker:
    st.subheader("📈 Aktuelle News von Finviz")
    news_df = scrape_finviz_news(ticker)
    st.dataframe(news_df, use_container_width=True)

    st.subheader("🧾 Earnings-History von Zacks")
    earnings_df = scrape_zacks_earnings(ticker)
    st.dataframe(earnings_df, use_container_width=True)
