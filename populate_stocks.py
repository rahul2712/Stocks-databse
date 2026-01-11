import pandas as pd
from db_utils import add_stock, init_db

NIFTY_500_URL = "https://raw.githubusercontent.com/kprohith/nse-stock-analysis/master/ind_nifty500list.csv"

def populate_stocks():
    print(f"Downloading stock list from {NIFTY_500_URL}...")
    try:
        # Read CSV directly from URL
        df = pd.read_csv(NIFTY_500_URL)
        
        # Expecting columns: 'Company Name', 'Industry', 'Symbol', 'Series', 'ISIN Code'
        # We will use Symbol + '.BO' for BSE ticker
        
        print(f"Found {len(df)} stocks in the list.")
        
        count = 0
        for index, row in df.iterrows():
            symbol = row.get('Symbol')
            name = row.get('Company Name')
            sector = row.get('Industry')
            
            if symbol and name:
                ticker = f"{symbol}.BO"
                stock_id = add_stock(ticker, name, sector)
                if stock_id:
                    count += 1
                    if count % 50 == 0:
                        print(f"Added {count} stocks...")
                else:
                    print(f"Failed to add {ticker}")
                    
        print(f"Population complete. Total stocks added: {count}")

    except Exception as e:
        print(f"Error downloading or processing stock list: {e}")

if __name__ == "__main__":
    init_db()  # Ensure DB is created
    populate_stocks()
