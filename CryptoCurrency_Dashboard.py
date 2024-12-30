import yfinance as yf
import pandas as pd
import plotly.express as px
import streamlit as st

def fetch_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    if not data.empty:
        data.columns = [col if isinstance(col, str) else '_'.join(col) for col in data.columns]
        data.rename(columns={f'Close_{symbol}': 'Close', f'High_{symbol}': 'High', 
                             f'Low_{symbol}': 'Low', f'Open_{symbol}': 'Open'}, inplace=True)
        data['Year'], data['Month'], data['Day'] = data.index.year, data.index.month, data.index.day
        return data[(data['Year'] >= 2021) & (data['Year'] <= 2024)]
    return None

def plot_daily_fluctuation(data, month_selection, name):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    selected_month_num = months.index(month_selection) + 1
    month_data = data[data['Month'] == selected_month_num]
    month_data['Avg_Close_Open'] = (month_data['Close'] + month_data['Open']) / 2
    monthly_avg_data = month_data.groupby(['Year', 'Day'])['Avg_Close_Open'].mean().reset_index()

    fig_daily = px.line(monthly_avg_data, x='Day', y='Avg_Close_Open', color='Year', line_shape='linear',
                        title=f'{name} Daily Fluctuation for {month_selection} (2021-2024)', 
                        labels={'Day': 'Day of Month', 'Avg_Close_Open': 'Avg Price (USD)', 'Year': 'Year'}, markers=True)
    st.plotly_chart(fig_daily)

def plot_monthly_avg_price(data, name):
    data['Overall_Avg'] = (data['High'] + data['Low'] + data['Open'] + data['Close']) / 4
    monthly_avg = data.groupby(['Year', 'Month'])['Overall_Avg'].mean().reset_index()
    fig_monthly = px.line(monthly_avg, x='Month', y='Overall_Avg', color='Year',
                          title=f"{name} Monthly Average Price (2021-2024)",
                          labels={'Month': 'Month', 'Overall_Avg': 'Avg Price (USD)'})
    st.plotly_chart(fig_monthly)

st.title("Cryptocurrency Price Analysis Dashboard for 2021-2024")
st.sidebar.header("Select Cryptocurrency and Date Range")

cryptos = [("BTC-USD", "Bitcoin"), ("ETH-USD", "Ethereum"), ("USDT-USD", "Tether"), 
           ("XOR-USD", "XOR"), ("BNB-USD", "BNB"), ("SOL-USD", "Solana"),
           ("DOGE-USD", "Dogecoin"), ("USDC-USD", "USDC"), ("ADA-USD", "Cardano"), ("TRX-USD", "Tron")]

crypto_selection = st.sidebar.selectbox("Choose Cryptocurrency", cryptos, format_func=lambda x: x[1])
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2021-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2024-12-31"))

symbol, name = crypto_selection
data = fetch_data(symbol, start_date, end_date)

if data is not None:
    month_selection = st.select_slider("Select a Month", options=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    plot_daily_fluctuation(data, month_selection, name)
    plot_monthly_avg_price(data, name)
else:
    st.warning(f"No data available for {name} between the selected dates.")
