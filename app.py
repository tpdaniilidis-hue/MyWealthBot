import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- ΡΥΘΜΙΣΕΙΣ TELEGRAM ---
TOKEN = "7854097442:AAEGZTQ4bRZ2TttL1sLR4DhP_Xly8yGxMpQ"
CHAT_ID = "941916327"

def send_telegram(msg):
    url = f"https://api.telegram.org{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
    try: requests.get(url, timeout=5)
    except: pass

# --- ΛΙΣΤΑ ΠΑΓΚΟΣΜΙΩΝ ΜΕΤΟΧΩΝ ΠΡΟΣ ΣΑΡΩΣΗ ---
WATCHLIST = [
    "NVDA", "AAPL", "MSFT", "TSLA", # ΗΠΑ (Tech)
    "MC.PA", "ASML.AS", "SAP.DE",   # Ευρώπη (LVMH, ASML, SAP)
    "EEE.AT", "OPAP.AT", "ALPHA.AT", # Ελλάδα (Coca-Cola, ΟΠΑΠ, Alpha)
    "BTC-USD", "ETH-USD"             # Crypto
]

@st.cache_data(ttl=3600)
def scan_markets(tickers):
    opportunities = []
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            hist = stock.history(period="1mo")
            if hist.empty: continue
            
            # Τεχνική Ανάλυση (RSI)
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (gain.iloc[-1]/loss.iloc[-1]))) if loss.iloc[-1] != 0 else 100
            
            price = float(stock.fast_info.last_price)
            
            # ΚΡΙΤΗΡΙΟ ΠΡΟΤΑΣΗΣ: RSI < 40 (Υποτιμημένη/Ευκαιρία)
            if rsi < 45:
                opportunities.append({"Σύμβολο": t, "Τιμή": f"{price:.2f}", "RSI": f"{rsi:.1f}", "Κατάσταση": "🔥 ΕΥΚΑΙΡΙΑ"})
            elif rsi > 70:
                opportunities.append({"Σύμβολο": t, "Τιμή": f"{price:.2f}", "RSI": f"{rsi:.1f}", "Κατάσταση": "⚠️ ΥΠΕΡΤΙΜΗΜΕΝΗ"})
        except:
            continue
    return opportunities

# --- UI ΕΦΑΡΜΟΓΗΣ ---
st.set_page_config(page_title="AI Market Hunter 2026", layout="wide")
st.title("🏹 AI Market Hunter: Παγκόσμιες Ευκαιρίες")
st.write(f"Ημερομηνία: 25 Φεβρουαρίου 2026")

if st.button("🔍 Σάρωση Αγορών Τώρα"):
    with st.spinner("Αναζήτηση για ευκαιρίες σε ΗΠΑ, Ευρώπη και Ελλάδα..."):
        results = scan_markets(WATCHLIST)
        
        if results:
            df = pd.DataFrame(results)
            st.table(df)
            
            # Αυτόματη ειδοποίηση Telegram για την καλύτερη ευκαιρία
            best_buy = df[df['Κατάσταση'] == "🔥 ΕΥΚΑΙΡΙΑ"].head(1)
            if not best_buy.empty:
                ticker_name = best_buy['Σύμβολο'].values[0]
                send_telegram(f"🎯 ΝΕΑ ΕΥΚΑΙΡΙΑ: Η μετοχή {ticker_name} είναι σε τιμή ευκαιρίας σήμερα!")
        else:
            st.info("Δεν βρέθηκαν έντονες ευκαιρίες αυτή τη στιγμή. Η αγορά είναι σε ισορροπία.")

st.sidebar.header("⚙️ Ρυθμίσεις Σάρωσης")
st.sidebar.write("Το σύστημα ελέγχει:")
st.sidebar.write("- RSI (Relative Strength Index)")
st.sidebar.write("- Παγκόσμια Χρηματιστήρια (.AT, .DE, .PA)")
