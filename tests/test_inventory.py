# Filename: test_inventory.py
# Created on: November 21, 2026
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

from bobo import inventory


def test_add_and_find_item() -> None:
    conn = inventory.connect(":memory:")
    inventory.add_item(conn, "pen", 10, 2.5)
    assert inventory.find_item(conn, "pen") == ("pen", 10, 2.5)


def test_process_order() -> None:
    conn = inventory.connect(":memory:")
    inventory.add_item(conn, "pen", 10, 2.5)
    total = inventory.process_order(conn, {"items": [{"name": "pen", "qty": 2}]})
    assert total == 5.0
