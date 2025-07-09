import sqlite3, json, os

DB_PATH = os.getenv("DB_PATH", "transport_ai_navi.db")

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)
