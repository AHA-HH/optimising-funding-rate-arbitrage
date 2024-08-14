from helperFunctions import fetch_funding_rate_history_to_csv, process_and_calculate_basis

start = 1625097600000  # 1 July 2021 00:00:00
end = 1719792000000    # 1 July 2024 00:00:00

# fetch_funding_rate_history_to_csv(exchange="binance", symbol="BTC/USDT:USDT", limit=1000, start_time=start, end_time=end, file_path='./data/processed/Binance_BTCUSDT_Funding_Rate.csv')
# fetch_funding_rate_history_to_csv(exchange="binance", symbol="BTCUSD_PERP", limit=1000, start_time=start, end_time=end, file_path='./data/processed/Binance_BTCUSD_PERP_Funding_Rate.csv')


# process_and_calculate_basis(spot_file='./data/raw/Binance/Binance_BTCUSDT_1h.csv', future_file='./data/raw/Binance/BTCUSDT_Binance_futures_UM_hour.csv', additional_files=['./data/raw/Binance/BTCUSD_PERP_Binance_futures_CM_hour.csv'], save_path= './data/processed/Binance_BTC_Basis.csv', start_time=start, end_time=end)

