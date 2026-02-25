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

# --- ΛΙΣΤΑ ΠΡΟΪΟΝΤΩΝ 2026 (Stocks, ETFs, Crypto, Bonds) ---
ASSET_LIST = {
    "AI Tech (Stocks)": ["NVDA", "PLTR", "MSFT", "AMZN"],
    "Dividends (Stocks)": ["SCL", "GRC", "VIG", "VYM"],
    "Global & Safe (ETFs)": ["VOO", "VWCE.DE", "GLD"],
    "Bonds (Fixed Income)": ["BND", "IBHF", "TLT"],
    "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD"]
}

@st.cache_data(ttl=3600)
def get_asset_data(ticker):
    try:
        obj = yf.Ticker(ticker)
        hist = obj.history(period="1y")
        price = float(obj.fast_info.last_price)
        # Τεχνική Ανάλυση RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1]/loss.iloc[-1]))) if loss.iloc[-1] != 0 else 100
        return {"price": price, "rsi": rsi, "change": ((price - hist['Close'].iloc[0])/hist['Close'].iloc[0])*100}
    except: return None

# --- UI ΕΦΑΡΜΟΓΗΣ ---
st.set_page_config(page_title="AI Wealth Hub 2026", layout="wide")
st.title("💰 AI Wealth Hub: Ολοκληρωμένες Προτάσεις 2026")

# 1. ΑΥΤΟΜΑΤΟ SCANNER
st.header("🔍 Market Scanner: Οι Καλύτερες Προτάσεις Τώρα")
if st.button("🚀 Σάρωση Όλων των Επενδυτικών Προϊόντων"):
    all_recommendations = []
    for category, tickers in ASSET_LIST.items():
        for t in tickers:
            data = get_asset_data(t)
            if data:
                status = "🔥 ΕΥΚΑΙΡΙΑ" if data['rsi'] < 45 else "⚖️ HOLD"
                if data['rsi'] > 70: status = "⚠️ OVERBOUGHT"
                all_recommendations.append({"Κατηγορία": category, "Προϊόν": t, "Τιμή": f"{data['price']:.2f}$", "RSI": f"{data['rsi']:.1f}", "Απόδοση 1Y": f"{data['change']:.1f}%", "Σήμα": status})
    
    df = pd.DataFrame(all_recommendations)
    st.dataframe(df.style.highlight_max(subset=['Σήμα'], color='#2ecc71'), use_container_width=True)

# 2. ΕΝΑΛΛΑΚΤΙΚΕΣ ΠΡΟΤΑΣΕΙΣ (Peerberry & P2P)
st.divider()
st.header("🏛️ Εναλλακτικό Πορτοφόλι (Εκτός Χρηματιστηρίου)")
col1, col2 = st.columns(2)
with col1:
    st.subheader("PeerBerry (P2P Lending)")
    st.write("Αναμενόμενη Απόδοση: **9% - 12%**")
    st.info("Ιδανικό για σταθερό εισόδημα όταν οι μετοχές έχουν υψηλό ρίσκο.")
    st.markdown('[🔗 Άνοιγμα PeerBerry](https://peerberry.com)', unsafe_allow_html=True)
with col2:
    st.subheader("Κρατικά Ομόλογα (Bonds)")
    st.write("Απόδοση 10ετούς ΗΠΑ: **~4.03%**")
    st.write("Απόδοση Γερμανίας: **~2.70%**")
    st.success("Προτείνεται για προστασία κεφαλαίου το 2026.")

# 3. ΔΥΝΑΜΙΚΟ PORTFOLIO ADVISOR
st.divider()
st.subheader("🤖 AI Advisor: Προτεινόμενη Κατανομή")
market_mood = "BULLISH" # Παράδειγμα
if market_mood == "BULLISH":
    st.write("- **50%** Μετοχές & ETFs (Revolut)")
    st.write("- **30%** Ομόλογα (BND/IBHF)")
    st.write("- **10%** P2P Lending (Peerberry)")
    st.write("- **10%** Crypto (BTC/ETH)")

if st.button("📢 Στείλε το Πλάνο στο Telegram"):
    send_telegram("Το AI Wealth Hub προτείνει: 50% ETFs, 30% Bonds, 20% Alternates.")
    st.toast("Το πλάνο εστάλη!")
