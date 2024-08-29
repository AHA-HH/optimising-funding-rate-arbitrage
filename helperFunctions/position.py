from enum import Enum
from dataclasses import dataclass

# @staticmethod
def get_exchange_fee_rate(exchange: str, trade: str, margin: str) -> float:
    if exchange == "binance":
        if trade == "spot":
            return 0.001
        elif trade == "futures":
            if margin == "usd":
                return 0.0005
            elif margin == "coin":
                return 0.0005


class PositionType(Enum):
    LONG: str = "long"
    SHORT: str = "short"


@dataclass
class Position:
    position_type: PositionType
    open_timestamp: str
    asset: str
    quantity: float
    carryover_open_quantity: float
    open_price: float
    open_transaction_cost: float = 0
    close_price: float = None
    close_transaction_cost: float = 0
    closed: bool = False
    close_timestamp: str = None
    transaction_cost_pct: float = 0.0003
    leverage: float = 1
    open_margin_amount: float = 0
    rebalance_margin_pct: float = 0
    rebalance_margin_amount: float = 0
    liquidation_margin_pct: float = 0
    liquidation_margin_amount: float = 0
    liquidation_cost_pct: float = 0.003
    liquidation_cost: float = 0
    transaction_cost: float = 0
    carryover_close_shares: float = 0
    gross_profit: float = 0
    net_profit: float = 0
    
    def __post_init__(self):
        self.open_transaction_cost = ((self.quantity - self.carryover_open_quantity) * self.transaction_cost_pct * self.open_price)
        self.transaction_cost = self.open_transaction_cost
        self.open_value = self.quantity * self.open_price
        self.open_margin_amount = self.open_value / self.leverage
        self.rebalance_margin_amount = self.open_margin_amount * self.rebalance_margin_pct
        self.liquidation_margin_amount = self.open_margin_amount * self.liquidation_margin_pct
    
    def unrealised_profit(self, current_price: float) -> float:
        if self.closed:
            raise Exception("Position is already closed")
        else:
            if self.position_type == PositionType.LONG:
                unrealised = (current_price - self.open_price) * self.quantity
            elif self.position_type == PositionType.SHORT:
                unrealised = (self.open_price - current_price) * self.quantity
            return unrealised - self.quantity - self.transaction_cost_pct * current_price
        
    def current_margin_amount(self, current_price: float) -> float:
        if self.closed:
            raise Exception("Position is already closed")
        else:
            return self.open_margin_amount + self.unrealised_profit(current_price)
        
    def close(self, close_date: str, close_price: float, carryover_close_shares: float = 0) -> None:
        self.carryover_close_shares = carryover_close_shares
        self.close_date = close_date
        self.close_price = close_price
        self.close_value = self.quantity * self.close_price
        self.close_transaction_cost = ((self.quantity - self.carryover_close_shares) * self.transaction_cost_pct * self.close_price)

        if self.current_margin_amount(close_price) < self.liquidation_margin_amount:
            self.liquidation_cost = (self.quantity * self.liquidation_cost_pct * self.close_price)

        self.transaction_cost = self.open_transaction_cost + self.close_transaction_cost

        if self.position_type == PositionType.LONG:
            self.gross_profit = self.close_value - self.open_value
        else:
            self.gross_profit = self.open_value - self.close_value

        self.net_profit = self.gross_profit - self.transaction_cost - self.liquidation_cost

        self.closed = True
         
