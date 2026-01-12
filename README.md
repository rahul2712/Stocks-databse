# BSE 500 Stocks Database

A comprehensive database and web dashboard to track 10 years of historical Opening and Closing prices for BSE 500 stocks. Built with Python, SQLite, and Flask.

## Features

*   **Robust Data Collection**:
    *   Automated fetching of BSE 500 stock list (via Nifty 500 proxy).
    *   Historical backfill of 10 years of OHLCV data using `yfinance`.
*   **Normalized Database**: efficient SQLite schema with active stock tracking.
*   **Modern Web Dashboard**:
    *   Dark-themed "Fintech" UI with glassmorphism design.
    *   Instant search with autocomplete.
    *   Interactive charts powered by Chart.js.
    *   Scrollable raw data tables.

## Tech Stack

*   **Backend**: Python 3.12, Flask, SQLite
*   **Data Processing**: Pandas, yfinance
*   **Frontend**: HTML5, Vanilla CSS, JavaScript, Chart.js

## Intallation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd Stocks\ Database
    ```

2.  **Create a virtual environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### 1. Initialize & Backfill Data
If you are starting fresh, run these scripts to populate the database:

```bash
# 1. Initialize DB and populate stock list
python3 populate_stocks.py

# 2. Fetch 10-year historical data (takes time)
python3 backfill_data.py
```

### 2. Daily Price Updates
To keep the database current with the latest trading data, run the update script after market hours:

```bash
python3 update_prices.py
```

### 3. Run the Web Dashboard
Start the Flask server to visualize the data:

```bash
python3 app.py
```

Open your browser and navigate to: **[http://localhost:5000](http://localhost:5000)**

## Project Structure

*   `app.py`: Flask application server.
*   `stocks.db`: SQLite database file.
*   `populate_stocks.py`: Script to fetch stock list.
*   `backfill_data.py`: Script to download historical data.
*   `update_prices.py`: Script to fetch latest daily prices (upsert).
*   `db_utils.py`: Database helper functions.
*   `static/`: CSS and JavaScript files.
*   `templates/`: HTML templates.

## Disclaimer
This tool uses `yfinance` to fetch data from Yahoo Finance. It is intended for personal research and educational purposes.
