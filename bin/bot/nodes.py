import dearpygui.dearpygui as dpg
import pandas as pd
from maldives.technical_analysis import TA
from maldives.bot.exchanges.binance_exchange import BinanceExchange
from abc import ABC, abstractmethod
from datetime import datetime, timedelta


def introspect(obj):
    for func in [type, id, dir, vars, callable]:
        print("%s(%s):\t\t%s" % (func.__name__, introspect.__code__.co_varnames[0], func(obj)))


class Node(ABC):
    node_id: int
    output_node_ids: []

    def __init__(self, node_id):
        self.output_node_ids = []
        self.node_id = node_id

    def update(self):
        if self.update_internal():
            for i in self.output_node_ids:
                dpg.get_item_user_data(i).update()

    @abstractmethod
    def update_internal(self) -> bool:
        return True

    @abstractmethod
    def good(self) -> bool:
        return True

    def connect_output(self, node: int):
        self.output_node_ids.append(node)

    def disconnect_output(self, node: int):
        self.output_node_ids.remove(node)


class DealerNode(Node):
    binance: BinanceExchange

    def __init__(self, node_id, dealer):
        super().__init__(node_id)
        self.binance = dealer

    def update_internal(self) -> bool:
        return super().update_internal()

    def good(self) -> bool:
        return self.binance is not None


class SymbolNode(Node):
    symbols: []

    def __init__(self, node_id):
        super().__init__(node_id)
        self.symbols = ['BTC']

    def update_symbol(self, symbol):
        self.symbols = [symbol]
        self.update()

    def update_internal(self) -> bool:
        return True

    def good(self) -> bool:
        return len(self.symbols) > 0


class CurrentPriceNode(Node):
    # inputs
    dealer_id: int
    dealer: DealerNode
    symbols_id: int
    symbols: SymbolNode
    # data
    current_prices: {}
    text_id: int

    def __init__(self, node_id):
        super().__init__(node_id)
        self.current_price = {}
        self.dealer_id = 0
        self.symbols_id = 0
        self.dealer = None
        self.symbols = None
        self.text_id = 0

    def update_internal(self) -> bool:
        # remove text
        if self.text_id != 0:
            dpg.delete_item(self.text_id)
            self.text_id = 0

        if self.dealer is None or self.symbols is None:
            return True

        if not self.dealer.good() or not self.symbols.good():
            return True

        self.current_prices = self.dealer.binance.symbol_ticker(self.symbols.symbols)

        # add plot if needed
        if self.text_id == 0:
            self.text_id = dpg.add_node_attribute(parent=self.node_id, attribute_type=dpg.mvNode_Attr_Static)
            for s in self.current_prices:
                dpg.add_text(s + ' R$ %.2f' % float(self.current_prices[s].current), parent=self.text_id)

        return True

    def good(self) -> bool:
        return self.dealer is not None and self.symbols is not None and len(self.current_prices) > 0


class HistoryNode(Node):
    # inputs
    dealer_id: int
    dealer: DealerNode
    symbols_id: int
    symbols: SymbolNode
    # data
    prices: {}
    plot_id: int

    def __init__(self, node_id):
        super().__init__(node_id)
        self.prices = {}
        self.dealer = None
        self.symbols = None
        self.period = '1w'
        self.interval = '1h'
        self.dealer_id = 0
        self.symbols_id = 0
        self.plot_id = 0

    def update_internal(self) -> bool:
        # remove plot
        if self.plot_id != 0:
            dpg.delete_item(self.plot_id)
            self.plot_id = 0

        if self.dealer is None or self.symbols is None:
            return True

        start_date = datetime(year=2021, month=6, day=29)
        end_date = datetime(year=2021, month=6, day=30)

        if self.period == '1y':
            start_date = end_date - timedelta(days=365)
        elif self.period == '6m':
            start_date = end_date - timedelta(days=182)
        elif self.period == '1m':
            start_date = end_date - timedelta(days=30)
        elif self.period == '1w':
            start_date = end_date - timedelta(days=7)
        elif self.period == '1d':
            start_date = end_date - timedelta(days=1)

        if self.period == '1y' or self.period == '6m' or self.period == '1m':
            if self.interval == '15m' or self.interval == '30m':
                print('changing interval to 1h')
                self.interval = '1h'

        self.prices = self.dealer.binance.historical_candle_series(self.symbols.symbols, start_date, end_date,
                                                                   self.interval)
        # add plot if needed
        if self.plot_id == 0:
            data = self.prices[self.symbols.symbols[0]]['ta'].data['close'].to_list()
            self.plot_id = dpg.add_node_attribute(parent=self.node_id, attribute_type=dpg.mvNode_Attr_Static)
            dpg.add_simple_plot(label='', default_value=data, parent=dpg.last_item(), width=110, height=70)

        return True

    def update_interval(self, interval: str):
        self.interval = interval
        self.update()

    def update_period(self, period: str):
        self.period = period
        self.update()

    def good(self) -> bool:
        return self.dealer is not None and self.dealer.good() and \
               self.symbols is not None and self.symbols.good() and len(self.prices) > 0


