import streamlit as st
import yfinance as yf
import pandas as pd

def get_earnings_history_yf(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.quarterly_earnings.copy()
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        # Wachstum zum Vorjahresquartal
        df["Earnings YoY"] = df["Earnings"].pct_change(periods=4) * 100
        df["Revenue YoY"] = df["Revenue"].pct_change(periods=4) * 100

        # Nur letzte 4 Quartale
        df = df.iloc[-4:].copy()

        # Formatierungen
        df_display = df.copy()
        df_display.index = df_display.index.strftime("%Y-Q%q")  # Format wie "2023-Q4"
        df_display["Earnings"] = df_display["Earnings"].map("{:.2f}".format)
        df_display["Revenue"] = df_display["Revenue"].map(lambda x: f"{x/1e9:.2f}B")
        df_display["Earnings YoY"] = df_display["Earnings YoY"].map(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A")
        df_display["Revenue YoY"] = df_display["Revenue YoY"].map(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A")

        df_display = df_display[["Earnings", "Earnings YoY", "Revenue", "Revenue YoY"]]
        return df_display
    except Exception as e:
        return pd.DataFrame({"Fehler": [str(e)]})

# Streamlit UI
st.title("Test: Earnings History (via yfinance)")

with st.form(key="debug_form"):
    ticker = st.text_input("Ticker eingeben:")
    submitted = st.form_submit_button("Fetch Earnings History")

if submitted and ticker:
    st.write("### Earnings History (yfinance)")
    df_history = get_earnings_history_yf(ticker.strip().upper())
    st.dataframe(df_history, use_container_width=True)
