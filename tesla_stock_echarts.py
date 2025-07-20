import os
import yfinance as yf
import pandas as pd
import numpy as np
import webbrowser
import tempfile
import datetime

# Set proxy environment variables for yfinance (requests)
proxy = "http://127.0.0.1:10809"
os.environ['HTTP_PROXY'] = proxy
os.environ['HTTPS_PROXY'] = proxy

def calculate_rsi(data, window=14):
    delta = data[('Close', 'TSLA')].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(com=window-1, min_periods=window).mean()
    avg_loss = loss.ewm(com=window-1, min_periods=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data, fast=12, slow=26, signal=9):
    exp1 = data[('Close', 'TSLA')].ewm(span=fast, adjust=False).mean()
    exp2 = data[('Close', 'TSLA')].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

def generate_html(data):
    # Prepare data for JS
    dates = data.index.strftime('%Y-%m-%d').tolist()
    close_prices = data[('Close', 'TSLA')].round(2).tolist()
    rsi = data['RSI'].round(2).tolist()
    macd = data['MACD'].round(2).tolist()
    signal = data['Signal'].round(2).tolist()
    histogram = data['Histogram'].round(2).tolist()

    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Tesla Stock Price with RSI and MACD</title>
    <!-- Import ECharts -->
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
</head>
<body>
    <h2>Tesla Stock Price with RSI and MACD</h2>
    <div id="main" style="width: 100%; height: 70vh;"></div>
    <script type="text/javascript">
        var chartDom = document.getElementById('main');
        var myChart = echarts.init(chartDom);
        var option;

        var dates = {dates};
        var closePrices = {close_prices};
        var rsi = {rsi};
        var macd = {macd};
        var signal = {signal};
        var histogram = {histogram};

        option = {{
            tooltip: {{
                trigger: 'axis'
            }},
            legend: {{
                data: ['Close Price', 'RSI', 'MACD', 'Signal', 'Histogram']
            }},
            xAxis: {{
                type: 'category',
                data: dates
            }},
            yAxis: [
                {{
                    type: 'value',
                    name: 'Price',
                    position: 'left',
                    scale: true,
                    min: 'dataMin',
                    max: 'dataMax'
                }},
                {{
                    type: 'value',
                    name: 'RSI',
                    position: 'right',
                    min: 0,
                    max: 100
                }},
                {{
                    type: 'value',
                    name: 'MACD',
                    position: 'right',
                    offset: 60
                }}
            ],
            dataZoom: [
                {{
                    type: 'inside',
                    xAxisIndex: 0,
                    start: 50,
                    end: 100
                }},
                {{
                    start: 50,
                    end: 100
                }}
            ],
            series: [
                {{
                    name: 'Close Price',
                    type: 'line',
                    data: closePrices,
                    yAxisIndex: 0,
                    smooth: true,
                    symbol: 'none',
                    lineStyle: {{
                        width: 2
                    }}
                }},
                {{
                    name: 'RSI',
                    type: 'line',
                    data: rsi,
                    yAxisIndex: 1,
                    smooth: true,
                    symbol: 'none',
                    lineStyle: {{
                        width: 1
                    }}
                }},
                {{
                    name: 'MACD',
                    type: 'line',
                    data: macd,
                    yAxisIndex: 2,
                    smooth: true,
                    symbol: 'none',
                    lineStyle: {{
                        width: 1
                    }}
                }},
                {{
                    name: 'Signal',
                    type: 'line',
                    data: signal,
                    yAxisIndex: 2,
                    smooth: true,
                    symbol: 'none',
                    lineStyle: {{
                        width: 1
                    }}
                }},
                {{
                    name: 'Histogram',
                    type: 'bar',
                    data: histogram,
                    yAxisIndex: 2,
                    itemStyle: {{
                        color: function(params) {{
                            return params.data >= 0 ? '#26a69a' : '#ef5350';
                        }}
                    }}
                }}
            ]
        }};

        option && myChart.setOption(option);
    </script>
</body>
</html>
"""
    return html_template

def main():
    # Download Tesla stock data from 2010-01-01 to today
    ticker = "TSLA"
    start_date = "2018-01-01"
    end_date = datetime.date.today().strftime("%Y-%m-%d")
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    print("Data columns:", data.columns)


    # Calculate indicators
    data['RSI'] = calculate_rsi(data)
    macd, signal, histogram = calculate_macd(data)
    data['MACD'] = macd
    data['Signal'] = signal
    data['Histogram'] = histogram

    # Drop rows with NaN values from indicators
    data = data.dropna()

    # Generate HTML content
    html_content = generate_html(data)

    # Save to a temporary HTML file
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
        f.write(html_content)
        temp_html_path = f.name

    # Open the HTML file in the default web browser
    webbrowser.open(f'file://{temp_html_path}')

if __name__ == "__main__":
    main()
