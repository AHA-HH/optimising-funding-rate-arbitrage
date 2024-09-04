import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helperFunctions.position import Position
from helperFunctions.portfolio import Portfolio

class Strategy:
    """
    Class for conducting a backtest of a funding rate trading strategy across multiple exchanges and assets.
    """
    def __init__(
        self,
        filepath: str,
        entry_threshold: float,
        exit_threshold: float,
        capital: float = 0,
        
    ) -> None:
        
        self.filepath = filepath
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.capital = capital
        
        self.df = pd.read_csv(filepath)
        self.portfolio = Portfolio(initial_capital=capital)

        
    def generate_entry_signals(self, current_time) -> None:
        """
        Identify buy opportunity based on the funding rate.
        """
        time_filter = self.df['time'] == current_time
        perp_filter = self.df['contract'] == 'perpetual'
        fr_filter = self.df[time_filter & perp_filter]
        
        buy_opp = fr_filter[fr_filter['funding rate'] > self.entry_threshold]
        
        entry_signals = []
        
        if not buy_opp.empty:
            for _, row in buy_opp.iterrows():
                entry_signal = {
                    'exchange': row['exchange'],
                    'crypto': row['crypto'],
                    'pair': row['pair'],
                    'contract': row['contract'],
                    'open_price': row['open'],
                    'close_price': row['close'],
                    'funding_rate': row['funding rate'],
                    'time': row['time']
                }
                entry_signals.append(entry_signal)
        return entry_signals
    
    
    def check_entry_signal(self, entry_signal) -> bool:
        """
        Generate entry signal based on the funding rate.
        """
        exchange = entry_signal['exchange']
        crypto = entry_signal['crypto']
        pair = entry_signal['pair']
        contract = entry_signal['contract']
        open_price = entry_signal['open_price']
        close_price = entry_signal['close_price']
        funding_rate = entry_signal['funding_rate']
        time = entry_signal['time']
        
        # if logic to determine whether a position is already open etc etc to see if signal should be acted upon
        if exchange == 'binance':
            return True
        else:
            return False
        
        
    def open_positions(self, entry_signal) -> None:
        """
        Open long and corresponding short position based on the entry signals.
        """
        time = entry_signal['time']
        exchange = entry_signal['exchange']
        crypto = entry_signal['crypto']
        future_pair = entry_signal['pair']
        # future_market = entry_signal['contract']
        future_price = entry_signal['open_price']
        
        spot_filter = self.df[(self.df['time'] == time) & (self.df['contract'] == 'spot') & (self.df['exchange'] == exchange) & (self.df['crypto'] == crypto)]
        spot_pair = spot_filter['pair'].values[0]
        # spot_market = spot_filter['contract'].values[0]
        spot_price = spot_filter['open'].values[0]
        # future_pair = entry_signal['pair']
        if future_pair == 'BTCUSDT' or future_pair == 'ETHUSDT':
            margin = 'usd'
        elif future_pair == 'BTCUSDCM' or future_pair == 'ETHUSDCM':
            margin = 'coin'
        else:
            raise ValueError("Invalid future pair.")
        
        # position_capital = self.portfolio.calculate_position_size()
        position_capital = self.capital
        
        # Create a new long position
        new_long_position = Position(
            position_type='long',
            exchange=exchange,
            crypto=crypto,
            pair=spot_pair,
            margin=margin,
            open_time=time,
            quantity=position_capital / spot_price,
            open_price=spot_price
        )
        
        collateral = new_long_position.quantity * new_long_position.open_price
        
        self.portfolio.open_position(new_long_position)
        
        # Create a new short position
        new_short_position = Position(
            position_type='short',
            exchange=exchange,
            crypto=crypto,
            pair=future_pair,
            margin=margin,
            open_time=time,
            quantity=collateral / future_price,
            open_price=future_price
        )
        
        self.portfolio.open_position(new_short_position)
        
    
    def generate_exit_signals(self, current_time) -> None:
        """
        Identify sell opportunity based on the funding rate.
        """
        time_filter = self.df['time'] == current_time
        perp_filter = self.df['contract'] == 'perpetual'
        fr_filter = self.df[time_filter & perp_filter]
        
        sell_opp = fr_filter[fr_filter['funding rate'] < self.exit_threshold]
        
        exit_signals = []
        
        if not sell_opp.empty:
            for _, row in sell_opp.iterrows():
                exit_signal = {
                    'exchange': row['exchange'],
                    'crypto': row['crypto'],
                    'pair': row['pair'],
                    'contract': row['contract'],
                    'open_price': row['open'],
                    'close_price': row['close'],
                    'funding_rate': row['funding rate'],
                    'time': row['time']
                }
                exit_signals.append(exit_signal)
        return exit_signals
    

    def close_positions(self, exit_signal) -> None:
        """
        Close short and corresponding long position based on the exit signals.
        """
        time = exit_signal['time']
        exchange = exit_signal['exchange']
        crypto = exit_signal['crypto']
        close_price = exit_signal['open_price']
        future_pair = exit_signal['pair']
        
        if future_pair == 'BTCUSDT' or future_pair == 'ETHUSDT':
            margin = 'usd'
        elif future_pair == 'BTCUSDCM' or future_pair == 'ETHUSDCM':
            margin = 'coin'
        else:
            raise ValueError("Invalid future pair.")
        
        close_short_position = self.portfolio.find_open_position(crypto, future_pair, exchange, 'short', margin)
        
        if close_short_position is not None:
            self.portfolio.close_position(close_short_position, close_price, time)
            
            
        spot_filter = self.df[(self.df['time'] == time) & (self.df['contract'] == 'spot') & (self.df['exchange'] == exchange) & (self.df['crypto'] == crypto)]
        spot_pair = spot_filter['pair'].values[0]
        spot_market = spot_filter['contract'].values[0]
        spot_price = spot_filter['open'].values[0]
        
        
        close_long_position = self.portfolio.find_open_position(crypto, spot_pair, exchange, 'long', margin)
        
        if close_long_position is not None:
            self.portfolio.close_position(close_long_position, spot_price, time)

        
    def run(self):
        """
        Run the backtest.
        """
        timestamps = self.df['time'].unique()
        # # print(self.portfolio.initial_capital)
        
        # loop through all timestamps
        # for current_time in timestamps:
        for current_time in timestamps[0:1]:
            print(current_time)
            
            
            # look for open short positions and calculate funding rate payments
            for short_position in self.portfolio.get_open_short_positions():
                long_position = self.portfolio.get_corresponding_long_position(short_position)
                self.portfolio.calculate_funding_payment_and_pnl_interval(self.df, short_position, long_position, current_time)
                
                
            # look for negative funding rates and close positions that match the signal
            for signal in self.generate_exit_signals(current_time):
                # if signal is in self.portfolio.get_open_short_positions(): then close positions, should come before entry signals
                    self.close_positions(signal)
                
                
            # calculate notional value of portfolio and the max position size
            collateral_notional = self.portfolio.calculate_collateral_values(self.df, current_time)
            max_position_size = self.portfolio.calculate_max_portfolio_value_weightings(collateral_notional)
            print(max_position_size['assets']['binance']['BTC']['max_value'])
            
            
            # look for positive funding rates and open positions that match the signal
            for signal in self.generate_entry_signals(current_time):
                if self.check_entry_signal(signal) == True:
                    
                    self.open_positions(signal)
                    
            # self.portfolio.calculate_collateral_values(self.df, current_time)
                    
        # print(self.portfolio.logger.get_logs(log_type='trades'))
                    
        print(f"Total number of trades executed: {self.portfolio.trade_count}")
        print(f"Total number of trades opened: {self.portfolio.trade_open_count}")
        print(f"Total number of trades closed: {self.portfolio.trade_close_count}")
        
        trades_log = self.portfolio.logger.get_logs(log_type='trades')
        
        if trades_log:
            trades_df = pd.DataFrame(trades_log)
            trades_df.to_csv('./data/raw/trades_log.csv', index=False)
            print("Trades saved to 'trades_log.csv'.")
        
        
        funding_payments_log = self.portfolio.logger.get_logs(log_type='funding_payments')

        # Check if the log is not empty
        if funding_payments_log:
            # Convert the list of dictionaries to a DataFrame
            funding_payments_df = pd.DataFrame(funding_payments_log)
            
            # Sum the values in the 'funding payment' column
            total_funding_payments = funding_payments_df['funding payment'].sum()
            print(f"Total Funding Payments: {total_funding_payments}")
            # Save the DataFrame to a CSV file
            funding_payments_df.to_csv('./data/raw/funding_payments_log.csv', index=False)
            print("Funding payments saved to 'funding_payments_log.csv'.")
        else:
            print("No funding payments logged.")
        
        # print(self.portfolio.logger.get_logs(log_type='collateral_values'))
        # collateral_values = self.portfolio.logger.get_logs(log_type='collateral_values')

        # # Check if there are any logs to save
        # if collateral_values:
        #     # Convert the list of logs to a DataFrame
        #     df_collateral = pd.DataFrame(collateral_values)

        #     # Save the DataFrame to a CSV file
        #     df_collateral.to_csv('collateral_values_log.csv', index=False)
        #     print("Collateral values saved to 'collateral_values_log.csv'.")
        # else:
        #     print("No collateral values logged yet.")

        
        # for position in self.portfolio.positions:
        #     print(position)
                
        print("Backtest completed.")