#!/usr/bin/python

from __future__ import annotations

import pandas as pd
import urwid

import okane.io as io

g_columns = [
    # w0 s1  n2        align 3
    (10, 10, io.IOColumns.DATE, "left"),
    (3, 1, " ", "center"),
    (15, 15, io.IOColumns.AMOUNT, "right"),
    (3, 1, " ", "center"),
    (50, 50, io.IOColumns.DESCRIPTION, "right"),
    (3, 1, " ", "center"),
    (20, 20, io.IOColumns.ACCOUNT_TYPE, "center"),
    (3, 1, " ", "center"),
    (20, 20, io.IOColumns.CATEGORY, "center"),
]


def fmt(s, size):
    text = str(s)
    if len(text) > size:
        return text[:size]
    return text


class _Edit(urwid.Edit):

    def __init__(self, controller):
        urwid.Edit.__init__(self, [("label", "Search: ")], "")
        self.controller = controller

    def keypress(self, size, key):
        result = urwid.Edit.keypress(self, size, key)
        txt = self.get_edit_text()
        if result is not None:
            if key == "enter":
                self.controller.update_category(txt)
                return None
        return result


class _Row(urwid.WidgetWrap):

    def __init__(self, row, panel):
        self.panel = panel
        self.row = row

        cols = []
        for column in g_columns:
            if column[2] == " ":
                cols.append((column[0], urwid.Text(" ")))
            else:
                cols.append(
                    (
                        column[0],
                        urwid.Text(fmt(row[column[2]], column[1]), align=column[3]),
                    )
                )

        self.columns = urwid.Columns(cols)

        amount = float(str(row[io.IOColumns.AMOUNT]).replace(",", "").strip())
        account_type = str(row[io.IOColumns.ACCOUNT_TYPE])

        focused_color = "amount = focus"
        color = "amount ="

        if account_type == "debit" or account_type == "savings":
            if amount < 0:
                focused_color = "amount - focus"
                color = "amount -"
            else:
                focused_color = "amount + focus"
                color = "amount +"

        if account_type == "credit":
            if amount > 0:
                focused_color = "amount = focus"
                color = "amount ="
            else:
                focused_color = "amount - focus"
                color = "amount -"

        self.attr = urwid.AttrMap(self.columns, color, focused_color)
        urwid.WidgetWrap.__init__(self, self.attr)

    def selectable(self):
        return True

    def keypress(self, size, key):
        if key == "enter":
            print("what = ", self.row[io.IOColumns.DESCRIPTION])
            input_text = _Edit(self)
            self.panel.app.main_widget.set_footer(urwid.Columns([input_text]))
            self.panel.app.main_widget.set_focus("footer")
            return None
        return key

    def update_category(self, new_category):
        self.panel.app.main_widget.set_footer(self.panel.app.footer)


class TransactionsPanel(urwid.WidgetWrap):

    def __init__(self, app):
        # prepare data
        self.app = app
        # header
        self.header = urwid.Columns(
            [(column[0], urwid.Text(column[2])) for column in g_columns]
        )

        # create table rows
        self.transactions = []
        for index, row in self.app.data.iterrows():
            self.transactions.append(_Row(row, self))

        self.walker = urwid.SimpleFocusListWalker(self.transactions)
        self.view = urwid.ListBox(self.walker)
        self.widget = urwid.Frame(self.view, header=self.header)

        urwid.WidgetWrap.__init__(self, self.widget)

    def keypress(self, size, key):
        return super().keypress(size, key)
