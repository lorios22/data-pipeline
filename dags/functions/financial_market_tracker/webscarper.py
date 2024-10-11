import yfinance as yf
import requests
import os

# Mapping stock market indices to their Yahoo Finance symbols
yahoo_symbols = {
    'Nikkei 225 (Japan)': '^N225',
    'Hang Seng Index (Hong Kong)': '^HSI',
    'Shanghai Composite (China)': '000001.SS',  # Added Shanghai Composite
    'FTSE 100 (UK)': '^FTSE',
    'DAX (Germany)': '^GDAXI',
    'S&P 500 (USA)': '^GSPC',
    'NASDAQ Composite (USA)': '^IXIC',
    'US Dollar Index': 'DX-Y.NYB'
}

# Mapping cryptocurrencies to their identifiers in CoinGecko API
cryptocurrencies = {
    'Bitcoin (BTC)': 'bitcoin',
    'Ethereum (ETH)': 'ethereum'
}

# Mapping commodities to their Yahoo Finance symbols
commodities = {
    'Gold': 'GC=F',
    'Oil (Brent Crude)': 'BZ=F'
}

# Function to detect the market type based on the file name
def detect_market(filename):
    """
    Detect the market type based on the given filename.
    
    Parameters:
    filename (str): Name of the file to analyze.
    
    Returns:
    str: The market type (Asian, American, European, or Global).
    """
    if 'asian' in filename.lower():
        return 'Asian market'
    elif 'american' in filename.lower():
        return 'American market'
    elif 'european' in filename.lower():
        return 'European market'
    else:
        return 'Global market'

# Function to retrieve stock/commodity data from Yahoo Finance
def get_yahoo_data(symbol, period='1d'):
    """
    Retrieve the last closing price for a given symbol from Yahoo Finance.
    
    Parameters:
    symbol (str): The Yahoo Finance symbol for the asset.
    period (str): The period for which to retrieve the data (default is '1d').
    
    Returns:
    float or None: The last closing price, or None if data is not available.
    """
    ticker = yf.Ticker(symbol)
    data = ticker.history(period=period)
    if not data.empty:
        last_close = data['Close'].iloc[-1]
        return last_close
    else:
        return None

# Function to retrieve cryptocurrency prices from CoinGecko
def get_coingecko_price(crypto_id):
    """
    Retrieve the current price of a cryptocurrency from the CoinGecko API.
    
    Parameters:
    crypto_id (str): The CoinGecko identifier for the cryptocurrency.
    
    Returns:
    float or None: The price in USD, or None if data is unavailable.
    """
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get(crypto_id, {}).get('usd', None)
    return None

# Main function to save market data to a file
def save_market_data_to_file(filepath):
    """
    Extracts stock, cryptocurrency, and commodity data and saves it to a file.
    
    Parameters:
    filepath (str): The path to the file where the data will be saved.
    
    The function writes the last closing prices for major stock indices, 
    cryptocurrencies, commodities, and the US Dollar Index based on the detected market.
    """
    market = detect_market(filepath)  # Detect market type based on the file name
    
    with open(filepath, "w") as file:
        file.write(f"Closing prices for {market}\n\n")
        
        # 1. Collect and save stock market indices data
        file.write("Stock market indices:\n")
        for name, symbol in yahoo_symbols.items():
            last_close = get_yahoo_data(symbol)
            if last_close:
                file.write(f"- {name}: \nLast close in {market}: {last_close:,.2f} \n\n")
            else:
                file.write(f"- {name}:\nLast close: Data not available\n\n")
        file.write("\n")  # New line after stock indices
        
        # 2. Collect and save cryptocurrency data
        file.write("Cryptocurrencies:\n")
        for crypto, crypto_id in cryptocurrencies.items():
            price = get_coingecko_price(crypto_id)
            if price:
                file.write(f"- {crypto}: \nLast close in {market}: {price:,.2f} \n\n")
            else:
                file.write(f"- {crypto}: \nLast close: Data not available\n\n")
        file.write("\n")  # New line after cryptocurrencies
        
        # 3. Collect and save commodity data
        file.write("Commodities:\n")
        for commodity, symbol in commodities.items():
            last_close = get_yahoo_data(symbol)
            if last_close:
                file.write(f"- {commodity}: \nLast close in {market}: {last_close:,.2f}\n\n")
            else:
                file.write(f"- {commodity}: \nLast close: Data not available\n\n")
        file.write("\n")  # New line after commodities

        # 4. Collect and save US Dollar Index data
        file.write("Currency:\n")
        last_close = get_yahoo_data(yahoo_symbols['US Dollar Index'])  # Only DXY
        if last_close:
            file.write(f"- US Dollar Index: \nLast close in {market}: {last_close:,.2f} \n\n")
        else:
            file.write(f"- US Dollar Index: \nLast close: Data not available\n\n")

    print(f"Data successfully written to '{filepath}'")

