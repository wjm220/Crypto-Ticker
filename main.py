import os
import tkinter as tk
import tkinter.font as font

from binance.client import Client
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor

# TODO: add functionality that allows the user to choose which crypto they want to watch
# TODO: add a stopwatch display that indicates how long the program has been running

# Binance api key and secret key have been stored as environment variables
api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')
client = Client(api_key, api_secret)

initial_price = 0.0
current_price = 0.0
last_price = 0.0
iter_counter = 0


def btc_trade_history(msg):
    global current_price
    global last_price
    global initial_price
    global iter_counter
    last_price = round(float(msg['b']), 2)

    # Changes text colour based on change from the last price
    if last_price > current_price:
        price_label['fg'] = 'green'
    elif last_price == current_price or current_price == 0.0:
        price_label['fg'] = 'black'
    else:
        price_label['fg'] = 'red'

    current_price = round(float(msg['b']), 2)

    # Change arrow direction and colour based on percent change from initial price (when the program started)
    if msg['e'] != 'error':
        price_label['text'] = '$' + str(current_price)
        if calc_percent_change() > 0:
            percent_label['text'] = '\u25B2' + str(calc_percent_change()) + '%'
            percent_label['fg'] = 'green'
        elif calc_percent_change() == 0:
            percent_label['text'] = '\u25B2' + str(-calc_percent_change()) + '%'
            percent_label['fg'] = 'black'
        else:
            percent_label['text'] = '\u25BC' + str(-calc_percent_change()) + '%'
            percent_label['fg'] = 'red'
    else:
        price_label['text'] = 'error has occurred'

    # The initial price is stored only when iter_counter == 0 (i.e. when the program starts)
    if iter_counter == 0:
        initial_price = current_price

    iter_counter += 1


def calc_percent_change():
    if initial_price == 0:
        return 0
    return round(((current_price - initial_price) / initial_price) * 100, 2)


def on_closing():
    bsm.stop_socket(conn_key)
    reactor.stop()
    frame.destroy()
    frame.quit()


bsm = BinanceSocketManager(client)
conn_key = bsm.start_symbol_ticker_socket('BTCAUD', btc_trade_history)

# Create GUI
frame = tk.Tk()
frame.title('BTC/AUD Ticker')
frame.iconbitmap(default='bitcoin.ico')
frame.resizable(False, False)

font = font.Font(size=30, family='Calibri')

text = tk.Label(text="BTC/AUD Price")
text['font'] = font
text.grid(row=1, column=2)

time_label = tk.Label(font=font)
time_label.grid(row=1, column=3)

price_label = tk.Label(font=font)
price_label.grid(row=2, column=2)

percent_label = tk.Label(font=font)
percent_label.grid(row=2, column=3)
bsm.start()

# Runs the on_closing() function when main window is closed
frame.protocol('WM_DELETE_WINDOW', on_closing)
frame.mainloop()
