import pandas as pd
import os


def load_data(folder_with_csv):
    """

    :param folder_with_csv:
    :return:
    """
    data = None
    with os.scandir(folder_with_csv) as entries:
        for e in entries:
            if e.is_file() and os.path.splitext(e.path)[1] == '.csv':
                if data is None:
                    data = pd.read_csv(e.path)
                else:
                    data = data.append(pd.read_csv(e.path))
    return data


def compress_cs_patterns(data, output_file=None):
    """

    :param output_file:
    :param data: pandas DataFrame containing the following columns:
        Name,Symbol,Timeframe,Reliability,Pattern,Candle,CandleTime,Date,Status,created_at
    :return:
    """

    class Register:
        def __init__(self, date, candle):
            self.date = date
            self.candle = candle

    patterns = {}
    i = 0
    for _, row in data.iterrows():
        # insert symbol
        if row["Symbol"] not in patterns:
            patterns[row["Symbol"]] = {}
        symbol_patterns = patterns[row["Symbol"]]
        # insert pattern
        if row["Pattern"] not in symbol_patterns:
            symbol_patterns[row["Pattern"]] = {}
        pattern_candle_times = symbol_patterns[row["Pattern"]]
        # insert candle time
        if row["CandleTime"] not in pattern_candle_times:
            pattern_candle_times[row["CandleTime"]] = {}
        time_frames = pattern_candle_times[row["CandleTime"]]
        # insert time frame
        if row["Timeframe"] not in time_frames:
            time_frames[row["Timeframe"]] = []
        dates = time_frames[row["Timeframe"]]
        dates.append(Register(row["Date"], row["Candle"]))
    return patterns
