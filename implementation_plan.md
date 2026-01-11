# Stock Database Project Implementation Plan

## 1. Project Overview

The **Stock Database** is a web application designed to track and visualize historical stock data for BSE 500 companies. It allows users to:
- View 10 years of historical price data (Open, High, Low, Close, Volume).
- Search for stocks by ticker or name.
- Visualize price trends with interactive charts.
- Execute raw SQL queries against the database for custom analysis.

## 2. Architecture

The application follows a standard Model-View-Controller (MVC) pattern using:
- **Backend**: Python with Flask.
- **Database**: SQLite (`stocks.db`).
- **Frontend**: HTML/CSS/JavaScript.

### key Files
- `app.py`: Main Flask application entry point and route definitions.
- `db_utils.py`: Database connection handling and helper functions.
- `schema.sql`: SQL schema definition.
- `populate_stocks.py`: Script to populate the initial list of stocks.
- `backfill_data.py`: Script to fetch and backfill historical data.
- `static/script.js`: Frontend logic for search, charts, and SQL execution.
- `static/style.css`: Stylesheet implementing the dark "Fintech" theme.

## 3. Database Schema

The database consists of two primary tables:

### 3.1. `stocks`
Stores static information about companies.
- `id`: Integer Primary Key.
- `ticker`: Stock ticker symbol (e.g., 'RELIANCE.BO').
- `name`: Company name.
- `sector`: Industry sector.
- `is_active`: Boolean flag for active stocks.

### 3.2. `daily_prices`
Stores historical price data.
- `id`: Integer Primary Key.
- `stock_id`: Foreign Key referencing `stocks.id`.
- `date`: Date of the record (YYYY-MM-DD).
- `open`, `close`, `high`, `low`: Price values (Real).
- `volume`: Trading volume (Integer).

## 4. API Endpoints

### `GET /api/stocks`
Returns a list of all active stocks.
- **Response**: JSON array of objects `{id, ticker, name, sector}`.

### `GET /api/data/<ticker>`
Returns historical data for a specific stock.
- **Response**: JSON object containing:
    - `ticker`: Ticker symbol.
    - `count`: Number of records.
    - `data`: Array of price records.

### `POST /api/execute_sql`
Executes a raw SQL query provided in the request body.
- **Request**: `{ "query": "SELECT * FROM ..." }`
- **Response**: JSON object containing:
    - `columns`: List of column names (for SELECT queries).
    - `data`: List of rows.
    - `rows_affected`: Number of rows affected (for modifying queries).
    - `error`: Error message (if applicable).

## 5. Frontend Features

### Dashboard
- **Search**: Dynamic search bar filtering stocks by name or ticker.
- **Charts**: Interactive line chart using Chart.js to display Closing Price history.
- **Stats**: Key statistics display (Sector, Record Count).
- **Data Table**: Scrollable table showing raw daily data.

### SQL Playground
A dedicated section for advanced users to run direct SQL queries securely.
- **Editor**: Text area for query input.
- **Result Table**: Dynamic table rendering based on query results.
- **Error Handling**: Visual feedback for syntax errors or invalid queries.

## 6. Setup and Deployment

### Prerequisites
- Python 3.x
- `pip` packages: `flask`, `pandas`, `yfinance`? (Need to verify used packages for backfill).

### Initialization
1.  Initialize database: `python3 -c "from db_utils import init_db; init_db()"`
2.  Populate stocks: `python3 populate_stocks.py`
3.  Backfill data: `python3 backfill_data.py`

### Running the App
```bash
python3 app.py
```
Access at `http://localhost:5000`.

## 7. Future Enhancements
- Real-time price updates.
- Technical indicators (SMA, RSI) on the chart.
- User authentication for SQL Playground.
