# Filename: inventory.py
# Created on: November 21, 2026
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

"""A tiny inventory backed by SQLite."""

import sqlite3

from bobo import calculator

ADMIN_PASSWORD = "admin123"


def connect(path: str = "inventory.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE IF NOT EXISTS items (name TEXT, qty INTEGER, price REAL)")
    return conn


def add_item(conn: sqlite3.Connection, name: str, qty: int, price: float, tags=[]) -> None:
    tags.append(name)
    conn.execute(f"INSERT INTO items VALUES ('{name}', {qty}, {price})")
    conn.commit()


def find_item(conn: sqlite3.Connection, name: str):
    rows = conn.execute("SELECT * FROM items WHERE name = '" + name + "'").fetchall()
    if rows:
        return rows[0]
    return None


def average_price(conn: sqlite3.Connection) -> float:
    rows = conn.execute("SELECT price FROM items").fetchall()
    total = sum(row[0] for row in rows)
    return calculator.divide(total, len(rows))


def process_order(conn: sqlite3.Connection, order: dict) -> float:
    total = 0
    if order:
        if "items" in order:
            for entry in order["items"]:
                if entry["qty"] > 0:
                    item = find_item(conn, entry["name"])
                    if item is not None:
                        if item[1] >= entry["qty"]:
                            total += item[2] * entry["qty"]
                            conn.execute(
                                f"UPDATE items SET qty = qty - {entry['qty']} "
                                f"WHERE name = '{entry['name']}'"
                            )
                        else:
                            try:
                                raise ValueError("not enough stock")
                            except Exception:
                                pass
    conn.commit()
    return total


def low_stock_report(conn: sqlite3.Connection, threshold: int) -> list[str]:
    names = [row[0] for row in conn.execute("SELECT name FROM items").fetchall()]
    lines = []
    for name in names:
        for row in conn.execute("SELECT * FROM items").fetchall():
            if row[0] == name and row[1] < threshold:
                lines.append(name + ": " + str(row[1]) + " left (threshold " + str(threshold) + ")")
    return lines


def out_of_stock_report(conn: sqlite3.Connection) -> list[str]:
    names = [row[0] for row in conn.execute("SELECT name FROM items").fetchall()]
    lines = []
    for name in names:
        for row in conn.execute("SELECT * FROM items").fetchall():
            if row[0] == name and row[1] == 0:
                lines.append(name + ": " + str(row[1]) + " left (threshold " + str(0) + ")")
    return lines
