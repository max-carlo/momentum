import streamlit as st
from playwright.sync_api import sync_playwright

@st.cache_data(show_spinner=True)
def get_earnings_data(url):
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)

            # Warte auf Element (.earningstable als Beispiel)
            page.wait_for_selector(".earningstable", timeout=10000)

            earnings_html = page.inner_html(".earningstable")
            browser.close()

            return earnings_html

    except Exception as e:
        st.error(f"Fehler beim Abrufen der Daten: {e}")
        return None

# Streamlit-Frontend
st.title("Earnings Daten abrufen")

url = st.text_input("URL der Webseite eingeben:")

if st.button("Daten abrufen"):
    if url:
        data = get_earnings_data(url)
        if data:
            st.markdown(data, unsafe_allow_html=True)
        else:
            st.error("Keine Daten gefunden oder Fehler beim Laden.")
    else:
        st.warning("Bitte URL eingeben.")
