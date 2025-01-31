import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helperFunctions.dataHandling import DataHandler

dataHandler = DataHandler()

start_timestamp = 1672531100000  # 31 Dec 2022 23:59:59
end_timestamp = 1719792000000    # 1 July 2024 00:00:00

# Binance

bin_btc_spot = dataHandler.make_spot_df(exchange="binance", symbol="BTC/USDT", start_time=start_timestamp, end_time=end_timestamp)
bin_btc_usdm = dataHandler.make_perp_df(exchange="binance", symbol="BTC/USDT:USDT", pair="BTCUSDT", start_time=start_timestamp, end_time=end_timestamp)
bin_btc_coinm = dataHandler.make_perp_df(exchange="binance", symbol="BTCUSD_PERP", pair="BTCUSDCM", start_time=start_timestamp, end_time=end_timestamp)

bin_btc_perp = dataHandler.merge_dfs(bin_btc_usdm, bin_btc_coinm, 'binance_btc')
bin_btc = dataHandler.merge_dfs(bin_btc_perp, bin_btc_spot, 'binance_btc')

print("Binance BTC saved")

bin_eth_spot = dataHandler.make_spot_df(exchange="binance", symbol="ETH/USDT", start_time=start_timestamp, end_time=end_timestamp)
bin_eth_usdm = dataHandler.make_perp_df(exchange="binance", symbol="ETH/USDT:USDT", pair="ETHUSDT", start_time=start_timestamp, end_time=end_timestamp)
bin_eth_coinm = dataHandler.make_perp_df(exchange="binance", symbol="ETHUSD_PERP", pair="ETHUSDCM", start_time=start_timestamp, end_time=end_timestamp)

bin_eth_perp = dataHandler.merge_dfs(bin_eth_usdm, bin_eth_coinm, 'binance_eth')
bin_eth = dataHandler.merge_dfs(bin_eth_perp, bin_eth_spot, 'binance_eth')

print("Binance ETH saved")

bin_df = dataHandler.merge_dfs(bin_btc, bin_eth, 'binance')

print("Binance data saved")

# Bybit

bybit_btc_spot = dataHandler.make_spot_df(exchange="bybit", symbol="BTC/USDT", start_time=start_timestamp, end_time=end_timestamp)
bybit_btc_usdm = dataHandler.make_perp_df(exchange="bybit", symbol="BTCUSDT", pair="BTCUSDT", start_time=start_timestamp, end_time=end_timestamp)
bybit_btc_coinm = dataHandler.make_perp_df(exchange="bybit", symbol="BTCUSD", pair="BTCUSDCM", start_time=start_timestamp, end_time=end_timestamp)

bybit_btc_perp = dataHandler.merge_dfs(bybit_btc_usdm, bybit_btc_coinm, 'bybit_btc')
bybit_btc = dataHandler.merge_dfs(bybit_btc_perp, bybit_btc_spot, 'bybit_btc')

print("Bybit BTC saved")

bybit_eth_spot = dataHandler.make_spot_df(exchange="bybit", symbol="ETH/USDT", start_time=start_timestamp, end_time=end_timestamp)
bybit_eth_usdm = dataHandler.make_perp_df(exchange="bybit", symbol="ETHUSDT", pair="ETHUSDT", start_time=start_timestamp, end_time=end_timestamp)
bybit_eth_coinm = dataHandler.make_perp_df(exchange="bybit", symbol="ETHUSD", pair="ETHUSDCM", start_time=start_timestamp, end_time=end_timestamp)

bybit_eth_perp = dataHandler.merge_dfs(bybit_eth_usdm, bybit_eth_coinm, 'bybit_eth')
bybit_eth = dataHandler.merge_dfs(bybit_eth_perp, bybit_eth_spot, 'bybit_eth')

print("Bybit ETH saved")

bybit_df = dataHandler.merge_dfs(bybit_btc, bybit_eth, 'bybit')

print("Bybit data saved")

# OKX

input_folder = './data/raw/okx/' 
output_file = './data/processed/okx_funding_rates.csv'
instruments = ['BTC-USDT-SWAP', 'BTC-USD-SWAP', 'ETH-USDT-SWAP', 'ETH-USD-SWAP']

dataHandler.fetch_funding_rates_okx(input_folder, output_file, instruments)

print("OKX funding rates saved")

okx_btc_spot = dataHandler.make_spot_df(exchange="okx", symbol="BTC/USDT", start_time=start_timestamp, end_time=end_timestamp)
okx_btc_usdm = dataHandler.make_perp_df(exchange="okx", symbol="BTC-USDT-SWAP", pair="BTCUSDT", start_time=start_timestamp, end_time=end_timestamp)
okx_btc_coinm = dataHandler.make_perp_df(exchange="okx", symbol="BTC-USD-SWAP", pair="BTCUSDCM", start_time=start_timestamp, end_time=end_timestamp)

okx_btc_perp = dataHandler.merge_dfs(okx_btc_usdm, okx_btc_coinm, 'okx_btc')
okx_btc = dataHandler.merge_dfs(okx_btc_perp, okx_btc_spot, 'okx_btc')

print("OKX BTC saved")

okx_eth_spot = dataHandler.make_spot_df(exchange="okx", symbol="ETH/USDT", start_time=start_timestamp, end_time=end_timestamp)
okx_eth_usdm = dataHandler.make_perp_df(exchange="okx", symbol="ETH-USDT-SWAP", pair="ETHUSDT", start_time=start_timestamp, end_time=end_timestamp)
okx_eth_coinm = dataHandler.make_perp_df(exchange="okx", symbol="ETH-USD-SWAP", pair="ETHUSDCM", start_time=start_timestamp, end_time=end_timestamp)

okx_eth_perp = dataHandler.merge_dfs(okx_eth_usdm, okx_eth_coinm, 'okx_eth')
okx_eth = dataHandler.merge_dfs(okx_eth_perp, okx_eth_spot, 'okx_eth')

print("OKX ETH saved")

okx_df = dataHandler.merge_dfs(okx_btc, okx_eth, 'okx')

print("OKX data saved")

merged_df = pd.concat([bin_df, bybit_df, okx_df])

merged_df.sort_index(level='time', inplace=True)

merged_df.to_csv(f'./data/all_exchanges.csv', index=True)

print(f'Data saved to ./data/all_exchanges.csv')

print("All exchange data saved and ready for use")

# Risk-free Rate for Metrics Calculation

# rf_df = pd.read_excel('./data/raw/Search.xlsx')

# # Create a new DataFrame with only the transformed Date and Rate columns
# new_df = pd.DataFrame()
# new_df['date'] = pd.to_datetime(rf_df['Effective Date'])
# new_df['rate'] = rf_df['Rate (%)'] / 100

# # Sort the DataFrame by date in ascending order
# new_df = new_df.sort_values('date')

# # Create a date range that covers all dates between the min and max date in the data
# all_dates = pd.date_range(start=new_df['date'].min(), end=new_df['date'].max())

# # Reindex the DataFrame to include all dates, forward fill the missing rates
# new_df = new_df.set_index('date').reindex(all_dates).fillna(method='ffill')

# # Reset the index and rename the index column back to 'Effective Date'
# new_df = new_df.rename_axis('date').reset_index()

# new_df.to_csv('./data/processed/risk_free_rate.csv', index=False)

# print("Risk-free rate saved and ready for use")