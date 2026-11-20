# Filename: test_stats.py
# Created on: November 21, 2026
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

from bobo import stats


def test_mean() -> None:
    assert stats.mean([1, 2, 3]) == 2


def test_median_of_an_odd_list() -> None:
    assert stats.median([3, 1, 2]) == 2
