import sqlite3
import pandas as pd
from typing import List, Tuple, Optional

DB_NAME = "stocks.db"

def get_connection():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME)

def init_db(schema_file: str = "schema.sql"):
    """Initializes the database using the provided schema file."""
    conn = get_connection()
    try:
        with open(schema_file, 'r') as f:
            schema = f.read()
        conn.executescript(schema)
        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def add_stock(ticker: str, name: str, sector: str = None) -> int:
    """Adds a new stock to the stocks table. Returns the stock ID."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO stocks (ticker, name, sector) VALUES (?, ?, ?)",
            (ticker, name, sector)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        # Stock already exists, fetch its ID
        cursor.execute("SELECT id FROM stocks WHERE ticker = ?", (ticker,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        conn.close()

def get_all_stocks() -> List[Tuple[int, str]]:
    """Returns a list of all active stocks (id, ticker)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, ticker FROM stocks WHERE is_active = 1")
    rows = cursor.fetchall()
    conn.close()
    return rows

def save_daily_data(stock_id: int, df: pd.DataFrame):
    """
    Saves daily price data to the daily_prices table.
    Expects a DataFrame with index 'Date' and columns 'Open', 'High', 'Low', 'Close', 'Volume'.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Prepare data for bulk insert
    data_to_insert = []
    for date, row in df.iterrows():
        # Format date as YYYY-MM-DD
        date_str = date.strftime('%Y-%m-%d')
        data_to_insert.append((
            stock_id,
            date_str,
            row.get('Open'),
            row.get('Close'),
            row.get('High'),
            row.get('Low'),
            int(row.get('Volume', 0))
        ))
    
    try:
        cursor.executemany(
            """
            INSERT OR REPLACE INTO daily_prices (stock_id, date, open, close, high, low, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            data_to_insert
        )
        conn.commit()
        print(f"Saved {cursor.rowcount} records for stock ID {stock_id}.")
    except Exception as e:
        print(f"Error saving data for stock ID {stock_id}: {e}")
    finally:
        conn.close()
