import sqlite3
import pandas as pd
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('mcx_trades.db', check_same_thread=False)
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pair TEXT,
            side TEXT,
            status TEXT,
            entry_price REAL,
            target REAL,
            stop_loss REAL,
            pnl REAL,
            open_time TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_trade(pair, side, status, entry, target, sl):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO trades (pair, side, status, entry_price, target, stop_loss, pnl, open_time)
        VALUES (?, ?, ?, ?, ?, ?, 0, ?)
    ''', (pair, side, status, entry, target, sl, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
