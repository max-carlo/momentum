from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def get_earnings_data(ticker):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    url = f"https://www.earningswhispers.com/stocks/{ticker}"
    driver.get(url)

    wait = WebDriverWait(driver, 10)

    earnings_data = {}

    try:
        eps = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//div[contains(text(),"Consensus EPS Forecast")]/following-sibling::div')
        )).text
        earnings_data["EPS"] = eps
    except Exception as e:
        earnings_data["EPS"] = f"Fehler: EPS nicht gefunden ({str(e)})"

    try:
        revenue = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//div[contains(text(),"Consensus Revenue Forecast")]/following-sibling::div')
        )).text
        earnings_data["Revenue"] = revenue
    except Exception as e:
        earnings_data["Revenue"] = f"Fehler: Revenue nicht gefunden ({str(e)})"

    try:
        growth = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//div[contains(text(),"Expected Growth")]/following-sibling::div')
        )).text
        earnings_data["Growth"] = growth
    except Exception as e:
        earnings_data["Growth"] = f"Fehler: Growth nicht gefunden ({str(e)})"

    driver.quit()
    return earnings_data

if __name__ == "__main__":
    ticker = input("Bitte den Ticker eingeben: ")
    earnings = get_earnings_data(ticker.upper())
    print(earnings)
