#!/usr/bin/py

def minIndex(v, f, l):
    minI = f
    for i in range(f,l+1):
        if v[minI] > v[i]:
            minI = i
    return minI

def maxIndex(v, f, l):
    maxI = f
    for i in range(f,l+1):
        if v[maxI] < v[i]:
            maxI = i
    return maxI

def regionalLocals(prices, windowRadius = 15):
    maxima = []
    minima = []
    for i in range(windowRadius, len(prices) - windowRadius):
        if maxIndex(prices, i - windowRadius, i + windowRadius) == i:
            maxima.append(i)
        elif minIndex(prices, i - windowRadius, i + windowRadius) == i:
            minima.append(i)
    return maxima, minima

def perceptuallyImportantPoints(prices, n=5):
    pips = [0, len(prices) - 1]
    def distance(x0, y0, x1, y1):
        return (x0 - x1)**2 + (y0 - y1)**2
    def pip(l, h):
        m = 0
        mi = 0
        for i in range(l + 1, h):
            dist = distance(i, prices[i], l, prices[l]) + distance(i, prices[i], h, prices[h])
            if dist > m:
                m = dist
                mi = i
        return mi, m
    while len(pips) < n:
        m = 0
        mi = 0
        for i in range(len(pips) - 1):
            if pips[i + 1] - 1 > pips[i]:
                mmi, mm = pip(pips[i], pips[i + 1])
                if mm > m:
                    m = mm
                    mi = mmi
        pips.append(mi)
        pips.sort()
    return pips

def simplifySeries(prices, k = 18, t=0.5):
    def mergeCost(s1, s2):
        cost = 0
        A = prices[int(s1[0])]
        B = prices[int(s2[1])]
        for i in range(s1[0],s2[1] + 1):
            a = (i - s1[0]) / (s2[1] - s1[0])
            cost = cost + (prices[i] - (a * A + (1 - a)*B))**2
        return cost
    segments = []
    for i in range(int(len(prices)/2)):
        segments.append([i * 2, i * 2 + 1])
    costs = (len(segments) - 1) * [0]
    for i in range(len(costs)):
        costs[i] = mergeCost(segments[i], segments[i+1])
    while len(segments) > len(prices) / k:
        minI = minIndex(costs,0,len(costs)-1)
        segments[minI][1] = segments[minI + 1][1]
        del segments[minI + 1]
        if minI > 0:
            costs[minI - 1] = mergeCost(segments[minI - 1], segments[minI])
        if len(segments) > minI + 1:
            costs[minI] = mergeCost(segments[minI], segments[minI + 1])
        if len(costs) - 1 > minI:
            del costs[minI + 1]
        else:
            del costs[minI]
    s = []
    for i in range(len(segments)):
        s.append(segments[i])
        if i < len(segments) - 1:
            s.append([segments[i][1], segments[i+1][0]])
    changed = True
    while changed:
        changed = False
        # merge trends
        for i in range(len(s) - 1):
            if (prices[s[i][0]] - prices[s[i][1]]) * (prices[s[i + 1][0]] - prices[s[i + 1][1]]) >= 0:
                s[i][1] = s[i+1][1]
                del s[i+1]
                changed = True
                break
        # fix extremes
        for i in range(len(s) - 1):
            if prices[s[i][0]] - prices[s[i][1]] < 0: 
                s[i][1] = s[i+1][0] = maxIndex(prices,s[i][0],s[i+1][1])
            else:
                s[i][1] = s[i+1][0] = minIndex(prices,s[i][0],s[i+1][1])
        # remove small variation segments
        for i in range(len(s)):
            if abs(prices[s[i][0]] - prices[s[i][1]]) < t:
                changed = True
                if i == 0:
                    s[i + 1][0] = s[i][0]
                elif i == len(s) - 1:
                    s[i- 1][1] = s[i][1]
                else:
                    s[i - 1][1] = s[i + 1][0]
                del s[i]
                break
    l = []
    for k in s:
        l.append(k[0])
    l.append(s[-1][1])
    return l