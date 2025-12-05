# pip install streamlit yahooquery feedparser pandas matplotlib plotly yfinance

import streamlit as st
from yahooquery import search, Ticker
import yfinance as yf
import feedparser
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go

# --- Streamlit Setup ---
st.set_page_config(page_title="💹 Company Growth Dashboard", page_icon="💹", layout="centered")

st.markdown("""
    <h1 style='text-align:center; color:indigo;'>💹 Company Growth & Stock Dashboard</h1>
    <p style='text-align:center; color:indigo;'>Track stock price, growth trends, and latest leadership or merger news — all in one place!</p>
""", unsafe_allow_html=True)

# --- Input Section ---
company_name = st.text_input("🔍 Enter company name or ticker:")
keywords = ["CEO", "chief executive", "merger", "acquisition", "guidance", "forecast",
            "outlook", "leadership", "appoints"]
growth_keywords = ["growth", "expansion", "revenue increase", "profit rise", "sales growth",
                   "market share", "scaling", "business growth", "quarterly growth", "performance improvement"]


# --- Helper: Calculate Growth % ---
def calc_growth(df, period_days):
    try:
        df = df.sort_index()
        start_date = df.index.max() - timedelta(days=period_days)
        df_period = df[df.index >= start_date]
        if len(df_period) < 2:
            return "N/A"
        start_price = df_period["close"].iloc[0]
        end_price = df_period["close"].iloc[-1]
        growth = ((end_price - start_price) / start_price) * 100
        return f"{growth:.2f}%"
    except Exception:
        return "N/A"


# --- Main Logic ---
if st.button("Get Insights") and company_name.strip():
    company_name = company_name.strip()

    # --- Step 1: Fetch ticker info from YahooQuery ---
    try:
        results = search(company_name)
        if not results.get("quotes"):
            st.warning("⚠️ No ticker found for this company.")
        else:
            ticker_info = results["quotes"][0]
            ticker_symbol = ticker_info.get("symbol", "N/A")
            description = ticker_info.get("shortname", company_name)

            st.markdown(f"<h2 style='color:indigo;'>{description}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:indigo;'><b>Ticker:</b> {ticker_symbol}</p>", unsafe_allow_html=True)

            # --- Step 2: Current Stock Price ---
            stock_yq = Ticker(ticker_symbol)
            price_data = stock_yq.price.get(ticker_symbol, {})
            current_price = price_data.get("regularMarketPrice", "N/A")
            currency = price_data.get("currency", "")
            if current_price != "N/A":
                st.success(f"💰 **Current Price:** {current_price} {currency}")
            else:
                st.info("Stock price not available right now.")

            st.divider()

            # --- Step 3: Historical Data & Growth % ---
            try:
                hist = stock_yq.history(period="max")
                if hist.empty:
                    st.warning("No historical data available.")
                else:
                    hist = hist.reset_index()
                    if "symbol" in hist.columns:
                        hist = hist[hist["symbol"] == ticker_symbol]
                    hist = hist.set_index("date")

                    # Growth periods
                    periods = {
                        "1 Day": 1,
                        "1 Month": 30,
                        "1 Year": 365,
                        "3 Years": 3 * 365,
                        "5 Years": 5 * 365,
                        "7 Years": 7 * 365,
                        "11 Years": 11 * 365,
                    }
                    growth_data = {p: calc_growth(hist, d) for p, d in periods.items()}
                    growth_df = pd.DataFrame(list(growth_data.items()), columns=["Period", "Growth %"])
                    st.markdown("<h3 style='color:indigo;'>📊 Growth Overview</h3>", unsafe_allow_html=True)
                    st.dataframe(growth_df, hide_index=True, use_container_width=True)

                    # Step 4: Price Chart (Interactive with Plotly)
                    st.markdown("<h3 style='color:indigo;'>📈 Long-Term Price Trend</h3>", unsafe_allow_html=True)
                    fig_price = go.Figure()
                    fig_price.add_trace(go.Candlestick(
                        x=hist.index,
                        open=hist["open"],
                        high=hist["high"],
                        low=hist["low"],
                        close=hist["close"],
                        name='Candlestick'
                    ))
                    fig_price.update_layout(xaxis_title='Date', yaxis_title='Price',
                                            font=dict(color='indigo'))
                    st.plotly_chart(fig_price, use_container_width=True)
            except Exception as e:
                st.error(f"Error fetching historical data: {e}")

            st.divider()

            # --- Step 5: News Section (RSS) ---
            st.markdown("<h3 style='color:indigo;'>🗞️ Latest Growth & Leadership News</h3>", unsafe_allow_html=True)
            rss_url = f"https://news.google.com/rss/search?q={company_name}"
            news_feed = feedparser.parse(rss_url)
            if not news_feed.entries:
                st.warning("⚠️ No recent news found.")
            else:
                # Filter news by keywords + growth keywords
                important_news = []
                for entry in news_feed.entries[:30]:
                    title_lower = entry.title.lower()
                    if company_name.lower() in title_lower and (
                            any(k.lower() in title_lower for k in keywords + growth_keywords)
                    ):
                        important_news.append(entry)

                news_to_display = important_news[:15] if important_news else news_feed.entries[:15]
                keyword_count = Counter()
                date_count = Counter()
                for i, entry in enumerate(news_to_display, start=1):
                    with st.expander(f"🔹 {i}. {entry.title}"):
                        st.write(entry.summary[:300] + "...")
                        st.caption(f"[Read more]({entry.link}) | {entry.published}")

                    # Count keywords in headlines
                    title_lower = entry.title.lower()
                    for k in growth_keywords + keywords:
                        if k.lower() in title_lower:
                            keyword_count[k] += 1
                    date_count[entry.published[:10]] += 1

                # --- Step 6: Charts for News ---
                if keyword_count:
                    st.markdown("<h3 style='color:indigo;'>Keyword Frequency in Headlines</h3>", unsafe_allow_html=True)
                    fig_kw = px.bar(
                        x=list(keyword_count.keys()),
                        y=list(keyword_count.values()),
                        labels={'x': 'Keyword', 'y': 'Count'},
                        color_discrete_sequence=['indigo']
                    )
                    st.plotly_chart(fig_kw, use_container_width=True)

                if date_count:
                    st.markdown("<h3 style='color:indigo;'>News Over Time</h3>", unsafe_allow_html=True)
                    dates_sorted = sorted(date_count.keys())
                    counts_sorted = [date_count[d] for d in dates_sorted]
                    fig_date = px.line(
                        x=dates_sorted,
                        y=counts_sorted,
                        labels={'x': 'Date', 'y': 'Number of Articles'},
                        markers=True
                    )
                    fig_date.update_traces(line_color='indigo')
                    st.plotly_chart(fig_date, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
