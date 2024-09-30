import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helperFunctions.strategy import Strategy
from helperFunctions.metrics import Metrics
from helperFunctions.plotter import Plotter

input_data_file = './data/all_exchanges.csv'
entry_signal = 
exit_signal = 
capital = 
binance_pct = 
okx_pct = 
bybit_pct = 
output_folder = 'hold' # 'hold', 'simple_threshold', 'complex_threshold', 'simple_reinvest', 'complex_reinvest'
threshold_logic = 'hold' # 'hold', 'simple', 'complex'
reinvest = False
close_positions = False

strategy = Strategy(
    filepath=input_data_file,
    entry_threshold=entry_signal, 
    exit_threshold=exit_signal, 
    capital=capital, 
    binance_pct=binance_pct,
    okx_pct=okx_pct,
    bybit_pct=bybit_pct,
    output_dir=output_folder,
    threshold_logic=threshold_logic,
    reinvest_logic=reinvest,
    close_all=close_positions
    )

strategy.run()    

metrics = Metrics(
    input_dir=output_folder,
    strategy_type=threshold_logic
    )

metrics.calculate()

plotter = Plotter(
    input_dir=output_folder,
    strategy_type=threshold_logic,
    initial_capital=capital,
    reinvest_type=reinvest
    )

plotter.visualise()