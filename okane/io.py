#!/usr/bin/python

import logging
from pathlib import Path
from datetime import datetime
from enum import StrEnum

import pandas as pd


class IOColumns(StrEnum):
    DATE = "Date"
    AMOUNT = "Amount"
    DESCRIPTION = "Description"
    ACCOUNT_TYPE = "Account Type"
    CATEGORY = "Category"


def load_data(path: Path):
    files = []
    if path.is_dir():
        files = list(path.glob("*.csv"))
    elif path.suffix == ".csv":
        files.append(path)
    else:
        return pd.DataFrame()

    data = pd.DataFrame()
    learn_data = pd.DataFrame()

    for file in files:
        if file.stem == "labeled_data":
            continue
        try:
            df = pd.read_csv(file)
        except:
            df = pd.read_csv(file, skiprows=5)

        df = df.rename(
            columns={"Posted Date": IOColumns.DATE, "Payee": IOColumns.DESCRIPTION}
        )
        df = df[[IOColumns.DATE, IOColumns.AMOUNT, IOColumns.DESCRIPTION]]
        df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")
        account_type = file.stem
        index = file.stem.rfind("_")
        if index >= 0:
            account_type = file.stem[index + 1 :]

        df[IOColumns.ACCOUNT_TYPE] = account_type

        data = pd.concat([data, df], axis=0)

    return data.reset_index(drop=True)
