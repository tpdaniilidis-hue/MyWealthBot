importimport streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- ΡΥΘΜΙΣΕΙΣ TELEGRAM ---
TOKEN = "7854097442:AAEGZTQ4bRZ2TttL1sLR4DhP_Xly8yGxMpQ"
CHAT_ID = "941916327"

def send_telegram(msg):
    url = f"https://api.telegram.org{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
    try:
        requests.get(url, timeout=5)
    except:
        pass

# --- ΛΕΙΤΟΥΡΓΙΑ CACHE (Διορθωμένη για το σφάλμα Serialization) ---
@st.cache_data(ttl=3600)
def get_clean_data(symbol):
    ticker_obj = yf.Ticker(symbol)
    # Παίρνουμε το ιστορικό (είναι DataFrame, άρα serializable)
    hist = ticker_obj.history(period="1y")
    
    # Αντί για όλο το info, παίρνουμε μόνο την τελευταία τιμή και το χρέος
    # Τα μετατρέπουμε σε απλούς αριθμούς (float)
    price = float(ticker_obj.fast_info.last_price)
    
    # Προσπαθούμε να πάρουμε το Debt to Equity, αν δεν υπάρχει βάζουμε 0
    try:
        debt = float(ticker_obj.info.get('debtToEquity', 0))
    except:
        debt = 0.0
        
    return hist, price, debt

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="AI Wealth Mentor 2026", layout="wide")
st.title("🏛️ AI Wealth Mentor & Simulator")

# --- INITIAL STATE ---
if 'balance' not in st.session_state:
    st.session_state.balance = 10000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

# --- SIDEBAR ---
ticker = st.sidebar.text_input("Σύμβολο (π.χ. NVDA, AAPL):", "NVDA").upper()

# --- ΚΥΡΙΑ ΑΝΑΛΥΣΗ ---
try:
    hist, price, debt = get_clean_data(ticker)
    
    if not hist.empty:
        # Υπολογισμός RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        avg_gain = gain.iloc[-1]
        avg_loss = loss.iloc[-1]
        rsi = 100 - (100 / (1 + (avg_gain / avg_loss))) if avg_loss != 0 else 100
        
        st.header(f"📊 Ανάλυση για την {ticker}")
        
        col1, col2 = st.columns(2)
        with col1:
            is_safe = rsi < 70 and debt < 150
            if is_safe:
                st.success("🎯 ΠΡΟΤΑΣΗ: ΑΓΟΡΑ / ΔΙΑΤΗΡΗΣΗ")
                advice = "Καλή τιμή και υγιή οικονομικά."
            else:
                st.warning("⚠️ ΠΡΟΤΑΣΗ: ΥΨΗΛΟ ΡΙΣΚΟ")
                advice = "Προσοχή, η μετοχή είναι ακριβή ή υπερδανεισμένη."
            
            st.write(f"**RSI:** {rsi:.1f} | **Debt/Equity:** {debt:.1f}")

        with col2:
            st.metric("Τιμή", f"{price:.2f} $")
            if st.button("📢 Αποστολή στο Telegram"):
                send_telegram(f"Ανάλυση {ticker}: {advice} Τιμή: {price}$")
                st.toast("Εστάλη!")

        # ΕΚΠΑΙΔΕΥΣΗ
        with st.expander("📖 Γιατί αυτή η πρόταση;"):
            st.write(f"**RSI ({rsi:.1f}):** Δείχνει αν η αγορά 'υπερθερμάνθηκε'.")
            st.write(f"**Debt/Equity ({debt:.1f}):** Δείχνει πόσο χρέος έχει η εταιρεία σε σχέση με τα κεφάλαιά της.")

        # LINKS
        st.divider()
        c1, c2 = st.columns(2)
        c1.markdown(f'<a href="revolut://app/wealth" target="_blank"><button style="width:100%; height:40px; background-color:#0075eb; color:white; border:none; border-radius:5px; cursor:pointer;">REVOLUT</button></a>', unsafe_allow_html=True)
        c2.markdown(f'<a href="https://peerberry.com" target="_blank"><button style="width:100%; height:40px; background-color:#2ecc71; color:white; border:none; border-radius:5px; cursor:pointer;">PEERBERRY</button></a>', unsafe_allow_html=True)

        # SIMULATION
        st.divider()
        st.subheader("🎮 Simulation Trading")
        qty = st.number_input("Ποσότητα:", min_value=1, step=1)
        if st.button("Εικονική Αγορά"):
            cost = qty * price
            if st.session_state.balance >= cost:
                st.session_state.balance -= cost
                st.session_state.portfolio[ticker] = st.session_state.portfolio.get(ticker, 0) + qty
                st.success("Αγοράστηκε!")
            else:
                st.error("Ανεπαρκές υπόλοιπο.")

        st.sidebar.metric("Υπόλοιπο", f"{st.session_state.balance:.2f} $")
        st.sidebar.write("📦 Πορτοφόλι:", st.session_state.portfolio)
        st.line_chart(hist['Close'])

except Exception as e:
    st.error(f"Αναμονή για δεδομένα (Yahoo). Περίμενε 2 λεπτά και δοκίμασε ξανά. Σφάλμα: {e}")
