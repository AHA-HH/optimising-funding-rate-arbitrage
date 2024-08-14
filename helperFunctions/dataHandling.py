import ccxt
import time
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def fetch_funding_rate_history_to_csv(exchange: str, symbol: str, limit: int, start_time: int, end_time: int, file_path: str) -> None:
    """
    Fetch funding rates on perpetual contracts listed on the exchange iteratively over a time range and save to a CSV file.

    Args:
        exchange (str): Name of exchange (binance, bybit, ...).
        symbol (str): Symbol (BTC/USDT:USDT, ETH/USDT:USDT, ...).
        limit (int): Number of records to fetch per API call (max 1000).
        start_time (int): Start timestamp in milliseconds (inclusive).
        end_time (int): End timestamp in milliseconds (inclusive).
        file_path (str): File path where the CSV file will be saved.
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
        # funding_rate = [d["fundingRate"] * 100 for d in funding_history_dict]
        funding_rate = [d["fundingRate"] for d in funding_history_dict]
        
        funding_rates.extend(list(zip(funding_time, funding_rate)))
        
        # Update start_time to the timestamp of the last fetched record + 1 to avoid duplicates
        start_time = funding_history_dict[-1]["timestamp"] + 1

        # If we fetched less than the limit, we assume there's no more data available
        if len(funding_history_dict) < limit:
            break

    # Create a DataFrame from the collected data
    df = pd.DataFrame(funding_rates, columns=["Time", "Funding Rate"])
    
    # Save the DataFrame to a CSV file
    df.to_csv(file_path, index=False)
    print(f"Data saved to {file_path}")

def load_and_prepare_df(file_path, price_label, start_time=None, end_time=None):
    """
    Helper function to load, rename columns, filter by Unix time, and prepare the DataFrame.
    
    Args:
        file_path (str): Path to the CSV file.
        price_label (str): The label to use for the 'Close' column after renaming.
        start_time (int): The start time as a Unix timestamp (in milliseconds). Default is None.
        end_time (int): The end time as a Unix timestamp (in milliseconds). Default is None.

    Returns:
        pd.DataFrame: The prepared DataFrame.
    """
    df = pd.read_csv(file_path, skiprows=1)
    df.rename(columns={'Date': 'Time'}, inplace=True)
    df = df[['Unix', 'Time', 'Close']]
    
    if start_time and end_time:
        df = df[(df['Unix'] >= start_time) & (df['Unix'] <= end_time)]
    
    df.rename(columns={'Close': price_label}, inplace=True)
    df = df[['Time', price_label]]
    df['Time'] = pd.to_datetime(df['Time'])
    df.sort_values(by='Time', inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    return df

def process_and_calculate_basis(spot_file, future_file, additional_files=None, save_path=None, start_time=None, end_time=None):
    """
    Processes data from spot, futures, and optionally multiple additional CSV files, calculates the basis, and
    generates new columns based on the additional data. The final DataFrame is saved to a specified location.

    Args:
        spot_file (str): Path to the spot price CSV file.
        future_file (str): Path to the futures price CSV file.
        additional_files (list of str): List of paths to additional CSV files for further calculations. Default is None.
        save_path (str): Path to save the final DataFrame as a new CSV file. Default is None.
        start_time (int): The start time as a Unix timestamp (in milliseconds). Default is None.
        end_time (int): The end time as a Unix timestamp (in milliseconds). Default is None.

    Returns:
        pd.DataFrame: The final processed DataFrame.
    """

    # Load and prepare spot price data
    spot_df = load_and_prepare_df(spot_file, 'BTCUSDT Spot', start_time, end_time)

    # Load and prepare futures price data
    future_df = load_and_prepare_df(future_file, 'BTCUSDT Future', start_time, end_time)

    # Merge spot and futures data
    merged_df = pd.merge(spot_df, future_df, on='Time')

    # Calculate the basis (Futures - Spot)
    merged_df['Basis BTCUSDT Future'] = merged_df['BTCUSDT Future'] - merged_df['BTCUSDT Spot']

    # Process each additional file if provided
    if additional_files:
        for i, file in enumerate(additional_files):
            additional_df = load_and_prepare_df(file, 'BTCUSD PERP Future', start_time, end_time)
            merged_df = pd.merge(merged_df, additional_df, on='Time', how='left')
            
            merged_df['Basis BTCUSD PERP Future'] = merged_df['BTCUSD PERP Future'] - merged_df['BTCUSDT Spot']

    # Optionally save the final DataFrame to a CSV file
    if save_path:
        merged_df.to_csv(save_path, index=False)
        print(f"Final data saved to {save_path}")

    # Print the final DataFrame to the console
    print("Final Processed DataFrame:")
    print(merged_df.head())

    return merged_df

# import ccxt
# import time
# from datetime import datetime
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt

# class DataHandling:
#     def __init__(self, exchange: str):
#         self.exchange = getattr(ccxt, exchange)()
        
#     def fetch_funding_rate_history_to_csv(self, symbol: str, limit: int, start_time: int, end_time: int, file_path: str) -> None:
#         """
#         Fetch funding rates on perpetual contracts listed on the exchange iteratively over a time range and save to a CSV file.

