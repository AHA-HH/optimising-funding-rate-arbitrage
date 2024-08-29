import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helperFunctions.dataHandling import DataHandler

dataHandler = DataHandler()

start_timestamp = 1672531100000  # 31 Dec 2022 23:59:59
end_timestamp = 1719792000000    # 1 July 2024 00:00:00

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

# okx_btc_spot = dataHandler.make_spot_df(exchange="okx", symbol="BTC/USDT", start_time=start_timestamp, end_time=end_timestamp)
# okx_btc_usdm = dataHandler.make_perp_df(exchange="okx", symbol="BTC-USDT-SWAP", pair="BTCUSDT", start_time=start_timestamp, end_time=end_timestamp)
# okx_btc_coinm = dataHandler.make_perp_df(exchange="okx", symbol="BTC-USD-SWAP", pair="BTCUSDCM", start_time=start_timestamp, end_time=end_timestamp)

# okx_btc_perp = dataHandler.merge_dfs(okx_btc_usdm, okx_btc_coinm, 'okx_btc')
# okx_btc = dataHandler.merge_dfs(okx_btc_perp, okx_btc_spot, 'okx_btc')

# print("OKX BTC saved")

# okx_eth_spot = dataHandler.make_spot_df(exchange="okx", symbol="ETH/USDT", start_time=start_timestamp, end_time=end_timestamp)
# okx_eth_usdm = dataHandler.make_perp_df(exchange="okx", symbol="ETH-USDT-SWAP", pair="ETHUSDT", start_time=start_timestamp, end_time=end_timestamp)
# okx_eth_coinm = dataHandler.make_perp_df(exchange="okx", symbol="ETH-USD-SWAP", pair="ETHUSDCM", start_time=start_timestamp, end_time=end_timestamp)

# okx_eth_perp = dataHandler.merge_dfs(okx_eth_usdm, okx_eth_coinm, 'okx_eth')
# okx_eth = dataHandler.merge_dfs(okx_eth_perp, okx_eth_spot, 'okx_eth')

# print("OKX ETH saved")

# okx_df = dataHandler.merge_dfs(okx_btc, okx_eth, 'okx')

# print("OKX data saved")

# bybit_btc_spot = dataHandler.make_spot_df(exchange="bybit", symbol="BTC/USDT", start_time=start_timestamp, end_time=end_timestamp)
# bybit_btc_usdm = dataHandler.make_perp_df(exchange="bybit", symbol="BTCUSDT", pair="BTCUSDT", start_time=start_timestamp, end_time=end_timestamp)
# bybit_btc_coinm = dataHandler.make_perp_df(exchange="bybit", symbol="BTCUSD", pair="BTCUSDCM", start_time=start_timestamp, end_time=end_timestamp)

# bybit_btc_perp = dataHandler.merge_dfs(bybit_btc_usdm, bybit_btc_coinm, 'bybit_btc')
# bybit_btc = dataHandler.merge_dfs(bybit_btc_perp, bybit_btc_spot, 'bybit_btc')

# print("Bybit BTC saved")

# bybit_eth_spot = dataHandler.make_spot_df(exchange="bybit", symbol="ETH/USDT", start_time=start_timestamp, end_time=end_timestamp)
# bybit_eth_usdm = dataHandler.make_perp_df(exchange="bybit", symbol="ETHUSDT", pair="ETHUSDT", start_time=start_timestamp, end_time=end_timestamp)
# bybit_eth_coinm = dataHandler.make_perp_df(exchange="bybit", symbol="ETHUSD", pair="ETHUSDCM", start_time=start_timestamp, end_time=end_timestamp)

# bybit_eth_perp = dataHandler.merge_dfs(bybit_eth_usdm, bybit_eth_coinm, 'bybit_eth')
# bybit_eth = dataHandler.merge_dfs(bybit_eth_perp, bybit_eth_spot, 'bybit_eth')

# print("Bybit ETH saved")

# bybit_df = dataHandler.merge_dfs(bybit_btc, bybit_eth, 'bybit')

# print("Bybit data saved")

# bitget_btc_spot = dataHandler.make_spot_df(exchange="bitget", symbol="BTC/USDT", start_time=start_timestamp, end_time=end_timestamp, timeframe='4h')
# bitget_btc_usdm = dataHandler.make_perp_df(exchange="bitget", symbol="BTC/USDT:USDT", pair="BTCUSDT", start_time=start_timestamp, end_time=end_timestamp, timeframe='4h')
# bitget_btc_coinm = dataHandler.make_perp_df(exchange="bitget", symbol="BTCUSD", pair="BTCUSDCM", start_time=start_timestamp, end_time=end_timestamp, timeframe='4h')

# bitget_btc_perp = dataHandler.merge_dfs(bitget_btc_usdm, bitget_btc_coinm, 'bitget_btc')
# bitget_btc = dataHandler.merge_dfs(bitget_btc_perp, bitget_btc_spot, 'bitget_btc')

# print("Bitget BTC saved")

# bitget_eth_spot = dataHandler.make_spot_df(exchange="bitget", symbol="ETH/USDT", start_time=start_timestamp, end_time=end_timestamp, timeframe='4h')
# bitget_eth_usdm = dataHandler.make_perp_df(exchange="bitget", symbol="ETH/USDT:USDT", pair="ETHUSDT", start_time=start_timestamp, end_time=end_timestamp, timeframe='4h')
# bitget_eth_coinm = dataHandler.make_perp_df(exchange="bitget", symbol="ETHUSD", pair="ETHUSDCM", start_time=start_timestamp, end_time=end_timestamp, timeframe='4h')

# bitget_eth_perp = dataHandler.merge_dfs(bitget_eth_usdm, bitget_eth_coinm, 'bitget_eth')
# bitget_eth = dataHandler.merge_dfs(bitget_eth_perp, bitget_eth_spot, 'bitget_eth')

# print("Bitget ETH saved")

# bitget_df = dataHandler.merge_dfs(bitget_btc, bitget_eth, 'bitget')

# print("Bitget data saved")
