import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import pytz

def initialize_mt5():
    """Initialize connection to MetaTrader 5"""
    if not mt5.initialize():
        print("initialize() failed")
        mt5.shutdown()
        return False
    return True

def get_timeframe_mt5(timeframe_str):
    """Convert string timeframe to MT5 timeframe constant"""
    timeframe_map = {
        "1M": mt5.TIMEFRAME_M1,
        "5M": mt5.TIMEFRAME_M5,
        "15M": mt5.TIMEFRAME_M15,
    }
    return timeframe_map.get(timeframe_str)

def get_price_data(symbol="USDJPY", timeframe="1M", start_date=None, end_date=None):
    """
    Fetch price data from MetaTrader 5
    
    Parameters:
    - symbol (str): Trading symbol (default: "USDJPY")
    - timeframe (str): Timeframe ("1M", "5M", "15M")
    - start_date (datetime): Start date for data fetch
    - end_date (datetime): End date for data fetch
    
    Returns:
    - pandas DataFrame with OHLCV data
    """
    if not initialize_mt5():
        return None
        
    # Convert timeframe string to MT5 timeframe
    tf = get_timeframe_mt5(timeframe)
    if tf is None:
        print(f"Invalid timeframe: {timeframe}")
        return None
    
    # Set timezone to UTC
    timezone = pytz.timezone("Etc/UTC")
    
    # Get rates
    rates = mt5.copy_rates_range(symbol, tf, start_date, end_date)
    
    # Shutdown MT5 connection
    mt5.shutdown()
    
    if rates is None or len(rates) == 0:
        print(f"No data received for {symbol}")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    return df

def fetch_historical_data(symbol="EURUSD"):
    """Fetch historical data for specified symbol for years 2022-2024"""
    timeframes = ["1M", "5M", "15M"]
    years = [2022, 2023, 2024]
    
    # Initialize MT5
    if not initialize_mt5():
        return
    
    for year in years:
        for tf in timeframes:
            # Set date range for the year
            start_date = datetime(year, 1, 1, tzinfo=pytz.timezone("Etc/UTC"))
            if year == 2024:
                end_date = datetime.now(pytz.timezone("Etc/UTC"))
            else:
                end_date = datetime(year, 12, 31, 23, 59, tzinfo=pytz.timezone("Etc/UTC"))
            
            print(f"Fetching {symbol} data for {year}, timeframe: {tf}")
            df = get_price_data(symbol, tf, start_date, end_date)
            
            if df is not None:
                # Save to CSV
                filename = f"data/{symbol}_{tf}_{year}.csv"
                df.to_csv(filename, index=False)
                print(f"Saved data to {filename}")
            else:
                print(f"Failed to fetch data for {year}, timeframe: {tf}")
    
    mt5.shutdown()

if __name__ == "__main__":
    fetch_historical_data("EURUSD")