from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import pandas as pd
from html_table_parser import parser_functions
import time
import datetime
import json
import os
os.environ['WDM_LOG_LEVEL'] = '0'
class crawl():
  def __init__(self) -> None:
    pass
  
  def get_opinionText(self, invest_opinion):
    invest_opinion = float(invest_opinion)
    if  invest_opinion < 0.5:
      invest_opinionText = "강력매도"
    elif 0.5 <= invest_opinion < 1.5:
      invest_opinionText = "매도"
    elif 1.5 <= invest_opinion <= 3.5:
      invest_opinionText = "중립"
    elif 3.5 <= invest_opinion < 4.5:
      invest_opinionText = "매수"
    elif 4.5 < invest_opinion:
      invest_opinionText = "강력매수"
    return invest_opinionText
  
  def get_requestParser(self, url):
    response = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'})
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup 
  
  def judge_updown(self, rateDifference_price, current_price, difference_price):
    current_price = int(current_price.replace(",",""))
    if "-" in rateDifference_price:
      differnce_text = "하락"
      try:
        difference_price = int(difference_price.split("▼")[1].replace(",",""))
      except:
        difference_price = int(difference_price.split("↓")[1].replace(",",""))
      beforeDay_price = format(current_price+difference_price,',')
      difference_price = format(difference_price,',')
    elif "+" in rateDifference_price:
      differnce_text = "상승"
      try:
        difference_price = int(difference_price.split("▲")[1].replace(",",""))
      except:
        difference_price = int(difference_price.split("↑")[1].replace(",",""))
      beforeDay_price = format(current_price-difference_price,',')
      difference_price = format(difference_price,',')
    else:
      differnce_text = "보합"
      beforeDay_price = current_price
      difference_price = 0
    return differnce_text, beforeDay_price, difference_price
  
  def judge_curve(self, present_profit, future_profit):
    if present_profit < future_profit:
      curve = "우상향"
    else:
      curve = "우하향"
    return curve
    
  def crawl_stock(self, stock_dict):
    try:
      ###########################fnguide 크롤링###########################
      soup = self.get_requestParser(f"https://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A{stock_dict['stock_code']}")
      
      isOpinion = soup.select("#svdMainGrid9 > table > tbody > tr > td")[0].text
      
      if not isOpinion == "관련 데이터가 없습니다.":
        isOpinion = True
        # elemen = soup.find("img",{"id":"mainChart02"})['src']
        # invest_opinionImg = os.getcwd()+f"\\{stock_dict['stock_code']}_investOpinionImg.png"
        # opener=urllib.request.build_opener()
        # opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
        # urllib.request.install_opener(opener)
        # urllib.request.urlretrieve(elemen, invest_opinionImg) #기업 로고 이미지 다운로드
        # stock_dict['invest_opinionImg'] = invest_opinionImg
        elemen = soup.select("#svdMainGrid9 > table > tbody > tr > td")
        invest_opinion = elemen[0].text #투자의견
        stock_dict['invest_opinion'] = invest_opinion
        stock_dict['invest_opinionText'] = self.get_opinionText(invest_opinion)
        stock_dict['target_price'] = elemen[1].text #목표주가
        stock_dict['eps'] = elemen[2].text #EPS
        stock_dict['agency_num'] = elemen[4].text #추정기관수
      else:
        isOpinion = False
        return False
      stock_dict['isOpinion'] = isOpinion
      stock_dict['business_summary'] = soup.find("h3",{"id":"bizSummaryHeader"}).text #사업요약
      stock_dict['business_content'] = "" #사업현황
      content = soup.find("ul",{"id":"bizSummaryContent"}).find_all("li")
      for x in content:
        stock_dict['business_content'] += x.text
        
      data = soup.find("div",{"id":"highlight_D_Y"})
      table = parser_functions.make2d(data)
      df = pd.DataFrame(data=table[1:], columns=table[0])
      stock_dict['per'] = df.iloc[22][6] #PER
      stock_dict['pbr'] = df.iloc[23][6] #PBR
      stock_dict['roe'] = df.iloc[18][6] #ROE
      stock_dict['debt'] = df.iloc[13][6] #부채비율
      stock_dict['present_profit'] = df.iloc[2][6] #현재 영업이익
      stock_dict['future_profit'] = df.iloc[2][7] #미래 영업이익
      stock_dict['curve'] = self.judge_curve(int(stock_dict['present_profit'].replace(",","")), int(stock_dict['future_profit'].replace(",","")))
      print("fnguide 크롤링 완료")
      # ###########################관련기사 크롤링###########################
      # soup = self.get_requestParser(f"https://search.naver.com/search.naver?where=news&query={stock_dict['stock_name']}&sm=tab_opt&sort=1&photo=0&field=0&pd=1&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Add%2Cp%3A1w&is_sug_officeid=0")

      # link = soup.find_all(class_="news_tit")
      # stock_news = {'news_link':[],'news_tit':[]}
      # for i in link:
      #   stock_news['news_link'].append(i['href'])
      #   stock_news['news_tit'].append(i['title'])
        
      # stock_dict['stock_news'] = stock_news
      # print("관련기사 크롤링 완료")
      ###########################다음 금융 크롤링###########################
      pc_header = [
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36', #chrome 88
      ]
      print("크롬 실행")
      chrome_options = webdriver.ChromeOptions()
      chrome_options.add_argument('blink-settings=imagesEnabled=false') #이미지 로딩 X
      chrome_options.add_argument('headless') #창 띄우지않음
      chrome_options.add_argument("disable-gpu")
      chrome_options.add_argument("lang=ko_KR")
      chrome_options.add_argument('--incognito')
      chrome_options.add_argument('--no-sandbox')
      chrome_options.add_argument(f"user-agent={pc_header}")
      chrome_options.add_argument('--disable-blink-features=AutomationControlled')
      chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
      chrome_options.add_argument('--ignore-certificate-errors')
      chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
      chrome_options.add_experimental_option('useAutomationExtension', False)
      chrome_options.add_argument("--disable-setuid-sandbodx")
      chrome_options.add_argument("--disable-dev-shm-usage")
      chrome_options.add_argument("--disable-infobars")
      chrome_options.add_argument("--disable-browser-side-navigation")
      prefs = {'profile.default_content_setting_values': {'cookies' : 2, 'images': 2, 'plugins' : 2, 'popups': 2, 'geolocation': 2, 'notifications' : 2, 'auto_select_certificate': 2, 'fullscreen' : 2, 'mouselock' : 2, 'mixed_script': 2, 'media_stream' : 2, 'media_stream_mic' : 2, 'media_stream_camera': 2, 'protocol_handlers' : 2, 'ppapi_broker' : 2, 'automatic_downloads': 2, 'midi_sysex' : 2, 'push_messaging' : 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop' : 2, 'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement' : 2, 'durable_storage' : 2}}  
      chrome_options.add_experimental_option('prefs', prefs)
      driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
      driver.implicitly_wait(30) 
      
      url = f"window.open('https://finance.daum.net/quotes/A{stock_dict['stock_code']}#current/quote');"
      driver.execute_script(url)
      time.sleep(10)
      driver.switch_to.window(driver.window_handles[-1])
      dt = datetime.datetime.now()
      stock_dict['now'] = f"{dt.year}년 {dt.month}월 {dt.day}일 {dt.hour}시 {dt.minute}분 {dt.second}초" #현재시간
      pageString = driver.page_source  
      bsObj = BeautifulSoup(pageString, 'html.parser') 
      elemen = bsObj.find_all('td',{'class':'pR'})
      current_price = elemen[0].text #현재가
      stock_dict['current_price'] = current_price
      difference_price = elemen[2].text #전일비
      rateDifference_price = elemen[4].text #등락률
      stock_dict['rateDifference_price'] = rateDifference_price
      stock_dict['difference_text'], stock_dict['beforeDay_price'], stock_dict['difference_price'] = self.judge_updown(rateDifference_price, current_price, difference_price) #보합,상향,하향 #전일가 #전일비
      elemen = bsObj.find_all("dd")[6].find("p").text.strip(")").split("(")
      stock_dict['market_cap'] = elemen[0] #시가총액
      stock_dict['market_capRanking'] = elemen[1] #시가총액 순위
      
      driver.quit()
      print("크롬 종료")
      print("다음금융 크롤링 완료")
      
      self.save_stockDict(stock_dict)
      
      return stock_dict
    except Exception as e: 
      print(e)
      try:
        driver.quit()
      except:
        pass
      return False
    
  def save_stockDict(self, stock_dict):
    with open(f"{stock_dict['stock_code']}.json", "w", encoding="utf-8") as make_file:
      json.dump(stock_dict, make_file, ensure_ascii=False, indent="\t")
    print("json파일로 저장 완료")
  
    