#         Args:
#             symbol (str): Symbol (BTC/USDT:USDT, ETH/USDT:USDT, ...).
#             limit (int): Number of records to fetch per API call (max 1000).
#             start_time (int): Start timestamp in milliseconds (inclusive).
#             end_time (int): End timestamp in milliseconds (inclusive).
#             file_path (str): File path where the CSV file will be saved.
#         """
#         funding_rates = []

#         while start_time < end_time:
#             # Fetch funding rate history with start_time and end_time
#             funding_history_dict = self.exchange.fetch_funding_rate_history(symbol=symbol, limit=limit, since=start_time, params={"endTime": end_time})

#             if not funding_history_dict:
#                 break

#             funding_time = [
#                 datetime.fromtimestamp(d["timestamp"]/1000).strftime('%Y-%m-%d %H:%M:%S') for d in funding_history_dict
#             ]
#             funding_rate = [d["fundingRate"] for d in funding_history_dict]

#             funding_rates.extend(list(zip(funding_time, funding_rate)))

#             # Update start_time to the timestamp of the last fetched record + 1 to avoid duplicates
#             start_time = funding_history_dict[-1]["timestamp"] + 1

#             # If we fetched less than the limit, we assume there's no more data available
#             if len(funding_history_dict) < limit:
#                 break

#         # Create a DataFrame from the collected data
#         df = pd.DataFrame(funding_rates, columns=["Time", "Funding Rate"])
        
#         # Save the DataFrame to a CSV file
#         df.to_csv(file_path, index=False)
#         print(f"Data saved to {file_path}")

#     def load_and_prepare_df(self, file_path: str, price_label: str, start_time: int = None, end_time: int = None) -> pd.DataFrame:
#         """
#         Helper function to load, rename columns, filter by Unix time, and prepare the DataFrame.

#         Args:
#             file_path (str): Path to the CSV file.
#             price_label (str): The label to use for the 'Close' column after renaming.
#             start_time (int): The start time as a Unix timestamp (in milliseconds). Default is None.
#             end_time (int): The end time as a Unix timestamp (in milliseconds). Default is None.

#         Returns:
#             pd.DataFrame: The prepared DataFrame.
#         """
#         df = pd.read_csv(file_path, skiprows=1)
#         df.rename(columns={'Date': 'Time'}, inplace=True)
#         df = df[['Unix', 'Time', 'Close']]

#         if start_time and end_time:
#             df = df[(df['Unix'] >= start_time) & (df['Unix'] <= end_time)]

#         df.rename(columns={'Close': price_label}, inplace=True)
#         df = df[['Time', price_label]]
#         df['Time'] = pd.to_datetime(df['Time'])
#         df.sort_values(by='Time', inplace=True)
#         df.reset_index(drop=True, inplace=True)

