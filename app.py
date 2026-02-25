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

# --- ΠΑΓΚΟΣΜΙΑ ΛΙΣΤΑ ΣΑΡΩΣΗΣ (GLOBAL ASSETS 2026) ---
GLOBAL_WATCHLIST = {
    "Technology (USA)": ["NVDA", "PLTR", "TSLA", "AMD", "META"],
    "Europe Blue Chips": ["ASML.AS", "MC.PA", "SAP.DE", "SIE.DE"],
    "Safe Havens (ETFs/Gold)": ["GLD", "SLV", "VOO", "VWCE.DE"],
    "Fixed Income (Bonds)": ["BND", "TLT", "IBHF"], # iBonds 2026
    "Emerging Markets": ["EEM", "BABA", "RELIANCE.NS"],
    "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD"]
}

@st.cache_data(ttl=3600)
def fetch_opportunity(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        if hist.empty: return None
        
        # Υπολογισμός RSI (Τεχνική Ευκαιρία)
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1]/loss.iloc[-1]))) if loss.iloc[-1] != 0 else 100
        
        price = float(stock.fast_info.last_price)
        
        # ΦΙΛΤΡΟ ΕΥΚΑΙΡΙΑΣ: Εμφάνιση μόνο αν RSI < 45 (Υποτιμημένο)
        if rsi < 45:
            return {"Προϊόν": ticker, "Τιμή": f"{price:.2f}$", "RSI": round(rsi, 1), "Σήμα": "🔥 ΑΓΟΡΑ"}
        return None
    except: return None

# --- UI ΕΦΑΡΜΟΓΗΣ ---
st.set_page_config(page_title="Global Opportunity Hunter", layout="wide")
st.title("🌍 Global Opportunity Hunter 2026")
st.write(f"Ανάλυση Παγκόσμιας Αγοράς: {pd.Timestamp.now().strftime('%d/%m/%Y')}")

# ΚΟΥΜΠΙ ΣΑΡΩΣΗΣ
if st.button("🔍 Εντοπισμός Παγκόσμιων Ευκαιριών"):
    opportunities = []
    with st.spinner("Σάρωση Χρηματιστηρίων ΗΠΑ, Ευρώπης, Ασίας και Crypto..."):
        for category, tickers in GLOBAL_WATCHLIST.items():
            for t in tickers:
                result = fetch_opportunity(t)
                if result:
                    result["Κατηγορία"] = category
                    opportunities.append(result)
    
    if opportunities:
        st.subheader("🎯 Κορυφαίες Ευκαιρίες για Επένδυση Τώρα")
        df = pd.DataFrame(opportunities)
        st.table(df)
        
        # Ειδοποίηση Telegram
        best_pick = df.iloc[0]['Προϊόν']
        send_telegram(f"📢 ΝΕΑ ΠΑΓΚΟΣΜΙΑ ΕΥΚΑΙΡΙΑ: Η επένδυση στο {best_pick} πληροί τα κριτήρια αγοράς σήμερα!")
    else:
        st.info("Δεν βρέθηκαν έντονες ευκαιρίες (RSI < 45) αυτή τη στιγμή. Η παγκόσμια αγορά φαίνεται δίκαια αποτιμημένη.")

# ΕΠΕΝΔΥΤΙΚΗ ΔΙΔΑΣΚΑΛΙΑ
st.divider()
with st.expander("📖 Γιατί βλέπω μόνο αυτές τις προτάσεις;"):
    st.write("""
    Η εφαρμογή χρησιμοποιεί το **RSI (Relative Strength Index)** ως κύριο φίλτρο. 
    1. **RSI < 45:** Η επένδυση θεωρείται 'υποτιμημένη' ή σε φάση διόρθωσης. Είναι η στιγμή που οι 'έξυπνοι' επενδυτές αγοράζουν φθηνά.
    2. **Απουσία Μετοχών:** Αν μια μετοχή (π.χ. NVIDIA) λείπει από τη λίστα, σημαίνει ότι ο RSI της είναι υψηλός (>50), άρα θεωρείται ακριβή για είσοδο αυτή τη στιγμή.
    3. **Διασπορά:** Σαρώνουμε από Αμερικανική Τεχνολογία μέχρι Ευρωπαϊκά Luxury Brands και Crypto για να έχεις επιλογές σε κάθε τομέα.
    """)

# ΕΝΑΛΛΑΚΤΙΚΕΣ (PEERBERRY / BONDS)
st.sidebar.header("🛡️ Εναλλακτική Ασφάλεια")
st.sidebar.write("**PeerBerry P2P:** Απόδοση 9-12% (Σταθερό)")
st.sidebar.write("**US Bonds (BND):** Απόδοση ~4.05%")
st.sidebar.markdown('[Άνοιγμα PeerBerry](https://peerberry.com)')
