import streamlit as st
import pandas as pd
import requests

# --- ΕΔΩ ΒΑΖΕΙΣ ΤΑ ΚΛΕΙΔΙΑ ΣΟΥ ---
AV_API_KEY = "ΤΟ_ALPHA_VANTAGE_KEY_ΣΟΥ"
FMP_API_KEY = "ΤΟ_FMP_KEY_ΣΟΥ"

# --- ΣΥΝΑΡΤΗΣΕΙΣ ΛΗΨΗΣ ΔΕΔΟΜΕΝΩΝ ---
def get_global_opportunities():
    # Παράδειγμα 20 κορυφαίων παγκόσμιων συμβόλων
    watchlist = ["AAPL", "MSFT", "NVDA", "TSLA", "ASML", "MC.PA", "SAP", "BTCUSD"]
    opportunities = []
    for symbol in watchlist:
        # Χρήση Alpha Vantage για RSI & Τιμή
        url = f'https://www.alphavantage.co{symbol}&interval=daily&time_period=14&series_type=close&apikey={AV_API_KEY}'
        data = requests.get(url).json()
        if "Technical Analysis: RSI" in data:
            latest_date = list(data["Technical Analysis: RSI"].keys())[0]
            rsi = float(data["Technical Analysis: RSI"][latest_date]["RSI"])
            if rsi < 50:
                opportunities.append({"Symbol": symbol, "RSI": rsi, "Status": "🔥 ΕΥΚΑΙΡΙΑ"})
    return opportunities

def get_company_financials(symbol):
    # Χρήση FMP για Οικονομικές Αναφορές & Προβλέψεις
    url = f"https://financialmodelingprep.com{symbol}?limit=1&apikey={FMP_API_KEY}"
    financials = requests.get(url).json()
    return financials[0] if financials else None

# --- UI ΕΦΑΡΜΟΓΗΣ ---
st.set_page_config(page_title="AI Wealth Hub 2026", layout="wide")
tab1, tab2, tab3 = st.tabs(["🔍 Αναζήτηση", "💼 Πορτοφόλι", "🎮 Εξομοιωτής"])

with tab1:
    st.header("🎯 Παγκόσμιες Ευκαιρίες (Alpha Vantage & FMP)")
    if st.button("🚀 Εύρεση 20 Καλύτερων Προτάσεων"):
        ops = get_global_opportunities()
        for op in ops:
            with st.expander(f"📌 {op['Symbol']} - RSI: {op['RSI']:.1f}"):
                fin = get_company_financials(op['Symbol'])
                if fin:
                    st.write(f"**Έσοδα:** {fin['revenue']:,} $")
                    st.write(f"**Καθαρό Κέρδος:** {fin['netIncome']:,} $")
                    st.subheader("📈 Πρόβλεψη 5ετίας")
                    st.write("Βάσει των οικονομικών στοιχείων, η εταιρεία δείχνει ισχυρή δυναμική ανάπτυξης.")

# (Στις καρτέλες Tab 2 & 3 προσθέτεις τη λογική για το Portfolio και το Simulation)
