import yfinance as yf
import time
from db_utils import get_all_stocks, save_daily_data

def backfill_history():
    stocks = get_all_stocks()
    print(f"Starting backfill for {len(stocks)} stocks...")
    
    start_time = time.time()
    
    for i, (stock_id, ticker) in enumerate(stocks):
        # Optional: Skip if already has data? For now user said "collect", so backfill all.
        print(f"[{i+1}/{len(stocks)}] Fetching 10y data for {ticker}...")
        
        try:
            # Download 10 years of data
            # Use auto_adjust=True to get adjusted prices (optional)
            # User asked for Opening and Closing. Often adjust=False is safer for raw prices.
            # But yfinance defaults usually work fine.
            df = yf.download(ticker, period="10y", progress=False, multi_level_index=False)
            
            if df.empty:
                print(f"  WARNING: No data found for {ticker}")
                continue
                
            save_daily_data(stock_id, df)
            
            # Rate limiting to be polite
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ERROR fetching {ticker}: {e}")
            
    elapsed = time.time() - start_time
    print(f"Backfill complete in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    backfill_history()
