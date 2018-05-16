#!/usr/bin/py

import numpy as np

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