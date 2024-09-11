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
        capital: float = 0,
        
    ) -> None:
        
        self.filepath = filepath
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.capital = capital
        
        self.df = pd.read_csv(filepath)
        self.portfolio = Portfolio(initial_capital=capital)

        
    def generate_entry_signals(self, current_time) -> None:
        """
        Identify buy opportunity based on the funding rate.
        """
        time_filter = self.df['time'] == current_time
        perp_filter = self.df['contract'] == 'perpetual'
        fr_filter = self.df[time_filter & perp_filter]
        
        buy_opp = fr_filter[fr_filter['funding rate'] > self.entry_threshold]
        
        entry_signals = []
        
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
    

    def close_positions(self, exit_signal) -> None:
        """
        Close short and corresponding long position based on the exit signals.
        """
        time = exit_signal['time']
        exchange = exit_signal['exchange']
        crypto = exit_signal['crypto']
        close_price = exit_signal['open_price']
        future_pair = exit_signal['pair']
        
        pnl_short = None
        pnl_long = None
        
        if future_pair == 'BTCUSDT' or future_pair == 'ETHUSDT':
            margin = 'usd'
        elif future_pair == 'BTCUSDCM' or future_pair == 'ETHUSDCM':
            margin = 'coin'
        else:
            raise ValueError("Invalid future pair.")
        
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

        
    def run(self):
        """
        Run the backtest.
        """
        timestamps = self.df['time'].unique()
        
        # check initial capital and assign to exchanges
        print(self.portfolio.initial_capital)
        self.portfolio.assign_initial_capital_to_exchanges()
        
        # loop through all timestamps
        for current_time in timestamps:
        # for current_time in timestamps[0:10]:
            print(current_time)
            
            # look for open short positions and calculate funding rate payments
            for short_position in self.portfolio.get_open_short_positions():
                long_position = self.portfolio.get_corresponding_long_position(short_position)
                self.portfolio.calculate_funding_payment_and_pnl_interval(self.df, short_position, long_position, current_time)
                
                
            # look for negative funding rates and close positions that match the signal
            for signal in self.generate_exit_signals(current_time):
                # if signal is is in self.portfolio.get_open_short_positions(): # then close positions, should come before entry signals
                    self.close_positions(signal)
                
            
            # look for positive funding rates and open positions that match the signal
            entry_signals = self.generate_entry_signals(current_time)
            # print(entry_signals)
            for signal in entry_signals:
                long_position_size = self.portfolio.calculate_position_size(signal['exchange'], signal['crypto'], signal['pair'])
                if long_position_size != 0:
                    self.open_positions(signal, long_position_size)
            
            
            self.portfolio.calculate_collateral_values(current_time)

        print(self.portfolio.calculate_portfolio_notional_value())
        
        print(f"Total number of trades executed: {self.portfolio.trade_count}")
        print(f"Total number of trades opened: {self.portfolio.trade_open_count}")
        print(f"Total number of trades closed: {self.portfolio.trade_close_count}")
        
        trades_log = self.portfolio.logger.get_logs(log_type='trades')
        
        if trades_log:
            trades_df = pd.DataFrame(trades_log)
            trades_df.to_csv('./data/logging/trades_log.csv', index=False)
            print("Trades saved to 'trades_log.csv'.")
        
        funding_payments_log = self.portfolio.logger.get_logs(log_type='funding_payments')

        # Check if the log is not empty
        if funding_payments_log:
            # Convert the list of dictionaries to a DataFrame
            funding_payments_df = pd.DataFrame(funding_payments_log)
            
            # Sum the values in the 'funding payment' column
            total_funding_payments = funding_payments_df['funding payment'].sum()
            print(f"Total Funding Payments: {total_funding_payments}")
            # Save the DataFrame to a CSV file
            funding_payments_df.to_csv('./data/logging/funding_payments_log.csv', index=False)
            print("Funding payments saved to 'funding_payments_log.csv'.")
        else:
            print("No funding payments logged.")
        
        collateral_values_log = self.portfolio.logger.get_logs(log_type='collateral_values')

        # Check if there are any logs to save
        if collateral_values_log:
            # Convert the list of logs to a DataFrame
            df_collateral = pd.DataFrame(collateral_values_log)

            # Save the DataFrame to a CSV file
            df_collateral.to_csv('./data/logging/collateral_values_log.csv', index=False)
            print("Collateral values saved to 'collateral_values_log.csv'.")
        else:
            print("No collateral values logged yet.")
                
        print("Backtest completed.")