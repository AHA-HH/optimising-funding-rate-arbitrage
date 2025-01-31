from helperFunctions.position import Position
class Logger:
    def __init__(self):
        self.logs = {
            'trades': [],  # To log trade data
            'funding_payments': [],  # To log funding rate payments
            'collateral_values': [],  # To log collateral position values over time
            'metrics': [],  # To log performance metrics
            'yield': []  # To log average yield
        }
        
        
    def log_trade(self, position: Position, action: str):
        """
        Log the details of a trade. If the trade is closed, update the existing log entry.
        """
        if action == 'open':
            # Create a new log entry for the opening of the trade
            self.logs['trades'].append({
                'position_type': position.position_type,
                'position_size': position.position_size,
                'exchange': position.exchange,
                'crypto': position.crypto,
                'pair': position.pair,
                'margin': position.margin,
                'open_time': position.open_time,
                'quantity': position.quantity,
                'open_price': position.open_price,
                'transaction_cost_pct': position.transaction_cost_pct,
                'open_transaction_cost': position.open_transaction_cost,
                'open_value': position.open_value,
                'close_time': None,  # To be updated later
                'close_price': None,  # To be updated later
                'closed': False
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
                    trade['close_transaction_cost'] = position.close_transaction_cost
                    trade['close_value'] = position.close_value
                    trade['closed'] = True
                    trade['pnl'] = position.pnl
                    break


    def log_funding_payment_and_pnl(
        self, 
        time: str, 
        position: Position, 
        payment: float, 
        pnl: float, 
        initial_delta: float, 
        current_delta: float
        ):
        """
        Log the funding payment for a specific asset at a given time.
        """
        self.logs['funding_payments'].append({
            'time': time,
            'exchange': position.exchange,
            'pair': position.pair,
            'funding payment': payment,
            'pnl': pnl,
            'initial_delta': initial_delta,
            'current_delta': current_delta
        })
        
        
    def log_collateral(
        self, 
        time: str, 
        bin_btc: float, 
        bin_eth: float, 
        bin_liq: float, 
        okx_btc: float, 
        okx_eth: float, 
        okx_liq: float, 
        bybit_btc: float, 
        bybit_eth: float, 
        bybit_liq: float, 
        bin_fund: float, 
        okx_fund: float, 
        bybit_fund: float,
        bin_unrealised_pnl: float,
        okx_unrealised_pnl: float,
        bybit_unrealised_pnl: float
    ):
        """
        Log the collateral values at a given time.
        """
        self.logs['collateral_values'].append({
            'time': time,
            'binance_btc_collateral': bin_btc,
            'binance_eth_collateral': bin_eth,
            'binance_liquid_cash': bin_liq,          
            'okx_btc_collateral': okx_btc,
            'okx_eth_collateral': okx_eth,
            'okx_liquid_cash': okx_liq,            
            'bybit_btc_collateral': bybit_btc,
            'bybit_eth_collateral': bybit_eth,
            'bybit_liquid_cash': bybit_liq,
            'binance_funding': bin_fund,
            'okx_funding': okx_fund,
            'bybit_funding': bybit_fund,
            'binance_unrealised_pnl': bin_unrealised_pnl,
            'okx_unrealised_pnl': okx_unrealised_pnl,
            'bybit_unrealised_pnl': bybit_unrealised_pnl
        })
        
        
    def log_metrics(
        self, 
        period: str, 
        annualised_return: float, 
        sharpe_ratio: float, 
        max_drawdown: float, 
        sortino_ratio: float, 
        calmar_ratio: float
        ):
        """
        Log the performance metrics at a given time.
        """
        self.logs['metrics'].append({
            'time_horizon': period,
            'annualised_return': annualised_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio
        })
        
    
    def log_yield(
        self, 
        date: str, 
        bin_btcusd: float, 
        bin_btccm: float, 
        bin_ethusd: float, 
        bin_ethcm: float, 
        bybit_btcusd: float, 
        bybit_btccm: float, 
        bybit_ethusd: float, 
        bybit_ethcm: float, 
        okx_btcusd: float, 
        okx_btccm: float, 
        okx_ethusd: float, 
        okx_ethcm: float, 
        bin_btc: float, 
        bin_eth: float, 
        bybit_btc: float, 
        bybit_eth: float, 
        okx_btc: float, 
        okx_eth: float, 
        bin_total: float, 
        bybit_total: float, 
        okx_total: float, 
        btc_total: float,
        eth_total: float,
        total_yield: float
    ):
        """
        Log the average yield at a given time.
        """
        self.logs['yield'].append({
            'date': date,
            'binance_btcusd_yield': bin_btcusd,
            'binance_btccm_yield': bin_btccm,
            'binance_ethusd_yield': bin_ethusd,
            'binance_ethcm_yield': bin_ethcm,
            'bybit_btcusd_yield': bybit_btcusd,
            'bybit_btccm_yield': bybit_btccm,
            'bybit_ethusd_yield': bybit_ethusd,
            'bybit_ethcm_yield': bybit_ethcm,
            'okx_btcusd_yield': okx_btcusd,
            'okx_btccm_yield': okx_btccm,
            'okx_ethusd_yield': okx_ethusd,
            'okx_ethcm_yield': okx_ethcm,
            'binance_btc_yield': bin_btc, 
            'binance_eth_yield': bin_eth, 
            'bybit_btc_yield': bybit_btc, 
            'bybit_eth_yield': bybit_eth, 
            'okx_btc_yield': okx_btc, 
            'okx_eth_yield': okx_eth,
            'binance_total_yield': bin_total,
            'bybit_total_yield': bybit_total,
            'okx_total_yield': okx_total,
            'btc_total_yield': btc_total,
            'eth_total_yield': eth_total,
            'total_yield': total_yield
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