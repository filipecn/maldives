#!/usr/bin/python

from __future__ import annotations

import sys
import typing
import urwid
from rich.console import Console
from rich.table import Table
import logging
from pathlib import Path

import okane.io as io
from okane.categories import *
from okane.transactions_panel import TransactionsPanel
import pandas as pd


class App:

    palette = [
        ("foot", "black", "dark cyan"),
        ("normal", "white", ""),
        ("table_header", "black", "dark green"),
        ("amount - focus", "light red", "dark gray"),
        ("amount + focus", "light blue", "dark gray"),
        ("amount = focus", "light gray", "dark gray"),
        ("amount -", "dark red", ""),
        ("amount +", "white", ""),
        ("amount =", "light gray", ""),
    ]

    def __init__(self):
        self.data = io.load_data(Path("/home/filipecn/dev/maldives/okane/input"))
        self.data = cleanup_data(self.data)
        self.classifier = OneHotMatrix(
            Path("/home/filipecn/dev/maldives/okane/input/labeled_data.csv")
        )
        exit(0)

        self.data = self.data.sort_values(by=["Date"]).reset_index(drop=True)

        self.data = self.data.loc[~pd.isna(self.data[io.IOColumns.AMOUNT])]

        self.data[io.IOColumns.CATEGORY] = "cat"

        f1 = urwid.Button([("normal", "F1"), ("foot", "Help")])
        f10 = urwid.Button([("normal", "F10"), ("foot", "Quit")])
        urwid.connect_signal(f10, "click", self.handle_f10_buton)
        self.footer = urwid.Columns([f1, f10])

        self.transactions = TransactionsPanel(self)
        self.main_widget = urwid.Frame(self.transactions, footer=self.footer)
        self.loop = urwid.MainLoop(
            self.main_widget, self.palette, unhandled_input=self.handle_input
        )

    def handle_input(self, key):
        if type(key) == str:
            if key in ("q", "Q"):
                raise urwid.ExitMainLoop()

    def handle_f10_buton(self, key):
        raise urwid.ExitMainLoop()

    def run(self):
        self.loop.run()


if __name__ == "__main__":
    App().run()
    sys.exit(0)
