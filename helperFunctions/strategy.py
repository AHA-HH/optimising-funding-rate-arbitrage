import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helperFunctions.position import Position
from helperFunctions.portfolio import Portfolio

class Strategy:
    """
    Class for conducting a backtest of a funding rate trading strategy across multiple exchanges and assets.
    """
    def __init__(
        self,
        filepath: str,
        entry_threshold: float,
        exit_threshold: float,
        capital: float,
        binance_pct: float,
        okx_pct: float,
        bybit_pct: float,
        output_dir: str,
        threshold_logic: str = 'simple',
        reinvest_logic: bool = False,
        close_all: bool = False

    ) -> None:
        
        self.filepath = filepath
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.capital = capital
        self.binance_pct = binance_pct
        self.okx_pct = okx_pct
        self.bybit_pct = bybit_pct
        self.output_dir = output_dir
        self.threshold_logic = threshold_logic
        self.reinvest_logic = reinvest_logic
        self.close_all = close_all
        
        self.df = pd.read_csv(filepath)
        self.portfolio = Portfolio(initial_capital=capital, binance_pct=binance_pct, okx_pct=okx_pct, bybit_pct=bybit_pct, reinvest=reinvest_logic)
        
        results_folder = f'./results/{output_dir}'
        
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)

        
    def generate_entry_signals(self, current_time) -> None:
        """
        Identify buy opportunity based on the funding rate.
        """
        time_filter = self.df['time'] == current_time
        perp_filter = self.df['contract'] == 'perpetual'
        fr_filter = self.df[time_filter & perp_filter]
        
        buy_opp = fr_filter[fr_filter['funding rate'] > self.entry_threshold]
        
        entry_signals = []
        
        if self.threshold_logic == 'hold':
            for _, row in fr_filter.iterrows():
                entry_signal = {
                    'exchange': row['exchange'],
                    'crypto': row['crypto'],
                    'pair': row['pair'],
                    'contract': row['contract'],
                    'open_price': row['open'],
                    'close_price': row['close'],
                    'funding_rate': row['funding rate'],
                    'time': row['time']
                }
                entry_signals.append(entry_signal)
        
        elif self.threshold_logic == 'simple':
            if not buy_opp.empty:
                for _, row in buy_opp.iterrows():
                    entry_signal = {
                        'exchange': row['exchange'],
                        'crypto': row['crypto'],
                        'pair': row['pair'],
                        'contract': row['contract'],
                        'open_price': row['open'],
                        'close_price': row['close'],
                        'funding_rate': row['funding rate'],
                        'time': row['time']
                    }
                    entry_signals.append(entry_signal)
        elif self.threshold_logic == 'complex':
            if not fr_filter.empty:
                for _, row in fr_filter.iterrows():
                    # Get the previous funding rates for the same pair and exchange
                    pair_filter = self.df['pair'] == row['pair']
                    exchange_filter = self.df['exchange'] == row['exchange']

                    # Sort the dataframe by time and get the relevant previous funding rates
                    relevant_df = self.df[pair_filter & exchange_filter & perp_filter].sort_values(by='time')
                    current_idx = relevant_df[relevant_df['time'] == current_time].index[0]

                    # For OKX, check the previous twelve funding rates must be positive
                    if row['exchange'] == 'okx':
                        if current_idx >= 9:  # Ensure at least twelve previous rates exist
                            prev_twelve_rates = relevant_df.iloc[current_idx-9:current_idx]['funding rate']

                            # Ensure the previous twelve funding rates are positive
                            if not (prev_twelve_rates > 0).all():
                                continue  # Skip this row if the previous 12 rates aren't all positive

                    # For other exchanges, check the previous two funding rates must be positive
                    else:
                        if current_idx >= 3:  # Ensure at least two previous rates exist
                            prev_two_rates = relevant_df.iloc[current_idx-3:current_idx]['funding rate']

                            # Ensure the previous two funding rates are positive
                            if not (prev_two_rates > 0).all():
                                continue  # Skip this row if the previous 2 rates aren't all positive

                    # Check if the current funding rate is greater than the entry threshold
                    if row['funding rate'] > self.entry_threshold:
                        entry_signal = {
                            'exchange': row['exchange'],
                            'crypto': row['crypto'],
                            'pair': row['pair'],
                            'contract': row['contract'],
                            'open_price': row['open'],
                            'close_price': row['close'],
                            'funding_rate': row['funding rate'],
                            'time': row['time']
                        }
                        entry_signals.append(entry_signal)

        return entry_signals

    
    def open_positions(self, entry_signal, position_capital) -> None:
        """
        Open long and corresponding short position based on the entry signals.
        """
        time = entry_signal['time']
        exchange = entry_signal['exchange']
        crypto = entry_signal['crypto']
        future_pair = entry_signal['pair']
        future_price = entry_signal['open_price']
        
        spot_filter = self.df[(self.df['time'] == time) & (self.df['contract'] == 'spot') & (self.df['exchange'] == exchange) & (self.df['crypto'] == crypto)]
        spot_pair = spot_filter['pair'].values[0]
        spot_market = spot_filter['contract'].values[0]
        spot_price = spot_filter['open'].values[0]
        if future_pair == 'BTCUSDT' or future_pair == 'ETHUSDT':
            margin = 'usd'
        elif future_pair == 'BTCUSDCM' or future_pair == 'ETHUSDCM':
            margin = 'coin'
        else:
            raise ValueError("Invalid future pair.")
        
        # Check if long position already exists to avoid opening it again and avoid repeating capital allocation issues
        long_position_exists = self.portfolio.find_open_position(crypto, spot_pair, exchange, 'long', margin)
        
        if not long_position_exists:
            # Create a new long position
            new_long_position = Position(
                position_type='long',
                position_size=position_capital,
                exchange=exchange,
                crypto=crypto,
                pair=spot_pair,
                margin=margin,
                open_time=time,
                open_price=spot_price,
                transaction_cost_pct=self.portfolio.get_exchange_transaction_fee_pct(exchange, spot_market, margin)
            )
            
            self.portfolio.open_position(new_long_position)

            capital_used = new_long_position.position_size
            
            if exchange == 'binance':
                self.portfolio.binance_liquid_cash -= capital_used
                if crypto == 'bitcoin':
                    self.portfolio.binance_btc_collateral += capital_used
                elif crypto == 'ethereum':
                    self.portfolio.binance_eth_collateral += capital_used

            elif exchange == 'okx':
                self.portfolio.okx_liquid_cash -= capital_used
                if crypto == 'bitcoin':
                    self.portfolio.okx_btc_collateral += capital_used
                elif crypto == 'ethereum':
                    self.portfolio.okx_eth_collateral += capital_used

            elif exchange == 'bybit':
                self.portfolio.bybit_liquid_cash -= capital_used
                if crypto == 'bitcoin':
                    self.portfolio.bybit_btc_collateral += capital_used
                elif crypto == 'ethereum':
                    self.portfolio.bybit_eth_collateral += capital_used
            
            # Create a new short position
            new_short_position = Position(
                position_type='short',
                position_size=new_long_position.open_value,
                exchange=exchange,
                crypto=crypto,
                pair=future_pair,
                margin=margin,
                open_time=time,
                open_price=future_price,
                transaction_cost_pct=self.portfolio.get_exchange_transaction_fee_pct(exchange, 'futures', margin)
            )
            
            self.portfolio.open_position(new_short_position)
            
    
    def generate_exit_signals(self, current_time) -> None:
        """
        Identify sell opportunity based on the funding rate.
        """
        if self.threshold_logic == 'hold':
            return []
        
        time_filter = self.df['time'] == current_time
        perp_filter = self.df['contract'] == 'perpetual'
        fr_filter = self.df[time_filter & perp_filter]
        
        sell_opp = fr_filter[fr_filter['funding rate'] < self.exit_threshold]
        
        exit_signals = []
        
        if not sell_opp.empty:
            for _, row in sell_opp.iterrows():
                exit_signal = {
                    'exchange': row['exchange'],
                    'crypto': row['crypto'],
                    'pair': row['pair'],
                    'contract': row['contract'],
                    'open_price': row['open'],
                    'close_price': row['close'],
                    'funding_rate': row['funding rate'],
                    'time': row['time']
                }
                exit_signals.append(exit_signal)
        return exit_signals
    
    
    def generate_close_all_signals(self, current_time) -> None:
        """
        Generate exit signals for all open positions at the given timestamp.
        """
        time_filter = self.df['time'] == current_time
        perp_filter = self.df['contract'] == 'perpetual'
        fr_filter = self.df[time_filter & perp_filter]
        
        sell_opp = fr_filter[fr_filter['funding rate'] < 999999999]
        
        close_signals = []
        
        if not sell_opp.empty:
            for _, row in sell_opp.iterrows():
                exit_signal = {
                    'exchange': row['exchange'],
                    'crypto': row['crypto'],
                    'pair': row['pair'],
                    'contract': row['contract'],
                    'open_price': row['open'],
                    'close_price': row['close'],
                    'funding_rate': row['funding rate'],
                    'time': row['time']
                }
                close_signals.append(exit_signal)
        return close_signals
    

    def close_positions(self, exit_signal) -> None:
        """
        Close short and corresponding long position based on the exit signals.
        """
        time = exit_signal['time']
        exchange = exit_signal['exchange']
        crypto = exit_signal['crypto']
        close_price = exit_signal['open_price']
        future_pair = exit_signal['pair']
        current_date = pd.to_datetime(time).date()
        
        pnl_short = None
        pnl_long = None
        
        if future_pair == 'BTCUSDT' or future_pair == 'ETHUSDT':
            margin = 'usd'
        elif future_pair == 'BTCUSDCM' or future_pair == 'ETHUSDCM':
            margin = 'coin'
        else:
            raise ValueError("Invalid future pair.")
        
        if self.threshold_logic == 'simple':
            close_short_position = self.portfolio.find_open_position(crypto, future_pair, exchange, 'short', margin)
            
            if close_short_position is not None:
                self.portfolio.close_position(close_short_position, close_price, time)
                pnl_short = close_short_position.pnl
                
            spot_filter = self.df[(self.df['time'] == time) & (self.df['contract'] == 'spot') & (self.df['exchange'] == exchange) & (self.df['crypto'] == crypto)]
            spot_pair = spot_filter['pair'].values[0]
            spot_market = spot_filter['contract'].values[0]
            spot_price = spot_filter['open'].values[0]
            
            close_long_position = self.portfolio.find_open_position(crypto, spot_pair, exchange, 'long', margin)
            
            if close_long_position is not None:
                self.portfolio.close_position(close_long_position, spot_price, time)
                pnl_long = close_long_position.pnl
                capital_used = close_long_position.position_size
                
            if pnl_long is not None and pnl_short is not None:          
                net_pnl = pnl_long + pnl_short
                
                if exchange == 'binance':
                    self.portfolio.binance_liquid_cash += capital_used + net_pnl
                    if crypto == 'bitcoin':
                        self.portfolio.binance_btc_collateral -= capital_used
                    elif crypto == 'ethereum':
                        self.portfolio.binance_eth_collateral -= capital_used

                elif exchange == 'okx':
                    self.portfolio.okx_liquid_cash += capital_used + net_pnl
                    if crypto == 'bitcoin':
                        self.portfolio.okx_btc_collateral -= capital_used
                    elif crypto == 'ethereum':
                        self.portfolio.okx_eth_collateral -= capital_used

                elif exchange == 'bybit':
                    self.portfolio.bybit_liquid_cash += capital_used + net_pnl
                    if crypto == 'bitcoin':
                        self.portfolio.bybit_btc_collateral -= capital_used
                    elif crypto == 'ethereum':
                        self.portfolio.bybit_eth_collateral -= capital_used
        elif self.threshold_logic == 'complex':
            close_short_position = self.portfolio.find_open_position(crypto, future_pair, exchange, 'short', margin)
            
            # Determine the cooldown period
            if exchange == 'okx':
                cooldown_period = pd.Timedelta(days=3) 
            else:
                cooldown_period = pd.Timedelta(days=1)

            current_time = pd.to_datetime(time)

            if close_short_position is not None:
                # Convert open_time to datetime for comparison
                open_time = pd.to_datetime(close_short_position.open_time)
                if (current_time - open_time) > cooldown_period:
                    # Only close the position if it has been open for longer than the cooldown period
                    self.portfolio.close_position(close_short_position, close_price, time)
                    pnl_short = close_short_position.pnl

            spot_filter = self.df[(self.df['time'] == time) & (self.df['contract'] == 'spot') & 
                                (self.df['exchange'] == exchange) & (self.df['crypto'] == crypto)]
            spot_pair = spot_filter['pair'].values[0]
            spot_market = spot_filter['contract'].values[0]
            spot_price = spot_filter['open'].values[0]

            close_long_position = self.portfolio.find_open_position(crypto, spot_pair, exchange, 'long', margin)

            if close_long_position is not None:
                # Convert open_time to datetime for comparison
                open_time = pd.to_datetime(close_long_position.open_time)
                if (current_time - open_time) > cooldown_period:
                    # Only close the position if it has been open for longer than the cooldown period
                    self.portfolio.close_position(close_long_position, spot_price, time)
                    pnl_long = close_long_position.pnl
                    capital_used = close_long_position.position_size

            if pnl_long is not None and pnl_short is not None:
                net_pnl = pnl_long + pnl_short

                if exchange == 'binance':
                    self.portfolio.binance_liquid_cash += capital_used + net_pnl
                    if crypto == 'bitcoin':
                        self.portfolio.binance_btc_collateral -= capital_used
                    elif crypto == 'ethereum':
                        self.portfolio.binance_eth_collateral -= capital_used

                elif exchange == 'okx':
                    self.portfolio.okx_liquid_cash += capital_used + net_pnl
                    if crypto == 'bitcoin':
                        self.portfolio.okx_btc_collateral -= capital_used
                    elif crypto == 'ethereum':
                        self.portfolio.okx_eth_collateral -= capital_used

                elif exchange == 'bybit':
                    self.portfolio.bybit_liquid_cash += capital_used + net_pnl
                    if crypto == 'bitcoin':
                        self.portfolio.bybit_btc_collateral -= capital_used
                    elif crypto == 'ethereum':
                        self.portfolio.bybit_eth_collateral -= capital_used



    def save_logs(self, log_type: str, file_name: str) -> None:
        """
        Save the logs to CSV files in specified output directory.
        """
        log_data = self.portfolio.logger.get_logs(log_type=log_type)
        
        if log_data:
            df_log = pd.DataFrame(log_data)
            df_log.to_csv(f'./results/{self.output_dir}/{file_name}.csv', index=False)
            print(f"{log_type} saved to './results/{self.output_dir}/{file_name}.csv'.")
        else:
            print(f"No {log_type} logged yet.")
            
        
    def run(self):
        """
        Run the backtest.
        """
        timestamps = self.df['time'].unique()
        
        
        # check initial capital and assign to exchanges
        self.portfolio.assign_initial_capital_to_exchanges()
        
        
        # loop through all timestamps
        # for current_time in timestamps[0:1641]:
        for current_time in timestamps:
            print(current_time)
            
            
            # look for open short positions and calculate funding rate payments
            for short_position in self.portfolio.get_open_short_positions():
                long_position = self.portfolio.get_corresponding_long_position(short_position)
                self.portfolio.calculate_funding_payment_and_pnl_interval(self.df, short_position, long_position, current_time)
                
                
            # look for negative funding rates and close positions that match the signal
            for signal in self.generate_exit_signals(current_time):
                self.close_positions(signal)
                
            
            # look for positive funding rates and open positions that match the signal
            entry_signals = self.generate_entry_signals(current_time)
            for signal in entry_signals:
                long_position_size = self.portfolio.calculate_position_size(signal['exchange'], signal['crypto'], signal['pair'])
                if long_position_size != 0:
                    self.open_positions(signal, long_position_size)
            
            if self.close_all is True:
                if current_time == '2024-06-30 17:00:00':
                    print(f"Closing all positions at 2024-06-30 17:00:00")
                
                    # Close all open positions at this timestamp
                    for signal in self.generate_close_all_signals(current_time):
                        self.close_positions(signal)
                    
            
            
            # log the collateral values
            self.portfolio.calculate_collateral_values(current_time, self.df)

        self.portfolio.calculate_portfolio_notional_value()
        
        print(f"Total number of trades executed: {self.portfolio.trade_count}")
        print(f"Total number of trades opened: {self.portfolio.trade_open_count}")
        print(f"Total number of trades closed: {self.portfolio.trade_close_count}")

        self.save_logs('trades', 'trades_log')
        self.save_logs('funding_payments', 'funding_log')
        self.save_logs('collateral_values', 'collateral_log')
                
        print("Backtest completed.")





















