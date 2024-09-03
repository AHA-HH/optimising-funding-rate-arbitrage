from helperFunctions.position import Position
class Logger:
    def __init__(self):
        self.logs = {
            'trades': [],  # To log trade data
            'funding_payments': []  # To log funding rate payments
            # 'portfolio_values': []  # To log portfolio values over time
        }
        
    def log_trade(self, position: Position, action: str):
        """
        Log the details of a trade. If the trade is closed, update the existing log entry.
        """
        if action == 'open':
            # Create a new log entry for the opening of the trade
            self.logs['trades'].append({
                'position_type': position.position_type,
                'exchange': position.exchange,
                'crypto': position.crypto,
                'pair': position.pair,
                'margin': position.margin,
                'open_time': position.open_time,
                'quantity': position.quantity,
                'open_price': position.open_price,
                # 'open_transaction_cost': position.open_transaction_cost,
                'close_time': None,  # To be updated later
                # 'close_quantity': None,  # To be updated later
                'close_price': None,  # To be updated later
                'closed': False
                # 'close_transaction_cost': None,  # To be updated later
                # 'pnl': None,  # To be calculated when the position closes
            })

        elif action == 'close':
            # Find the corresponding open trade and update it with the closing information
            for trade in self.logs['trades']:
                if (trade['exchange'] == position.exchange and
                    trade['crypto'] == position.crypto and
                    trade['pair'] == position.pair and
                    trade['position_type'] == position.position_type and
                    trade['margin'] == position.margin and
                    trade['open_time'] == position.open_time and
                    trade['close_time'] is None):  # Match only open trades

                    trade['close_time'] = position.close_time
                    trade['close_price'] = position.close_price
                    trade['closed'] = True
                    # trade['close_transaction_cost'] = position.close_transaction_cost
                    # Calculate PnL (example calculation, adjust as needed)
                    # trade['pnl'] = (position.close_price - position.open_price) * position.quantity - (position.open_transaction_cost + position.close_transaction_cost)
                    break

    def log_funding_payment(self, time: str, position: Position, payment: float):
        """
        Log the funding payment for a specific asset at a given time.
        """
        self.logs['funding_payments'].append({
            'time': time,
            'exchange': position.exchange,
            'pair': position.pair,
            'funding payment': payment
        })

    def get_logs(self, log_type: str = None):
        """
        Retrieve the logs. If log_type is specified, return the logs for that type only.
        If no log_type is provided, return all logs.
        
        log_type: str - Can be 'trades', 'funding_payments', or 'portfolio_values'
        """
        if log_type:
            if log_type in self.logs:
                return self.logs[log_type]
            else:
                raise ValueError(f"Invalid log type: {log_type}. Available types are: 'trades', 'funding_payments', 'portfolio_values'.")
        else:
            return self.logs