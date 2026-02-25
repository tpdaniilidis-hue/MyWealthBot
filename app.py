import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# --- ΡΥΘΜΙΣΕΙΣ TELEGRAM ---
TOKEN = "7854097442:AAEGZTQ4bRZ2TttL1sLR4DhP_Xly8yGxMpQ"
CHAT_ID = "941916327"

def send_telegram(msg):
    url = f"https://api.telegram.org{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=Markdown"
    try: requests.get(url, timeout=5)
    except: pass

# --- ΛΙΣΤΑ ΠΑΓΚΟΣΜΙΩΝ ΠΡΟΪΟΝΤΩΝ ---
WATCHLIST = ["NVDA", "AAPL", "VWCE.DE", "BND", "BTC-USD", "GLD", "ASML.AS"]

@st.cache_data(ttl=1800) # 1800 δευτερόλεπτα = 30 λεπτά
def scan_global_markets():
    found = []
    for t in WATCHLIST:
        try:
            ticker = yf.Ticker(t)
            hist = ticker.history(period="1mo")
            if hist.empty: continue
            
            # Υπολογισμός RSI (Τεχνικό Σήμα)
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (gain.iloc[-1]/loss.iloc[-1]))) if loss.iloc[-1] != 0 else 100
            
            # Ακριβή Στοιχεία Προϊόντος
            full_name = ticker.info.get('longName', t)
            isin = ticker.info.get('isin', 'N/A')
            price = ticker.fast_info.last_price
            
            # Κριτήριο Ευκαιρίας (RSI < 45)
            if rsi < 45:
                # Link για Revolut (Ανοίγει την αναζήτηση με το σύμβολο)
                rev_link = f"https://revolut.me{t}" 
                found.append({
                    "Προϊόν": full_name,
                    "Σύμβολο": t,
                    "ISIN": isin,
                    "Τιμή": f"{price:.2f}$",
                    "RSI": round(rsi, 1),
                    "Link": rev_link
                })
        except: continue
    return found

# --- UI ΕΚΤΕΛΕΣΗ ---
st.set_page_config(page_title="AI Market Sentinel 2026", layout="wide")
st.title("🛰️ AI Market Sentinel: Αυτόματη Σάρωση (30')")

# Αυτόματη εκτέλεση κάθε φορά που ανοίγει η σελίδα ή μέσω του GitHub Action
results = scan_global_markets()

if results:
    st.subheader(f"🎯 Ευκαιρίες που εντοπίστηκαν στις {datetime.now().strftime('%H:%M')}")
    for item in results:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{item['Προϊόν']}** ({item['Σύμβολο']})")
                st.caption(f"ISIN: {item['ISIN']} | RSI: {item['RSI']}")
            with col2:
                # Κουμπί για αγορά
                st.link_button("ΑΓΟΡΑ (Revolut)", item['Link'])
    
    # Ειδοποίηση Telegram (Μόνο αν βρεθεί νέα ευκαιρία)
    if st.button("📢 Χειροκίνητη Αποστολή στο Telegram"):
        msg = f"*Νέα Ευκαιρία 2026:*\n{results[0]['Προϊόν']}\nΤιμή: {results[0]['Τιμή']}\n[Αγορά στη Revolut]({results[0]['Link']})"
        send_telegram(msg)
else:
    st.info("Η αγορά σαρώνεται... Δεν υπάρχουν έντονα σήματα αγοράς αυτή τη στιγμή.")

# Εναλλακτικά Προϊόντα (PeerBerry)
st.sidebar.subheader("🏛️ Εναλλακτικές Προτάσεις")
st.sidebar.write("**PeerBerry P2P**")
st.sidebar.write("Απόδοση: 9-12% (Σταθερό)")
st.sidebar.link_button("Άνοιγμα PeerBerry", "https://peerberry.com")
