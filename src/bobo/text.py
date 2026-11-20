# Filename: text.py
# Created on: November 21, 2026
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

"""Tiny text helpers."""

import re


def count_words(text: str) -> int:
    return len(text.split())


def slugify(text: str) -> str:
    lowered = text.strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
