import io
import streamlit as st
import pandas as pd
from engine import make_demo_data, evaluate, size_position, STOCKS

st.set_page_config(page_title="Nifty Signal Studio | Demo", page_icon="📈", layout="wide")
st.markdown("""<style>.block-container{padding-top:1.7rem;max-width:1170px}h1{letter-spacing:-.03em}.stMetric{background:#f4f7fc;padding:14px;border-radius:12px}</style>""", unsafe_allow_html=True)
st.title("📈 Nifty Signal Studio")
st.caption("Practice dashboard • Synthetic prices only • No broker connection • No real recommendations")
st.warning("DEMO DATA ONLY: All prices, trends and signals are artificially generated. Do not use these results to place real trades.")

with st.sidebar:
    st.header("Your dashboard")
    screen = st.radio("Choose a page", ["Stock scanner", "Stock details", "Risk calculator", "About this demo"])
    st.divider()
    st.info("Manual trading only. This website never accesses Groww or places orders.")

@st.cache_data

def data():
    return make_demo_data()

raw = data()
report, history = evaluate(raw)

if screen == "Stock scanner":
    st.subheader("Daily signal scanner")
    a, b, c = st.columns(3)
    a.metric("Sample stocks scanned", len(report))
    b.metric("Buy candidates", int((report.signal == "BUY CANDIDATE").sum()))
    c.metric("Waiting", int((report.signal == "WAIT").sum()))
    st.caption("Example historical-data cutoff: " + report.date.iloc[0] + " (not live)")
    selected_filter = st.selectbox("Show signals", ["All", "BUY CANDIDATE", "WAIT"])
    filtered = report if selected_filter == "All" else report[report.signal == selected_filter]
    st.dataframe(filtered[["symbol", "date", "close", "signal", "score", "rsi14"]].rename(columns={"symbol":"Stock", "date":"Date", "close":"Demo price (₹)", "signal":"Signal", "score":"Criteria score / 100", "rsi14":"RSI"}), use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download signal report (opens in Excel)", data=report.to_csv(index=False).encode("utf-8-sig"), file_name="DEMO_stock_signals.csv", mime="text/csv")
    st.info("BUY CANDIDATE means all five illustrative technical conditions passed. It is not a trade recommendation or a predicted probability of profit.")

elif screen == "Stock details":
    st.subheader("Understand an individual stock")
    symbol = st.selectbox("Choose sample stock", STOCKS)
    row = report.set_index("symbol").loc[symbol]
    price = history[symbol]
    st.line_chart(price.set_index("date")[["close", "sma50", "sma200"]].rename(columns={"close":"Demo close", "sma50":"50-day average", "sma200":"200-day average"}))
    st.write(f"**Example signal:** {row['signal']}  |  **Rules passed:** {row['score']}/100  |  **RSI:** {row['rsi14']}")
    st.subheader("Why did the scanner give this signal?")
    for part in row["reason"].split("; "):
        st.write(("✅ " if part.endswith("pass") else "⚪ ") + part)
    st.caption("These explanations come directly from the mathematical strategy, not from a paid AI model. A future version can add optional ChatGPT or Claude summaries.")

elif screen == "Risk calculator":
    st.subheader("Calculate a sample position size")
    st.write("Enter your hypothetical numbers. The calculator limits position size using both a risk budget and a 20% capital-allocation cap.")
    a, b = st.columns(2)
    capital = a.number_input("Trading capital (₹)", min_value=1000., value=100000., step=1000.)
    risk = b.select_slider("Risk per trade (%)", options=[0.25, 0.5, 0.75, 1.0, 1.5, 2.0], value=0.5)
    entry = a.number_input("Example entry price (₹)", min_value=1., value=1000., step=10.)
    stop = b.number_input("Example stop-loss price (₹)", min_value=0., value=970., step=10.)
    result = size_position(capital, risk, entry, stop)
    if result is None:
        st.error("Stop-loss must be below entry price.")
    else:
        x,y,z = st.columns(3)
        x.metric("Maximum shares", result["shares"])
        y.metric("Planned investment", f"₹{result['investment']:,.0f}")
        z.metric("Planned loss at stop", f"₹{result['planned_loss']:,.0f}")
        st.caption(f"Risk budget: ₹{result['risk_budget']:,.0f}. Actual losses can be higher because of gaps, slippage and costs.")

else:
    st.subheader("What this free website does")
    st.write("1. Generates reproducible artificial daily price histories for 15 sample NSE tickers.")
    st.write("2. Applies moving average, RSI, volume and breakout rules.")
    st.write("3. Displays rule explanations and offers a CSV report for Excel.")
    st.write("4. Calculates example risk-based position size.")
    st.write("**What it does not do:** fetch real NSE prices, connect Groww, place orders, predict returns, or call paid AI APIs.")
    st.write("**Future phase:** user-approved licensed historical data, full current Nifty 50 membership, backtesting, optional AI API, and scheduled alerts.")
