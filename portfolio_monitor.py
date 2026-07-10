"""
Portfolio monitor agent. Source of truth for what's actually held.
Reads directly from the broker rather than tracking state locally, so it
can never drift out of sync with reality.
"""
from execution import get_trading_client
import db


def get_account_state() -> dict:
    client = get_trading_client()
    account = client.get_account()
    positions = client.get_all_positions()

    positions_by_ticker = {p.symbol: p for p in positions}
    positions_value = sum(float(p.market_value) for p in positions)

    equity = float(account.equity)
    cash = float(account.cash)

    db.log_equity(equity=equity, cash=cash, positions_value=positions_value)

    return {
        "equity": equity,
        "cash": cash,
        "positions_value": positions_value,
        "positions_by_ticker": positions_by_ticker,
    }
