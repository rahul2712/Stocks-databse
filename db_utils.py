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

def get_stock_news(stock_id: int, limit: int = 20) -> List[dict]:
    """Retrieves recent news for a specific stock."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT n.headline, n.summary, n.url, n.publisher, n.published_at, n.sentiment_score
        FROM news n
        JOIN stock_news sn ON n.id = sn.news_id
        WHERE sn.stock_id = ?
        ORDER BY n.published_at DESC
        LIMIT ?
    """, (stock_id, limit))
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "headline": r[0],
            "summary": r[1],
            "url": r[2],
            "publisher": r[3],
            "published_at": r[4],
            "sentiment": r[5]
        } for r in rows
    ]

def get_market_news(limit: int = 15) -> List[dict]:
    """Retrieves recent news across all stocks."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT n.headline, n.summary, n.url, n.publisher, n.published_at, n.sentiment_score, s.ticker
        FROM news n
        JOIN stock_news sn ON n.id = sn.news_id
        JOIN stocks s ON s.id = sn.stock_id
        ORDER BY n.published_at DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "headline": r[0],
            "summary": r[1],
            "url": r[2],
            "publisher": r[3],
            "published_at": r[4],
            "sentiment": r[5],
            "ticker": r[6]
        } for r in rows
    ]

def get_news_price_correlation(stock_id: int, days: int = 30) -> dict:
    """
    Analyzes the correlation between news sentiment and price changes.
    Returns a summary of the impact.
    """
    conn = get_connection()
    
    # Get average sentiment per day
    news_query = """
        SELECT date(n.published_at) as news_date, AVG(n.sentiment_score) as avg_sentiment
        FROM news n
        JOIN stock_news sn ON n.id = sn.news_id
        WHERE sn.stock_id = ? AND n.published_at >= date('now', ?)
        GROUP BY news_date
    """
    news_df = pd.read_sql_query(news_query, conn, params=(stock_id, f'-{days} days'))
    
    if news_df.empty:
        conn.close()
        return {"correlation": 0, "message": "Not enough news data for analysis."}
        
    # Get daily price changes
    price_query = """
        SELECT date, (close - open) / open * 100 as pct_change
        FROM daily_prices
        WHERE stock_id = ? AND date >= date('now', ?)
    """
    price_df = pd.read_sql_query(price_query, conn, params=(stock_id, f'-{days} days'))
    
    conn.close()
    
    if price_df.empty:
        return {"correlation": 0, "message": "Not enough price data for analysis."}
        
    # Merge on date
    merged = pd.merge(news_df, price_df, left_on='news_date', right_on='date')
    
    if len(merged) < 3:
        return {"correlation": 0, "message": "Insufficient overlapping data points for correlation."}
        
    correlation = merged['avg_sentiment'].corr(merged['pct_change'])
    
    impact_msg = ""
    if correlation > 0.3:
        impact_msg = "Positive correlation: News sentiment strongly influences price movement."
    elif correlation < -0.3:
        impact_msg = "Inverse correlation: Prices often move opposite to news sentiment."
    else:
        impact_msg = "Weak correlation: News sentiment has limited direct impact on daily price."
        
    return {
        "correlation": round(correlation, 2),
        "message": impact_msg,
        "data_points": len(merged)
    }
