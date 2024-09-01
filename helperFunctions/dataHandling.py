import ccxt
from datetime import datetime
import pandas as pd
import numpy as np

class DataHandler:
    def __init__(self):
        pass

    def fetch_funding_rate_data(self, exchange: str, symbol: str, start_time: int, end_time: int, limit: int = 1000) -> None:
        """
        Fetch funding rates on perpetual contracts listed on the exchange iteratively over a time range and print to console.

        Args:
            exchange (str): Name of exchange (binance, bybit, ...).
            symbol (str): Symbol (BTC/USDT:USDT, ETH/USDT:USDT, ...).
            limit (int): Number of records to fetch per API call (max 1000).
            start_time (int): Start timestamp in milliseconds (inclusive).
            end_time (int): End timestamp in milliseconds (inclusive).
        """
        ex = getattr(ccxt, exchange)()
        funding_rates = []

        while start_time < end_time:
            # Fetch funding rate history with start_time and end_time
            funding_history_dict = ex.fetch_funding_rate_history(symbol=symbol, limit=limit, since=start_time, params={"endTime": end_time})
            
            if not funding_history_dict:
                break
            
            funding_time = [
                datetime.fromtimestamp(d["timestamp"]/1000).strftime('%Y-%m-%d %H:%M:%S') for d in funding_history_dict
            ]
            funding_rate = [d["fundingRate"] for d in funding_history_dict]
            
            # Combine funding time and rate into tuples and extend the list
            funding_rates.extend(list(zip(funding_time, funding_rate)))
            
            # Update start_time to the timestamp of the last fetched record + 1 to avoid duplicates
            start_time = funding_history_dict[-1]["timestamp"] + 1

            # If we fetched less than the limit, we assume there's no more data available
            if len(funding_history_dict) < limit:
                break
        
        print(f"Total rates fetched: {len(funding_rates)}")
        return funding_rates


    def fetch_candlestick_data(self, exchange: str, symbol: str, start_time: int, end_time: int, timeframe: str = "8h", limit: int = 600) -> list:
        """
        Fetch candlestick (OHLCV) data for perpetual futures contracts listed on the exchange iteratively over a time range.

        Args:
            exchange (str): Name of exchange (binance, bybit, ...).
            symbol (str): Symbol (BTC/USDT:USDT, ETH/USDT:USDT, ...).
            timeframe (str): Timeframe for the candlesticks (e.g., '1m', '5m', '1h', '1d').
            limit (int): Number of records to fetch per API call (max 1000).
            start_time (int): Start timestamp in milliseconds (inclusive).
            end_time (int): End timestamp in milliseconds (inclusive).

        Returns:
            list: A list of OHLCV data, where each item is a list [timestamp, open, high, low, close, volume].
                The timestamp is converted to a human-readable format.
        """
        ex = getattr(ccxt, exchange)()
        ohlcv_data = []

        if exchange == 'binance':
            # Calculate the maximum interval (200 days) in milliseconds
            max_interval = 200 * 24 * 60 * 60 * 1000  # 200 days in milliseconds

            while start_time < end_time:
                # Set the current end time to be the lesser of the actual end_time or 200 days after start_time
                current_end_time = min(start_time + max_interval, end_time)

                # Fetch OHLCV data for this interval
                candles = ex.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit, since=start_time, params={"endTime": current_end_time})

                if not candles:
                    print("No more candles found.")
                    break

                # Convert the timestamp to human-readable format and extend the list
                formatted_candles = [
                    [
                        datetime.fromtimestamp(candle[0] / 1000).strftime('%Y-%m-%d %H:%M:%S'),  # Format timestamp
                        candle[1],  # Open
                        candle[2],  # High
                        candle[3],  # Low
                        candle[4],  # Close
                        candle[5],  # Volume
                    ]
                    for candle in candles
                ]

                ohlcv_data.extend(formatted_candles)

                # Update start_time to the timestamp of the last fetched candlestick + 1 to avoid duplicates
                start_time = candles[-1][0] + 1

                # If we fetched less than the limit, we assume there's no more data available
                if len(candles) < limit:
                    print("Fetched less than the limit. Possibly no more data available.")
                    break
                
                print(f"Fetched {len(candles)} candles. New start_time: {datetime.fromtimestamp(start_time / 1000)}")

        print(f"Total candles fetched: {len(ohlcv_data)}")
        return ohlcv_data


    def make_spot_df(self, exchange: str, symbol: str, start_time: int, end_time: int) -> pd.DataFrame:
        """
        Fetch spot price data for the given exchange and symbol and return a DataFrame.

        Args:
            exchange (str): Name of exchange (binance, bybit, ...).
            symbol (str): Symbol (BTC/USDT, ETH/USDT, ...).
            start_time (int): Start timestamp in milliseconds (inclusive).
            end_time (int): End timestamp in milliseconds (inclusive).

        Returns:
            pd.DataFrame: A DataFrame containing the spot price data.
        """
        spot_data = DataHandler.fetch_candlestick_data(self, exchange=exchange, symbol=symbol, start_time=start_time, end_time=end_time)
        spot_df = pd.DataFrame(spot_data, columns=["time", "open", "high", "low", "close", "volume"])
        
        spot_df['exchange'] = exchange
        if symbol == 'BTC/USDT':
            spot_df['crypto'] = 'bitcoin'
        elif symbol == 'ETH/USDT':
            spot_df['crypto'] = 'ethereum'
        spot_df['pair'] = symbol
        spot_df['contract'] = 'spot'
        
        multi_index = pd.MultiIndex.from_arrays(
            [spot_df['time'], spot_df['exchange'], spot_df['crypto'], spot_df['pair'], spot_df['contract']],
            names=['time', 'exchange', 'crypto', 'pair', 'contract']
        )
        spot_df.set_index(multi_index, inplace=True)
        
        spot_df.drop(columns=['time', 'exchange', 'crypto', 'pair', 'contract'], inplace=True)
        spot_df['funding rate'] = np.nan
        
        return spot_df


    def make_perp_df(self, exchange: str, symbol: str, start_time: int, end_time: int, pair:str) -> pd.DataFrame:
        """
        Fetch perpetual futures price data for the given exchange and symbol and return a DataFrame.

        Args:
            exchange (str): Name of exchange (binance, bybit, ...).
            symbol (str): Symbol (BTC/USDT:USDT, ETH/USDT:USDT, ...).
            start_time (int): Start timestamp in milliseconds (inclusive).
            end_time (int): End timestamp in milliseconds (inclusive).

        Returns:
            pd.DataFrame: A DataFrame containing the perpetual futures price data.
        """
        perp_cs_data = DataHandler.fetch_candlestick_data(self, exchange=exchange, symbol=symbol, start_time=start_time, end_time=end_time)
        perp_cs_df = pd.DataFrame(perp_cs_data, columns=["time", "open", "high", "low", "close", "volume"])
        
        perp_fr_data = DataHandler.fetch_funding_rate_data(self,exchange=exchange, symbol=symbol, start_time=start_time, end_time=end_time)
        perp_fr_df = pd.DataFrame(perp_fr_data, columns=["time", "funding rate"])
        
        perp_df = pd.merge(perp_cs_df, perp_fr_df, on="time")
        
        perp_df['exchange'] = exchange
        if pair == 'BTCUSDT' or pair == 'BTCUSDCM':
            perp_df['crypto'] = 'bitcoin'
        elif pair == 'ETHUSDT' or pair == 'ETHUSDCM':
            perp_df['crypto'] = 'ethereum'
        perp_df['pair'] = pair
        perp_df['contract'] = 'perpetual'
        
        multi_index = pd.MultiIndex.from_arrays(
            [perp_df['time'], perp_df['exchange'], perp_df['crypto'], perp_df['pair'], perp_df['contract']],
            names=['time', 'exchange', 'crypto', 'pair', 'contract']
        )
        perp_df.set_index(multi_index, inplace=True)
        
        perp_df.drop(columns=['time', 'exchange', 'crypto', 'pair', 'contract'], inplace=True)
        
        return perp_df
    
    def merge_dfs(self, df1: pd.DataFrame, df2: pd.DataFrame, filename: str) -> pd.DataFrame:
        """
        Merge two DataFrames on the 'time' column.

        Args:
            df1 (pd.DataFrame): The first DataFrame.
            df2 (pd.DataFrame): The second DataFrame.

        Returns:
            pd.DataFrame: The merged DataFrame.
        """
        merged_df = pd.concat([df1, df2])
        merged_df.sort_index(level='time', inplace=True)
        merged_df.to_csv(f'./data/processed/{filename}.csv', index=True)
        print(f'Data saved to ./data/processed/{filename}.csv')
        return merged_df
    
    