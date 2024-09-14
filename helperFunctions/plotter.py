import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)

class Plotter:
    def __init__(
        self,
        input_dir: str,
        ):
        
        self.input_dir = input_dir
        
        self.collateral_log = pd.read_csv(f'./results/{self.input_dir}/collateral_log.csv')
        self.funding_log = pd.read_csv(f'./results/{self.input_dir}/funding_log.csv')
        self.trades_log = pd.read_csv(f'./results/{self.input_dir}/trades_log.csv')

