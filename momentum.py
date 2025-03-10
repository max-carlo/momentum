import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

@st.cache_data(show_spinner=True)
def get_earnings_data(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(url)

        # Beispielhafte Wartezeit auf ein Element
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".earningstable"))
        )

        earnings_table = driver.find_element(By.CSS_SELECTOR, ".earningstable")
        earnings_html = earnings_table.get_attribute('outerHTML')

        return earnings_html

    except Exception as e:
        st.error(f"Fehler beim Laden: {e}")
        return None

    finally:
        driver.quit()

# Streamlit App
st.title("Earnings Data Scraper")
url = st.text_input("Gib die URL zur Earnings-Seite ein:")

if st.button("Daten abrufen"):
    if url:
        data = get_earnings_data(url)
        if data:
            st.markdown(data, unsafe_allow_html=True)
    else:
        st.warning("Bitte gib eine gültige URL ein.")
