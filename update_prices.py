import yfinance as yf
import time
from db_utils import get_all_stocks, save_daily_data

def update_prices():
    """
    Fetches the latest data (1d) for all stocks in the database 
    and upserts into the daily_prices table.
    """
    stocks = get_all_stocks()
    print(f"Starting daily update for {len(stocks)} stocks...")
    
    start_time = time.time()
    success_count = 0
    
    for i, (stock_id, ticker) in enumerate(stocks):
        print(f"[{i+1}/{len(stocks)}] Fetching latest data for {ticker}...")
        
        try:
            # Download data for the last 1 day
            df = yf.download(ticker, period="1d", progress=False, multi_level_index=False)
            
            if df.empty:
                print(f"  WARNING: No data found for {ticker}")
                continue
                
            # save_daily_data now uses INSERT OR REPLACE (upsert)
            save_daily_data(stock_id, df)
            success_count += 1
            
            # Small delay to be polite to the API
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ERROR fetching {ticker}: {e}")
            
    elapsed = time.time() - start_time
    print(f"Update complete. Success: {success_count}/{len(stocks)}. Time taken: {elapsed:.2f} seconds.")

if __name__ == "__main__":
    update_prices()
