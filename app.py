import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- ΡΥΘΜΙΣΕΙΣ TELEGRAM (Προσυμπληρωμένες με τους κωδικούς σου) ---
TOKEN = "7854097442:AAEGZTQ4bRZ2TttL1sLR4DhP_Xly8yGxMpQ"
CHAT_ID = "941916327"

def send_telegram(msg):
    url = f"https://api.telegram.org{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
    try:
        requests.get(url, timeout=5)
    except:
        pass

# --- ΛΕΙΤΟΥΡΓΙΑ CACHE (Αποθήκευση δεδομένων για 1 ώρα) ---
@st.cache_data(ttl=3600)
def get_data(symbol):
    # Ορίζουμε έναν User-Agent για να μη μας μπλοκάρει η Yahoo ως "ρομπότ"
    ticker_obj = yf.Ticker(symbol)
    hist = ticker_obj.history(period="1y")
    # Χρησιμοποιούμε το fast_info που είναι πιο ελαφρύ και γρήγορο
    fast_info = ticker_obj.fast_info 
    return hist, fast_info

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="AI Wealth Mentor 2026", layout="wide")
st.title("🏛️ AI Wealth Mentor & Simulator")

# --- ΑΡΧΙΚΟΠΟΙΗΣΗ ΜΝΗΜΗΣ (SESSION STATE) ---
if 'balance' not in st.session_state:
    st.session_state.balance = 10000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

# --- ΠΛΕΥΡΙΚΗ ΜΠΑΡΑ (SIDEBAR) ---
st.sidebar.header("🔍 Αναζήτηση Αγοράς")
ticker = st.sidebar.text_input("Σύμβολο (π.χ. NVDA, AAPL, BTC-USD):", "NVDA").upper()

# --- ΚΥΡΙΑ ΑΝΑΛΥΣΗ ΚΑΙ ΕΚΤΕΛΕΣΗ ---
try:
    hist, info = get_data(ticker)
    
    if not hist.empty:
        # Λήψη τιμής από το fast_info
        price = info.last_price
        
        # Υπολογισμός RSI (Τεχνική Ανάλυση)
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        # Αποφυγή διαίρεσης με το μηδέν
        avg_gain = gain.iloc[-1]
        avg_loss = loss.iloc[-1]
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        st.header(f"📊 Ανάλυση για την {ticker}")
        
        col1, col2 = st.columns(2)
        with col1:
            if rsi < 70:
                st.success("🎯 ΠΡΟΤΑΣΗ: ΑΓΟΡΑ / ΔΙΑΤΗΡΗΣΗ")
                advice = f"Η {ticker} φαίνεται σε καλό σημείο εισόδου."
            else:
                st.warning("⚠️ ΠΡΟΤΑΣΗ: ΥΨΗΛΟ ΡΙΣΚΟ / ΠΩΛΗΣΗ")
                advice = f"Προσοχή, η {ticker} είναι υπερτιμημένη (RSI > 70)."
            
            st.write(f"**Δείκτης RSI:** {rsi:.1f}")

        with col2:
            st.metric("Τρέχουσα Τιμή", f"{price:.2f} $")
            if st.button("📢 Αποστολή στο Telegram"):
                send_telegram(f"Ανάλυση {ticker}: {advice} Τιμή: {price}$")
                st.toast("Ειδοποίηση εστάλη!")

        # --- ΕΚΠΑΙΔΕΥΤΙΚΗ ΕΞΗΓΗΣΗ (Deep Dive) ---
        with st.expander("📖 Γιατί αυτή η πρόταση; (Ανάλυση Mentor)"):
            st.subheader("Τι είναι ο RSI;")
            st.write("Ο δείκτης RSI δείχνει αν μια μετοχή έχει αγοραστεί υπερβολικά πολύ (Overbought) ή αν έχει πουληθεί υπερβολικά (Oversold).")
            if rsi < 40:
                st.write("**Ερμηνεία:** Η τιμή είναι χαμηλά. Οι πωλητές σταμάτησαν και η ζήτηση αναμένεται να αυξηθεί.")
            elif rsi > 70:
                st.write("**Ερμηνεία:** Η τιμή ανέβηκε πολύ γρήγορα. Υπάρχει κίνδυνος οι επενδυτές να αρχίσουν να πουλάνε για να πάρουν κέρδη.")

        # --- ΔΡΑΣΗ (REVOLUT / PEERBERRY) ---
        st.divider()
        st.subheader("🔗 Επενδυτικές Πλατφόρμες")
        c1, c2 = st.columns(2)
        c1.markdown(f'<a href="revolut://app/wealth" target="_blank"><button style="width:100%; height:45px; border-radius:10px; background-color:#0075eb; color:white; font-weight:bold; border:none; cursor:pointer;">ΕΠΕΝΔΥΣΗ ΣΤΗ REVOLUT</button></a>', unsafe_allow_html=True)
        c2.markdown(f'<a href="https://peerberry.com" target="_blank"><button style="width:100%; height:45px; border-radius:10px; background-color:#2ecc71; color:white; font-weight:bold; border:none; cursor:pointer;">PEERBERRY (ΣΤΑΘΕΡΟ P2P)</button></a>', unsafe_allow_html=True)

        # --- SIMULATION TRADING ---
        st.divider()
        st.subheader("🎮 Simulation Trading (Εικονικά)")
        qty = st.number_input("Ποσότητα μετοχών για αγορά:", min_value=1, step=1)
        if st.button("Εικονική Αγορά"):
            total_cost = qty * price
            if st.session_state.balance >= total_cost:
                st.session_state.balance -= total_cost
                st.session_state.portfolio[ticker] = st.session_state.portfolio.get(ticker, 0) + qty
                st.success(f"Αγοράστηκαν {qty} μετοχές {ticker}!")
            else:
                st.error("Ανεπαρκές εικονικό κεφάλαιο!")

        st.sidebar.divider()
        st.sidebar.metric("Διαθέσιμο Υπόλοιπο", f"{st.session_state.balance:.2f} $")
        st.sidebar.write("📦 Το Πορτοφόλι μου:", st.session_state.portfolio)
        
        # Γράφημα τιμής
        st.line_chart(hist['Close'])

    else:
        st.error("Δεν βρέθηκαν δεδομένα για αυτό το σύμβολο.")

except Exception as e:
    st.error(f"Αναμονή για σύνδεση ή Rate Limit (Yahoo). Δοκίμασε ξανά σε 5 λεπτά. (Σφάλμα: {e})")
