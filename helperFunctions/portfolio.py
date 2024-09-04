import pandas as pd

from helperFunctions.position import Position
from helperFunctions.logging import Logger

class Portfolio:
    def __init__(self, initial_capital: float = 0) -> None:
        self.positions = []  # List to hold all positions
        self.trade_count = 0  # Total number of trades
        self.trade_open_count = 0  # Number of open trades
        self.trade_close_count = 0  # Number of closed trades
        
        # Set weight ranges for portfolio allocation
        self.unallocated_weight_range = {'min': 0.1, 'max': 0.25}
    
        self.exchange_weight_range = {
                    'binance': {'min': 0.0, 'max': 0.6},
                    'okx': {'min': 0.0, 'max': 0.4},
                    'bybit': {'min': 0.0, 'max': 0.3} 
        }
        
        self.asset_weight_ranges = {
            'binance': {
                'BTC': {'min': 0.0, 'max': 0.42}, # 70% of binance capital in BTC
                'ETH': {'min': 0.0, 'max': 0.24}, # 40% of binance capital in ETH
                'liquid_cash': {'min': 0.0, 'max': 0.6} # 100% of binance capital in liquid cash
            },
            'okx': {
                'BTC': {'min': 0.0, 'max': 0.32}, # 80% of okx capital in BTC
                'ETH': {'min': 0.0, 'max': 0.3}, # 75% of okx capital in ETH
                'liquid_cash': {'min': 0.0, 'max': 0.4} # 100% of okx capital in liquid cash
            },
            'bybit': {
                'BTC': {'min': 0.0, 'max': 0.18}, # 60% of bybit capital in BTC
                'ETH': {'min': 0.0, 'max': 0.15}, # 50% of bybit capital in ETH
                'liquid_cash': {'min': 0.0, 'max': 0.3} # 100% of bybit capital in liquid cash
            }
        }
        
        self.crypto_weight_ranges = {
            'BTC': {'min': 0.0, 'max': 0.60}, # 60% of total capital in BTC and 65% of potential max BTC allocation
            'ETH': {'min': 0.0, 'max': 0.45}, # 45% of total capital in ETH and 65% of potential max ETH allocation
            'liquid_cash': {'min': 0.0, 'max': 1.0}
        }
        
        self.initial_capital = initial_capital
        
        self.binance_btc_collateral = 0
        self.binance_eth_collateral = 0
        self.binance_usdt_collateral = 0
        
        
        self.logger = Logger()
                

    def find_open_position(self, crypto: str, pair: str, exchange: str, position_type: str, margin: str):
        """
        Check if there's already an open position for the given asset, pair, exchange, and position type.
        """
        for position in self.positions:
            if (position.crypto == crypto and
                position.pair == pair and
                position.exchange == exchange and
                position.position_type == position_type and
                position.margin == margin and
                not position.closed):
                return position
        return None
    

    def open_position(self, position: Position):
        """
        Open a new position and add it to the portfolio.
        """
        if self.find_open_position(position.crypto, position.pair, position.exchange, position.position_type, position.margin) is None:
            self.positions.append(position)
            self.trade_count += 1
            self.trade_open_count += 1
            self.logger.log_trade(position, 'open')


    def close_position(self, position: Position, close_price: float, close_time: str):
        """
        Close an existing position.
        """
        position.close_price = close_price
        position.close_time = close_time
        position.closed = True
        self.trade_count += 1
        self.trade_close_count += 1
        self.logger.log_trade(position, 'close')


    def get_open_positions(self):
        """
        Return a list of all open positions.
        """
        return [position for position in self.positions if not position.closed]


    def get_closed_positions(self):
        """
        Return a list of all closed positions.
        """
        return [position for position in self.positions if position.closed]
    
    
    def get_open_short_positions(self):
        """
        Return a list of all open short positions.
        """
        return [position for position in self.positions if not position.closed and position.position_type == "short"]
    
    
    def get_open_long_positions(self, action: str):
        """
        Return a list of all open long positions.
        """
        if action == 'open':
            return [position for position in self.positions if not position.closed and position.position_type == "long"]
        elif action == 'closed':
            return [position for position in self.positions if position.closed and position.position_type == "long"]
    
    
    def get_corresponding_long_position(self, short_position: Position):
        """
        Find the corresponding long position for a given short position.
        """
        for position in self.positions:
            if (position.open_time == short_position.open_time and
                position.crypto == short_position.crypto and
                position.exchange == short_position.exchange and
                position.position_type == "long" and
                not position.closed):
                return position
        return None
    
    
    def calculate_funding_payment_and_pnl_interval(self, df: pd.DataFrame, short_position: Position, long_position: Position, time) -> float:
        """
        Calculate the funding rate payment and pnl for a given position at funding rate interval.
        """
        matching_row_short = df[
            (df['time'] == time) & 
            (df['exchange'] == short_position.exchange) & 
            (df['pair'] == short_position.pair)
        ]
        
        if not matching_row_short.empty:
            funding_rate = matching_row_short['funding rate'].values[0]
            short_current_price = matching_row_short['open'].values[0]
            nominal_position_value = short_position.quantity * short_current_price
            
            pnl_short = (short_position.open_price - short_current_price) * short_position.quantity
            
            if short_position.margin == 'usd':
                funding_payment = funding_rate * nominal_position_value
            elif short_position.margin == 'coin':
                funding_payment = funding_rate * short_position.quantity
            
        matching_row_long = df[
            (df['time'] == time) & 
            (df['exchange'] == long_position.exchange) & 
            (df['pair'] == long_position.pair)
        ]
        
        if not matching_row_long.empty:
            long_current_price = matching_row_long['open'].values[0]
            pnl_long = (long_current_price - long_position.open_price) * long_position.quantity
            
        pnl = pnl_long + pnl_short
        
        self.logger.log_funding_payment_and_pnl(time, short_position, funding_payment, pnl)
        
        return funding_payment, pnl
        
        
    def calculate_collateral_values(self, df: pd.DataFrame, time: str):
        """
        Calculate the current collateral values of the portfolio.
        """
        # self.binance_btc_collateral = 0
        # self.binance_eth_collateral = 0
        # self.binance_usdt_collateral = 0
        
        # new_open_positions = [pos for pos in self.positions if not pos.closed and pos.open_time == time and pos.position_type == 'long']
        # for position in new_open_positions:
        #     position_value = position.quantity * position.open_price
        #     if position.crypto == 'bitcoin':
        #         if position.exchange == 'binance':
        #             self.unallocated_collateral -= position_value
        #             self.binance_btc_collateral += position_value
        #     elif position.crypto == 'ethereum':
        #         if position.exchange == 'binance':
        #             self.unallocated_collateral -= position_value
        #             self.binance_eth_collateral += position_value
        
        # open_positions = [pos for pos in self.positions if not pos.closed and not pos.open_time == time and pos.position_type == 'long']
        # for position in open_positions:
        #     matching_row = df[
        #         (df['time'] == time) & 
        #         (df['exchange'] == position.exchange) & 
        #         (df['pair'] == position.pair)
        #     ]
            
        #     if not matching_row.empty:
        #         current_price = matching_row['open'].values[0]
        #         position_value = position.quantity * current_price
        #         if position.crypto == 'bitcoin':
        #             if position.exchange == 'binance':
        #                 self.binance_btc_collateral += position_value
        #         elif position.crypto == 'ethereum':
        #             if position.exchange == 'binance':
        #                 self.binance_eth_collateral += position_value
                
        # closed_positions = [pos for pos in self.positions if pos.closed and pos.close_time == time and pos.position_type == 'long']
        # for position in closed_positions:
        #     position_value = position.quantity * position.close_price
        #     if position.crypto == 'bitcoin':
        #         if position.exchange == 'binance':
        #             # self.binance_btc_collateral -= position_value
        #             # self.binance_usdt_collateral += position_value
        #             self.unallocated_collateral += position_value
        #     elif position.crypto == 'ethereum':
        #         if position.exchange == 'binance':
        #             # self.binance_eth_collateral -= position_value
        #             # self.binance_usdt_collateral += position_value
        #             self.unallocated_collateral += position_value
        
        # self.logger.log_collateral(time, self.binance_btc_collateral, self.binance_eth_collateral, self.binance_usdt_collateral, self.unallocated_collateral)
        
        # return self.binance_btc_collateral, self.binance_eth_collateral, self.binance_usdt_collateral, self.unallocated_collateral
        unallocated_capital = self.initial_capital
        collateral_notional = unallocated_capital
        return collateral_notional
    
    
    def calculate_max_portfolio_value_weightings(self, value: float):
        """
        Calculate the ideal portfolio value weightings for unallocated capital, exchanges, and assets
        based on the current portfolio value.
        
        Parameters:
        value (float): The total value of the portfolio.
        
        Returns:
        dict: A dictionary containing the ideal weightings for unallocated capital, each exchange, and each asset.
        """
        
        weightings = {
            'unallocated': {},
            'exchanges': {},
            'assets': {}
        }
        
        # Calculate ideal weight for unallocated capital
        unallocated_min = self.unallocated_weight_range['min'] * value
        unallocated_max = self.unallocated_weight_range['max'] * value
        weightings['unallocated'] = {'min_value': unallocated_min, 'max_value': unallocated_max}
        
        # Calculate ideal weight for each exchange
        for exchange, ranges in self.exchange_weight_range.items():
            min_value = ranges['min'] * value
            max_value = ranges['max'] * value
            weightings['exchanges'][exchange] = {'min_value': min_value, 'max_value': max_value}
        
        # Calculate ideal weight for each asset within each exchange
        for exchange, assets in self.asset_weight_ranges.items():
            weightings['assets'][exchange] = {}
            for asset, ranges in assets.items():
                min_value = ranges['min'] * value
                max_value = ranges['max'] * value
                weightings['assets'][exchange][asset] = {'min_value': min_value, 'max_value': max_value}
        
        return weightings


    def calculate_position_size(self):
        """
        Calculate the size of each position based on the current value of the portfolio.
        """

        pass
    

    
    def check_delta_neutral(self):
        """
        Check if the portfolio is delta neutral.
        """
        pass
    
    
    def adjust_positions(self):
        """
        Adjust the positions in the portfolio to maintain delta neutrality.
        """
        pass
    
    
    def calculate_portfolio_weighting(self):
        """
        Calculate the current weighting of each asset in the portfolio.
        """
        pass
    
    
    def rebalance_portfolio(self):
        """
        Rebalance the portfolio based on the current weighting of each asset.
        """
        pass
    