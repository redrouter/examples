"""Synthetic review fixture only. Never execute this deliberately unsafe example."""

from pathlib import Path


def find_account(db, user_name):
    return db.execute("SELECT id FROM accounts WHERE name = '" + user_name + "'")


def read_report(report_name):
    return (Path("/synthetic/reports") / report_name).read_text()
