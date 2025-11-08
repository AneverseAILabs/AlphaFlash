import streamlit as st
from yahooquery import search, Ticker
import feedparser
import pandas as pd
import plotly.graph_objects as go

# --- Streamlit Setup ---
st.set_page_config(page_title="💹 Company Insights Dashboard", page_icon="💹", layout="centered")

st.markdown("""
    <h1 style='text-align:center; color:indigo;'>💹 Company Stock & Change Insights</h1>
    <p style='text-align:center; color:blue;'>Interactive stock chart + major company updates — no API key required!</p>
""", unsafe_allow_html=True)

# --- Input ---
company_name = st.text_input("🔍 Enter company name:")

# Broadened keyword set for any impactful change
keywords = [
    "ceo", "chief executive", "leadership", "appointed", "resigns", "steps down", "joins",
    "merger", "acquisition", "partnership", "deal", "agreement",
    "launch", "release", "introduces", "unveils", "product", "service",
    "forecast", "guidance", "earnings", "revenue", "profit", "loss",
    "ipo", "investment", "funding", "valuation",
    "restructure", "layoffs", "expansion", "shutdown", "closing", "bankruptcy"
]

# --- Main Logic ---
if st.button("Get Insights") and company_name.strip():
    company_name = company_name.strip()

    try:
        # Step 1: Find Ticker
        results = search(company_name)
        if not results.get("quotes"):
            st.warning("⚠️ No ticker found for this company.")
        else:
            ticker_info = results["quotes"][0]
            ticker_symbol = ticker_info.get("symbol", "N/A")
            description = ticker_info.get("shortname", company_name)

            st.markdown(f"<h2 style='color:indigo;'>{description}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:blue;'><b>Ticker:</b> {ticker_symbol}</p>", unsafe_allow_html=True)

            # Step 2: Current Price
            stock = Ticker(ticker_symbol)
            price_data = stock.price.get(ticker_symbol, {})
            current_price = price_data.get("regularMarketPrice", "N/A")
            currency = price_data.get("currency", "")
            if current_price != "N/A":
                st.success(f"💰 **Current Price:** {current_price} {currency}")
            else:
                st.info("Stock price not available right now.")

            st.divider()

            # Step 3: Interactive Chart
            st.markdown("<h3 style='color:indigo;'>📈 Interactive Stock Chart</h3>", unsafe_allow_html=True)
            try:
                hist = stock.history(period="max")
                if hist.empty:
                    st.warning("No historical data available.")
                else:
                    hist = hist.reset_index()
                    if "symbol" in hist.columns:
                        hist = hist[hist["symbol"] == ticker_symbol]
                    hist = hist.set_index("date")

                    fig = go.Figure()

                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=hist["close"],
                        mode='lines',
                        name='Closing Price',
                        line=dict(color='blue', width=2)
                    ))

                    latest_price = hist["close"].iloc[-1]
                    latest_date = hist.index[-1]
                    fig.add_trace(go.Scatter(
                        x=[latest_date],
                        y=[latest_price],
                        mode="markers+text",
                        name="Latest",
                        text=[f"{latest_price:.2f}"],
                        textposition="top right",
                        marker=dict(color="red", size=8)
                    ))

                    fig.update_layout(
                        title=f"{ticker_symbol} Stock Price History",
                        title_x=0.5,
                        template="plotly_white",
                        xaxis_title="Date",
                        yaxis_title=f"Price ({currency})",
                        font=dict(color="indigo"),
                        plot_bgcolor="#f8faff",
                        hovermode="x unified",
                        height=400,
                        margin=dict(l=40, r=40, t=60, b=40),
                        xaxis=dict(rangeslider=dict(visible=True))
                    )

                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Error fetching chart data: {e}")

            st.divider()

            # Step 4: Smart News — Focus on Company Changes
            st.markdown("<h3 style='color:indigo;'>🗞️ Major Company Updates</h3>", unsafe_allow_html=True)
            rss_url = f"https://news.google.com/rss/search?q={company_name}+when:14d"
            news_feed = feedparser.parse(rss_url)

            if not news_feed.entries:
                st.warning("⚠️ No recent news found for this company.")
            else:
                news_entries = news_feed.entries[:40]

                important_news = []
                general_news = []
                for entry in news_entries:
                    title_lower = entry.title.lower()
                    if any(k in title_lower for k in keywords):
                        important_news.append(entry)
                    else:
                        general_news.append(entry)

                final_news = important_news + general_news
                final_news = final_news[:12]

                for i, entry in enumerate(final_news, start=1):
                    title_html = f"<span style='color:indigo; font-weight:600;'>{i}. {entry.title}</span>"
                    st.markdown(title_html, unsafe_allow_html=True)
                    st.caption(f"🕒 {entry.published}")
                    if hasattr(entry, "summary"):
                        st.write(entry.summary[:250] + "...")
                    st.markdown(f"[🔗 Read full article]({entry.link})")
                    st.divider()

    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