class RollingMeanNode(Node):
    # inputs
    series_id: int
    series: HistoryNode
    # data
    mean_type: str
    window_size: int
    data: {}
    plot_id: int

    def __init__(self, node_id):
        super().__init__(node_id)
        self.mean_type = 'SMA'
        self.window_size = 7
        self.data = {}
        self.series_id = 0
        self.series = None
        self.plot_id = 0

    def update_internal(self) -> bool:
        # remove plot
        if self.plot_id != 0:
            dpg.delete_item(self.plot_id)
            self.plot_id = 0

        if self.series is None or not self.series.good():
            return True

        if len(self.series.prices) == 0:
            return True

        plot_symbol = ''
        w = 0
        for s in self.series.symbols.symbols:
            plot_symbol = s
            w = min([len(self.series.prices[s]['ta'].data), self.window_size])
            if self.mean_type == 'SMA':
                self.data[s] = self.series.prices[s]['ta'].sma(w)
            elif self.mean_type == 'EMA':
                self.data[s] = self.series.prices[s]['ta'].ema(w)

        if w == 0 or len(plot_symbol) == 0:
            return True

        # add plot if needed
        if self.plot_id == 0:
            self.plot_id = dpg.add_node_attribute(parent=self.node_id, attribute_type=dpg.mvNode_Attr_Static)
            dpg.add_simple_plot(label='', default_value=self.data[plot_symbol].to_list()[w - 1:],
                                parent=dpg.last_item(), width=110,
                                height=70)

        return True

    def update_type(self, mean_type: str):
        self.mean_type = mean_type
        self.update()

    def update_window_size(self, window_size: int):
        self.window_size = window_size
        self.update()

    def good(self) -> bool:
        return len(self.data) > 0


class ResistanceLinesNode(Node):
    # inputs
    series_id: int
    series: Node
    reference_prices_id: int
    reference_prices: Node
    # config
    threshold: float
    min_strength: int
    # data
    data_id: int
    data: {}

    def __init__(self, node_id):
        super().__init__(node_id)
        self.series = None
        self.series_id = 0
        self.reference_prices = None
        self.reference_prices_id = 0
        self.data_id = 0
        self.data = {}
        self.threshold = 0.02
        self.min_strength = 0

    def update_internal(self) -> bool:
        if self.data_id:
            dpg.delete_item(self.data_id)
            self.data_id = 0

        if self.series is None or self.reference_prices is None:
            return True
        if not self.series.good() or not self.reference_prices.good():
            return True

        self.data['res'] = {}
        self.data['sup'] = {}

        for s in self.series.symbols.symbols:
            self.data['res'][s] = self.series.prices[s]['ta'].resistance_lines_for_price(
                float(self.reference_prices.current_prices[s].current),
                self.min_strength, self.threshold)
            self.data['sup'][s] = self.series.prices[s]['ta'].support_lines_for_price(
                float(self.reference_prices.current_prices[s].current),
                self.min_strength, self.threshold)

        if self.data_id == 0:
            self.data_id = dpg.add_node_attribute(parent=self.node_id, attribute_type=dpg.mvNode_Attr_Static)
            for s in self.data['res']:
                dpg.add_text('%s %d res lines' % (s, len(self.data['res'][s])), parent=self.data_id)
                if len(self.data['res'][s]):
                    dpg.add_text('closest %.2f (%d)' % (self.data['res'][s][0][0], self.data['res'][s][0][1]),
                                 parent=self.data_id)

                dpg.add_text('%s %d sup lines' % (s, len(self.data['sup'][s])), parent=self.data_id)
                if len(self.data['sup'][s]):
                    dpg.add_text('closest %.2f (%d)' % (self.data['sup'][s][0][0], self.data['sup'][s][0][1]),
                                 parent=self.data_id)

        return True

    def update_threshold(self, t: float):
        self.threshold = t / 100
        self.update()

    def update_min_strength(self, m: int):
        self.min_strength = m
        self.update()

    def good(self) -> bool:
        return self.series is not None and self.reference_prices is not None and len(self.data) > 0


