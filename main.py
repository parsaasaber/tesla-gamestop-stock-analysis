import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import warnings
import matplotlib.pyplot as plt
import os

os.makedirs("data", exist_ok=True)
warnings.filterwarnings('ignore')


def get_data(name):
    """
    Returns a DataFrame containing historical data about the stock prices
    """
    ticker_object = pd.DataFrame(yf.Ticker(name).history(period='max'))
    ticker_object.reset_index(inplace=True)
    return ticker_object


def get_rev(url):
    response = requests.get(url).text
    soup = BeautifulSoup(response, 'html.parser')
    tables = soup.find_all('tbody')[1].find_all('tr')
    revenue_data = pd.DataFrame(columns=['Date', 'Revenue'])
    for row in tables:
        col = row.find_all('td')
        date = col[0].text
        revenue = col[1].text
        revenue_data = pd.concat([
            revenue_data,
            pd.DataFrame({
                "Date": [date],
                "Revenue": [revenue]
            })
        ], ignore_index=True)
    revenue_data["Revenue"] = revenue_data['Revenue'].str.replace(',|\\$', "", regex=True)
    revenue_data.dropna(inplace=True)
    revenue_data = revenue_data[revenue_data['Revenue'] != ""]
    return revenue_data


# The make_graph function has been modified to use Matplotlib for static graphs. Earlier, it used Plotly to generate interactive dashboards, which caused issues when uploading the notebook in the MARK assignment submission.
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
    plt.show()


TSLA_URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-PY0220EN-SkillsNetwork/labs/project/revenue.htm"
GME_URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-PY0220EN-SkillsNetwork/labs/project/stock.html"

tesla_data = get_data("TSLA")
tesla_rev = get_rev(TSLA_URL)

gme_data = get_data('GME')
gme_rev = get_rev(GME_URL)

tesla_data.to_csv("data/tesla_stock.csv", index=False)
tesla_rev.to_csv("data/tesla_revenue.csv", index=False)
gme_data.to_csv("data/gme_stock.csv", index=False)
gme_rev.to_csv("data/gme_revenue.csv", index=False)

# make_graph(tesla_data, tesla_rev, 'TESLA')
# make_graph(gme_data, gme_rev, 'GameStop')
