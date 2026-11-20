# Filename: test_text.py
# Created on: November 21, 2026
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

from bobo import text


def test_count_words() -> None:
    assert text.count_words("uma frase qualquer") == 3
    assert text.count_words("") == 0


def test_slugify() -> None:
    assert text.slugify("  Olá, Mundo Bobo!  ") == "ol-mundo-bobo"
