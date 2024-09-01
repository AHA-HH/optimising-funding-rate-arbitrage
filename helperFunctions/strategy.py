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
        self.portfolio = Portfolio()
        
    # @staticmethod
    def get_exchange_fee_rate(self, exchange: str, trade: str, margin: str) -> float:
        if exchange == "binance":
            if trade == "spot":
                return 0.001
            elif trade == "futures":
                if margin == "usd":
                    return 0.0005
                elif margin == "coin":
                    return 0.0005
        
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
        
        
    def open_long_position(self, entry_signal) -> None:
        """
        Open a long position in spot market based on the entry signal.
        """
        time = entry_signal['time']
        exchange = entry_signal['exchange']
        crypto = entry_signal['crypto']
        
        spot_filter = self.df[(self.df['time'] == time) & (self.df['contract'] == 'spot') & (self.df['exchange'] == exchange) & (self.df['crypto'] == crypto)]
        spot_pair = spot_filter['pair'].values[0]
        spot_market = spot_filter['contract'].values[0]
        spot_price = spot_filter['open'].values[0]
        future_pair = entry_signal['pair']
        if future_pair == 'BTCUSDT' or future_pair == 'ETHUSDT':
            margin = 'usd'
        elif future_pair == 'BTCUSDCM' or future_pair == 'ETHUSDCM':
            margin = 'coin'
        else:
            raise ValueError("Invalid future pair.")
        
        # Create a new position
        new_position = Position(
            position_type='long',
            exchange=exchange,
            crypto=crypto,
            pair=spot_pair,
            margin=margin,
            open_time=time,
            quantity=self.capital / spot_price,
            open_price=spot_price
        )
        
        self.portfolio.open_position(new_position)
        
        
    def open_short_position(self, entry_signal) -> None:
        """
        Open a short position in perpetual futures market based on the entry signal.
        """
        time = entry_signal['time']
        exchange = entry_signal['exchange']
        crypto = entry_signal['crypto']
        
        future_pair = entry_signal['pair']
        future_market = entry_signal['contract']
        future_price = entry_signal['open_price']
        if future_pair == 'BTCUSDT' or future_pair == 'ETHUSDT':
            margin = 'usd'
        elif future_pair == 'BTCUSDCM' or future_pair == 'ETHUSDCM':
            margin = 'coin'
        else:
            raise ValueError("Invalid future pair.")
        
        # Create a new position
        new_position = Position(
            position_type='short',
            exchange=exchange,
            crypto=crypto,
            pair=future_pair,
            margin=margin,
            open_time=time,
            quantity=self.capital / future_price,
            open_price=future_price
        )
        
        self.portfolio.open_position(new_position)
        
    
    # def open_positions(self, entry_signals) -> None:
    #     """
    #     Open long and short positions based on the entry signals.
    #     """
    #     for signal in entry_signals:
    #         if self.check_entry_signal(signal) == True:
    #             self.open_long_position(signal)
    #             self.open_short_position(signal)
    
                
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
    
    
    def close_short_position(self, exit_signal) -> None:
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
        
        position = self.portfolio.find_open_position(crypto, exit_signal['pair'], exchange, 'short', margin)
        if position:
            self.portfolio.close_position(position, close_price, time)
            
    
    def close_long_position(self, exit_signal) -> None:
        time = exit_signal['time']
        exchange = exit_signal['exchange']
        crypto = exit_signal['crypto']
        # close_price = exit_signal['open_price']
        future_pair = exit_signal['pair']
        spot_filter = self.df[(self.df['time'] == time) & (self.df['contract'] == 'spot') & (self.df['exchange'] == exchange) & (self.df['crypto'] == crypto)]
        spot_pair = spot_filter['pair'].values[0]
        spot_market = spot_filter['contract'].values[0]
        spot_price = spot_filter['open'].values[0]
        
        if future_pair == 'BTCUSDT' or future_pair == 'ETHUSDT':
            margin = 'usd'
        elif future_pair == 'BTCUSDCM' or future_pair == 'ETHUSDCM':
            margin = 'coin'
        else:
            raise ValueError("Invalid future pair.")
        
        position = self.portfolio.find_open_position(crypto, spot_pair, exchange, 'long', margin)
        if position:
            self.portfolio.close_position(position, spot_price, time)


    # def close_positions(self, exit_signals) -> None:
    #     """
    #     Close short and long positions based on the exit signals.
    #     """
    #     for signal in exit_signals:
    #         self.close_short_position(signal)
    #         self.close_long_position(signal)
        
        
    def run(self):
        """
        Run the backtest.
        """
        timestamps = self.df['time'].unique()
        
        for current_time in timestamps:
        # for current_time in timestamps[0:10]:
            print(current_time)
            for signal in self.generate_entry_signals(current_time):
                if self.check_entry_signal(signal) == True:
                    self.open_long_position(signal)
                    self.open_short_position(signal)
            # print(self.generate_exit_signals(current_time))
            for signal in self.generate_exit_signals(current_time):
                    self.close_short_position(signal)
                    self.close_long_position(signal)
                    
        print(f"Total number of trades executed: {self.portfolio.trade_count}")
        print(f"Total number of open trades: {self.portfolio.trade_open_count}")
        print(f"Total number of closed trades: {self.portfolio.trade_close_count}")
        # for position in self.portfolio.positions:
        #     print(position)
                
        print("Backtest completed.")