import streamlit as st
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import pandas as pd

st.title("Ticker Scraper (Finviz + Zacks)")

ticker = st.text_input("Ticker eingeben:")

# --- FINVIZ SCRAPER ---
def scrape_finviz_news(ticker):
    url = f"https://finviz.com/quote.ashx?t={ticker}&p=d"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
            page = context.new_page()
            page.goto(url, timeout=60000)
            page.wait_for_selector(".news-link-container", timeout=30000)
            rows = page.query_selector_all("tr.cursor-pointer")
            data = []
            for row in rows:
                try:
                    time = row.query_selector("td").inner_text(timeout=3000)
                    link = row.query_selector("a.tab-link-news")
                    title = link.inner_text(timeout=3000)
                    href = link.get_attribute("href")
                    source = row.query_selector(".news-link-right span").inner_text(timeout=3000)
                    data.append({"Time": time, "Title": title, "Source": source, "URL": href})
                except:
                    continue
            browser.close()
            return pd.DataFrame(data)
    except PlaywrightTimeoutError as e:
        return f"Fehler beim Laden der Finviz-News: {e}"
    except Exception as e:
        return f"Allgemeiner Fehler bei Finviz-News: {e}"

# --- ZACKS SCRAPER ---
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

# --- BUTTONS ---
col1, col2 = st.columns(2)

with col1:
    if st.button("🔍 Finviz News laden") and ticker:
        st.subheader("📢 Finviz News")
        news = scrape_finviz_news(ticker.strip().upper())
        if isinstance(news, pd.DataFrame):
            for _, row in news.iterrows():
                st.markdown(f"**{row['Time']}** — [{row['Title']}]({row['URL']}) *(Quelle: {row['Source']})*")
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
