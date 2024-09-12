import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helperFunctions.strategy import Strategy
from helperFunctions.metrics import Metrics

filepath = './data/all_exchanges.csv'
entry_signal = 0.0000000001
exit_signal = 0
capital = 10000000
output_folder = 'test'

strategy = Strategy(
    filepath=filepath,
    entry_threshold=entry_signal, 
    exit_threshold=exit_signal, 
    capital=capital, 
    output_dir=output_folder
    )

strategy.run()    

metrics = Metrics(
    input_dir=output_folder
    )

metrics.run()