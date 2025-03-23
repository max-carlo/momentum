from playwright.sync_api import sync_playwright
import pandas as pd

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
        page.goto(url, wait_until="load", timeout=60000)

        # Wähle im Dropdown „100“ aus (zeigt alle Einträge)
        try:
            page.select_option('select[name="earnings_announcements_earnings_table_length"]', '100')
            page.wait_for_timeout(3000)  # warte kurz auf Neuladen der Tabelle
        except:
            print("⚠️ Dropdown konnte nicht geändert werden")

        # Warte bis Tabelle geladen ist
        page.wait_for_selector("table#earnings_announcements_earnings_table", timeout=10000)

        # Extrahiere den HTML der Tabelle
        table_html = page.inner_html("table#earnings_announcements_earnings_table")

        browser.close()

    # Nutze Pandas zum Parsen
    try:
        df_list = pd.read_html(f"<table>{table_html}</table>")
        df = df_list[0] if df_list else pd.DataFrame()
    except Exception as e:
        print(f"Fehler beim Parsen der Tabelle: {e}")
        df = pd.DataFrame()

    return df
