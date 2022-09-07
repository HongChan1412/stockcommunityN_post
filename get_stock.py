import requests
from bs4 import BeautifulSoup
import pandas as pd
url = "https://finance.naver.com/sise/lastsearch2.naver"

class stock_list():
  def get_stocks(self, market=None):
    market_type = ''
    if market == 'kospi':
        market_type = '&marketType=stockMkt'
    elif market == 'kosdaq':
        market_type = '&marketType=kosdaqMkt'
    elif market == 'konex':
        market_type = '&marketType=konexMkt'
    url = 'http://kind.krx.co.kr/corpgeneral/corpList.do?currentPageSize=5000&pageIndex=1&method=download&searchType=13{market_type}'.format(market_type=market_type)

    list_df_stocks = pd.read_html(url, header=0, converters={'종목코드': lambda x: str(x)})
    df_stocks = list_df_stocks[0]
    return df_stocks

  def get_stockCode(self, stock_name, stocks):
    for x in range(len(stocks)):
      if stock_name == stocks['회사명'][x]:
        stock_code = stocks['종목코드'][x]
        return stock_code
    
  def get_requestParser(self, url):
    response = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'})
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup
  
  def get_stockList(self):
    try:
      stocks_list = []
      soup = self.get_requestParser(url)  
      stocks = self.get_stocks()

      for i in soup.find_all("a",{"class":"tltle"}):
        stocks_list.append(i.text)
    
      for i in range(len(stocks_list)):
        stock_code = self.get_stockCode(stocks_list[i], stocks)
        stocks_list[i] = {'stock_name':stocks_list[i], 'stock_code':stock_code}
        
      return stocks_list
    except Exception as e:
      print(e)
      return False
