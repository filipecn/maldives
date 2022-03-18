import dearpygui.dearpygui as dpg
from dearpygui import core
from dearpygui.demo import show_demo
from logger import mvLogger
from maldives.bot.exchanges.binance_exchange import BinanceExchange
from datetime import datetime, timedelta
import indicators
import nodes
import os


def _hsv_to_rgb(h, s, v):
    if s == 0.0: return (v, v, v)
    i = int(h * 6.)  # XXX assume int() truncates!
    f = (h * 6.) - i;
    p, q, t = v * (1. - s), v * (1. - s * f), v * (1. - s * (1. - f));
    i %= 6
    if i == 0: return (255 * v, 255 * t, 255 * p)
    if i == 1: return (255 * q, 255 * v, 255 * p)
    if i == 2: return (255 * p, 255 * v, 255 * t)
    if i == 3: return (255 * p, 255 * q, 255 * v)
    if i == 4: return (255 * t, 255 * p, 255 * v)
    if i == 5: return (255 * v, 255 * p, 255 * q)


button_themes = 7 * [0]

for i_t in range(0, 7):
    with dpg.theme() as button_themes[i_t]:
        dpg.add_theme_color(dpg.mvThemeCol_Button, _hsv_to_rgb(i_t / 7.0, 0.6, 0.6))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, _hsv_to_rgb(i_t / 7.0, 0.8, 0.8))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, _hsv_to_rgb(i_t / 7.0, 0.7, 0.7))
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, i_t * 5)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, i_t * 3, i_t * 3)

logger = mvLogger()
logger.log_level = 0

exchange: BinanceExchange = None

tickers = ['BTC', 'ETH']
prices = {}


class WindowData:
    # plots
    candle_plot: int = 0
    volume_plot: int = 0
    # rline annotations
    rlines_annotation_ids = {}
    # axis
    candle_xaxis: int = 0
    candle_yaxis: int = 0
    volume_unit_yaxis: int = 0
    volume_yaxis: int = 0
    volume_xaxis: int = 0
    # ticker
    current_price: float = 0
    selected_ticker: str = ''
    main_window_title: int = 0
    interval: str = '15m'
    period: str = '1d'


window_data = WindowData()


