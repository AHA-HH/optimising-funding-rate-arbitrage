import pandas as pd

class Metrics:
    def __init__(
        self,
        input_dir: str,
        
    ) -> None:
        
        self.input_dir = input_dir
        
        self.collateral_log = pd.read_csv(f'./results/{self.input_dir}/collateral_log.csv')
        self.funding_log = pd.read_csv(f'./results/{self.input_dir}/funding_log.csv')
        self.trades_log = pd.read_csv(f'./results/{self.input_dir}/trades_log.csv')
        
        self.time_periods = [
            {"name": "Q1 2023", "start": "2023-01-01 00:00:00", "end": "2023-03-31 17:00:00", "days": 90}, 
            {"name": "Q2 2023", "start": "2023-04-01 01:00:00", "end": "2023-06-30 17:00:00", "days": 91},
            {"name": "Q3 2023", "start": "2023-07-01 01:00:00", "end": "2023-09-30 17:00:00", "days": 92},
            {"name": "Q4 2023", "start": "2023-10-01 01:00:00", "end": "2023-12-31 16:00:00", "days": 92},
            {"name": "Q1 2024", "start": "2024-01-01 00:00:00", "end": "2024-03-31 17:00:00", "days": 91},
            {"name": "Q2 2024", "start": "2024-04-01 01:00:00", "end": "2024-06-30 17:00:00", "days": 91},
            {"name": "H1 2023", "start": "2023-01-01 00:00:00", "end": "2023-06-30 17:00:00", "days": 181}, 
            {"name": "H2 2023", "start": "2023-07-01 01:00:00", "end": "2023-12-31 16:00:00", "days": 184},
            {"name": "H1 2024", "start": "2024-01-01 00:00:00", "end": "2024-06-30 17:00:00", "days": 182},
            {"name": "All", "start": "2023-01-01 00:00:00", "end": "2024-06-30 17:00:00", "days": 547}
        ]
    
    
    def calculate_metrics(self, start_time: str, end_time: str, number_of_days: int):
        """
        Calculate the performance metrics of the trading strategy.
        """
        period_collateral = self.collateral_log[(self.collateral_log['time'] >= start_time) & (self.collateral_log['time'] <= end_time)]
        period_funding = self.funding_log[(self.funding_log['time'] >= start_time) & (self.funding_log['time'] <= end_time)]
        
        annualised_return = self.calculate_annualised_return(start_time, end_time, period_collateral, period_funding, number_of_days)
        # self.calculate_sharpe_ratio()
        # self.calculate_max_drawdown()
        # self.calculate_alpha()
        return annualised_return
        
        
    def calculate_annualised_return(self, start_time: str, end_time: str, collateral_log: pd.DataFrame, funding_log: pd.DataFrame, number_of_days: int):
        """
        Calculate the annualised return of the trading strategy.
        """
        # Calculate initial portfolio value by summing collateral values at the start time
        initial_portfolio_value = collateral_log[collateral_log['time'] == start_time].drop(columns=['time']).sum(axis=1).values[0]
        
        # Calculate final portfolio value by summing collateral values at the end time
        final_portfolio_value = collateral_log[collateral_log['time'] == end_time].drop(columns=['time']).sum(axis=1).values[0]
        
        # Calculate total funding payments in the period
        total_funding_payments = funding_log['funding payment'].sum()
        
        # Calculate cumulative return
        cumulative_return = (final_portfolio_value - initial_portfolio_value + total_funding_payments) / initial_portfolio_value
        
        # Calculate annualized return
        annualised_return = (1 + cumulative_return) ** (365 / number_of_days) - 1
        
        return annualised_return
        
        
    # def calculate_sharpe_ratio(self):
    #     """
    #     Calculate the Sharpe ratio of the trading strategy.
    #     """
    #     pass
    
    
    # def calculate_max_drawdown(self):
    #     """
    #     Calculate the maximum drawdown of the trading strategy.
    #     """
    #     pass
    
    
    # def calculate_alpha(self):
    #     """
    #     Calculate the alpha of the trading strategy.
    #     """
    #     pass
    
    
    def run(self):
        """
        Run the metrics calculation.
        """
        for period in self.time_periods:
            start_time = period['start']
            end_time = period['end']
            number_of_days = period['days']
            period_name = period['name']

            metrics = self.calculate_metrics(start_time=start_time, end_time=end_time, number_of_days=number_of_days)
            
            print(f'{period_name}')
            print(f"Annualized Return: {metrics:.4f}")
            print(f"Sharpe Ratio: {metrics:.4f}")
            print(f"Max Drawdown: {metrics:.4f}")
            print(f"Alpha: {metrics:.4f}")
            
            
            