class DistanceNode(Node):
    # inputs
    a_id: int
    a: Node
    b_id: int
    b: Node
    # data
    text_id: int
    data: {}
    data_pct: {}

    def __init__(self, node_id):
        super().__init__(node_id)
        self.text_id = 0
        self.a = None
        self.b = None
        self.a_id = 0
        self.b_id = 0
        self.data = {}
        self.pct = {}

    def update_internal(self) -> bool:
        if self.text_id:
            dpg.delete_item(self.text_id)
            self.text_id = 0

        if self.a is None or self.b is None:
            return True

        if not self.a.good() or not self.b.good():
            return True

        def get_values(data):
            values = {}
            if type(data) is CurrentPriceNode:
                for s in data.current_prices:
                    values[s] = float(data.current_prices[s].current)
            elif type(data) is RollingMeanNode:
                for s in data.data:
                    values[s] = float(data.data[s].to_list()[-1])
            return values

        a_values = get_values(self.a)
        b_values = get_values(self.b)

        self.data = {}
        self.data_pct = {}
        for a in a_values:
            if a in b_values:
                self.data[a] = b_values[a] - a_values[a]
                self.data_pct[a] = b_values[a] / a_values[a]

        if self.text_id == 0:
            self.text_id = dpg.add_node_attribute(parent=self.node_id, attribute_type=dpg.mvNode_Attr_Static)
            for s in self.data:
                dpg.add_text('a = %.2f' % a_values[s], parent=self.text_id)
                dpg.add_text('b = %.2f' % b_values[s], parent=self.text_id)
                dpg.add_text('b - a = %.2f' % self.data[s], parent=self.text_id)
                dpg.add_text('a -> b = %.2f%%' % ((self.data_pct[s] - 1) * 100), parent=self.text_id)
                break
        return True

    def good(self) -> bool:
        return self.a is not None and self.b is not None and len(self.data) > 0 and len(self.data_pct) > 0


# node connection
node_connections = {
    (DealerNode, 'dealer'): [(HistoryNode, 'dealer'), (CurrentPriceNode, 'dealer')],
    (SymbolNode, 'symbol'): [(HistoryNode, 'symbols'), (CurrentPriceNode, 'symbols')],
    (HistoryNode, 'candles'): [(RollingMeanNode, 'series'), (ResistanceLinesNode, 'series')],
    (RollingMeanNode, 'mean'): [(DistanceNode, 'a'), (DistanceNode, 'b')],
    (CurrentPriceNode, 'prices'): [(DistanceNode, 'a'), (DistanceNode, 'b'), (ResistanceLinesNode, 'reference_prices')],
}

node_layouts = {
    DealerNode: {
        'inputs': [],
        'outputs': [('dealer', 'dealer')]
    },
    SymbolNode: {
        'inputs': [],
        'outputs': [('symbol', '')]
    },
    CurrentPriceNode: {
        'inputs': [('dealer', 'dealer'), ('symbols', 'symbols')],
        'outputs': [('prices', 'prices')]
    },
    HistoryNode: {
        'inputs': [('dealer', 'dealer'), ('symbols', 'symbols')],
        'outputs': [('candles', 'data')],
    },
    RollingMeanNode: {
        'inputs': [("series", "series")],
        'outputs': [("mean", "mean")]
    },
    DistanceNode: {
        'inputs': [('a', 'a'), ('b', 'b')],
        'outputs': [('a_b', 'a - b'), ('pct', 'pct')]
    },
    ResistanceLinesNode: {
        'inputs': [('series', 'prices'), ('reference_prices', 'ref prices')],
        'outputs': []
    }
}


def connect(a, b):
    global node_connections

    sender_node = dpg.get_item_parent(a)
    sender_class = dpg.get_item_user_data(sender_node)
    receiver_node = dpg.get_item_parent(b)
    receiver_class = dpg.get_item_user_data(receiver_node)

    # check
    a_key = (type(sender_class), dpg.get_item_label(a))
    b_key = (type(receiver_class), dpg.get_item_label(b))

    if a_key in node_connections and b_key in node_connections[a_key]:
        setattr(receiver_class, dpg.get_item_label(b), sender_class)
        sender_class.connect_output(receiver_node)
        receiver_class.update()
        return True

    return False


