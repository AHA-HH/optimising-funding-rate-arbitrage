from helperFunctions.position import Position

class Portfolio:
    def __init__(self, initial_capital: float = 0) -> None:
        self.positions = []  # List to hold all positions
        self.trade_count = 0  # Total number of trades
        self.trade_open_count = 0  # Number of open trades
        self.trade_close_count = 0  # Number of closed trades
        self.initial_capital = initial_capital
        self.unallocated_capital = initial_capital
        self.fr_capital = 0
        
        
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
        #     print(f"Opened {position.position_type} Position at {position.open_time} for {position.pair} on {position.exchange} at {position.open_price}")
        # else:
        #     print(f"Position already open for {position.crypto} on {position.exchange}.")

    def close_position(self, position: Position, close_price: float, close_time: str):
        """
        Close an existing position.
        """
        position.close_price = close_price
        position.close_time = close_time
        position.closed = True
        self.trade_count += 1
        self.trade_close_count += 1
        # print(f"Closed {position.position_type} Position for {position.pair} on {position.exchange} at {close_price}")

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

    # def calculate_portfolio_value(self):
    #     """
    #     Calculate the current value of the portfolio.
    #     """
    #     pass
    
    # def calculate_portfolio_weighting(self):
    #     """
    #     Calculate the current weighting of each asset in the portfolio.
    #     """
    #     pass
    
    # def rebalance_portfolio(self):
    #     """
    #     Rebalance the portfolio based on the current weighting of each asset.
    #     """
    #     pass
    
    def calculate_position_size(self):
        """
        Calculate the size of each position based on the current value of the portfolio.
        """
        # if self.unallocated_capital == 0:
        #     raise Exception("No capital available for trading")
        position_size = self.unallocated_capital
        return position_size
        
    
    def calculate_capital(self):
        """
        Calculate the current capital available for trading.
        """
        print(self.unallocated_capital)
        
        
    def calculate_exchange_capital(self, exchange: str):
        """
        Calculate the current capital available for trading on a specific exchange.
        """
        
        