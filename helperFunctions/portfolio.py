from helperFunctions.position import Position

class Portfolio:
    def __init__(self):
        self.positions = []  # List to hold all positions
        self.trade_count = 0  # Total number of trades
        self.trade_open_count = 0  # Number of open trades
        self.trade_close_count = 0  # Number of closed trades

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

    def calculate_portfolio_value(self):
        """
        Calculate the current value of the portfolio.
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