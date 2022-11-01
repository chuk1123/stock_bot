# Unused File

from helium import *
from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium.webdriver import ChromeOptions

def get_finviz_data(ticker):
    chrome_options = ChromeOptions()
    chrome_options.add_argument("user-agent=Chrome/80.0.3987.132")

    url = f'https://finviz.com/quote.ashx?t={ticker}&ty=c&ta=1&p=d'
    browser = start_chrome(url, headless=True, options=chrome_options)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find("table", {"class":"snapshot-table2"})
    df = pd.read_html(str(table), flavor='bs4')[0]

    insider_own = df.loc[0, 7]
    inst_own = df.loc[2, 7]
    shs_float = df.loc[1, 9]
    short_float = df.loc[2, 9]

    kill_browser()

    return insider_own, inst_own, shs_float, short_float