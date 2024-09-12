import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)

from helperFunctions.logging import Logger

class Metrics:
    def __init__(
        self,
        input_dir: str,
        
    ) -> None:
        
        self.input_dir = input_dir
        
        self.collateral_log = pd.read_csv(f'./results/{self.input_dir}/collateral_log.csv')
        self.funding_log = pd.read_csv(f'./results/{self.input_dir}/funding_log.csv')
        self.trades_log = pd.read_csv(f'./results/{self.input_dir}/trades_log.csv')
        
        self.risk_free_rate = pd.read_csv(f'./data/processed/risk_free_rate.csv')
        
        self.time_periods = [
            {"name": "H1 2023", "start": "2023-01-01 00:00:00", "end": "2023-06-30 17:00:00", "days": 181}, 
            {"name": "H2 2023", "start": "2023-07-01 01:00:00", "end": "2023-12-31 16:00:00", "days": 184},
            {"name": "H1 2024", "start": "2024-01-01 00:00:00", "end": "2024-06-30 17:00:00", "days": 182},
            {"name": "All", "start": "2023-01-01 00:00:00", "end": "2024-06-30 17:00:00", "days": 547}
        ]
        
        self.collateral_columns = [
        'binance_btc_collateral', 'binance_eth_collateral', 'binance_liquid_cash',
        'okx_btc_collateral', 'okx_eth_collateral', 'okx_liquid_cash',
        'bybit_btc_collateral', 'bybit_eth_collateral', 'bybit_liquid_cash',
        'binance_funding', 'okx_funding', 'bybit_funding'
        ]
    
        self.logger = Logger()
        
    
    def calculate_metrics(self, period: str, start_time: str, end_time: str, number_of_days: int):
        """
        Calculate the performance metrics of the trading strategy.
        """
        period_collateral = self.collateral_log[(self.collateral_log['time'] >= start_time) & (self.collateral_log['time'] <= end_time)]
        period_funding = self.funding_log[(self.funding_log['time'] >= start_time) & (self.funding_log['time'] <= end_time)]
        
        modified_start_time = start_time[:10]
        modified_end_time = end_time[:10]
        
        period_risk_free_rate = self.risk_free_rate[(self.risk_free_rate['date'] >= modified_start_time) & (self.risk_free_rate['date'] <= modified_end_time)]
        
        annualised_return = self.calculate_annualised_return(start_time, end_time, period_collateral, period_funding, number_of_days)
        sharpe_ratio, sortino_ratio = self.calculate_sharpe_and_sortino_ratio(period_collateral, period_funding, period_risk_free_rate)
        max_drawdown = self.calculate_max_drawdown(period_collateral)
        
        calmar_ratio = annualised_return / max_drawdown if max_drawdown != 0 else np.nan
        
        formatted_annualised_return = round(annualised_return, 3)
        formatted_sharpe_ratio = round(sharpe_ratio, 3)
        formatted_max_drawdown = round(max_drawdown, 3)
        formatted_sortino_ratio = round(sortino_ratio, 3)
        formatted_calmar_ratio = round(calmar_ratio, 3)


        self.logger.log_metrics(period, formatted_annualised_return, formatted_sharpe_ratio, formatted_max_drawdown, formatted_sortino_ratio, formatted_calmar_ratio)
            
        
    def calculate_annualised_return(self, start_time: str, end_time: str, collateral_log: pd.DataFrame, funding_log: pd.DataFrame, number_of_days: int):
        """
        Calculate the annualised return of the trading strategy.
        """
        initial_portfolio_value = collateral_log[collateral_log['time'] == start_time].drop(columns=['time']).sum(axis=1).values[0]
        
        final_portfolio_value = collateral_log[collateral_log['time'] == end_time].drop(columns=['time']).sum(axis=1).values[0]
        
        total_funding_payments = funding_log['funding payment'].sum()
        
        cumulative_return = (final_portfolio_value - initial_portfolio_value + total_funding_payments) / initial_portfolio_value
        
        annualised_return = ((1 + cumulative_return) ** (365 / number_of_days) - 1) * 100
        
        return annualised_return
        
        
    def calculate_sharpe_and_sortino_ratio(self, collateral_log: pd.DataFrame, funding_log: pd.DataFrame, risk_free_rate: pd.DataFrame):
        """
        Calculate the Sharpe ratio of the trading strategy.
        """
        funding_log['time'] = pd.to_datetime(funding_log['time'])
        funding_log['date'] = funding_log['time'].dt.date
        
        daily_funding = funding_log.groupby('date')['funding payment'].sum()
        
        collateral_log['time'] = pd.to_datetime(collateral_log['time'])
        collateral_log['date'] = collateral_log['time'].dt.date
        collateral_log['total_collateral'] = collateral_log[self.collateral_columns].sum(axis=1)
        
        daily_collateral = collateral_log.groupby('date')['total_collateral'].last()
        daily_collateral_change = daily_collateral.diff().fillna(0)
        
        daily_returns = daily_funding + daily_collateral_change
        
        risk_free_rate['date'] = pd.to_datetime(risk_free_rate['date']).dt.date
        risk_free_rate['daily_rate'] = risk_free_rate['rate'] / 365
        risk_free_rate.set_index('date', inplace=True)
        aligned_risk_free_rate = risk_free_rate['daily_rate'].reindex(daily_collateral.index, method='ffill')

        daily_risk_free_cost = aligned_risk_free_rate * daily_collateral

        daily_excess_returns = daily_returns - daily_risk_free_cost
        
        sharpe_ratio = daily_excess_returns.mean() / daily_excess_returns.std()
        
        downside_returns = daily_excess_returns[daily_excess_returns < 0]

        downside_deviation = np.sqrt(np.mean(downside_returns**2))
        
        mean_excess_return = daily_excess_returns.mean()
        
        sortino_ratio = mean_excess_return / downside_deviation if downside_deviation != 0 else np.nan
        
        return sharpe_ratio, sortino_ratio
    
    
    def calculate_max_drawdown(self, collateral_log: pd.DataFrame):
        """
        Calculate the maximum drawdown of the trading strategy.
        """
        collateral_log['time'] = pd.to_datetime(collateral_log['time'])
        collateral_log['date'] = collateral_log['time'].dt.date
        collateral_log['total_collateral'] = collateral_log[self.collateral_columns].sum(axis=1)

        daily_collateral = collateral_log.groupby('date')['total_collateral'].last()

        running_max = daily_collateral.cummax()

        drawdown = (daily_collateral - running_max) / running_max

        max_drawdown = - drawdown.min() * 100

        return max_drawdown
    
    
    def run(self):
        """
        Run the metrics calculation.
        """
        for period in self.time_periods:
            start_time = period['start']
            end_time = period['end']
            number_of_days = period['days']
            period_name = period['name']

            self.calculate_metrics(period=period_name, start_time=start_time, end_time=end_time, number_of_days=number_of_days)
            
            # metrics = self.calculate_metrics(period=period_name, start_time=start_time, end_time=end_time, number_of_days=number_of_days)
            
            # print(f'{period_name}')
            # print(f"Annualised Return: {metrics[0]:.4f}%")
            # print(f"Sharpe Ratio: {metrics[1]:.4f}")
            # print(f"Max Drawdown: {metrics[2]:.4f}%")
            # print(f"Sortino Ratio: {metrics[3]:.4f}")
            # print(f"Calmar Ratio: {metrics[4]:.4f}")
        
        log_data = self.logger.get_logs(log_type='metrics')
        
        if log_data:
            df_log = pd.DataFrame(log_data)
            df_log.to_csv(f'./results/{self.input_dir}/metrics.csv', index=False)
            print(f"metrics saved to './results/{self.input_dir}/metrics.csv'.")
        else:
            print(f"No metrics logged yet.")
            
            
            