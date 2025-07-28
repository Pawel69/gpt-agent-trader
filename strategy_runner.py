
from binance.client import Client
from binance.exceptions import BinanceAPIException
from binance.enums import *
from dotenv import load_dotenv
import time
import math
import os

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)

def get_free_balance(asset):
    balance = client.get_asset_balance(asset)
    if balance is None:
        raise ValueError(f"Brak aktywa {asset} na Twoim koncie SPOT.")
    return float(balance['free'])

def run_strategy(symbol):
    base_asset = symbol.replace("USDT", "").replace("USDC", "")

    try:
        total_qty = get_free_balance(base_asset)
    except ValueError as e:
        return str(e)

    if total_qty <= 0:
        return f"Brak dostępnego salda {base_asset} do handlu."

    print(f"Aktywne saldo {base_asset}: {total_qty}")

    qty_tp1 = round(total_qty * 0.5, 3)
    qty_tp2 = round(total_qty * 0.25, 3)
    qty_tp3 = round(total_qty * 0.25, 3)

    current_price = float(client.get_symbol_ticker(symbol=symbol)['price'])
    print(f"Aktualna cena {symbol}: {current_price}")

    sl_price_1 = round(current_price * 0.90, 2)
    tp1_price = round(current_price * 1.10, 2)
    tp2_target = round(current_price * 1.15, 2)
    tp3_target = round(current_price * 1.20, 2)

    # TP1 jako LIMIT SELL
    try:
        client.create_order(
            symbol=symbol,
            side=SIDE_SELL,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=qty_tp1,
            price=str(tp1_price)
        )
        print(f"🟢 TP1: Wystawiono LIMIT SELL {qty_tp1} {base_asset} po {tp1_price}")
    except BinanceAPIException as e:
        print(f"❌ Błąd przy TP1: {e.message}")

    # TP2 i TP3 z trailing SL (symulowanym)
    highest_price = current_price
    sl_tp2 = current_price
    sl_tp3 = current_price
    tp2_executed = False
    tp3_executed = False

    while not tp2_executed or not tp3_executed:
        current = float(client.get_symbol_ticker(symbol=symbol)['price'])

        if not tp2_executed and current >= tp2_target:
            highest_price = current
            sl_tp2 = current * 0.95
            print(f"🎯 TP2 aktywowany. Trailing SL ustawiony na {sl_tp2:.2f}")
        if not tp3_executed and current >= tp3_target:
            highest_price = current
            sl_tp3 = current * 0.95
            print(f"🎯 TP3 aktywowany. Trailing SL ustawiony na {sl_tp3:.2f}")

        if not tp2_executed and current < sl_tp2 and sl_tp2 != current_price:
            client.create_order(symbol=symbol, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=qty_tp2)
            print(f"✅ TP2: Sprzedano {qty_tp2} {base_asset} z trailing SL")
            tp2_executed = True

        if not tp3_executed and current < sl_tp3 and sl_tp3 != current_price:
            client.create_order(symbol=symbol, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=qty_tp3)
            print(f"✅ TP3: Sprzedano {qty_tp3} {base_asset} z trailing SL")
            tp3_executed = True

        time.sleep(5)

    return "Strategia zakończona."
