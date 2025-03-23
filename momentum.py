import streamlit as st
from playwright.sync_api import sync_playwright

def get_earnings_history(ticker):
    url = f"https://seekingalpha.com/symbol/{ticker}/earnings"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("table[data-test-id='table']", timeout=60000)
            rows = page.query_selector_all("table[data-test-id='table'] tbody tr")

            earnings_data = []
            for row in rows:
                cols = row.query_selector_all("td")
                if len(cols) >= 6:
                    period = cols[0].inner_text()
                    eps = cols[1].inner_text()
                    eps_beat_miss = cols[2].inner_text()
                    revenue = cols[3].inner_text()
                    yoy_growth = cols[4].inner_text()
                    revenue_beat_miss = cols[5].inner_text()
                    earnings_data.append(f"{period}: EPS {eps} ({eps_beat_miss}), Revenue {revenue} ({yoy_growth} YoY), Rev Surprise {revenue_beat_miss}")

        except Exception as e:
            return [f"Fehler beim Laden der Earnings-History: {e}"]

        browser.close()
    return earnings_data

# Streamlit UI
st.title("Test: Seeking Alpha Earnings History")

with st.form(key="debug_form"):
    ticker = st.text_input("Ticker eingeben:")
    submitted = st.form_submit_button("Fetch Earnings History")

if submitted and ticker:
    history = get_earnings_history(ticker.strip().upper())
    st.write("### Earnings History (Seeking Alpha)")
    for entry in history:
        st.write(entry)
