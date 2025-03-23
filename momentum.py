import streamlit as st
import yfinance as yf
import pandas as pd

def get_quarterly_earnings_data(ticker):
    t = yf.Ticker(ticker)

    # Versuch EPS-Daten zu laden
    try:
        eps_df = t.quarterly_earnings
        if eps_df is None or eps_df.empty:
            return "EPS-Daten fehlen."
    except Exception as e:
        return f"Fehler beim Abrufen der EPS-Daten: {e}"

    # Versuch Revenue-Daten zu laden
    try:
        income_stmt = t.quarterly_financials
        if income_stmt is None or income_stmt.empty:
            return "Revenue-Daten fehlen."
        revenue_series = income_stmt.loc["Total Revenue"]
    except Exception as e:
        return f"Fehler beim Abrufen der Revenue-Daten: {e}"

    # Konvertiere und kombiniere
    try:
        eps_df = eps_df[::-1]
        eps_df.index = pd.to_datetime(eps_df.index)
        revenue_series.index = pd.to_datetime(revenue_series.index)

        combined = pd.DataFrame({
            "EPS": eps_df["Earnings"],
            "Revenue": revenue_series
        })

        combined = combined.dropna().sort_index(ascending=False).head(5)
        combined["EPS YoY"] = combined["EPS"].pct_change(4) * 100
        combined["Revenue YoY"] = combined["Revenue"].pct_change(4) * 100
        return combined
    except Exception as e:
        return f"Fehler beim Kombinieren der Daten: {e}"

# UI
st.title("Earnings & Revenue Growth")

with st.form("earnings_form"):
    ticker = st.text_input("Ticker eingeben:")
    submitted = st.form_submit_button("Abrufen")

if submitted and ticker:
    result = get_quarterly_earnings_data(ticker.strip().upper())
    
    if isinstance(result, str):
        st.error(result)  # Fehlertext ausgeben
    else:
        st.dataframe(result.style.format({
            "EPS": "{:.2f}",
            "Revenue": "{:,.0f}",
            "EPS YoY": "{:.1f}%",
            "Revenue YoY": "{:.1f}%"
        }))
