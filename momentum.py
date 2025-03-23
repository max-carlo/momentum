import yfinance as yf
import pandas as pd
import streamlit as st

def get_yfinance_earnings_history(ticker):
    try:
        t = yf.Ticker(ticker)
        earnings_df = t.quarterly_earnings

        if earnings_df is None or earnings_df.empty:
            return pd.DataFrame(), "Keine Earnings-Daten gefunden."

        earnings_df = earnings_df.copy()
        earnings_df.reset_index(inplace=True)
        earnings_df.columns = ['Quarter', 'EPS']

        try:
            rev_df = t.quarterly_financials.T[['Total Revenue']]
            rev_df.reset_index(inplace=True)
            rev_df.columns = ['Quarter', 'Revenue']
        except Exception:
            rev_df = pd.DataFrame(columns=['Quarter', 'Revenue'])

        merged_df = pd.merge(earnings_df, rev_df, on='Quarter', how='outer')
        merged_df.sort_values('Quarter', inplace=True, ascending=False)
        merged_df = merged_df.head(8)  # Für YoY-Vergleich

        merged_df['EPS YoY'] = merged_df['EPS'].pct_change(4) * 100
        merged_df['Revenue YoY'] = merged_df['Revenue'].pct_change(4) * 100

        merged_df['EPS YoY'] = merged_df['EPS YoY'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A")
        merged_df['Revenue YoY'] = merged_df['Revenue YoY'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A")

        return merged_df.head(4), ""
    except Exception as e:
        return pd.DataFrame(), str(e)

# Streamlit App
st.title("Hanabi Scraper – Earnings History (via yFinance)")

with st.form(key="yfinance_form"):
    ticker = st.text_input("Ticker eingeben:")
    submitted = st.form_submit_button("Fetch Earnings History")

if submitted and ticker:
    df, error = get_yfinance_earnings_history(ticker.strip().upper())
    if error:
        st.error(error)
    else:
        st.write("### Letzte 4 Quartale (inkl. YoY-Wachstum)")
        st.dataframe(df)
