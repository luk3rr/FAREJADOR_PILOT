# Filename: test_discount.py
# Created on: November 23, 2026
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import sqlite3

import pytest

from bobo import discount


@pytest.fixture
def db(tmp_path, monkeypatch):
    path = str(tmp_path / "bobo.db")
    monkeypatch.setattr(discount, "DB_PATH", path)
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE customers (id INTEGER PRIMARY KEY, blocked INTEGER)")
    conn.execute("INSERT INTO customers VALUES (1, 0), (2, 1)")
    conn.commit()
    conn.close()
    return path


@pytest.mark.parametrize(
    ("kind", "expected"),
    [("regular", 95), ("silver", 90), ("gold", 85), ("vip", 75), ("other", 100)],
)
def test_rate_by_kind(db, kind, expected) -> None:
    assert discount.discount(1, kind, 100) == pytest.approx(expected)


def test_volume_bonus_applies_above_the_threshold(db) -> None:
    assert discount.discount(1, "gold", 1000) == pytest.approx(1000 * (1 - 0.17))
    assert discount.discount(1, "gold", 500) == pytest.approx(500 * (1 - 0.15))


def test_blocked_customer_gets_no_discount(db) -> None:
    assert discount.discount(2, "vip", 100) == 100


def test_unreadable_database_gets_no_discount(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(discount, "DB_PATH", str(tmp_path / "missing" / "bobo.db"))
    assert discount.discount(1, "vip", 100) == 100


def test_unreadable_database_is_logged(tmp_path, monkeypatch, caplog) -> None:
    monkeypatch.setattr(discount, "DB_PATH", str(tmp_path / "missing" / "bobo.db"))
    discount.discount(1, "vip", 100)
    assert "Could not check whether customer 1 is blocked" in caplog.text
