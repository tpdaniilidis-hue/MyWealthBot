import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- CONFIG ---
st.set_page_config(page_title="AI Wealth Master 2026", layout="wide")

# Λειτουργία λήψης δεδομένων με μηχανισμό προστασίας (Retry)
@st.cache_data(ttl=3600)
def fetch_data_safe(symbol):
    for i in range(3): # Προσπάθεια 3 φορές αν αποτύχει
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            if not hist.empty:
                # Χρήση fast_info για ταχύτητα και αποφυγή μπλοκαρίσματος
                price = float(ticker.fast_info.last_price)
                info = ticker.info # Θεμελιώδη
                return hist, price, info
        except:
            time.sleep(1) # Αναμονή 1 δευτερόλεπτο πριν την επανάληψη
    return None, None, None

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["🔍 Ευκαιρίες", "💼 Πορτοφόλι", "🎮 Εξομοιωτής"])

with tab1:
    st.header("🎯 Παγκόσμιες Επενδυτικές Ευκαιρίες")
    
    # Λίστα μετοχών (Global Watchlist)
    watchlist = ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN", "META", "ASML.AS", "MC.PA", "SAP.DE", "EEE.AT", "OPAP.AT", "BTC-USD", "ETH-USD"]

    if st.button("🚀 Αναζήτηση Προτάσεων"):
        opportunities = []
        progress_bar = st.progress(0)
        
        for idx, t in enumerate(watchlist):
            hist, price, info = fetch_data_safe(t)
            if hist is not None and not hist.empty:
                # Υπολογισμός RSI
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (gain.iloc[-1]/loss.iloc[-1]))) if loss.iloc[-1] != 0 else 100
                
                # Προσθήκη όλων των μετοχών, αλλά με σήμανση ευκαιρίας
                status = "🔥 ΕΥΚΑΙΡΙΑ" if rsi < 55 else "⚖️ HOLD"
                opportunities.append({
                    "Σύμβολο": t,
                    "Όνομα": info.get('longName', t),
                    "Τιμή": f"{price:.2f}$",
                    "RSI": round(rsi, 1),
                    "Σήμα": status,
                    "Info": info,
                    "Hist": hist
                })
            progress_bar.progress((idx + 1) / len(watchlist))

        if opportunities:
            # Μετατροπή σε DataFrame για εμφάνιση
            df = pd.DataFrame(opportunities)[["Σύμβολο", "Τιμή", "RSI", "Σήμα"]]
            st.table(df)

            # Λεπτομερής Ανάλυση με Expander
            st.subheader("💡 Αναλυτική Αιτιολόγηση")
            for op in opportunities:
                with st.expander(f"Ανάλυση για {op['Όνομα']} ({op['Σύμβολο']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Γιατί προτείνεται;**")
                        if float(op['RSI']) < 50:
                            st.write("Η μετοχή είναι υποτιμημένη βάσει του δείκτη RSI, υποδηλώνοντας καλό σημείο εισόδου.")
                        else:
                            st.write("Η μετοχή βρίσκεται σε φάση σταθεροποίησης.")
                        
                        st.write("**Οικονομικά Στοιχεία:**")
                        st.write(f"- Debt/Equity: {op['Info'].get('debtToEquity', 'N/A')}")
                        st.write(f"- Profit Margin: {op['Info'].get('profitMargins', 0)*100:.2f}%")
                    with col2:
                        st.write("**Πρόβλεψη 5ετίας:**")
                        # Απλό AI μοντέλο πρόβλεψης
                        growth = (op['Hist']['Close'].pct_change().mean() * 252)
                        future = float(op['Τιμή'].replace('$', '')) * (1 + growth)**5
                        st.write(f"Εκτιμώμενη τιμή (2031): **{future:.2f}$**")
                        st.line_chart(op['Hist']['Close'])
        else:
            st.error("Δεν ήταν δυνατή η σύνδεση με τη Yahoo Finance. Δοκίμασε ξανά σε λίγα λεπτά.")

# (Οι καρτέλες Tab 2 και Tab 3 παραμένουν ίδιες με τον προηγούμενο κώδικα)
