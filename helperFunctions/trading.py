import pandas as pd

class Trading:
    def __init__(self, funding_rate_threshold=0.05, lookback_period=3):
        """
        Initializes the trading strategy with configurable parameters.

        Args:
            funding_rate_threshold (float): The threshold above which to consider entering a trade.
            lookback_period (int): The number of previous funding rate intervals to check for consistency.
        """
        self.funding_rate_threshold = funding_rate_threshold
        self.lookback_period = lookback_period

    def check_entry_signal(self, funding_rates):
        """
        Checks if the conditions to enter a trade are met based on the funding rate.

        Args:
            funding_rates (pd.Series): A series of funding rates, with the most recent rate last.

        Returns:
            bool: True if the entry conditions are met, False otherwise.
        """
        if funding_rates.iloc[-1] > self.funding_rate_threshold:
            if all(funding_rates.iloc[-self.lookback_period:] > self.funding_rate_threshold):
                return True
        return False

    
# enter trade, exit/close trade - signal generation
# execute trade (account for slippage)
# stop-loss, take-profit mechanism, position sizing(risk management)
# portfolio management, rebalancing, adjusting positions