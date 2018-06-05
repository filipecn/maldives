#!/usr/bin/py

import numpy as np
import pandas as pd
import math

def hsars(prices, x = 0.05, s = 2):
    L1 = min(prices) / (1 + x/2)
    Ln = max(prices) * (1 + x/2)
    n = math.log(Ln / L1) / math.log(1 + x)
    N = int(n + 0.5)
    X = (abs(Ln / L1))**(1 / N) - 1
    bounds = []
    for i in range(N+1):
        bounds.append((L1 * (1 + X)**i))
    freq = len(bounds) * [0]
    for p in prices:
        for i in range(len(bounds) - 1):
            if p >= bounds[i] and p < bounds[i+1]:
                freq[i] = freq[i] + 1
    sar = []
    for i in range(len(freq)):
        if freq[i] >= s:
            sar.append([bounds[i], bounds[i + 1]])
    return sar

def computeResistenceLines(openPrices, closePrices, threshold=0.02):
    support = []
    supportIds = []
    for i in range(1, len(openPrices) - 1):
        #find minima
        t_0 = max(openPrices[i-1], closePrices[i-1])
        t_1 = max(openPrices[i+0], closePrices[i+0])
        t_2 = max(openPrices[i+1], closePrices[i+1])
        if t_1 >= t_0 and t_1 >= t_2:
            #check if this one belongs to past support points
            found = False
            for j in range(len(support)):
                if abs ((np.mean(support[j]) - t_1) / t_1) <= threshold:
                    support[j].append(t_1)
                    supportIds[j].append(i)
                    found = True
                    break
            if not found:
                support.append([t_1])
                supportIds.append([i])

            #define support lines and their strength
    return support, supportIds

def computeSupportLines(openPrices, closePrices, threshold=0.02):
    support = []
    supportIds = []
    for i in range(1, len(openPrices) - 1):
        #find minima
        t_0 = min(openPrices[i-1], closePrices[i-1])
        t_1 = min(openPrices[i+0], closePrices[i+0])
        t_2 = min(openPrices[i+1], closePrices[i+1])
        if t_1 <= t_0 and t_1 <= t_2:
            #check if this one belongs to past support points
            found = False
            for j in range(len(support)):
                if abs ((np.mean(support[j]) - t_1) / t_1) <= threshold:
                    support[j].append(t_1)
                    supportIds[j].append(i)
                    found = True
                    break
            if not found:
                support.append([t_1])
                supportIds.append([i])

            #define support lines and their strength
    return support, supportIds

def bollingerBands(price, windowSize=10, numOfStd=5):
    rolling_mean = price.rolling(window=windowSize).mean()
    rolling_std  = price.rolling(window=windowSize).std()
    upper_band = rolling_mean + (rolling_std*numOfStd)
    lower_band = rolling_mean - (rolling_std*numOfStd)
    return rolling_mean, upper_band, lower_band

def computeRSI(price, initialSize=250, windowSize=14):
    gain = len(price) * [0]
    loss = len(price) * [0]
    for i in range(1, len(price)):
        if price[i] > price[i-1]:
            gain[i] = price[i] - price[i-1]
        else:
            loss[i] = price[i-1] - price[i]
    averageGain = np.mean(gain[:initialSize + 1])
    averageLoss = np.mean(loss[:initialSize + 1])
    rsi = len(price) * [50]
    for i in range(initialSize, len(price)):
        averageGain = (averageGain * (windowSize - 1) + gain[i]) / windowSize
        averageLoss = (averageLoss * (windowSize - 1) + loss[i]) / windowSize
        rs = averageGain
        if averageLoss != 0:
            rs = rs / averageLoss
        rsi[i] = 100 - 100 / (1 + rs)
    return rsi
    