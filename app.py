from flask import Flask, jsonify, render_template, request
import sqlite3
import pandas as pd
from db_utils import get_connection

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stocks')
def get_stocks_api():
    """Returns a list of all active stocks."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, ticker, name, sector FROM stocks WHERE is_active = 1 ORDER BY ticker")
    rows = cursor.fetchall()
    conn.close()
    
    stocks = [
        {"id": r[0], "ticker": r[1], "name": r[2], "sector": r[3]} 
        for r in rows
    ]
    return jsonify(stocks)

@app.route('/api/data/<ticker>')
def get_stock_data(ticker):
    """Returns historical data for a given ticker."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get stock ID first
    cursor.execute("SELECT id FROM stocks WHERE ticker = ?", (ticker,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({"error": "Stock not found"}), 404
        
    stock_id = result[0]
    
    # Fetch price data
    # Filter by date range if query params provided
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    query = """
        SELECT date, open, close, high, low, volume 
        FROM daily_prices 
        WHERE stock_id = ?
    """
    
    params = [stock_id]
    
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
        
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
        
    query += " ORDER BY date ASC"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    # Convert to list of dicts
    data = df.to_dict(orient='records')
    return jsonify({
        "ticker": ticker,
        "count": len(data),
        "data": data
    })

@app.route('/api/execute_sql', methods=['POST'])
def execute_sql():
    """Executes a raw SQL query and returns the results."""
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
        
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        
        # If it's a SELECT query, fetch results
        if cursor.description:
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            # Convert rows to list of dicts? Or just list of lists?
            # List of lists is easier for dynamic table rendering if we send columns separately
            results = [list(row) for row in rows]
            
            return jsonify({
                "columns": columns,
                "data": results
            })
        else:
            # For INSERT, UPDATE, DELETE
            conn.commit()
            return jsonify({
                "message": f"Query executed successfully. Rows affected: {cursor.rowcount}",
                "rows_affected": cursor.rowcount
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
