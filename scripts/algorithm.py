import pandas as pd

binance_btc_price_basis = pd.read_csv('./data/processed/Binance_BTCUSDT_Basis.csv')
binance_btc_usd_funding_rate = pd.read_csv('./data/processed/Binance_BTCUSDT_Funding_Rate.csv')
binance_btc_coin_funding_rate = pd.read_csv('./data/processed/Binance_BTCUSD_PERP_Funding_Rate.csv')