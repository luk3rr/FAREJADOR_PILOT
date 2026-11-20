# Filename: test_cli.py
# Created on: November 21, 2026
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import pytest

from bobo.cli import main


def test_add(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["add", "2", "3"]) == 0
    assert capsys.readouterr().out.strip() == "5.0"


def test_words(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["words", "uma frase qualquer"]) == 0
    assert capsys.readouterr().out.strip() == "3"
