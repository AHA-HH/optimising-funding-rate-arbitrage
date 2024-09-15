import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helperFunctions.strategy import Strategy
from helperFunctions.metrics import Metrics

input_data_file = './data/all_exchanges.csv'
entry_signal = 0.0000000001
exit_signal = 0
capital = 10000000
binance_pct = 0.6
okx_pct = 0.2
bybit_pct = 0.2
output_folder = 'simple_hold_open_test'
threshold_logic = 'hold'
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
    input_dir=output_folder
    )

metrics.calculate()
