from bsedata.bse import BSE
import yfinance as yf

b = BSE()
print("Updating Scrip Codes...")
try:
    b.updateScripCodes()
    codes = b.getScripCodes()
    print(f"Total Scrip Codes: {len(codes)}")
    
    # Check for indices
    # bsedata usually doesn't have a direct "get constituents" for index AFAIK, but valid method checks might help
    # Let's just print a few codes
    first_5 = list(codes.items())[:5]
    print(f"Sample: {first_5}")
    
    # Check reliance (500325)
    reliance_code = '500325'
    if reliance_code in codes:
        print(f"Reliance found: {codes[reliance_code]}")
    
    # Test yfinance with code
    ticker_code = f"{reliance_code}.BO"
    print(f"Testing yfinance with {ticker_code}...")
    import yfinance as yf
    try:
        dat_code = yf.download(ticker_code, period="1d", progress=False)
        if not dat_code.empty:
            print(f"Success fetching {ticker_code}")
            print(dat_code.head())
        else:
            print(f"No data for {ticker_code}")
    except Exception as e:
        print(f"yfinance error: {e}")

    # Test INFY.BO
    ticker_infy = "INFY.BO"
    print(f"Testing yfinance with {ticker_infy}...")
    try:
        dat_infy = yf.download(ticker_infy, period="1d", progress=False)
        if not dat_infy.empty:
            print(f"Success fetching {ticker_infy}")
            print(dat_infy.head())
        else:
            print(f"No data for {ticker_infy}")
    except Exception as e:
        print(f"yfinance error for INFY: {e}")

except Exception as e:
    print(f"Error: {e}")
