import requests
import pandas as pd
import matplotlib.pyplot as plt
import datetime

def fetch_and_plot_shanghai_index():
    # Sina Finance API endpoint for Shanghai Composite Index historical data
    api_url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
    # Update params to fetch data from 2010 to now
    # Since the API uses 'datalen' for number of data points, increase it to cover more days (e.g. 3250)
    params = {
        "symbol": "sh000001",
        "scale": "240",  # daily data
        "ma": "no",
        "datalen": "3250"  # number of data points to cover from 2010 to now approximately
    }
    
    response = requests.get(api_url, params=params)
    if response.status_code != 200:
        print("Failed to fetch data from Sina Finance.")
        return
    
    data_str = response.text
    print("Raw response text:", data_str[:500])  # Debug print first 500 chars to check data format
    
    # Fix the string to proper JSON format
    import re
    import io
    # Insert commas between key-value pairs inside objects where missing
    # The original regex was incorrect, fix it to insert commas between key-value pairs properly
    # Replace occurrences of "key":"value""key2":"value2" with "key":"value","key2":"value2"
    # This regex inserts commas between adjacent quoted key-value pairs without commas
    data_str = re.sub(r'"\s*"\s*', '","', data_str)
    # Insert commas between objects
    data_str = data_str.replace('}{', '},{')
    
    try:
        data_json = pd.read_json(io.StringIO(data_str))
    except Exception as e:
        print("Failed to parse data:", e)
        return
    
    # Convert day column to datetime
    data_json['day'] = pd.to_datetime(data_json['day'])
    
    # Sort by date ascending
    data_json = data_json.sort_values(by='day')
    
    # Plot the closing prices
    plt.figure(figsize=(12, 6))
    plt.plot(data_json['day'], data_json['close'], label='Close Price')
    plt.title('Shanghai Composite Index Closing Prices (Recent)')
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    fetch_and_plot_shanghai_index()
