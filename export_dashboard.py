"""
Reads the trade database and writes docs/data.json - a plain data file
the dashboard (docs/index.html) fetches. Run this after main.py each
cycle. Keeping the dashboard "static" (just HTML+JS reading a JSON file)
means it can be hosted for free on GitHub Pages with zero server needed.
"""
import json
import os
import sqlite3
import config


def export():
    if not os.path.exists(config.DB_PATH):
        data = {"mode": config.MODE, "equity_history": [], "recent_cycles": [], "halted": False}
    else:
        conn = sqlite3.connect(config.DB_PATH)
        conn.row_factory = sqlite3.Row

        equity_rows = conn.execute(
            "SELECT timestamp, equity, cash, positions_value FROM equity_snapshots "
            "ORDER BY id DESC LIMIT 500"
        ).fetchall()
        equity_history = [dict(r) for r in reversed(equity_rows)]

        cycle_rows = conn.execute(
            "SELECT timestamp, ticker, technical_score, fundamental_score, composite_score, "
            "action, risk_decision, risk_reason, order_id, notes FROM cycles "
            "ORDER BY id DESC LIMIT 200"
        ).fetchall()
        recent_cycles = [dict(r) for r in cycle_rows]

        halt_rows = conn.execute(
            "SELECT timestamp, reason FROM halts ORDER BY id DESC LIMIT 5"
        ).fetchall()
        recent_halts = [dict(r) for r in halt_rows]

        conn.close()

        data = {
            "mode": config.MODE,
            "equity_history": equity_history,
            "recent_cycles": recent_cycles,
            "halted": os.path.exists(config.HALT_FILE),
            "recent_halts": recent_halts,
        }

    os.makedirs("docs", exist_ok=True)
    with open("docs/data.json", "w") as f:
        json.dump(data, f, indent=2, default=str)

    print(f"Exported {len(data['equity_history'])} equity points and "
          f"{len(data['recent_cycles'])} cycle records to docs/data.json")


if __name__ == "__main__":
    export()
