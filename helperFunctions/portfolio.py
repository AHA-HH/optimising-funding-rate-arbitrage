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
        self.unallocated_weight_range = {'min': 0.1, 'max': 0.2} # 10-20% of each exchanged unallocated for flexibility and risk management
        
        self.asset_weight_ranges = {
            'binance': {
                'bitcoin': {'min': 0.1, 'max': 0.6},
                'ethereum': {'min': 0.05, 'max': 0.3}
            },
            'okx': {
                'bitcoin': {'min': 0.1, 'max': 0.65},
                'ethereum': {'min': 0.1, 'max': 0.65}
            },
            'bybit': {
                'bitcoin': {'min': 0.1, 'max': 0.55},
                'ethereum': {'min': 0.05, 'max': 0.35}
            }
        }
        
        self.crypto_weight_ranges = {
            'bitcoin': {'min': 0.0, 'max': 0.60},
            'ethereum': {'min': 0.0, 'max': 0.45}
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
            
            new_notional_short = short_position.quantity * short_current_price
            
            if short_position.margin == 'usd':
                funding_payment = funding_rate * nominal_position_value
            elif short_position.margin == 'coin':
                # funding_payment = funding_rate * short_position.quantity
                funding_payment_coin = funding_rate * short_position.quantity
                funding_payment = funding_payment_coin * short_current_price
            
        matching_row_long = df[
            (df['time'] == time) & 
            (df['exchange'] == long_position.exchange) & 
            (df['pair'] == long_position.pair)
        ]
        
        if not matching_row_long.empty:
            long_current_price = matching_row_long['open'].values[0]
            pnl_long = (long_current_price - long_position.open_price) * long_position.quantity
            
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
        # Use local variables to avoid changing the instance variables
        bin_liquid = 0 if self.binance_liquid_cash < 1 else self.binance_liquid_cash
        bin_btc = 0 if self.binance_btc_collateral < 1 else self.binance_btc_collateral
        bin_eth = 0 if self.binance_eth_collateral < 1 else self.binance_eth_collateral

        okx_liquid = 0 if self.okx_liquid_cash < 1 else self.okx_liquid_cash
        okx_btc = 0 if self.okx_btc_collateral < 1 else self.okx_btc_collateral
        okx_eth = 0 if self.okx_eth_collateral < 1 else self.okx_eth_collateral

        byb_liquid = 0 if self.bybit_liquid_cash < 1 else self.bybit_liquid_cash
        byb_btc = 0 if self.bybit_btc_collateral < 1 else self.bybit_btc_collateral
        byb_eth = 0 if self.bybit_eth_collateral < 1 else self.bybit_eth_collateral
        
        self.logger.log_collateral(
            time, 
            bin_btc, 
            bin_eth, 
            bin_liquid, 
            okx_btc, 
            okx_eth, 
            okx_liquid, 
            byb_btc, 
            byb_eth, 
            byb_liquid)


    def calculate_portfolio_notional_value(self):
        self.binance_notional = self.binance_liquid_cash + self.binance_btc_collateral + self.binance_eth_collateral
        self.okx_notional = self.okx_liquid_cash + self.okx_btc_collateral + self.okx_eth_collateral
        self.bybit_notional = self.bybit_liquid_cash + self.bybit_btc_collateral + self.bybit_eth_collateral
        self.portfolio_notional = self.binance_notional + self.okx_notional + self.bybit_notional
        return self.portfolio_notional


    def calculate_position_size(self, exchange: str, crypto: str, pair: str):
        """
        Calculate the size of each position based on the current value of the portfolio.
        """
            
        # Calculate the total collateral for each exchange
        exchange_collaterals = {
            'binance': self.binance_liquid_cash + self.binance_btc_collateral + self.binance_eth_collateral,
            'okx': self.okx_liquid_cash + self.okx_btc_collateral + self.okx_eth_collateral,
            'bybit': self.bybit_liquid_cash + self.bybit_btc_collateral + self.bybit_eth_collateral
        }

        # Get the collateral for the specific exchange
        collateral = exchange_collaterals[exchange]
        
        # Get the liquid cash available for the specific exchange
        total_liquid_cash = 0
        if exchange == 'binance':
            total_liquid_cash = self.binance_liquid_cash
        elif exchange == 'okx':
            total_liquid_cash = self.okx_liquid_cash
        elif exchange == 'bybit':
            total_liquid_cash = self.bybit_liquid_cash
            
        # Get the collateral already used in the specific asset    
        collateral_in_asset = 0
        if exchange == 'binance':
            if crypto == 'bitcoin':
                collateral_in_asset = self.binance_btc_collateral
            elif crypto == 'ethereum':
                collateral_in_asset = self.binance_eth_collateral
        elif exchange == 'okx':
            if crypto == 'bitcoin':
                collateral_in_asset = self.okx_btc_collateral
            elif crypto == 'ethereum':
                collateral_in_asset = self.okx_eth_collateral
        elif exchange == 'bybit':
            if crypto == 'bitcoin':
                collateral_in_asset = self.bybit_btc_collateral
            elif crypto == 'ethereum':
                collateral_in_asset = self.bybit_eth_collateral

        # Calculate liquid cash ranges based on notional value of exchange
        liquid_cash_min = self.unallocated_weight_range['min'] * collateral
        liquid_cash_max = self.unallocated_weight_range['max'] * collateral
        
        liquid_cash_available_safe = total_liquid_cash - liquid_cash_max
        liquid_cash_available_risky = total_liquid_cash - liquid_cash_min
        
        # Calculate the max value for the crypto asset based on its weighting range
        asset_max_value = self.asset_weight_ranges[exchange][crypto]['max'] * collateral
        asset_min_value = self.asset_weight_ranges[exchange][crypto]['min'] * collateral
        
        position_size = 0
        # usd margin positions max position size
        if pair == 'BTCUSDT' or pair == 'ETHUSDT':
            max_position_size = asset_max_value
        # coin margin positions 5th of the max position size
        elif pair == 'BTCUSDCM' or pair == 'ETHUSDCM':
            max_position_size = asset_max_value / 4
            
        # Check if the new position would exceed the safe limit
        if max_position_size <= liquid_cash_available_safe:
            # Now check if the new position would exceed the allowed asset allocation
            if collateral_in_asset + max_position_size <= asset_max_value:
                position_size = max_position_size
            else:
                # Adjust position size if it exceeds asset max value
                adjusted_position_size = asset_max_value - collateral_in_asset
                if adjusted_position_size >= asset_min_value:
                    position_size = adjusted_position_size
        # If we cannot meet the safe limit, check if we can use the risky limit
        elif liquid_cash_available_safe < max_position_size <= liquid_cash_available_risky:
            if collateral_in_asset + max_position_size <= asset_max_value:
                position_size = max_position_size
            else:
                adjusted_position_size = asset_max_value - collateral_in_asset
                if adjusted_position_size >= asset_min_value:
                    position_size = adjusted_position_size
        elif max_position_size > liquid_cash_available_risky:
            if collateral_in_asset + liquid_cash_available_risky <= asset_max_value:
                position_size = liquid_cash_available_risky
            else:
                adjusted_position_size = asset_max_value - collateral_in_asset
                if adjusted_position_size >= asset_min_value:
                    position_size = adjusted_position_size

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
    