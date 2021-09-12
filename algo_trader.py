import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
import time
import schedule
import pytz

# DEMO ACCOUNT INFORMATION
login=52064612
password="voxi8nom"

def connect(login, password):
    mt5.initialize(login=login, server="MetaQuotes-Demo",password=password)
    authorized=mt5.login(login=login, server="MetaQuotes-Demo",password=password)

    if authorized:
        print("Connected: Connecting to MT5 Client")
    else:
        print("Failed to connect at account #{}, error code: {}"
              .format(login, mt5.last_error()))


def open_position(pair, order_type, size, tp_distance=None, stop_distance=None):
    symbol_info = mt5.symbol_info(pair)
    if symbol_info is None:
        print(pair, "not found")
        return

    if not symbol_info.visible:
        print(pair, "is not visible, trying to switch on")
        if not mt5.symbol_select(pair, True):
            print("symbol_select({}}) failed, exit",pair)
            return
    print(pair, "found!")

    point = symbol_info.point
    
    if(order_type == "BUY"):
        order = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(pair).ask
        if(stop_distance):
            sl = price - (stop_distance * point)
        if(tp_distance):
            tp = price + (tp_distance * point)
            
    if(order_type == "SELL"):
        order = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(pair).bid
        if(stop_distance):
            sl = price + (stop_distance * point)
        if(tp_distance):
            tp = price - (tp_distance * point)

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": pair,
        "volume": float(size),
        "type": order,
        "price": price,
        "sl": sl,
        "tp": tp,
        "magic": 234000,
        "comment": "",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Failed to send order :(")
    else:
        print ("Order successfully placed!")

def positions_get(symbol=None):
    if(symbol is None):
	    res = mt5.positions_get()
    else:
        res = mt5.positions_get(symbol=symbol)

    if(res is not None and res != ()):
        df = pd.DataFrame(list(res),columns=res[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
    
    return pd.DataFrame()

def close_position(deal_id):
    open_positions = positions_get()
    open_positions = open_positions[open_positions['ticket'] == deal_id]
    order_type  = open_positions["type"][0]
    symbol = open_positions['symbol'][0]
    volume = open_positions['volume'][0]

    if(order_type == mt5.ORDER_TYPE_BUY):
        order_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
    else:
        order_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask
	
    close_request={
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(volume),
        "type": order_type,
        "position": deal_id,
        "price": price,
        "magic": 234000,
        "comment": "Close trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(close_request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Failed to close order :(")
    else:
        print ("Order successfully closed!")

def close_positons_by_symbol(symbol):
    open_positions = positions_get(symbol)
    open_positions['ticket'].apply(lambda x: close_position(x))

def get_data(time_frame):
    pairs = ['EURUSD', 'USDCAD']
    pair_data = dict()
    for pair in pairs:
        utc_from = datetime(2021, 1, 1, tzinfo=pytz.timezone('Europe/Athens'))
        date_to = datetime.now().astimezone(pytz.timezone('Europe/Athens'))
        date_to = datetime(date_to.year, date_to.month, date_to.day, hour=date_to.hour, minute=date_to.minute)
        rates = mt5.copy_rates_range(pair, time_frame, utc_from, date_to)
        rates_frame = pd.DataFrame(rates)
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
        rates_frame.drop(rates_frame.tail(1).index, inplace = True)
        pair_data[pair] = rates_frame
    return pair_data

# Testing initial connection
# connect(login, password)
# utc_from = datetime(2021, 9, 1)
# utc_to = datetime(2021, 9, 10)

# rates = mt5.copy_rates_range("EURUSD", mt5.TIMEFRAME_H4, utc_from, utc_to)

# for rate in rates:
#     print(rate)

# Testing function calls
# connect(login, password)
# open_position("Fake_Pair", "BUY", 1)
# open_position("EURUSD", "BUY", 1.0)
# positions_get()
# close_positions_by_symbol("EURUSD")
