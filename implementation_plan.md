# Database Plan for BSE 500 Stocks (Last 10 Years)

This plan outlines the architecture, schema, and data collection strategy to store daily Open and Close values for BSE 500 stocks.

## Goal Description
Create a reliable database system to store 10 years of historical data for BSE 500 stocks and robustly collect daily updates going forward.

## User Review Required
> [!IMPORTANT]
> **Data Source**: This plan uses the `yfinance` Python library (Yahoo Finance) as a free source for historical data. It is reliable for personal use but unofficial. If you require guaranteed SLA or commercial rights, a paid API (like Zerodha or Twelve Data) would be needed.

> [!NOTE]
> **Database Choice**: I have selected **SQLite** for this plan as it is serverless, zero-configuration, and highly performant for a dataset of this size (~1.2 million rows for 500 stocks * 10 years * 250 days). Easy to migrate to PostgreSQL later if needed.

## Proposed Architecture

### 1. Technology Stack
*   **Language**: Python 3.x
*   **Database**: SQLite 3 (File-based storage)
*   **Data Source**: `yfinance` (Yahoo Finance API wrapper)
*   **Libraries**: `pandas`, `yfinance`, `sqlalchemy` (for ORM)

### 2. Database Schema
We will use two normalized tables.

#### Table: `stocks`
Stores metadata about the companies.
*   `id` (Integer, Primary Key): Internal ID
*   `ticker` (String, Unique): BSE symbol (e.g., "RELIANCE.BO")
*   `name` (String): Company name
*   `sector` (String, Optional): Industry sector
*   `is_active` (Boolean): To track delisted/removed stocks

#### Table: `daily_prices`
Stores the time-series data.
*   `id` (Integer, Primary Key): Auto-increment
*   `stock_id` (Integer, Foreign Key -> stocks.id)
*   `date` (Date): Trading date
*   `open` (Float): Opening price
*   `close` (Float): Closing price
*   `high` (Float, Optional): Day High
*   `low` (Float, Optional): Day Low
*   `volume` (Integer, Optional): Traded volume

**Indices**:
*   Composite Index on `daily_prices(stock_id, date)` for fast retrieval and ensuring uniqueness per stock per day.

### 3. Data Collection Strategy

#### Phase 1: Stock List Acquisition
*   Fetch the current list of BSE 500 stocks.
*   Source: BSE website CSV or a predefined list.
*   Action: Populate the `stocks` table.

#### Phase 2: Historical Backfill (10 Years)
*   Iterate through all active stocks in `stocks` table.
*   Use `yfinance.download(ticker, period="10y")`.
*   Bulk insert data into `daily_prices`.
*   Handle rate limits by adding small delays if necessary.

#### Phase 3: Daily Updates
*   A script `update_prices.py` to be run daily (e.g., via cron) at 4:00 PM IST.
*   Fetches data for `period="1d"` for all stocks.
*   Upserts (Update if exists, Insert if new) into the database.

## Proposed Changes

### [New Project Structure]
#### [NEW] [schema.sql](file:///home/rahul/Antigravity/Stocks%20Database/schema.sql)
SQL script to create tables and indices.

#### [NEW] [populate_stocks.py](file:///home/rahul/Antigravity/Stocks%20Database/populate_stocks.py)
Script to initialize the `stocks` table with BSE 500 tickers.

#### [NEW] [backfill_data.py](file:///home/rahul/Antigravity/Stocks%20Database/backfill_data.py)
Script to fetch 10 years of history for all stocks.

#### [NEW] [db_utils.py](file:///home/rahul/Antigravity/Stocks%20Database/db_utils.py)
Helper functions for database connections and queries.

## Verification Plan

### Automated Tests
*   **Schema Validation**: Run a script to verify tables exist and have correct columns.
*   **Data Integrity Check**:
    *   Fetch count of records for a major stock (e.g., Reliance) -> Should be ~2500 records (10 years).
    *   Check for duplicates (Grouping by date/stock should have count 1).

### Manual Verification
*   Run `sqlite3 stocks.db "SELECT * FROM daily_prices LIMIT 5;"` to inspect data manually.
*   Compare a sample date's Open/Close with a public website (e.g., Google Finance) for accuracy.

# Phase 2: Web Interface Plan

## Goal Description
Build a modern, responsive web interface to query, visualize, and analyze the collected BSE 500 stock data.

## Proposed Changes

### Tech Stack
*   **Backend**: Flask (Python) - lightweight and integrates easily with the existing SQLite/Pandas setup.
*   **Frontend**: HTML5, Vanilla CSS, Vanilla JavaScript (Premium "Fintech" Aesthetic).
*   **Visualization**: Chart.js (for rendering stock price charts).

### Components

#### [NEW] [app.py](file:///home/rahul/Antigravity/Stocks%20Database/app.py)
*   **Flask Application**: Serves the static assets and provides API endpoints.
*   **API Endpoints**:
    *   `GET /api/stocks`: Returns list of stocks for autocomplete.
    *   `GET /api/data/<ticker>`: Returns historical data (JSON) for a specific stock within a date range.

#### [NEW] [templates/index.html](file:///home/rahul/Antigravity/Stocks%20Database/templates/index.html)
*   **Search Bar**: Auto-complete search for stock tickers/names.
*   **Chart Section**: Interactive line chart showing Open/Close prices.
*   **Data Table**: Scrollable table showing raw daily values.

#### [NEW] [static/style.css](file:///home/rahul/Antigravity/Stocks%20Database/static/style.css)
*   **Design**: Dark mode, glassmorphism, vibrant accent colors (Neon Blue/Green), smooth transitions.
*   **Responsive**: Works on desktop and mobile.

#### [NEW] [static/script.js](file:///home/rahul/Antigravity/Stocks%20Database/static/script.js)
*   **Logic**:
    *   Fetches stock list on load.
    *   Handles search input and selection.
    *   Fetches data and updates Chart.js instance.
    *   Renders data table.

## Verification Plan
*   **Start Server**: Run `python3 app.py`.
*   **Browser Test**: Open `http://localhost:5000`.
    *   Search for "RELIANCE.BO".
    *   Verify chart renders 10 years (or selected range) of data.
    *   Verify table matches database data.
