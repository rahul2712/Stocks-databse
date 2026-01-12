# Walkthrough: BSE 500 Stocks Database

I have successfully set up a database system to collect and store 10 years of historical data for BSE 500 stocks.

## 1. System Architecture
*   **Database**: SQLite (`stocks.db`)
*   **Language**: Python 3.12 (in `.venv`)
*   **Data Source**: Yahoo Finance (`yfinance`) using Nifty 500 list as a proxy (roughly equivalent to BSE 500).

## 2. Key Components
### Database Schema
Two main tables were created:
*   `stocks`: Stores metadata (Ticker, Company Name, Sector).
*   `daily_prices`: Stores historical OHLCV data.

### Scripts
*   `populate_stocks.py`: Downloads the Nifty 500 list and populates the `stocks` table with BSE tickers (e.g., `RELIANCE.BO`).
*   `backfill_data.py`: Iterates through all stocks and downloads 10 years of historical data.
*   `db_utils.py`: Helper functions for database interaction.

## 3. Usage
### Installation
```bash
# Activate virtual environment
source .venv/bin/activate
# Install dependencies
pip install pandas yfinance bsedata
```

### Running the Backfill
```bash
python3 backfill_data.py
```
This script acts as a crawler, fetching data for each stock with rate limiting to ensure reliability.

### Querying Data
You can query the database using Python:
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("stocks.db")
df = pd.read_sql("SELECT * FROM daily_prices WHERE stock_id = 1", conn)
print(df.head())
```

## 4. Verification
The system has been initialized with **501 stocks**.
The backfill process is currently running and populating the `daily_prices` table with ~2500 records per stock.

<carousel>
![Database Schema](/home/rahul/Antigravity/Stocks%20Database/schema.png)
<!-- slide -->
```python
# Check total records
import sqlite3
conn = sqlite3.connect('stocks.db')
c = conn.cursor()
c.execute('SELECT count(*) FROM daily_prices')
print(c.fetchone())
```
</carousel>

## 5. Web Interface (Phase 2)
A Flask-based web dashboard was added to visualize the data.

### Features
*   **Search**: Auto-complete search for 500+ stocks.
*   **Interactive Chart**: 10-year price history visualization using Chart.js.
*   **Data Table**: Scrollable list of raw daily data.
*   **Design**: Modern "Dark Fintech" aesthetic with glassmorphism effects.

### Running the Dashboard
```bash
source .venv/bin/activate
python3 app.py
```
Access at: `http://localhost:5000`
