import ccxt
from datetime import datetime
import pandas as pd

class DataHandler:
    def __init__(self):
        pass

    def fetch_funding_rate_history_to_csv(self, exchange: str, symbol: str, limit: int, start_time: int, end_time: int, file_path: str) -> None:
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

    def load_and_prepare_df(self, file_path: str, price_label: str, start_time: int = None, end_time: int = None) -> pd.DataFrame:
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
        df = df[['Time', 'Close']]
        
        if start_time and end_time:
            df = df[(df['Time'] >= start_time) & (df['Time'] <= end_time)]
        
        df.rename(columns={'Close': price_label}, inplace=True)
        df = df[['Time', price_label]]
        df['Time'] = pd.to_datetime(df['Time'])
        df.sort_values(by='Time', inplace=True)
        df.reset_index(drop=True, inplace=True)
        
        return df
    
    def process_and_merge_df(self, df1, df2, save_path: str) -> pd.DataFrame:
        """
        Processes data from two CSV files, merges them, and generates new columns based on the data. The final DataFrame is saved to a specified location.

        Args:
            first_file (str): Path to the first CSV file.
            second_file (str): Path to the second CSV file.
            save_path (str): Path to save the final DataFrame as a new CSV file. Default is None.
            start_time (int): The start time as a Unix timestamp (in milliseconds). Default is None.
            end_time (int): The end time as a Unix timestamp (in milliseconds). Default is None.

        Returns:
            pd.DataFrame: The final processed DataFrame.
        """
        merged_df = pd.merge(df1, df2, on='Time')
        
        merged_df.to_csv(save_path, index=False)
        print(f"Final data saved to {save_path}")

        return merged_df