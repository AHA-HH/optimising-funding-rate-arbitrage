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
        
        position_capital = self.portfolio.calculate_position_size()
        
        # Create a new long position
        new_long_position = Position(
            position_type='long',
            # position_size=position_capital,
            exchange=exchange,
            crypto=crypto,
            pair=spot_pair,
            margin=margin,
            open_time=time,
            quantity=position_capital / spot_price,
            open_price=spot_price
        )
        
        collateral = new_long_position.quantity * new_long_position.open_price
        
        # print(collateral)
        
        self.portfolio.open_position(new_long_position)
        
        self.portfolio.unallocated_capital -= position_capital
        
        # future_pair = entry_signal['pair']
        # future_market = entry_signal['contract']
        # future_price = entry_signal['open_price']
        # if future_pair == 'BTCUSDT' or future_pair == 'ETHUSDT':
        #     margin = 'usd'
        # elif future_pair == 'BTCUSDCM' or future_pair == 'ETHUSDCM':
        #     margin = 'coin'
        # else:
        #     raise ValueError("Invalid future pair.")
        
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
        
        # print(new_short_position.quantity)
    
                
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
        
            collateral_used = close_short_position.quantity * close_price
            
            # if close_short_position:
            self.portfolio.close_position(close_short_position, close_price, time)
            
            
        spot_filter = self.df[(self.df['time'] == time) & (self.df['contract'] == 'spot') & (self.df['exchange'] == exchange) & (self.df['crypto'] == crypto)]
        spot_pair = spot_filter['pair'].values[0]
        spot_market = spot_filter['contract'].values[0]
        spot_price = spot_filter['open'].values[0]
        
        
        close_long_position = self.portfolio.find_open_position(crypto, spot_pair, exchange, 'long', margin)
        
        if close_long_position is not None:
        
            capital_returned = close_long_position.quantity * spot_price

            
            # if close_long_position:
            self.portfolio.close_position(close_long_position, spot_price, time)
            
            self.portfolio.unallocated_capital += capital_returned
            
    
    def calculate_funding_rate_payment(self, position: Position, current_time) -> float:
        """
        Calculate the funding rate payment for a given position.
        """
        # position.exchange
        # position.pair
        # position.margin
        # position.quantity
        
        matching_row = self.df[
            (self.df['time'] == current_time) & 
            (self.df['exchange'] == position.exchange) & 
            (self.df['pair'] == position.pair)
        ]
        
        if not matching_row.empty:
            funding_rate = matching_row['funding rate'].values[0]
            # print(funding_rate)
            if position.margin == 'usd':
                mark_price = matching_row['open'].values[0]
                funding_fee = funding_rate * position.quantity * mark_price
            elif position.margin == 'coin':
                funding_fee = funding_rate * position.quantity
            self.portfolio.fr_capital += funding_fee
            return funding_fee
        
        
        
    def run(self):
        """
        Run the backtest.
        """
        timestamps = self.df['time'].unique()
        print(self.portfolio.initial_capital)
        
        # for current_time in timestamps:
        for current_time in timestamps[0:10]:
            print(current_time)
            for position in self.portfolio.get_open_short_positions():
                funding_rate_payment = self.calculate_funding_rate_payment(position, current_time)
                # print(funding_rate_payment)
            for signal in self.generate_entry_signals(current_time):
                if self.check_entry_signal(signal) == True:
                    # self.open_long_position(signal)
                    # self.open_short_position(signal)
                    self.open_positions(signal)
            for signal in self.generate_exit_signals(current_time):
                    self.close_positions(signal)
                    
        print(self.portfolio.unallocated_capital)
        print(self.portfolio.fr_capital)
                    
        # print(f"Total number of trades executed: {self.portfolio.trade_count}")
        # print(f"Total number of trades opened: {self.portfolio.trade_open_count}")
        # print(f"Total number of trades closed: {self.portfolio.trade_close_count}")
        
        # print(self.portfolio.get_open_positions())
        # print(self.portfolio.get_closed_positions())
        # print(self.portfolio.get_open_short_positions())
        
        # for position in self.portfolio.positions:
        #     print(position)
                
        # print("Backtest completed.")