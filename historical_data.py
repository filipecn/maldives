#!/usr/bin/py
import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class B3Register:
    def __init__(self, string):
        #B3 register structure
        self.attributes = {}
        self.attributes["type"] = string[0:2]
        self.attributes["date"] = '-'.join([string[6:8], string[8:10], string[2:6]])
        self.attributes["bdiCode"] = string[10:12]
        self.attributes["negotiationCode"] = string[12:24]
        self.attributes["marketType"] = string[24:27]
        self.attributes["name"] = string[27:39]
        self.attributes["specification"] = string[39:49]
        self.attributes["termMarketDue"] = string[49:52]
        self.attributes["currency"] = string[52:56]
        self.attributes["openPrice"] = float(string[56:69])
        self.attributes["maxPrice"] = float(string[69:82])
        self.attributes["minPrice"] = float(string[82:95])
        self.attributes["medPrice"] = float(string[95:108])
        self.attributes["closePrice"] = float(string[108:121])
        self.attributes["bestBuyOffer"] = float(string[121:134])
        self.attributes["bestSellOffer"] = float(string[134:147])
        self.attributes["negotiationVolume"] = int(string[147:152])
        self.attributes["titleNegotiationCount"] = int(string[152:170])
        self.attributes["titleNegotiationVolume"] = int(string[170:188])
        self.attributes["preexe"] = string[188:201]
        self.attributes["indopc"] = string[201:202]
        self.attributes["datven"] = string[202:210]
        self.attributes["quoteFactor"] = string[210:217]
        self.attributes["ptoexe"] = string[217:230]
        self.attributes["codisi"] = string[230:242]
        self.attributes["dismes"] = string[242:245]


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
    print(df.describe())

