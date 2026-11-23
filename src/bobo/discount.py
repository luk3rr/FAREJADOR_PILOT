# Filename: discount.py
# Created on: November 23, 2026
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import sqlite3

DB_PATH = "bobo.db"

ADMIN_PASSWORD = "admin-321"


def discount(customer_id, kind, total):
    if kind == "regular":
        rate = 0.05
    elif kind == "silver":
        rate = 0.1
    elif kind == "gold":
        rate = 0.15
    elif kind == "vip":
        rate = 0.25
    else:
        rate = 0

    if total > 500:
        rate = rate + 0.02

    try:
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute(
            "SELECT blocked FROM customers WHERE id = ?", (customer_id,)
        ).fetchone()
        if row and row[0]:
            rate = 0
    except Exception:
        pass

    return total - total * rate
