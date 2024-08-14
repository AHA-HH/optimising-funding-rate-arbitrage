import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helperFunctions.dataHandling import DataHandler

# start_timestamp = 1625097600000  # 1 July 2021 00:00:00
start_timestamp = 1672531200000  # 1 Jan 2023 00:00:00
end_timestamp = 1719792000000    # 1 July 2024 00:00:00

# start_date = '2021-07-01 00:00:00'
start_date = '2023-01-01 00:00:00'
end_date = '2024-07-01 00:00:00'

data_handler = DataHandler()

data_handler.fetch_funding_rate_history_to_csv(exchange="binance", symbol="BTC/USDT:USDT", limit=1000, start_time=start_timestamp, end_time=end_timestamp, file_path='./data/processed/Binance_BTCUSDT_Funding_Rate.csv')

spot_df = data_handler.load_and_prepare_df(file_path='./data/raw/Binance/Binance_BTCUSDT_1h.csv', price_label='BTCUSDT Spot', start_time=start_date, end_time=end_date)
usdm_df = data_handler.load_and_prepare_df(file_path='./data/raw/Binance/BTCUSDT_Binance_futures_UM_hour.csv', price_label='BTCUSDT USDM', start_time=start_date, end_time=end_date)

data_handler.process_and_merge_df(spot_df, usdm_df, save_path='./data/processed/Binance_BTC_Prices.csv')

# spot_d_df = data_handler.load_and_prepare_df(file_path='./data/raw/Binance/Binance_BTCUSDT_d.csv', price_label='BTCUSDT Spot', start_time=start_date, end_time=end_date)
# usdm_d_df = data_handler.load_and_prepare_df(file_path='./data/raw/Binance/BTCUSDT_Binance_futures_UM_day.csv', price_label='BTCUSDT USDM', start_time=start_date, end_time=end_date)

# data_handler.process_and_merge_df(spot_d_df, usdm_d_df, save_path='./data/processed/Binance_BTC_Prices_daily.csv')

# fetch_funding_rate_history_to_csv(exchange="binance", symbol="BTCUSD_PERP", limit=1000, start_time=start, end_time=end, file_path='./data/processed/Binance_BTCUSD_PERP_Funding_Rate.csv')