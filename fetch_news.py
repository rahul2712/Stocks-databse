import yfinance as yf
from textblob import TextBlob
from db_utils import get_connection, get_all_stocks
import sqlite3
import datetime
import time

def analyze_sentiment(text):
    if not text:
        return 0.0
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

def fetch_and_store_news(limit=None):
    stocks = get_all_stocks()
    if limit:
        stocks = stocks[:limit]
    
    conn = get_connection()
    cursor = conn.cursor()
    
    print(f"Starting news fetch for {len(stocks)} stocks...")
    
    for stock_id, ticker in stocks:
        try:
            print(f"Fetching news for {ticker}...")
            # BSE stocks usually end with .BO in yfinance
            yf_ticker = ticker
            if not yf_ticker.endswith(".BO") and not yf_ticker.endswith(".NS"):
                yf_ticker += ".BO"
                
            t = yf.Ticker(yf_ticker)
            news_items = t.news
            
            if not news_items:
                print(f"No news found for {ticker}")
                continue
                
            for item in news_items:
                title = item.get('title')
                summary = item.get('summary', '')
                url = item.get('link')
                publisher = item.get('publisher')
                # yfinance provides providerPublishTime in seconds
                pub_time = item.get('providerPublishTime')
                published_at = datetime.datetime.fromtimestamp(pub_time).strftime('%Y-%m-%d %H:%M:%S') if pub_time else None
                
                # Analyze sentiment of title and summary
                sentiment = analyze_sentiment(f"{title} {summary}")
                
                try:
                    # Insert news article if it doesn't exist
                    cursor.execute("""
                        INSERT OR IGNORE INTO news (headline, summary, url, publisher, published_at, sentiment_score)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (title, summary, url, publisher, published_at, sentiment))
                    
                    # Get the news_id (either from insert or existing)
                    if cursor.rowcount > 0:
                        news_id = cursor.lastrowid
                    else:
                        cursor.execute("SELECT id FROM news WHERE url = ?", (url,))
                        res = cursor.fetchone()
                        news_id = res[0] if res else None
                    
                    if news_id:
                        # Link news to stock
                        cursor.execute("""
                            INSERT OR IGNORE INTO stock_news (stock_id, news_id)
                            VALUES (?, ?)
                        """, (stock_id, news_id))
                        
                except Exception as e:
                    print(f"Error storing news item for {ticker}: {e}")
            
            conn.commit()
            # Small sleep to avoid hitting rate limits
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error fetching news for {ticker}: {e}")
            
    conn.close()
    print("News fetch completed.")

if __name__ == "__main__":
    # For testing, we can run with a small limit
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    fetch_and_store_news(limit=limit)
