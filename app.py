import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- ΡΥΘΜΙΣΕΙΣ TELEGRAM ---
# Αντικατάστησε τα κενά μέσα στα εισαγωγικά με τους κωδικούς σου
TOKEN = "7854097442:AAEGZTQ4bRZ2TttL1sLR4DhP_Xly8yGxMpQ"
CHAT_ID = "5943916637"

def send_telegram(message):
    url = f"https://api.telegram.org{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try: requests.get(url)
    except: pass

st.set_page_config(page_title="AI Wealth Mentor", layout="wide")
st.title("🏛️ AI Wealth Mentor & Simulator")

# --- INITIAL STATE ---
if 'balance' not in st.session_state:
    st.session_state.balance = 10000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

# --- SIDEBAR ---
ticker = st.sidebar.text_input("Αναζήτηση Μετοχής:", "NVDA").upper()
stock = yf.Ticker(ticker)

# --- ΚΥΡΙΑ ΑΝΑΛΥΣΗ ---
try:
    data = stock.history(period="1y")
    if not data.empty:
        info = stock.info
        price = info.get('currentPrice', data['Close'].iloc[-1])
        
        # Υπολογισμός RSI (Τεχνική Ανάλυση)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
        
        # Θεμελιώδη (Fundamental)
        debt = info.get('debtToEquity', 0)

        # ΠΡΟΤΑΣΗ
        st.header(f"Ανάλυση για {ticker}")
        is_safe = rsi < 70 and debt < 150
        
        col1, col2 = st.columns(2)
        with col1:
            if is_safe:
                st.success("🎯 ΠΡΟΤΑΣΗ: ΑΓΟΡΑ / ΔΙΑΤΗΡΗΣΗ")
                msg = f"Η {ticker} είναι σε καλό σημείο."
            else:
                st.warning("⚠️ ΠΡΟΤΑΣΗ: ΥΨΗΛΟ ΡΙΣΚΟ")
                msg = f"Προσοχή στην {ticker}!"
            st.write(f"RSI: {rsi:.1f} | Χρέος: {debt:.1f}")
            
        with col2:
            st.metric("Τιμή", f"{price:.2f} $")
            if st.button("📢 Ειδοποίηση στο Telegram"):
                send_telegram(f"{ticker}: {msg} Τιμή: {price}$")

        # ΕΚΠΑΙΔΕΥΣΗ
        with st.expander("📖 Γιατί αυτή η πρόταση;"):
            st.write("Ο RSI δείχνει αν η μετοχή είναι 'ακριβή' ή 'φθηνή'.")
            st.write("Το Χρέος δείχνει αν η εταιρεία κινδυνεύει από τα επιτόκια του 2026.")

        # SIMULATION
        st.divider()
        st.subheader("🎮 Simulation Trading")
        qty = st.number_input("Ποσότητα:", min_value=1)
        if st.button("Εικονική Αγορά"):
            cost = qty * price
            if st.session_state.balance >= cost:
                st.session_state.balance -= cost
                st.session_state.portfolio[ticker] = st.session_state.portfolio.get(ticker, 0) + qty
                st.success("Επιτυχής αγορά στο simulation!")
            else: st.error("Δεν έχεις αρκετά εικονικά χρήματα.")

        st.sidebar.metric("Υπόλοιπο", f"{st.session_state.balance:.2f} $")
        st.sidebar.write("📦 Πορτοφόλι:", st.session_state.portfolio)
        st.line_chart(data['Close'])
    else:
        st.error("Το σύμβολο δεν βρέθηκε.")
except Exception as e:
    st.error(f"Σφάλμα: {e}")