#         return df

#     def process_and_calculate_basis(self, spot_file: str, future_file: str, additional_files: list = None, save_path: str = None, start_time: int = None, end_time: int = None) -> pd.DataFrame:
#         """
#         Processes data from spot, futures, and optionally multiple additional CSV files, calculates the basis, and
#         generates new columns based on the additional data. The final DataFrame is saved to a specified location.

#         Args:
#             spot_file (str): Path to the spot price CSV file.
#             future_file (str): Path to the futures price CSV file.
#             additional_files (list of str): List of paths to additional CSV files for further calculations. Default is None.
#             save_path (str): Path to save the final DataFrame as a new CSV file. Default is None.
#             start_time (int): The start time as a Unix timestamp (in milliseconds). Default is None.
#             end_time (int): The end time as a Unix timestamp (in milliseconds). Default is None.

#         Returns:
#             pd.DataFrame: The final processed DataFrame.
#         """

#         # Load and prepare spot price data
#         spot_df = self.load_and_prepare_df(spot_file, 'BTCUSDT Spot', start_time, end_time)

#         # Load and prepare futures price data
#         future_df = self.load_and_prepare_df(future_file, 'BTCUSDT Future', start_time, end_time)

#         # Merge spot and futures data
#         merged_df = pd.merge(spot_df, future_df, on='Time')

#         # Calculate the basis (Futures - Spot)
#         merged_df['Basis BTCUSDT Future'] = merged_df['BTCUSDT Future'] - merged_df['BTCUSDT Spot']

#         # Process each additional file if provided
#         if additional_files:
#             for i, file in enumerate(additional_files):
#                 additional_df = self.load_and_prepare_df(file, 'BTCUSD PERP Future', start_time, end_time)
#                 merged_df = pd.merge(merged_df, additional_df, on='Time', how='left')
                
#                 merged_df['Basis BTCUSD PERP Future'] = merged_df['BTCUSD PERP Future'] - merged_df['BTCUSDT Spot']

#         # Optionally save the final DataFrame to a CSV file
#         if save_path:
#             merged_df.to_csv(save_path, index=False)
#             print(f"Final data saved to {save_path}")

#         # Print the final DataFrame to the console
#         print("Final Processed DataFrame:")
#         print(merged_df.head())

#         return merged_df

# from helperFunctions import DataHandling

# # Define your time range
# start = 1625097600000  # 1 July 2021 00:00:00
# end = 1719792000000    # 1 July 2024 00:00:00

# # Initialize the DataHandling class with the exchange
# data_handler = DataHandling(exchange="binance")

# # Fetch funding rate history for BTC/USDT perpetual futures and save to CSV
# data_handler.fetch_funding_rate_history_to_csv(
#     symbol="BTC/USDT:USDT",
#     limit=1000,
#     start_time=start,
#     end_time=end,
#     file_path='./data/processed/Binance_BTCUSDT_Funding_Rate.csv'
# )

# # Fetch funding rate history for BTCUSD perpetual futures and save to CSV
# data_handler.fetch_funding_rate_history_to_csv(
#     symbol="BTCUSD_PERP",
#     limit=1000,
#     start_time=start,
#     end_time=end,
#     file_path='./data/processed/Binance_BTCUSD_PERP_Funding_Rate.csv'
# )

# # Process and calculate basis using the spot and futures price data
# data_handler.process_and_calculate_basis(
#     spot_file='./data/raw/Binance/Binance_BTCUSDT_1h.csv',
#     future_file='./data/raw/Binance/BTCUSDT_Binance_futures_UM_hour.csv',
#     additional_files=['./data/raw/Binance/BTCUSD_PERP_Binance_futures_CM_hour.csv'],
#     save_path='./data/processed/Binance_BTC_Basis.csv',
#     start_time=start,
#     end_time=end
# )