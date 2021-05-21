import numpy as np
import math
from pandas import DataFrame


def min_rw_index(prices, start, end):
    """
        Searches min price index inside window [start,end]

    :param prices: in list format
    :param start: window start index
    :param end: window end index
    :return:
    """
    matching_index = start
    for i in range(start, end + 1):
        if prices[matching_index] > prices[i]:
            matching_index = i
    return matching_index


def max_rw_index(prices, start, end):
    """
        Searches min price index inside window [start,end]

    :param prices: in list format
    :param start: window start index
    :param end: window end index
    :return:
    """
    matching_index = start
    for i in range(start, end + 1):
        if prices[matching_index] < prices[i]:
            matching_index = i
    return matching_index


def get_closest_resistance(values_and_indices, price, current_index):
    values = values_and_indices[0]
    indices = values_and_indices[1]
    value = 10000000
    resistance_index = -1
    for i in range(len(values)):
        avg = np.array(values[i]).mean()
        if price <= avg <= value and min(indices[i]) <= current_index:
            value = avg
            resistance_index = i
    return value, resistance_index


def get_closest_support(values_and_indices, price, current_index):
    values = values_and_indices[0]
    indices = values_and_indices[1]
    value = -10000000
    support_index = -1
    for i in range(len(values)):
        avg = np.array(values[i]).mean()
        if value <= avg <= price and min(indices[i]) <= current_index:
            value = avg
            support_index = i
    return value, support_index


