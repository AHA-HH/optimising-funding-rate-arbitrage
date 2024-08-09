import ccxt
import time
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def fetch_funding_rate_history(exchange: str, symbol: str, limit: int) -> tuple:
    """
    Fetch funding rates on perpetual contracts listed on the exchange.

    Args:
        exchange (str): Name of exchange (binance, bybit, ...)
        symbol (str): Symbol (BTC/USDT:USDT, ETH/USDT:USDT, ...).

    Returns (tuple): settlement time, funding rate.

    """
    ex = getattr(ccxt, exchange)()
    funding_history_dict = ex.fetch_funding_rate_history(symbol=symbol, limit=limit)
    # funding_time = [
    #     datetime.fromtimestamp(d["timestamp"] * 0.001) for d in funding_history_dict
    # ]
    
    funding_time = [
        datetime.fromtimestamp(d["timestamp"]/1000).strftime('%Y-%m-%d %H:%M:%S') for d in funding_history_dict
        ]
    funding_rate = [d["fundingRate"] * 100 for d in funding_history_dict]
    return funding_time, funding_rate
    # return funding_history_dict

print(fetch_funding_rate_history(exchange="binance", symbol="BTC/USDT:USDT", limit=1000))