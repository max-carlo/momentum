import streamlit as st
import yfinance as yf
import pandas as pd

def get_quarterly_earnings_data(ticker):
    t = yf.Ticker(ticker)

    # Hole EPS
    eps_df = t.quarterly_earnings
    if eps_df is None or eps_df.empty:
        return None

    eps_df = eps_df[::-1]  # Neueste nach unten
    eps_df.index = pd.to_datetime(eps_df.index)

    # Hole Revenue (aus Income Statement)
    income_stmt = t.quarterly_financials
    if income_stmt is None or income_stmt.empty:
        return None

    revenue_series = income_stmt.loc["Total Revenue"]
    revenue_series.index = pd.to_datetime(revenue_series.index)

    # Kombiniere beide
    combined = pd.DataFrame({
        "EPS": eps_df["Earnings"],
        "Revenue": revenue_series
    })

    combined = combined.dropna().sort_index(ascending=False).head(5)  # Die letzten 5 Quartale (falls Q/Q-Vergleich gewünscht)
    
    # Wachstum YoY berechnen (aktuelles Q vs Vorjahres-Q)
    combined["EPS YoY"] = combined["EPS"].pct_change(4) * 100
    combined["Revenue YoY"] = combined["Revenue"].pct_change(4) * 100

    return combined

# Streamlit UI
st.title("Earnings & Revenue (YoY)")

with st.form("earnings_form"):
    ticker = st.text_input("Ticker eingeben:")
    submitted = st.form_submit_button("Abrufen")

if submitted and ticker:
    df = get_quarterly_earnings_data(ticker.strip().upper())
    if df is None or df.empty:
        st.error("Keine Earnings- oder Revenue-Daten gefunden.")
    else:
        st.dataframe(df.style.format({
            "EPS": "{:.2f}",
            "Revenue": "{:,.0f}",
            "EPS YoY": "{:.1f}%",
            "Revenue YoY": "{:.1f}%"
        }))