def _ticker_drop(sender, app_data, user_data):
    global window_data
    global prices

    # update data
    window_data.selected_ticker = app_data

    if app_data == '':
        return

    dpg.set_value(window_data.main_window_title, 'Ticker: ' + window_data.selected_ticker)

    # clean plots
    for i in dpg.get_item_children(window_data.candle_yaxis)[1]:
        dpg.delete_item(i)
    if window_data.volume_unit_yaxis != 0:
        dpg.delete_item(window_data.volume_unit_yaxis)
    for i in dpg.get_item_children(window_data.volume_yaxis)[1]:
        dpg.delete_item(i)

    # load data
    start_date = datetime(year=2021, month=6, day=29)
    end_date = datetime(year=2021, month=6, day=30)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    if window_data.period == '1y':
        start_date = end_date - timedelta(days=365)
    elif window_data.period == '6m':
        start_date = end_date - timedelta(days=182)
    elif window_data.period == '1m':
        start_date = end_date - timedelta(days=30)
    elif window_data.period == '1w':
        start_date = end_date - timedelta(days=7)
    elif window_data.period == '1d':
        start_date = end_date - timedelta(days=1)

    # current price
    window_data.current_price = float(
        exchange.symbol_ticker(window_data.selected_ticker)[window_data.selected_ticker].current)
    # candle history
    prices = exchange.historical_candle_series([window_data.selected_ticker], start_date, end_date,
                                               window_data.interval)

    # compute ticker data
    new_dates = (prices[window_data.selected_ticker]['ta'].data['date'].astype('int64') // 1e9).to_list()
    new_closes = prices[window_data.selected_ticker]['ta'].data['close'].to_list()
    new_lows = prices[window_data.selected_ticker]['ta'].data['low'].to_list()
    new_highs = prices[window_data.selected_ticker]['ta'].data['high'].to_list()
    new_opens = prices[window_data.selected_ticker]['ta'].data['open'].to_list()
    # create candle stick graph
    dpg.add_candle_series(new_dates, new_opens, new_closes, new_lows, new_highs,
                          label=app_data,
                          parent=window_data.candle_yaxis)

    dpg.add_hline_series([window_data.current_price], label='cur price', parent=window_data.candle_yaxis)

    # add indicators
    indicators.add_sma_series(3, new_dates, window_data.candle_yaxis,
                              prices[window_data.selected_ticker]['ta'])
    indicators.add_sma_series(7, new_dates, window_data.candle_yaxis,
                              prices[window_data.selected_ticker]['ta'])
    indicators.add_sma_series(14, new_dates, window_data.candle_yaxis,
                              prices[window_data.selected_ticker]['ta'])
    # create volume graph
    values = prices[window_data.selected_ticker]['ta'].data['volume'].to_list()
    dpg.add_bar_series(new_dates, values, parent=window_data.volume_yaxis, weight=500)

    # fit plot views
    dpg.fit_axis_data(window_data.candle_xaxis)
    dpg.fit_axis_data(window_data.candle_yaxis)
    dpg.fit_axis_data(window_data.volume_yaxis)
    dpg.fit_axis_data(window_data.volume_xaxis)


def _candle_plot_drop(sender, app_data, user_data):
    global prices
    global window_data

    if window_data.selected_ticker == '':
        return

    ta = prices[window_data.selected_ticker]['ta']
    dates = (ta.data['date'].astype('int64') // 1e9).to_list()

    # indicator comes in app_data
    logger.log('adding indicator ' + app_data[0])
    if app_data[0] == 'RLINES':
        current_price = float(exchange.symbol_ticker(window_data.selected_ticker)[window_data.selected_ticker].current)
        threshold = dpg.get_value(app_data[1]) / 100
        min_strength = dpg.get_value(app_data[2])
        resistance_lines = ta.resistance_lines_for_price(current_price, min_strength, threshold)
        resistance_levels = [v[0] for v in resistance_lines]
        resistance_strengths = [v[1] for v in resistance_lines]
        resistance_lines = ta.support_lines_for_price(current_price, min_strength, threshold)
        resistance_levels += [v[0] for v in resistance_lines]
        resistance_strengths += [v[1] for v in resistance_lines]
        logger.log(str(resistance_levels))
        hlid = dpg.add_hline_series(resistance_levels, label='RLINES', parent=window_data.candle_yaxis)

        def delete_hl_series(s, a, u):
            dpg.delete_item(u)
            for an in window_data.rlines_annotation_ids[u]:
                dpg.delete_item(an)
            window_data.rlines_annotation_ids[u] = []

        dpg.add_button(label="Delete", user_data=dpg.last_item(), parent=dpg.last_item(),
                       callback=delete_hl_series)
        window_data.rlines_annotation_ids[hlid] = []
        # add annotations
        for ri in range(len(resistance_levels)):
            dpg.add_plot_annotation(label=str(resistance_strengths[ri]),
                                    default_value=(dates[-1], resistance_levels[ri]), offset=(10, 0),
                                    clamped=False, parent=window_data.candle_plot)
            window_data.rlines_annotation_ids[hlid].append(dpg.last_item())
    elif app_data[0] == 'SMA':
        indicators.add_sma_series(app_data[1], dates, window_data.candle_yaxis, ta)
    elif app_data[0] == 'EMA':
        indicators.add_ema_series(app_data[1], dates, window_data.candle_yaxis, ta)
    elif app_data[0] == 'BOLLINGER_BANDS':
        indicators.add_bbands_series(app_data[1], app_data[2], dates, ta, window_data.candle_yaxis)

    dpg.add_button(label="Delete", user_data=dpg.last_item(), parent=dpg.last_item(),
                   callback=lambda s, a, u: dpg.delete_item(u))
    # if app_data == 'SMA':


def _volume_plot_drop(sender, app_data, user_data):
    ta = prices[window_data.selected_ticker]['ta']
    dates = (ta.data['date'].astype('int64') // 1e9).to_list()
    if app_data[0] == 'RSI':
        if window_data.volume_unit_yaxis == 0:
            window_data.volume_unit_yaxis = dpg.add_plot_axis(dpg.mvYAxis, label="RSI",
                                                              parent=window_data.volume_plot)
        indicators.add_rsi_series(dpg.get_value(app_data[1]), dpg.get_value(app_data[2]), dates, ta,
                                  window_data.volume_unit_yaxis)
        dpg.set_axis_limits(window_data.volume_unit_yaxis, 0, 100)


def _candle_indicators():
    # with dpg.collapsing_header(label='indicators'):
    indicators.rlines()
    indicators.sma()
    indicators.ema()
    indicators.rsi()
    indicators.bbands()


def _ticker_list(parent_id):
    # dpg.add_text("TICKER LIST")
    with dpg.filter_set(parent=parent_id) as filter_id:
        filter_container = dpg.last_container()
        for ticker in tickers:
            with dpg.group(filter_key=ticker, horizontal=True):
                item = dpg.last_item()
                dpg.add_button(label=ticker, user_data=ticker,
                               callback=lambda s, a, u: logger.log_info(u))
                dpg.set_item_theme(dpg.last_item(), button_themes[2])
                tick = exchange.symbol_ticker(ticker)[ticker]
                dpg.add_text("%.2f %s" % (float(tick.current), tick.currency))
            with dpg.drag_payload(parent=item, drag_data=ticker, payload_type='main_window'):
                dpg.add_text('asdfasf')
    dpg.add_input_text(parent=parent_id, label="", before=filter_container, user_data=filter_container,
                       callback=lambda s, a, u: dpg.set_value(u, a))


def _interval(sender, app_data, user_data):
    logger.log("picking interval " + app_data)
    window_data.interval = app_data
    _ticker_drop(sender, window_data.selected_ticker, user_data)


def _period(sender, app_data, user_data):
    window_data.period = app_data
    logger.log('picking period: ' + app_data)
    if app_data == '1y' or app_data == '6m' or app_data == '1m':
        if window_data.interval == '15m' or window_data.interval == '30m':
            logger.log_warning('changing interval to 1h')
    _ticker_drop(sender, window_data.selected_ticker, user_data)


def _link_node(sender, app_data, user_data):
    if nodes.connect(app_data[0], app_data[1]):
        dpg.add_node_link(app_data[0], app_data[1], parent=sender, user_data=app_data)


def _delink_node(sender, app_data, user_data):
    nodes.disconnect(dpg.get_item_user_data(app_data)[0], dpg.get_item_user_data(app_data)[1])
    dpg.delete_item(app_data)


def _node_editor():
    dpg.add_separator(label='BOT')
    dpg.add_text('STRATEGY ALGORITHM')
    with dpg.node_editor(callback=_link_node, delink_callback=_delink_node, menubar=True, height=500) as node_editor_id:
        with dpg.menu_bar():
            with dpg.menu(label='New'):
                dpg.add_menu_item(label='dealer', callback=lambda: nodes.add_dealer(node_editor_id, exchange))
                dpg.add_menu_item(label='current price', callback=lambda: nodes.add_current_price(node_editor_id))
                dpg.add_menu_item(label='symbol', callback=lambda: nodes.add_symbol(node_editor_id))
                dpg.add_menu_item(label='historical period', callback=lambda: nodes.add_history(node_editor_id))
                dpg.add_menu_item(label='rolling mean', callback=lambda: nodes.add_rolling_mean(node_editor_id))
                dpg.add_menu_item(label='distance', callback=lambda: nodes.add_distance(node_editor_id))
                dpg.add_menu_item(label='rlines', callback=lambda: nodes.add_rlines(node_editor_id))

        nodes.add_symbol(node_editor_id)
        nodes.add_current_price(node_editor_id)
        nodes.add_history(node_editor_id)
        nodes.add_rlines(node_editor_id)


with dpg.window(label='Main', no_title_bar=True):
    core.set_primary_window(dpg.last_item(), True)
    with dpg.menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="show dpg demo", callback=lambda: show_demo())
            dpg.add_menu_item(label="show dpg doc", callback=lambda: dpg.show_documentation())
    with dpg.group():
        main_parent = dpg.last_item()
        # menu bar
        # main
        with dpg.group(horizontal=True):
            with dpg.child(label='column_0', width=150, height=500):
                _candle_indicators()
            with dpg.child(label='column_1', width=700, height=500, payload_type='main_window',
                           drop_callback=_ticker_drop):
                window_data.main_window_title = dpg.add_text('Ticker: ')
                # dpg.add_button(label='Period')
                # with dpg.popup(dpg.last_item(), modal=True, mousebutton=dpg.mvMouseButton_Left) as modal_id:
                #     period_start = ''
                #     dpg.add_date_picker(level=dpg.mvDatePickerLevel_Day,
                #                         default_value={'month_day': 8, 'year': 93, 'month': 5},
                #                         callback=)
                #     dpg.add_button(label="OK", width=75, user_data=modal_id, callback=_period)
                dpg.add_radio_button(("1y", '6m', '1m', '1w', '1d'), callback=_period, horizontal=True)
                dpg.add_same_line()
                dpg.add_text(' on intervals of: ')
                dpg.add_same_line()
                dpg.add_radio_button(("15m", '30m', '1h', '1d'), callback=_interval, horizontal=True)

                # with dpg.menu(label='date'):
                #     dpg.add_time_picker(default_value={'hour': 14, 'min': 32, 'sec': 23})
                with dpg.plot(label="Candle Series", height=400, width=-1, drop_callback=_candle_plot_drop,
                              payload_type='candle_plot', no_title=True, anti_aliased=True) as window_data.candle_plot:
                    dpg.add_plot_legend()
                    window_data.candle_xaxis = dpg.add_plot_axis(dpg.mvXAxis, label="", time=True)
                    window_data.candle_yaxis = dpg.add_plot_axis(dpg.mvYAxis, label="BRL")
                with dpg.plot(label='volume_plot', height=300, width=-1, no_title=True, payload_type='volume_plot',
                              drop_callback=_volume_plot_drop, callback=_volume_plot_drop) as window_data.volume_plot:
                    dpg.add_plot_legend()
                    window_data.volume_xaxis = dpg.add_plot_axis(dpg.mvXAxis, label="", time=True)
                    window_data.volume_yaxis = dpg.add_plot_axis(dpg.mvYAxis, label="VOL")

                _node_editor()

            with dpg.child(label='column_2', width=200, height=500):
                left_parent = dpg.last_item()
        # footer
        with dpg.child(label='footer', height=200):
            logger.init(dpg.last_item())

# positive numbers > 1  mean actual size
# positive numbers <= 1 mean percentage size
# negative numbers      mean total - quantity
layout = {
    'column_0': [200, 0.82],
    'column_1': [-400, 0.82],
    'column_2': [200, 0.82],
    'footer': [0, 0.15],
}


def resize_r(node, w, h):
    def _compute_value(input_value, total_size):
        if input_value < 0:
            return total_size + input_value
        if input_value > 1:
            return input_value
        return int(input_value * total_size)

    label = dpg.get_item_label(node)
    if label in layout:
        if layout[label][0] != 0:
            dpg.set_item_width(node, _compute_value(layout[label][0], w))
        if layout[label][1] != 0:
            dpg.set_item_height(node, _compute_value(layout[label][1], h))
    children = dpg.get_item_children(node)
    for item, value in children.items():
        if len(value):
            for v in value:
                resize_r(v, w, h)


def resize_all(w, h):
    for win in dpg.get_windows():
        if dpg.get_item_label(win) == 'Main':
            resize_r(win, w, h)


core.set_viewport_resize_callback(lambda a, b: resize_all(b[0], b[1]))

exchange = BinanceExchange(os.environ['binance_key'], os.environ['binance_secret'], logger)
exchange.cache_file = "../../data/binance_data.csv"
exchange.currency = 'BRL'
# prices = exchange.historical_candle_series(tickers, start_date, end_date, '15m')
_ticker_list(left_parent)

dpg.start_dearpygui()