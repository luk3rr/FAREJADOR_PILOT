# Filename: inventory.py
# Created on: November 21, 2026
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

"""A tiny inventory backed by SQLite."""

import sqlite3
from collections.abc import Mapping, Sequence
from typing import Any


class OrderError(ValueError):
    """The order cannot be fulfilled; nothing was changed."""


def _check_quantity(quantity: object, name: str) -> int:
    """A quantity is a whole number of units; ``bool`` and fractions are rejected."""
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise OrderError(f"quantity for {name} must be a whole number: {quantity!r}")
    return quantity


def connect(path: str = "inventory.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS items "
        "(name TEXT PRIMARY KEY, qty INTEGER NOT NULL CHECK (qty >= 0), price REAL NOT NULL)"
    )
    return conn


def add_item(conn: sqlite3.Connection, name: str, qty: int, price: float) -> None:
    """Add stock for an item; an existing item gets the extra quantity and the new price."""
    qty = _check_quantity(qty, name)
    if qty < 0:
        raise OrderError(f"quantity for {name} cannot be negative: {qty}")
    with conn:
        conn.execute(
            "INSERT INTO items (name, qty, price) VALUES (?, ?, ?) "
            "ON CONFLICT(name) DO UPDATE SET qty = qty + excluded.qty, price = excluded.price",
            (name, qty, price),
        )


def find_item(conn: sqlite3.Connection, name: str) -> tuple[str, int, float] | None:
    row = conn.execute("SELECT name, qty, price FROM items WHERE name = ?", (name,)).fetchone()
    return None if row is None else (row[0], row[1], row[2])


def average_price(conn: sqlite3.Connection) -> float:
    """The mean price over all items; 0.0 when the inventory is empty."""
    average = conn.execute("SELECT AVG(price) FROM items").fetchone()[0]
    return 0.0 if average is None else float(average)


def _price_line(conn: sqlite3.Connection, entry: Mapping[str, Any]) -> float:
    """Check one order line against the stock and return its price."""
    quantity = _check_quantity(entry["qty"], entry["name"])
    if quantity <= 0:
        raise OrderError(f"invalid quantity for {entry['name']}: {quantity}")
    item = find_item(conn, entry["name"])
    if item is None:
        raise OrderError(f"unknown item: {entry['name']}")
    if item[1] < quantity:
        raise OrderError(f"not enough stock for {entry['name']}: {item[1]} left, {quantity} asked")
    return item[2] * quantity


def process_order(conn: sqlite3.Connection, order: Mapping[str, Any]) -> float:
    """Fulfil an order and return its total.

    The write transaction opens before anything is read, and the stock check is part of each
    ``UPDATE``, so another connection cannot change the stock in between. If any line cannot be
    fulfilled, an ``OrderError`` is raised and nothing is changed.
    """
    entries: Sequence[Mapping[str, Any]] = order.get("items", [])
    needed: dict[str, int] = {}
    for entry in entries:
        quantity = _check_quantity(entry["qty"], entry["name"])
        needed[entry["name"]] = needed.get(entry["name"], 0) + quantity
    conn.execute("BEGIN IMMEDIATE")
    try:
        total = sum(_price_line(conn, entry) for entry in entries)
        for name, quantity in needed.items():
            updated = conn.execute(
                "UPDATE items SET qty = qty - ? WHERE name = ? AND qty >= ?",
                (quantity, name, quantity),
            )
            if updated.rowcount == 0:
                raise OrderError(f"not enough stock for {name}")
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    return total


def _report(conn: sqlite3.Connection, threshold: int) -> list[str]:
    rows = conn.execute(
        "SELECT name, qty FROM items WHERE qty < ? ORDER BY name", (threshold,)
    ).fetchall()
    return [f"{name}: {qty} left (threshold {threshold})" for name, qty in rows]


def low_stock_report(conn: sqlite3.Connection, threshold: int) -> list[str]:
    return _report(conn, threshold)


def out_of_stock_report(conn: sqlite3.Connection) -> list[str]:
    return _report(conn, 1)
