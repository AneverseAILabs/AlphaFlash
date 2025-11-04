import streamlit as st
from yahooquery import search, Ticker
import feedparser
import pandas as pd

# --- App Setup ---
st.set_page_config(page_title="Company Stock + News", page_icon="💹", layout="centered")

st.markdown("""
    <h1 style='text-align:center; color:indigo;'>💹 Company Stock & News Insights</h1>
    <p style='text-align:center; color:green;'>Get real-time stock prices and latest news (CEO, Mergers, Guidance) — no API key needed!</p>
""", unsafe_allow_html=True)

# --- Input ---
company_name = st.text_input("Enter company name:")

keywords = ["CEO", "chief executive", "merger", "acquisition", "guidance", "forecast", "outlook", "leadership", "appoints"]

if st.button("Get Insights") and company_name.strip():
    company_name = company_name.strip()

    try:
        # --- Step 1: Find Ticker ---
        results = search(company_name)
        if not results.get("quotes"):
            st.warning("⚠️ No ticker found for this company.")
        else:
            ticker_info = results["quotes"][0]
            ticker_symbol = ticker_info.get("symbol", "N/A")
            description = ticker_info.get("shortname", company_name)

            st.markdown(f"<h2 style='color:indigo;'>{description}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:green;'><b>Ticker Symbol:</b> {ticker_symbol}</p>", unsafe_allow_html=True)

            # --- Step 2: Latest Stock Price ---
            try:
                stock = Ticker(ticker_symbol)
                price_data = stock.price.get(ticker_symbol, {})
                current_price = price_data.get("regularMarketPrice", "N/A")
                currency = price_data.get("currency", "")
                if current_price != "N/A":
                    st.success(f"💰 **Current Stock Price:** {current_price} {currency}")
                else:
                    st.info("Stock price not available right now.")
            except Exception as e:
                st.error(f"Couldn't fetch stock price: {e}")

            st.divider()

            # --- Step 3: Fetch News ---
            rss_url = f"https://news.google.com/rss/search?q={company_name}"
            news_feed = feedparser.parse(rss_url)

            if not news_feed.entries:
                st.warning("⚠️ No recent news found for this company.")
            else:
                st.subheader(f"🗞️ Latest 11 News about {description}")

                # Filter for leadership / merger / guidance
                important_news = []
                for entry in news_feed.entries[:20]:
                    title_lower = entry.title.lower()
                    if any(word in title_lower for word in [k.lower() for k in keywords]):
                        important_news.append(entry)

                # If none found, show normal top 11
                if not important_news:
                    st.info("No CEO / merger / guidance news found — showing latest 11 headlines.")
                    news_to_display = news_feed.entries[:11]
                else:
                    st.success(f"🔍 Found {len(important_news)} leadership / guidance updates!")
                    news_to_display = important_news[:11]

                for i, entry in enumerate(news_to_display, start=1):
                    st.markdown(f"### {i}. [{entry.title}]({entry.link})")
                    st.caption(entry.published)
                    st.divider()

    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
