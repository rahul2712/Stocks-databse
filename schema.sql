CREATE TABLE IF NOT EXISTS stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    sector TEXT,
    is_active BOOLEAN DEFAULT 1
);
CREATE TABLE IF NOT EXISTS daily_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    open REAL,
    close REAL,
    high REAL,
    low REAL,
    volume INTEGER,
    FOREIGN KEY (stock_id) REFERENCES stocks(id),
    UNIQUE(stock_id, date)
);
CREATE INDEX IF NOT EXISTS idx_daily_prices_stock_date ON daily_prices(stock_id, date);
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    headline TEXT NOT NULL,
    summary TEXT,
    url TEXT UNIQUE,
    publisher TEXT,
    published_at TEXT,
    sentiment_score REAL
);
CREATE TABLE IF NOT EXISTS stock_news (
    stock_id INTEGER,
    news_id INTEGER,
    FOREIGN KEY (stock_id) REFERENCES stocks(id),
    FOREIGN KEY (news_id) REFERENCES news(id),
    PRIMARY KEY (stock_id, news_id)
);