# Filename: test_inventory.py
# Created on: November 21, 2026
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import pytest

from bobo import inventory


def make() -> inventory.sqlite3.Connection:
    conn = inventory.connect(":memory:")
    inventory.add_item(conn, "pen", 10, 2.5)
    return conn


def test_add_and_find_item() -> None:
    assert inventory.find_item(make(), "pen") == ("pen", 10, 2.5)
    assert inventory.find_item(make(), "ghost") is None


def test_adding_the_same_item_again_adds_stock_instead_of_a_duplicate() -> None:
    conn = make()
    inventory.add_item(conn, "pen", 5, 3.0)
    assert inventory.find_item(conn, "pen") == ("pen", 15, 3.0)
    assert conn.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 1


def test_a_hostile_name_is_data_not_sql() -> None:
    conn = make()
    inventory.add_item(conn, "x'); DROP TABLE items; --", 1, 1.0)
    assert inventory.find_item(conn, "x'); DROP TABLE items; --") is not None
    assert inventory.find_item(conn, "pen") is not None


def test_average_price_of_an_empty_inventory_is_zero() -> None:
    assert inventory.average_price(inventory.connect(":memory:")) == 0.0
    assert inventory.average_price(make()) == 2.5


def test_process_order() -> None:
    conn = make()
    assert inventory.process_order(conn, {"items": [{"name": "pen", "qty": 2}]}) == 5.0
    assert inventory.find_item(conn, "pen") == ("pen", 8, 2.5)


def test_an_order_that_cannot_be_fulfilled_changes_nothing() -> None:
    conn = make()
    inventory.add_item(conn, "ink", 1, 9.0)
    order = {"items": [{"name": "pen", "qty": 2}, {"name": "ink", "qty": 5}]}
    with pytest.raises(inventory.OrderError, match="not enough stock for ink"):
        inventory.process_order(conn, order)
    assert inventory.find_item(conn, "pen") == ("pen", 10, 2.5)


def test_repeated_lines_of_the_same_item_are_summed_against_the_stock() -> None:
    conn = make()
    order = {"items": [{"name": "pen", "qty": 6}, {"name": "pen", "qty": 6}]}
    with pytest.raises(inventory.OrderError):
        inventory.process_order(conn, order)
    assert inventory.find_item(conn, "pen") == ("pen", 10, 2.5)


@pytest.mark.parametrize("entry", [{"name": "ghost", "qty": 1}, {"name": "pen", "qty": 0}])
def test_unknown_items_and_bad_quantities_are_errors(entry: dict[str, object]) -> None:
    with pytest.raises(inventory.OrderError):
        inventory.process_order(make(), {"items": [entry]})


def test_the_reports_list_only_what_is_low_or_out() -> None:
    conn = make()
    inventory.add_item(conn, "ink", 0, 9.0)
    assert inventory.low_stock_report(conn, 5) == ["ink: 0 left (threshold 5)"]
    assert inventory.out_of_stock_report(conn) == ["ink: 0 left (threshold 1)"]


def test_a_writer_on_another_connection_waits_while_an_order_is_in_progress(tmp_path) -> None:  # type: ignore[no-untyped-def]
    path = str(tmp_path / "inv.db")
    first = inventory.connect(path)
    inventory.add_item(first, "pen", 10, 2.5)
    second = inventory.sqlite3.connect(path, timeout=0.05)
    first.execute("BEGIN IMMEDIATE")  # what process_order does before it reads anything
    with pytest.raises(inventory.sqlite3.OperationalError, match="locked"):
        second.execute("UPDATE items SET qty = 0")
    first.rollback()
    second.close()
    first.close()
