# Optimising Funding Rate Arbitrage through Basis Trading

Optimising Funding Rate Arbitrage - this project aims to explore and develop funding rate arbitrage strategies that exploit the funding rate mechanism present in cryptocurrency perpetual futures contracts. The objective is to create an algorithm that can find abritrage opportunities, execute trades and manage an ongoing portfolio of assets. This will be done via a basis trading approach using this funding rate as the sole indicator for signal generation.

## Repository Structure
The project organised as follows:

```bash
│
├── analysis/                  # Contains Jupyter notebooks used for specific calculations and plots
│
├── data/                      # Directory containing data for testing
│   └── all_exchanges.csv      # Preprocessed cryptocurrency data
│
├── helperFunctions/           # Helper functions for project
│   ├── dataHandling.py        # Class for preprocessing data
│   ├── logging.py             # Class for producing logs
│   ├── metrics.py             # Class for calculating metrics
│   ├── plotter.py             # Class for producing plots
│   ├── portfolio.py           # Class for portfolio management
│   ├── position.py            # Class for managing position data
│   └── strategy.py            # Class for strategy logic
│
├── results/                   # Directory for storing plots, logs and metrics
│
├── scripts/                   # Scripts to run for the project
│   ├── algorithm.py           # Script to run the strategy through the simulation
│   └── dataPipeline.py        # Script to obtain the data needed for the simulation
│
├── README.md                  # Documentation
└── requirements.txt           # Python dependencies
```

## Run Project
To run the project, follow these steps:
1. Install Python Dependencies
2. Configure Algorithm
Navigate to the script algorithm.py, manually input values for the following variables:
    - entry_signal (value set as a threshold for entry signals)
    - exit_signal (value set as a threshold for exit signals)
    - capital (value set as initial capital allocated to portfolio)
    - binance_pct (percentage of capital allocated to Binance exchange)
    - bybit_pct (percentage of capital allocated to Bybit exchange)
    - okx_pct (percentage of capital allocated to OKX exchange)
    - output_folder = 'hold' (choose from 5 output folders each representing a strategy: 'hold', 'simple_threshold', 'complex_threshold', 'simple_reinvest', 'complex_reinvest')
    - threshold_logic = 'hold' (assign based on output_folder value: 'hold' if output_folder is 'hold', 'simple' if output_folder is 'simple_threshold' or 'simple_reinvest', 'complex' if output_folder is 'complex_threshold' or 'complex_reinvest')
    - reinvest = False (assign based on output_folder value: True if output_folder is 'simple_reinvest' or 'complex_reinvest', otherwise input False)
3. Execute Algorithm
Run the algorithm.py file to run selected configuration, the following steps occur:
    - Load Data: An 18-month historical dataset is loaded to be used for the simulation.
    - Run Simulation: The selected strategy is run through the backtesting environment, carrying out trading activity and producing logs.
    - Results: Using the logs, metrics are calculated and plots are produced, the results are saved to the results directory for evaluation.
