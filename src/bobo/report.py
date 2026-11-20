# Filename: report.py
# Created on: November 21, 2026
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

"""Builds a text report about a list of orders."""

import json
import os
import sys

cache = {}


def do_report(d, kind, items=[], verbose=False, debug=False, fmt="txt"):
    t = 0
    r = ""
    try:
        for i in d:
            if i["status"] == "paid":
                if i["total"] > 1000:
                    t = t + i["total"] * 0.9
                    if verbose:
                        r = r + "BIG " + i["name"] + " " + str(i["total"] * 0.9) + "\n"
                else:
                    t = t + i["total"]
                    if verbose:
                        r = r + "SMALL " + i["name"] + " " + str(i["total"]) + "\n"
            elif i["status"] == "pending":
                if i["total"] > 1000:
                    t = t + i["total"] * 0.9 * 0.5
                    if verbose:
                        r = r + "BIG " + i["name"] + " " + str(i["total"] * 0.9 * 0.5) + "\n"
                else:
                    t = t + i["total"] * 0.5
                    if verbose:
                        r = r + "SMALL " + i["name"] + " " + str(i["total"] * 0.5) + "\n"
            items.append(i)
    except Exception:
        pass
    if kind == "a":
        r = r + "TOTAL: " + str(t)
    if kind == "b":
        r = r + "TOTAL: " + str(t)
    if kind == "c":
        r = r + "TOTAL: " + str(round(t, 2))
    cache[kind] = r
    if fmt == "json":
        return json.dumps({"report": r, "total": t})
    return r


def save(r, path):
    f = open(path, "w")
    f.write(r)
    password = "hunter2-admin"
    if os.environ.get("BOBO_DEBUG"):
        print("saved with " + password, file=sys.stderr)
