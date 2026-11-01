import os
import matplotlib.pyplot as plt
import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup
import warnings

# Suppress library warnings (e.g. FutureWarning / DeprecationWarning from pandas
# and yfinance saying a feature will be removed in newer versions). They don't
# affect the results, but they clutter the terminal output.
warnings.filterwarnings('ignore') #

DATA_DIR = "data"
CHARTS_DIR = "charts"

TSLA_URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-PY0220EN-SkillsNetwork/labs/project/revenue.htm"
GME_URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-PY0220EN-SkillsNetwork/labs/project/stock.html"


def get_data(name):
    """
    Returns a DataFrame containing historical data about the stock prices
    """
    ticker_object = pd.DataFrame(yf.Ticker(name).history(period='max'))
    ticker_object.reset_index(inplace=True)
    return ticker_object


def get_rev(url):
    """
    Scrapes the quarterly revenue table from the given URL and
    returns a cleaned DataFrame with the columns Date and Revenue.
    """
    response = requests.get(url, timeout=30).text
    soup = BeautifulSoup(response, 'html.parser')
    rows = soup.find_all('tbody')[1].find_all('tr')

    # Collect rows in a list first and build the DataFrame once (much faster
    # than calling pd.concat inside the loop).
    records = []
    for row in rows:
        col = row.find_all('td')
        records.append({"Date": col[0].text, "Revenue": col[1].text})

    revenue_data = pd.DataFrame(records, columns=['Date', 'Revenue'])
    revenue_data["Revenue"] = revenue_data['Revenue'].str.replace(',|\\$', "", regex=True)
    revenue_data.dropna(inplace=True)
    revenue_data = revenue_data[revenue_data['Revenue'] != ""]
    return revenue_data


# make_graph uses Matplotlib for static graphs. Earlier it used Plotly to generate
# interactive dashboards, which caused issues when uploading the notebook in the
# MARK assignment submission.
def make_graph(stock_data, revenue_data, stock):
    stock_data_specific = stock_data[stock_data.Date <= '2021-06-14']
    revenue_data_specific = revenue_data[revenue_data.Date <= '2021-04-30']

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Stock price
    axes[0].plot(pd.to_datetime(stock_data_specific.Date), stock_data_specific.Close.astype("float"),
                 label="Share Price", color="blue")
    axes[0].set_ylabel("Price ($US)")
    axes[0].set_title(f"{stock} - Historical Share Price")

    # Revenue
    axes[1].plot(pd.to_datetime(revenue_data_specific.Date), revenue_data_specific.Revenue.astype("float"),
                 label="Revenue", color="green")
    axes[1].set_ylabel("Revenue ($US Millions)")
    axes[1].set_xlabel("Date")
    axes[1].set_title(f"{stock} - Historical Revenue")

    plt.tight_layout()

    # Save the chart so it can be used in the README, then display it.
    os.makedirs(CHARTS_DIR, exist_ok=True)
    fig.savefig(os.path.join(CHARTS_DIR, f"{stock.lower()}_price_vs_revenue.png"), dpi=150)
    plt.show()


def save_data(frames):
    """
    Saves each DataFrame in the dict {filename: DataFrame} as a CSV in DATA_DIR.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    for filename, df in frames.items():
        df.to_csv(os.path.join(DATA_DIR, filename), index=False)


def main():
    tesla_data = get_data("TSLA")
    tesla_rev = get_rev(TSLA_URL)

    gme_data = get_data("GME")
    gme_rev = get_rev(GME_URL)

    save_data({
        "tesla_stock.csv": tesla_data,
        "tesla_revenue.csv": tesla_rev,
        "gme_stock.csv": gme_data,
        "gme_revenue.csv": gme_rev,
    })

    make_graph(tesla_data, tesla_rev, "Tesla")
    make_graph(gme_data, gme_rev, "GameStop")


if __name__ == "__main__":
    main()
