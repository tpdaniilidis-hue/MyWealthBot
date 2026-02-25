import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests

# --- ΡΥΘΜΙΣΕΙΣ TELEGRAM (Βάλε τους κωδικούς σου εδώ) ---
TOKEN = "7854097442:AAEGZTQ4bRZ2TttL1sLR4DhP_Xly8yGxMpQ"
CHAT_ID = "5943916637"

def send_telegram(msg):
    url = f"https://api.telegram.org{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
    try: requests.get(url, timeout=5)
    except: pass

# --- ΛΕΙΤΟΥΡΓΙΑ CACHE (Λύνει το πρόβλημα Rate Limit) ---
@st.cache_data(ttl=600) # Κρατάει τα δεδομένα για 10 λεπτά στη μνήμη
def get_data(symbol):
    ticker_obj = yf.Ticker(symbol)
    hist = ticker_obj.history(period="1y")
    info = ticker_obj.info
    return hist, info

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="AI Wealth Mentor 2026", layout="wide")
st.title("🏛️ AI Wealth Mentor & Simulator (v2.0)")

# --- INITIAL STATE ---
if 'balance' not in st.session_state:
    st.session_state.balance = 10000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

# --- SIDEBAR & ΑΝΑΖΗΤΗΣΗ ---
st.sidebar.header("🔍 Live Market Scan")
ticker = st.sidebar.text_input("Σύμβολο (π.χ. NVDA, AAPL, BTC-USD):", "NVDA").upper()

# --- ΚΥΡΙΑ ΑΝΑΛΥΣΗ ---
try:
    hist, info = get_data(ticker)
    
    if not hist.empty:
        price = info.get('currentPrice', hist['Close'].iloc[-1])
        
        # Τεχνική Ανάλυση (RSI)
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]
        
        # Θεμελιώδη (Debt/Equity)
        debt = info.get('debtToEquity', 0)

        # 1. ΠΡΟΤΑΣΗ & ΡΙΣΚΟ
        st.header(f"📊 Ανάλυση για την {ticker}")
        is_safe = rsi < 70 and debt < 150
        risk_level = "ΧΑΜΗΛΟ" if is_safe else "ΥΨΗΛΟ"

        col1, col2 = st.columns(2)
        with col1:
            if is_safe:
                st.success(f"🎯 ΠΡΟΤΑΣΗ: ΑΓΟΡΑ / ΔΙΑΤΗΡΗΣΗ (Ρίσκο: {risk_level})")
                advice = "Η μετοχή φαίνεται υγιής και σε καλή τιμή."
            else:
                st.warning(f"⚠️ ΠΡΟΤΑΣΗ: ΑΠΟΦΥΓΗ (Ρίσκο: {risk_level})")
                advice = "Προσοχή! Η τιμή είναι 'φουσκωμένη' ή το χρέος είναι μεγάλο."
            
            st.write(f"**RSI:** {rsi:.1f} | **Debt/Equity:** {debt:.1f}")

        with col2:
            st.metric("Τρέχουσα Τιμή", f"{price:.2f} $")
            if st.button("📢 Αποστολή Alert στο Telegram"):
                send_telegram(f"Ανάλυση {ticker}: {advice} Τιμή: {price}$")
                st.toast("Ειδοποίηση εστάλη!")

        # 2. ΕΚΠΑΙΔΕΥΤΙΚΟDeep Dive
        with st.expander("📖 Γιατί αυτή η πρόταση; (Αναλυτική Εξήγηση)"):
            st.subheader("Γιατί κινείται η τιμή;")
            if rsi < 40:
                st.write("**RSI Χαμηλός:** Η μετοχή θεωρείται 'φθηνή'. Οι επενδυτές αναμένεται να αγοράσουν σύντομα.")
            elif rsi > 70:
                st.write("**RSI Υψηλός:** Η μετοχή είναι 'ακριβή'. Υπάρχει κίνδυνος οι επενδυτές να αρχίσουν να πουλάνε για να πάρουν τα κέρδη τους.")
            
            st.subheader("Οικονομική Υγεία")
            if debt < 100:
                st.write("**Χαμηλό Χρέος:** Η εταιρεία είναι σταθερή. Το 2026, αυτό είναι κρίσιμο λόγω των επιτοκίων.")
            else:
                st.write("**Υψηλό Χρέος:** Η εταιρεία δανείζεται πολύ, κάτι που μπορεί να ρίξει την τιμή της στο μέλλον.")

        # 3. ΔΡΑΣΗ & ΕΝΑΛΛΑΚΤΙΚΕΣ
        st.divider()
        st.subheader("🔗 Επενδυτικά Προϊόντα")
        c1, c2 = st.columns(2)
        c1.markdown(f'<a href="revolut://app/wealth" target="_blank"><button style="width:100%; height:50px; border-radius:10px; background-color:#0075eb; color:white; font-weight:bold; border:none; cursor:pointer;">ΕΠΕΝΔΥΣΗ ΣΤΗ REVOLUT</button></a>', unsafe_allow_html=True)
        c2.markdown(f'<a href="https://peerberry.com" target="_blank"><button style="width:100%; height:50px; border-radius:10px; background-color:#2ecc71; color:white; font-weight:bold; border:none; cursor:pointer;">ΕΝΑΛΛΑΚΤΙΚΗ ΣΤΗΝ PEERBERRY</button></a>', unsafe_allow_html=True)

        # 4. SIMULATION
        st.divider()
        st.subheader("🎮 Simulation Trading (Εικονικά)")
        qty = st.number_input("Ποσότητα μετοχών:", min_value=1, step=1)
        if st.button("Εικονική Αγορά"):
            cost = qty * price
            if st.session_state.balance >= cost:
                st.session_state.balance -= cost
                st.session_state.portfolio[ticker] = st.session_state.portfolio.get(ticker, 0) + qty
                st.success("Επιτυχής αγορά στο Simulation!")
            else: st.error("Δεν έχεις αρκετό εικονικό υπόλοιπο!")

        st.sidebar.metric("Εικονικό Κεφάλαιο", f"{st.session_state.balance:.2f} $")
        st.sidebar.write("📦 Πορτοφόλι:", st.session_state.portfolio)
        st.line_chart(hist['Close'])

    else:
        st.error("Το σύμβολο δεν βρέθηκε. Δοκιμάστε ξανά.")

except Exception as e:
    st.error(f"Παρουσιάστηκε πρόβλημα (Rate Limit ή Σύνδεση). Περιμένετε 5 λεπτά και δοκιμάστε ξανά. Σφάλμα: {e}")
