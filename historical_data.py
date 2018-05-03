#!/usr/bin/py
import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from b3_register import B3Register

if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument("file", type=str, help="b3 historical data .txt file")
    args = parse.parse_args()
    columns = []
    registers = []
    with open(args.file, 'r') as f:
        lines = f.readlines()
        for i in range(1, len(lines)-1):
            b3Register = B3Register(lines[i])
            register = []
            for attribute in b3Register.attributes:
                register.append(b3Register.attributes[attribute])
                if i == 1:
                    columns.append(attribute)
            registers.append(register)
    data = np.array(registers)
    df = pd.DataFrame(data = data[0:,0:],columns=columns)
    vale5 = df[df['negotiationCode'] == 'VALE5']
    vale5Close = vale5[['date', 'closePrice']]
    # Calculate the 20 and 100 days moving averages of the closing prices
    short_rolling = vale5Close.rolling(window=10).mean()
    long_rolling = vale5Close.rolling(window=20).mean()

    # Plot everything by leveraging the very powerful matplotlib package
    fig, ax = plt.subplots(figsize=(16,9))

    ax.plot(vale5Close['date'], vale5Close['closePrice'], label='VALE5')
    # ax.plot(short_rolling['date'], short_rolling['closePrice'], label='20 days rolling')
    ax.plot(long_rolling['date'], long_rolling['closePrice'], label='100 days rolling')

    ax.set_xlabel('Date')
    ax.set_ylabel('Adjusted closing price ($)')
    ax.legend()

    plt.show()