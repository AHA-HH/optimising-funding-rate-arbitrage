# Everett, Caleb. 2024. finm33150-final-project. URL https://github.com/CalebEverett/finm33150-final-project/tree/master. Accessed: 23/08/2024.
from dataclasses import dataclass

@dataclass
class Position:
    position_type: str
    position_size: float # initial size before fees in usd
    exchange: str
    crypto: str
    pair: str
    margin: str
    open_time: str
    open_price: float
    quantity: float = 0 # in coin
    open_transaction_cost: float = 0
    open_value: float = 0
    close_transaction_cost: float = 0
    transaction_cost_pct: float = 0.001
    close_price: float = None
    close_time: str = None
    close_value: float = None
    closed: bool = False
    pnl: float = 0

    
    def __post_init__(self):
        self.open_transaction_cost = self.position_size * self.transaction_cost_pct
        self.open_value = self.position_size - self.open_transaction_cost
        self.quantity = self.open_value / self.open_price