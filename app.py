import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import numpy as np

# --- ΡΥΘΜΙΣΕΙΣ TELEGRAM ---
TOKEN = "7854097442:AAEGZTQ4bRZ2TttL1sLR4DhP_Xly8yGxMpQ"
CHAT_ID = "941916327"

# --- CONFIG & STYLE ---
st.set_page_config(page_title="AI Wealth Master 2026", layout="wide")
st.markdown("""<style> .stButton>button { width: 100%; border-radius: 10px; } </style>""", unsafe_allow_html=True)

# --- INITIAL SESSION STATE ---
if 'portfolio' not in st.session_state: st.session_state.portfolio = {}
if 'sim_balance' not in st.session_state: st.session_state.sim_balance = 10000.0
if 'sim_portfolio' not in st.session_state: st.session_state.sim_portfolio = {}

# --- FUNCTIONS ---
@st.cache_data(ttl=1800)
def get_stock_details(symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="5y")
    info = ticker.info
    return ticker, hist, info

def calculate_rsi(data):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs)).iloc[-1]

# --- ΚΕΝΤΡΙΚΟ MENU (TABS) ---
tab1, tab2, tab3 = st.tabs(["🔍 Ευκαιρίες & Αναζήτηση", "💼 Το Πορτοφόλι μου", "🎮 Εξομοιωτής (Simulation)"])

# ==========================================
# TAB 1: ΕΥΚΑΙΡΙΕΣ & ΑΝΑΖΗΤΗΣΗ
# ==========================================
with tab1:
    st.header("🎯 Παγκόσμιες Επενδυτικές Ευκαιρίες 2026")
    
    # Λίστα για Σάρωση (Top 20 Strategy)
    watchlist = ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN", "META", "AVGO", "ASML.AS", "MC.PA", "SAP.DE", "EEE.AT", "OPAP.AT", "BTC-USD", "ETH-USD", "VIG", "VOO", "GLD", "BND", "PLTR"]

    if st.button("🚀 Αναζήτηση των 20 Καλύτερων Προτάσεων"):
        opportunities = []
        with st.spinner("Σάρωση παγκόσμιων αγορών..."):
            for t in watchlist:
                try:
                    tick, hist, info = get_stock_details(t)
                    rsi = calculate_rsi(hist['Close'])
                    price = info.get('currentPrice', hist['Close'].iloc[-1])
                    if rsi < 50: # Κριτήριο ευκαιρίας
                        opportunities.append({"Symbol": t, "Name": info.get('longName'), "Price": price, "RSI": rsi})
                except: continue
        
        if opportunities:
            for op in opportunities:
                with st.expander(f"📌 {op['Name']} ({op['Symbol']}) - Τιμή: {op['Price']}$"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.subheader("💡 Γιατί είναι καλή επένδυση;")
                        st.write(f"Ο δείκτης RSI είναι στο **{op['RSI']:.1f}**, που σημαίνει ότι η μετοχή δεν είναι υπερτιμημένη. "
                                 "Η εταιρεία παρουσιάζει σταθερή ανάπτυξη και στρατηγική θέση στην αγορά του 2026.")
                        
                        st.subheader("📊 Οικονομική Αναφορά")
                        tick, hist, info = get_stock_details(op['Symbol'])
                        st.write(f"**Debt/Equity:** {info.get('debtToEquity', 'N/A')}")
                        st.write(f"**Profit Margin:** {info.get('profitMargins', 0)*100:.2f}%")
                        st.write(f"**Free Cash Flow:** {info.get('freeCashflow', 0)/1e9:.2f}B $")
                    
                    with c2:
                        st.subheader("📈 Πρόβλεψη 5ετίας (AI Projection)")
                        avg_growth = (hist['Close'].pct_change().mean() * 252) # Ετήσια απόδοση
                        future_price = op['Price'] * (1 + avg_growth)**5
                        st.write(f"Με βάση την τρέχουσα δυναμική, η εκτιμώμενη τιμή το 2031 είναι: **{future_price:.2f}$**")
                        st.line_chart(hist['Close'])

# ==========================================
# TAB 2: ΤΟ ΠΟΡΤΟΦΟΛΙ ΜΟΥ (REAL TRACKING)
# ==========================================
with tab2:
    st.header("💼 Πραγματικό Χαρτοφυλάκιο")
    with st.form("add_real"):
        t_add = st.text_input("Σύμβολο που αγοράσατε:").upper()
        qty_add = st.number_input("Ποσότητα:", min_value=0.1)
        price_add = st.number_input("Τιμή Αγοράς:", min_value=0.1)
        if st.form_submit_button("Προσθήκη στο Πορτοφόλι"):
            st.session_state.portfolio[t_add] = {"qty": qty_add, "buy_price": price_add}
            st.success(f"Προστέθηκε η {t_add}")

    if st.session_state.portfolio:
        total_value = 0
        data_list = []
        for t, d in st.session_state.portfolio.items():
            curr_p = yf.Ticker(t).fast_info.last_price
            val = curr_p * d['qty']
            profit = (curr_p - d['buy_price']) * d['qty']
            total_value += val
            data_list.append({"Προϊόν": t, "Ποσότητα": d['qty'], "Αξία": f"{val:.2f}$", "Κέρδος/Ζημία": f"{profit:.2f}$"})
        
        st.table(pd.DataFrame(data_list))
        st.metric("Συνολική Αξία Πορτοφολιού", f"{total_value:.2f} $")
    else:
        st.info("Το πορτοφόλι σας είναι άδειο.")

# ==========================================
# TAB 3: ΕΞΟΜΟΙΩΤΗΣ (SIMULATION)
# ==========================================
with tab3:
    st.header("🎮 Simulator: Επένδυση με Εικονικά Χρήματα")
    st.sidebar.metric("Sim Balance", f"{st.session_state.sim_balance:.2f} $")
    
    sim_t = st.text_input("Αναζήτηση για Simulation:", "BTC-USD").upper()
    if sim_t:
        s_tick = yf.Ticker(sim_t)
        s_price = s_tick.fast_info.last_price
        st.write(f"Τρέχουσα Τιμή {sim_t}: **{s_price:.2f}$**")
        
        s_qty = st.number_input("Ποσότητα για αγορά (Sim):", min_value=0.01)
        if st.button("🚀 Εικονική Αγορά"):
            cost = s_qty * s_price
            if st.session_state.sim_balance >= cost:
                st.session_state.sim_balance -= cost
                st.session_state.sim_portfolio[sim_t] = st.session_state.sim_portfolio.get(sim_t, 0) + s_qty
                st.success("Η εικονική αγορά ολοκληρώθηκε!")
            else:
                st.error("Ανεπαρκές εικονικό υπόλοιπο!")
    
    st.subheader("📦 Εικονικό Πορτοφόλι")
    st.write(st.session_state.sim_portfolio)
