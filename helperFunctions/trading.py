import pandas as pd

class Trading:
    def __init__(self, entry_signal=0.00001, lookback_period=3, exit_signal=0):
        """
        Initializes the trading strategy with configurable parameters.

        Args:
            funding_rate_threshold (float): The threshold above which to consider entering a trade.
            lookback_period (int): The number of previous funding rate intervals to check for consistency.
        """
        self.entry_signal = entry_signal
        self.lookback_period = lookback_period
        self.exit_signal = exit_signal

    def check_entry_signal(self, funding_rates):
        """
        Checks if the conditions to enter a trade are met based on the funding rate.

        Args:
            funding_rates (pd.Series): A series of funding rates, with the most recent rate last.

        Returns:
            bool: True if the entry conditions are met, False otherwise.
        """
        if funding_rates.iloc[-1] > self.entry_signal:
            if all(funding_rates.iloc[-self.lookback_period:] > self.entry_signal):
                return True
        return False
    
    def check_exit_signal(self, funding_rates):
        """
        Checks if the conditions to exit a trade are met based on the funding rate.

        Args:
            funding_rates (pd.Series): A series of funding rates, with the most recent rate last.

        Returns:
            bool: True if the exit conditions are met, False otherwise.
        """
        if funding_rates.iloc[-1] < self.funding_rate_threshold:
            return True
        return False
    
    def execute_trade(self, spot_price, perp_price):
        """
        Executes a hedged trade: long on the spot market and short on the perpetual futures market.

        Args:
            spot_price (float): The current spot price.
            perp_price (float): The current perpetual futures price.

        Returns:
            dict: A dictionary with details of the executed trade.
        """
        trade_value = self.position_size * spot_price
        
        # Going long on the spot market
        spot_position = trade_value / spot_price
        
        # Shorting the perpetual futures market
        perp_position = -trade_value / perp_price

        print(f"Trade executed: Long {spot_position} units on spot at {spot_price} and Short {perp_position} units on perp at {perp_price}")

    def deleverage_trade(self, fraction):
        """
        Deleverages the current position by reducing both the spot and perpetual futures positions.

        Args:
            fraction (float): The fraction of the position to reduce. 
                            For example, 0.5 means reducing the position by 50%.

        Returns:
            dict: A dictionary with details of the updated trade, or None if no active trade.
        """
        if not (0 < fraction <= 1):
            print("Invalid fraction: must be between 0 and 1.")
            return None

        # Deleveraging the spot and perp positions
        spot_position = self.active_trade['spot'] * (1 - fraction)
        perp_position = self.active_trade['perp'] * (1 - fraction)

        print(f"Deleveraged trade: Reduced positions by {fraction * 100}%.")
        print(f"Updated position: Long {spot_position} units on spot and Short {perp_position} units on perp.")


        
