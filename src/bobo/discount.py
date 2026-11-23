# Filename: discount.py
# Created on: November 23, 2026
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

"""Customer discounts: a rate by customer kind, a volume bonus and a blocked-customer check."""

import sqlite3
from contextlib import closing

DB_PATH = "bobo.db"

RATES_BY_KIND = {"regular": 0.05, "silver": 0.10, "gold": 0.15, "vip": 0.25}
VOLUME_THRESHOLD = 500
VOLUME_BONUS = 0.02


def _is_blocked(customer_id: int) -> bool:
    """Tell whether the customer is blocked; an unreadable database counts as blocked."""
    try:
        with closing(sqlite3.connect(DB_PATH)) as conn:
            row = conn.execute(
                "SELECT blocked FROM customers WHERE id = ?", (customer_id,)
            ).fetchone()
    except sqlite3.Error:
        return True
    return bool(row and row[0])


def discount(customer_id: int, kind: str, total: float) -> float:
    """Return the total after the discount.

    The rate comes from the customer kind (unknown kinds get none), orders above
    VOLUME_THRESHOLD get VOLUME_BONUS on top, and blocked customers get no discount.
    """
    rate = RATES_BY_KIND.get(kind, 0)
    if total > VOLUME_THRESHOLD:
        rate += VOLUME_BONUS
    if _is_blocked(customer_id):
        rate = 0
    return total - total * rate