def disconnect(a, b):
    sender_node = dpg.get_item_parent(a)
    sender_class = dpg.get_item_user_data(sender_node)
    receiver_node = dpg.get_item_parent(b)
    receiver_class = dpg.get_item_user_data(receiver_node)

    # search attribute
    for attr in vars(receiver_class):
        if len(attr) > len('_id') and attr.endswith('_id') and b == getattr(receiver_class, attr):
            setattr(receiver_class, attr[:-3], None)
            receiver_class.update()

    sender_class.disconnect_output(receiver_node)


def _add_inputs_and_outputs(obj, layout: {}):
    for attr in layout['inputs']:
        with dpg.node_attribute(label=attr[0], attribute_type=dpg.mvNode_Attr_Input):
            setattr(obj, attr[0] + '_id', dpg.last_item())
            dpg.add_text(attr[1])
    for attr in layout['outputs']:
        with dpg.node_attribute(label=attr[0], attribute_type=dpg.mvNode_Attr_Output):
            dpg.add_text(attr[1])


def add_dealer(parent, dealer):
    pid = dpg.generate_uuid()
    with dpg.node(label="Dealer", pos=[10, 10], parent=parent, user_data=DealerNode(pid, dealer), id=pid):
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            dpg.add_text('BINANCE')
        _add_inputs_and_outputs(dpg.get_item_user_data(pid), node_layouts[DealerNode])


def add_current_price(parent):
    pid = dpg.generate_uuid()
    with dpg.node(label="Current Price", pos=[10, 10], parent=parent, user_data=CurrentPriceNode(pid), id=pid):
        _add_inputs_and_outputs(dpg.get_item_user_data(pid), node_layouts[CurrentPriceNode])


def add_history(parent):
    pid = dpg.generate_uuid()
    with dpg.node(label="History", pos=[10, 10], parent=parent, user_data=HistoryNode(pid), id=pid):
        _add_inputs_and_outputs(dpg.get_item_user_data(pid), node_layouts[HistoryNode])
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            dpg.add_combo(('1y', '6m', '1m', '1w', '1d'), label='period', default_value='1w', user_data=pid,
                          callback=lambda s, a, u: dpg.get_item_user_data(pid).update_period(a), width=50)
            dpg.add_combo(('1d', '1h', '30m', '15m'), label='interval', default_value='1h', user_data=pid,
                          callback=lambda s, a, u: dpg.get_item_user_data(pid).update_interval(a), width=50)


def add_symbol(parent):
    pid = dpg.generate_uuid()
    with dpg.node(label="Symbol", pos=[10, 10], parent=parent, user_data=SymbolNode(pid), id=pid):
        with dpg.node_attribute(label='symbol', attribute_type=dpg.mvNode_Attr_Output):
            dpg.add_combo(('BTC', 'ETH'), default_value='BTC',
                          callback=lambda s, a: dpg.get_item_user_data(pid).update_symbol(a), width=100)


def add_rolling_mean(parent):
    pid = dpg.generate_uuid()
    with dpg.node(label="Rolling Mean", pos=[10, 10], parent=parent, user_data=RollingMeanNode(pid), id=pid):
        _add_inputs_and_outputs(dpg.get_item_user_data(pid), node_layouts[RollingMeanNode])
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            dpg.add_combo(('SMA', 'EMA'), label='type', default_value='SMA', user_data=pid,
                          callback=lambda s, a, u: dpg.get_item_user_data(pid).update_type(a), width=50)
            dpg.add_slider_int(label='window size', default_value=7, min_value=3, max_value=200,
                               callback=lambda s, a, u: dpg.get_item_user_data(pid).update_window_size(a), width=50)


def add_distance(parent):
    pid = dpg.generate_uuid()
    with dpg.node(label="Distance A to B", pos=[10, 10], parent=parent, user_data=DistanceNode(pid), id=pid):
        _add_inputs_and_outputs(dpg.get_item_user_data(pid), node_layouts[DistanceNode])


def add_rlines(parent):
    pid = dpg.generate_uuid()
    with dpg.node(label="Resistance Lines", pos=[10, 10], parent=parent, user_data=ResistanceLinesNode(pid), id=pid):
        _add_inputs_and_outputs(dpg.get_item_user_data(pid), node_layouts[ResistanceLinesNode])
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            dpg.add_slider_float(label='threshold', default_value=2, min_value=0.1, max_value=5,
                                 callback=lambda s, a, u: dpg.get_item_user_data(pid).update_threshold(a), width=50)
            dpg.add_slider_int(label='min strength', default_value=0, min_value=0, max_value=50,
                               callback=lambda s, a, u: dpg.get_item_user_data(pid).update_min_strength(a), width=50)
