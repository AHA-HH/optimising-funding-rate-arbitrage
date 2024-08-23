
import pandas as pd
from typing import Dict, List, Tuple

class Strategy:
    """
    Class for conducting a backtest of a funding rate trading strategy across multiple exchanges and assets.
    """

    def __init__(
        self,
        exchanges: list,
        assets: list,
        df_data: pd.DataFrame,
        open_threshold: float,
        close_threshold: float,
        transaction_cost_pct: float = 0.0003,
        funding_rate_freq: str = "8h",
        capital: float = 0,
        leverage: float = 1,
        rebalance_margin_pct: float = 0.55,
        liquidation_margin_pct: float = 0.50,
        liquidation_cost_pct: float = 0.003,
        run: bool = True,
    ):
        # Store the exchanges and assets
        self.exchanges = exchanges
        self.assets = assets
        
        # DataFrame containing all data to test strategy
        self.df_data = df_data
        
        # Thresholds for opening and closing positions based on funding rate
        self.open_threshold = open_threshold
        self.close_threshold = close_threshold
        
        # Cost and leverage parameters
        self.transaction_cost_pct = transaction_cost_pct
        self.leverage = leverage
        self.rebalance_margin_pct = rebalance_margin_pct
        self.liquidation_margin_pct = liquidation_margin_pct
        self.liquidation_cost_pct = liquidation_cost_pct
        
        # Capital allocation
        self.capital = capital
        
        # Initialise dictionaries to store positions, closed positions and statistics
        self.positions = {}
        self.closed_positions = {}
        self.stats = {}
        
        # Initialise funding rate dates
        # self.start_date = self.df_data.index.min()
        # self.end_date = self.df_data.index.max()
        # # datetime.fromtimestamp(d["timestamp"]/1000).strftime('%Y-%m-%d %H:%M:%S')
        # self.funding_rate_dates = (
        #     pd.date_range(self.start_date, self.end_date, freq=funding_rate_freq)
        #     .strftime("%Y-%m-%d %H:%M")
        #     .to_list()
        # )

        # Initialise for each exchange and asset pair
        for exchange in self.exchanges:
            for asset in self.assets:
                pair_key = (exchange, asset)
                self.positions[pair_key] = {"long_position": None, "short_position": None}
                self.closed_positions[pair_key] = []
                self.stats[pair_key] = []

        # Optionally run the backtest upon initialization
        if run:
            self.run()
            
        @property
        def net_profit(self):
            return (self.position_profit + self.funding_rate_profit - self.transaction_cost -self.liquidation_cost)
        
        @property
        def unrealised_profit(self):
            if self.long_position:
                return self.long_position.unrealized_profit(
                self.current_prices[self.long_position.security]
            ) + self.short_position.unrealized_profit(
                self.current_prices[self.short_position.security]
            )
            else:
                return 0
        
        def open_long_position(
            self,
            open_timestamp: str,
            asset: str,
            quantity: float,
            open_price: float,
            carryover_open_quantity: float = 0,  
        ):