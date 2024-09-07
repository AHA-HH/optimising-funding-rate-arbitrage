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
                    'binance': {'min': 0.0, 'max': 0.6}, # based on market share for exchanges
                    'okx': {'min': 0.0, 'max': 0.2},
                    'bybit': {'min': 0.0, 'max': 0.2} 
        }
        
        self.asset_weight_ranges = {
            'binance': {
                'bitcoin': {'min': 0.0, 'max': 0.42}, # 70% of binance capital in BTC
                'ethereum': {'min': 0.0, 'max': 0.24}, # 40% of binance capital in ETH
                'liquid_cash': {'min': 0.1, 'max': 1.0} # 100% of binance capital in liquid cash
            },
            'okx': {
                'bitcoin': {'min': 0.0, 'max': 0.15}, # 75% of okx capital in BTC
                'ethereum': {'min': 0.0, 'max': 0.15}, # 75% of okx capital in ETH
                'liquid_cash': {'min': 0.1, 'max': 1.0} # 100% of okx capital in liquid cash
            },
            'bybit': {
                'bitcoin': {'min': 0.0, 'max': 0.12}, # 60% of bybit capital in BTC
                'ethereum': {'min': 0.0, 'max': 0.1}, # 50% of bybit capital in ETH
                'liquid_cash': {'min': 0.1, 'max': 1.0} # 100% of bybit capital in liquid cash
            }
        }
        
        self.crypto_weight_ranges = {
            'bitcoin': {'min': 0.0, 'max': 0.60}, # 60% of total capital in BTC and 65% of potential max BTC allocation
            'ethereum': {'min': 0.0, 'max': 0.45}, # 45% of total capital in ETH and 65% of potential max ETH allocation
            'liquid_cash': {'min': 0.1, 'max': 1.0}
        }
        
        self.initial_capital = initial_capital
        
        self.binance_liquid_cash = 0
        
        self.okx_liquid_cash = 0 
        
        self.bybit_liquid_cash = 0
        
        self.binance_btc_collateral = 0
        self.binance_eth_collateral = 0
        
        self.okx_btc_collateral = 0
        self.okx_eth_collateral = 0
        
        self.bybit_btc_collateral = 0
        self.bybit_eth_collateral = 0
        
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
        position.close_transaction_cost = position.quantity * close_price * position.transaction_cost_pct
        position.close_time = close_time
        position.close_value = (position.quantity * close_price) - position.close_transaction_cost
        if position.position_type == 'long':
            position.pnl = position.close_value - position.open_value
        elif position.position_type == 'short':
            position.pnl = position.open_value - position.close_value
        position.closed = True
        # position.close(close_time, close_price)
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
            
            # old_notional_short = short_position.quantity * short_position.open_price
            new_notional_short = short_position.quantity * short_current_price
            
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
            
            # old_notional_long = long_position.quantity * long_position.open_price
            new_notional_long = long_position.quantity * long_current_price
            
        pnl = pnl_long + pnl_short
        
        old_delta = long_position.open_value - short_position.open_value
        new_delta = new_notional_long - new_notional_short
        
        self.logger.log_funding_payment_and_pnl(time, short_position, funding_payment, pnl, old_delta, new_delta)
        
        return funding_payment, pnl, old_delta, new_delta
    
    
    def assign_initial_capital_to_exchanges(self):
        """
        Assign capital to a specific exchange.
        """
        self.binance_liquid_cash = 0.6 * self.initial_capital

        self.okx_liquid_cash = 0.2 * self.initial_capital

        self.bybit_liquid_cash = 0.2 * self.initial_capital
        
        if self.binance_liquid_cash + self.okx_liquid_cash + self.bybit_liquid_cash != self.initial_capital:
            raise Exception("Initial capital allocation to exchanges is incorrect")
        
        return self.binance_liquid_cash, self.okx_liquid_cash, self.bybit_liquid_cash
    
    
    def calculate_collateral_values(self, time: str):
        """
        Calculate the current collateral values of the portfolio.
        """
        self.logger.log_collateral(time, self.binance_btc_collateral, self.binance_eth_collateral, self.binance_liquid_cash, self.okx_btc_collateral, self.okx_eth_collateral, self.okx_liquid_cash, self.bybit_btc_collateral, self.bybit_eth_collateral, self.bybit_liquid_cash)
        print(self.binance_liquid_cash, self.binance_btc_collateral)


    def calculate_portfolio_notional_value(self):
        self.binance_notional = self.binance_liquid_cash + self.binance_btc_collateral + self.binance_eth_collateral
        self.okx_notional = self.okx_liquid_cash + self.okx_btc_collateral + self.okx_eth_collateral
        self.bybit_notional = self.bybit_liquid_cash + self.bybit_btc_collateral + self.bybit_eth_collateral
        self.portfolio_notional = self.binance_notional + self.okx_notional + self.bybit_notional
        return self.portfolio_notional
    
    
    def calculate_max_portfolio_value_weightings(self, portfolio_value: float):
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
        
        # Calculate max weight for unallocated capital
        unallocated_min = self.unallocated_weight_range['min'] * portfolio_value
        unallocated_max = self.unallocated_weight_range['max'] * portfolio_value
        weightings['unallocated'] = {'min_value': unallocated_min, 'max_value': unallocated_max}
        
        # Calculate max weight for each exchange
        for exchange, ranges in self.exchange_weight_range.items():
            min_value = ranges['min'] * portfolio_value
            max_value = ranges['max'] * portfolio_value
            weightings['exchanges'][exchange] = {'min_value': min_value, 'max_value': max_value}
        
        # Calculate max weight for each asset within each exchange
        for exchange, assets in self.asset_weight_ranges.items():
            weightings['assets'][exchange] = {}
            for asset, ranges in assets.items():
                min_value = ranges['min'] * portfolio_value
                max_value = ranges['max'] * portfolio_value
                weightings['assets'][exchange][asset] = {'min_value': min_value, 'max_value': max_value}
        
        return weightings


    def calculate_position_size(self, max_weightings: dict, exchange: str, crypto: str, pair: str):
        """
        Calculate the size of each position based on the current value of the portfolio.
        """
        position_size = 0
        # usd margin positions half of the max position size
        if pair == 'BTCUSDT' or pair == 'ETHUSDT':
            position_size = max_weightings['assets'][exchange][crypto]['max_value'] / 2
        # coin margin positions 5th of the max position size
        elif pair == 'BTCUSDCM' or pair == 'ETHUSDCM':
            position_size = max_weightings['assets'][exchange][crypto]['max_value'] / 5
        
        return position_size
    
    
    def get_exchange_transaction_fee_pct(self, exchange: str, trade: str, margin: str) -> float:
        if exchange == "binance":
            if trade == "spot":
                return 0.001
            elif trade == "futures":
                if margin == "usd":
                    return 0.0005
                elif margin == "coin":
                    return 0.0005

    
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
    