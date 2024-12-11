#!/usr/bin/py

import pandas as pd
import os


# Holds investing.com candlestick patterns
class CSPatternList:
    def __init__(self, path):
        self.data = None
        with os.scandir(path) as entries:
            for e in entries:
                if e.is_file() and os.path.splitext(e.path)[1] == '.csv':
                    if self.data is None:
                        self.data = pd.read_csv(e.path)
                    else:
                        self.data.append(pd.read_csv(e.path))
        # imgui settings
        self.selected_row = 0

    def draw_filter_menu(self, imgui):
        imgui.separator()

    def draw(self, imgui):
        imgui.begin("CS Patterns")
        imgui.columns(len(self.data.columns) + 1, "asodf")
        imgui.separator()
        imgui.text("")
        imgui.next_column()
        for c in self.data.columns:
            imgui.text(c)
            imgui.next_column()
        imgui.separator()
        # fill with data
        for i in range(10):
            label = str(i)
            clicked, _ = imgui.selectable(
                label=label,
                selected=self.selected_row == i,
                flags=imgui.SELECTABLE_SPAN_ALL_COLUMNS,
            )
            if clicked:
                self.selected_row = i
            hovered = imgui.is_item_hovered()
            row = self.data.loc[i]
            imgui.next_column()
            for c in self.data.columns:
                imgui.text(row[c])
                imgui.next_column()
        imgui.end()
