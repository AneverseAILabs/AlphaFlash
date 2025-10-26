import streamlit as st
from yahooquery import search, Ticker
import pandas as pd
import numpy as np
import plotly.express as px

# --- Page Setup ---
st.set_page_config(page_title="Investor Insights", page_icon="💹")

# --- Indigo font style ---
st.markdown("<h1 style='text-align:center; color:indigo;'>💹 Company Investor Insights</h1>", unsafe_allow_html=True)

# --- User Input ---
company_name = st.text_input("Enter company name:")

if st.button("Get Insights") and company_name.strip() != "":
    company_name = company_name.strip()

    try:
        # --- Get Ticker via yahooquery ---
        results = search(company_name)
        if not results['quotes']:
            st.warning("No ticker found for this company.")
        else:
            # Take first match
            ticker_symbol = results['quotes'][0]['symbol']
            description = results['quotes'][0]['shortname'] or results['quotes'][0]['symbol']

            st.markdown(f"<h2 style='color:indigo;'>{description} ({ticker_symbol})</h2>", unsafe_allow_html=True)

            # --- Fetch Historical Stock Data ---
            stock = Ticker(ticker_symbol)
            df_stock = stock.history(period="max")

            if df_stock.empty:
                st.warning("No historical data found for this ticker.")
            else:
                df_stock_reset = df_stock.reset_index()
                if 'date' not in df_stock_reset.columns:
                    df_stock_reset = df_stock_reset.rename(columns={df_stock_reset.columns[0]: 'date'})

                # --- Better Chart ---
                fig = px.line(
                    df_stock_reset, x='date', y='close',
                    title=f"{description} Closing Price",
                    labels={'close': 'Closing Price', 'date': 'Date'},
                    template='plotly_dark',  # dark theme
                )
                fig.update_traces(line_color='indigo', line_width=3)
                fig.update_layout(
                    title_font=dict(size=20, color='indigo'),
                    xaxis_title_font=dict(size=16, color='indigo'),
                    yaxis_title_font=dict(size=16, color='indigo'),
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)

                # --- Investor Insights ---
                df_stock_reset['Return'] = df_stock_reset['close'].pct_change()
                df_stock_reset['Year'] = pd.DatetimeIndex(df_stock_reset['date']).year
                yearly_return = df_stock_reset.groupby('Year')['close'].last().pct_change().mean() * 100
                volatility = df_stock_reset['Return'].std() * np.sqrt(252) * 100

                if len(df_stock_reset) > 252:
                    if df_stock_reset['close'].iloc[-1] > df_stock_reset['close'].iloc[-252]:
                        trend = "uptrend 📈"
                    elif df_stock_reset['close'].iloc[-1] < df_stock_reset['close'].iloc[-252]:
                        trend = "downtrend 📉"
                    else:
                        trend = "sideways ↔️"
                else:
                    trend = "Not enough data"

                st.markdown("<h3 style='color:indigo;'>💡 Investor Insights</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:indigo;'>- <b>Average Annual Return:</b> {yearly_return:.2f}%</p>",
                            unsafe_allow_html=True)
                #st.markdown(f"<p style='color:indigo;'>- <b>Annualized Volatility:</b> {volatility:.2f}%</p>",
                            #unsafe_allow_html=True)
                st.markdown(f"<p style='color:indigo;'>- <b>Current Trend:</b> {trend}</p>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error fetching data: {e}")
