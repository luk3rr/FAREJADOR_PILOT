# Filename: test_calculator.py
# Created on: November 21, 2026
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import pytest

from bobo import calculator


def test_the_four_operations() -> None:
    assert calculator.add(2, 3) == 5
    assert calculator.subtract(5, 3) == 2
    assert calculator.multiply(4, 3) == 12
    assert calculator.divide(9, 3) == 3


def test_dividing_by_zero_is_an_error() -> None:
    with pytest.raises(ValueError):
        calculator.divide(1, 0)