class TA:
    data: DataFrame

    def __init__(self, data):
        self.data = data.reset_index(drop=False)

    def run(self, callback, user_data):
        close_prices = self.data["close"].to_list()

        for i in range(len(close_prices)):
            callback(self, i, close_prices[i], user_data)

    # PATTERNS
    def candle_directions(self, tail=0):
        if tail == 0:
            tail = len(self.data['close'])
        close_prices = self.data['close'].tail(tail).to_list()
        open_prices = self.data['open'].tail(tail).to_list()
        colors = tail * [1]
        for i in range(tail):
            if close_prices[i] < open_prices[i]:
                colors[i] = -1
        return colors

    def reversals(self):
        close_prices = self.data['close'].to_list()
        open_prices = self.data['open'].to_list()
        r = len(close_prices) * [0]
        for i in range(2, len(close_prices)):
            min_0 = min([open_prices[i - 2], close_prices[i - 2]])
            min_1 = min([open_prices[i - 1], close_prices[i - 1]])
            min_2 = min([open_prices[i - 0], close_prices[i - 0]])
            if min_1 < min_0 and min_1 < min_2:
                r[i] = -1
                continue
            max_0 = min([open_prices[i - 2], close_prices[i - 2]])
            max_1 = min([open_prices[i - 1], close_prices[i - 1]])
            max_2 = min([open_prices[i - 0], close_prices[i - 0]])
            if max_1 > max_0 and max_1 > max_2:
                r[i] = 1
        return r

    # INDICATORS
    def resistance_lines(self, resistance_type, threshold=0.02):
        """
        Support occurs when falling prices stop, change direction, and begin to
        rise. Support is often viewed as a “floor” which is supporting, or
        holding up, prices.

        Resistance is a price level where rising prices stop, change direction,
        and begin to fall. Resistance is often viewed as a “ceiling” keeping
        prices from rising higher.
        
        If price breaks support or resistance, the price often continues to the
        next level of support or resistance. Support and resistance levels are
        not always exact; they are usually a zone covering a small range of prices
        so levels can be breached, or pierced, without necessarily being broken.
        As a result, support/resistance levels help identify possible points where
        price may change directions.

        :param resistance_type: 's' for support lines, 'r' for resistance lines
        :param threshold:
        :return:
        """
        values, ids = [], []

        open_prices = self.data["open"].to_list()
        close_prices = self.data["close"].to_list()

        for i in range(1, len(open_prices) - 1):
            # find minima/maxima
            t_0 = min(open_prices[i - 1], close_prices[i - 1])
            t_1 = min(open_prices[i + 0], close_prices[i + 0])
            t_2 = min(open_prices[i + 1], close_prices[i + 1])
            if resistance_type == 'r':
                t_0 = max(open_prices[i - 1], close_prices[i - 1])
                t_1 = max(open_prices[i + 0], close_prices[i + 0])
                t_2 = max(open_prices[i + 1], close_prices[i + 1])
            check = t_1 >= t_0 and t_1 >= t_2
            if resistance_type == "s":
                check = t_1 <= t_0 and t_1 <= t_2
            if check:
                # check if this one belongs to past support points
                found = False
                for j in range(len(values)):
                    if abs((np.mean(values[j]) - t_1) / t_1) <= threshold:
                        values[j].append(t_1)
                        ids[j].append(i)
                        found = True
                        break
                if not found:
                    values.append([t_1])
                    ids.append([i])

        return values, ids

    def rsi(self, initial_size=14, window_size=14):
        """
        The relative strength index (RSI) is most commonly used to indicate
        temporarily overbought or oversold conditions in a market.
        
        A market is overbought when the RSI value is over 70 and indicates
        oversold conditions when RSI readings are under 30.

        A weakness of the RSI is that sudden, sharp price movements can cause
        it to spike repeatedly up or down, and, thus, it is prone to giving
        false signals. However, if those spikes or falls show a trading
        confirmation when compared with other signals, it could signal an entry
        or exit point.

        :param initial_size: 
        :param window_size: 
        :return: 
        """
        price = self.data["close"].to_list()

        gain = len(price) * [0]
        loss = len(price) * [0]
        for i in range(1, len(price)):
            if price[i] > price[i - 1]:
                gain[i] = price[i] - price[i - 1]
            else:
                loss[i] = price[i - 1] - price[i]
        average_gain = np.mean(gain[:initial_size + 1])
        average_loss = np.mean(loss[:initial_size + 1])
        rsi = len(price) * [50]
        for i in range(initial_size, len(price)):
            average_gain = (average_gain * (window_size - 1) + gain[i]) / window_size
            average_loss = (average_loss * (window_size - 1) + loss[i]) / window_size
            rs = average_gain
            if average_loss != 0:
                rs = rs / average_loss
            rsi[i] = 100 - 100 / (1 + rs)
        return rsi

    def bollinger_bands(self, window_size=10, num_of_std=5):
        """
        Bollinger Bands are a form of technical analysis that traders
        use to plot trend lines that are two standard deviations away
        from the simple moving average price of a security. The goal is
        to help a trader know when to enter or exit a position by identifying
        when an asset has been overbought or oversold.

        :param window_size: 
        :param num_of_std: 
        :return: 
        """
        price = self.data["close"]
        rolling_mean = price.rolling(window=window_size).mean()
        rolling_std = price.rolling(window=window_size).std()
        upper_band = rolling_mean + (rolling_std * num_of_std)
        lower_band = rolling_mean - (rolling_std * num_of_std)
        return rolling_mean, upper_band, lower_band

    def regional_locals(self, window_radius=15):
        """
        Compute minima and maxima points within a rolling window

        :param window_radius: rolling window half size (full size is 2w+1)
        :return:
        """
        prices = self.data["close"]

        maxima = []
        minima = []
        for i in range(window_radius, len(prices) - window_radius):
            if max_rw_index(prices, i - window_radius, i + window_radius) == i:
                maxima.append(i)
            elif min_rw_index(prices, i - window_radius, i + window_radius) == i:
                minima.append(i)
        return maxima, minima

    def sma(self, window):
        """
        Computes the Simple Moving Average given a rolling window size
        :param window: window size
        :return:
        """
        prices = self.data["close"]
        return prices.rolling(window=window).mean()

    def ema(self, window):
        """
        Computes the Exponential Moving Average
        :param window:
        :return:
        """
        prices = self.data["close"]
        # return prices.ewm(span=window).mean()
        sma_w = self.sma(window)
        mod_price = prices.copy()
        mod_price.iloc[0:window] = sma_w[0:window]
        return mod_price.ewm(span=window, adjust=False).mean()

    def mac(self, short_window, long_window, average_type="sma"):
        """
        Compute Moving Averages Crossovers

        :param short_window:
        :param long_window:
        :param average_type:
        :return:
        """
        short = np.array(self.sma(short_window))
        long = np.array(self.sma(long_window))
        mac = short - long
        signal = len(short) * [0]
        for i in range(long_window + 1, len(signal)):
            if mac[i] > 0 and mac[i - 1] < 0:
                signal[i] = 1
            elif mac[i] < 0 and mac[i - 1] > 0:
                signal[i] = -1
        return mac, signal

    # MEASURES
    def pct_change(self, window_size=1):
        prices = self.data["close"]
        return prices.pct_change(periods=window_size)

    def max_in_range(self, start_index: int = 0, end_index: int = -1):
        if end_index < 0:
            end_index = len(self.data) - 1
        prices = self.data["close"].to_list()
        i = max_rw_index(prices, start_index, end_index)
        return prices[i], i - start_index

    def max_pct_in_range(self, start_index: int = 0, end_index: int = -1):
        if end_index < 0:
            end_index = len(self.data) - 1
        prices = self.data["close"].to_list()
        i = max_rw_index(prices, start_index, end_index)
        return (prices[i] - prices[start_index]) / prices[start_index] * 100.0, i - start_index

    def single_pct_change(self, start_index: int = 0, end_index: int = -1):
        if end_index < 0:
            end_index = len(self.data) - 1
        prices = self.data["close"].to_list()
        return (prices[end_index] - prices[start_index]) / prices[start_index] * 100.0

    # SIMPLIFICATION
    def pips(self, n=5, distance_type="euclidean"):
        """
            Finds n Perceptually Important Points(PIPs)

            The algorithm starts by characterizing the first and the
            last observation as the first two PIPs. Subsequently, it
            calculates the distance between all remaining observations
            and the two initial PIPs and signifies as the third PIP the
            one with the maximum distance.
        :param n: total number of pips
        :param distance_type: distance type between pips: "euclidean",
                              "perpendicular" or "vertical"
        :return:
        """

        def pip_euclidean_distance(xi, xt, xtt, pi, pt, ptt):
            return math.sqrt((xt - xi) ** 2 + (pt - pi) ** 2) + math.sqrt((xtt - xi) ** 2 + (ptt - pi) ** 2)

        def pip_perpendicular_distance(xi, xt, xtt, pi, pt, ptt):
            s = (ptt - pt) / (xtt - xt)
            c = pt - xt * s
            return abs(s * xi + c - pi) / math.sqrt(s * s + 1)

        def pip_vertical_distance(xi, xt, xtt, pi, pt, ptt):
            s = (ptt - pt) / (xtt - xt)
            c = pt - xt * s
            return abs(s * xi + c - pi)

        prices = self.data["close"]
        pips = [0, len(prices) - 1]

        # function to find pip that maximizes the distance between left and right
        def pip(left, right):
            maximum_distance = 0
            maximum_distance_index = 0
            for i in range(left + 1, right):
                dist = pip_euclidean_distance(i, left, right, prices[i], prices[left], prices[right])
                if dist > maximum_distance:
                    maximum_distance = dist
                    maximum_distance_index = i
            return maximum_distance_index, maximum_distance

        # generate pips
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

    def decimate(self, k=18, t=0.5):
        """

        :param k:
        :param t:
        :return:
        """
        prices = self.data["close"]

        def merge_cost(s1, s2):
            cost = 0
            A = prices[int(s1[0])]
            B = prices[int(s2[1])]
            for i in range(s1[0], s2[1] + 1):
                a = (i - s1[0]) / (s2[1] - s1[0])
                cost = cost + (prices[i] - (a * A + (1 - a) * B)) ** 2
            return cost

        segments = []
        for i in range(int(len(prices) / 2)):
            segments.append([i * 2, i * 2 + 1])
        costs = (len(segments) - 1) * [0]
        for i in range(len(costs)):
            costs[i] = merge_cost(segments[i], segments[i + 1])
        while len(segments) > len(prices) / k:
            minI = min_rw_index(costs, 0, len(costs) - 1)
            segments[minI][1] = segments[minI + 1][1]
            del segments[minI + 1]
            if minI > 0:
                costs[minI - 1] = merge_cost(segments[minI - 1], segments[minI])
            if len(segments) > minI + 1:
                costs[minI] = merge_cost(segments[minI], segments[minI + 1])
            if len(costs) - 1 > minI:
                del costs[minI + 1]
            else:
                del costs[minI]
        s = []
        for i in range(len(segments)):
            s.append(segments[i])
            if i < len(segments) - 1:
                s.append([segments[i][1], segments[i + 1][0]])
        changed = True
        while changed:
            changed = False
            # merge trends
            for i in range(len(s) - 1):
                if (prices[s[i][0]] - prices[s[i][1]]) * (prices[s[i + 1][0]] - prices[s[i + 1][1]]) >= 0:
                    s[i][1] = s[i + 1][1]
                    del s[i + 1]
                    changed = True
                    break
            # fix extremes
            for i in range(len(s) - 1):
                if prices[s[i][0]] - prices[s[i][1]] < 0:
                    s[i][1] = s[i + 1][0] = max_rw_index(prices, s[i][0], s[i + 1][1])
                else:
                    s[i][1] = s[i + 1][0] = min_rw_index(prices, s[i][0], s[i + 1][1])
            # remove small variation segments
            for i in range(len(s)):
                if abs(prices[s[i][0]] - prices[s[i][1]]) < t:
                    changed = True
                    if i == 0:
                        s[i + 1][0] = s[i][0]
                    elif i == len(s) - 1:
                        s[i - 1][1] = s[i][1]
                    else:
                        s[i - 1][1] = s[i + 1][0]
                    del s[i]
                    break
        l = []
        for k in s:
            l.append(k[0])
        l.append(s[-1][1])
        return l

    # TODO
    def hsars(self, x=0.05, s=2):
        """
        Horizontal Support And Resistance levelS


        Input are regional locals

        :param x: desired percentage that will give the bounds for the HSARs
        :param s:
        :return:
        """
        prices = self.data["close"]

        lower_bound = min(prices) / (1 + x / 2)
        upper_bound = max(prices) * (1 + x / 2)
        # approximate number of bins
        approx_n = math.log(upper_bound / lower_bound) / math.log(1 + x)
        # actual number of bins
        n = int(approx_n + 0.5)
        # actual percentage for each bin
        actual_pct = (abs(upper_bound / lower_bound)) ** (1 / n) - 1
        bounds = []
        for i in range(n + 1):
            bounds.append((lower_bound * (1 + actual_pct) * i))
        freq = len(bounds) * [0]
        for p in prices:
            for i in range(len(bounds) - 1):
                if bounds[i] <= p < bounds[i + 1]:
                    freq[i] = freq[i] + 1
        sar = []
        for i in range(len(freq)):
            if freq[i] >= s:
                sar.append([bounds[i], bounds[i + 1]])
        return sar
