import MetaTrader5 as mt5
from datetime import datetime

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

# Testing rate collection
# utc_from = datetime(2021, 9, 1)
# utc_to = datetime(2021, 9, 10)

# rates = mt5.copy_rates_range("EURUSD", mt5.TIMEFRAME_H4, utc_from, utc_to)

# for rate in rates:
#     print(rate)

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

# Testing calls
# connect(login, password)
# open_position("Fake_Pair", "BUY", 1)
# open_position("EURUSD", "BUY", 1.0)
