from get_stock import stock_list
from stock_crawl import crawl
from community_post import communityPost
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
import time

def job(id ,pw, term):
  done_list = []
  isDone = False
  while not isDone:
    try:
      for i in stock_list().get_stockList():
        if i['stock_code']:
          if i['stock_code'] not in done_list:
            stock_dict = crawl().crawl_stock(i)
            if stock_dict:
              if communityPost(id, pw).do_post(stock_dict):
                done_list.append(stock_dict['stock_code'])
              print(done_list)
              if len(done_list) == 30:
                isDone = True
                break
              time.sleep(60 * int(term))
    except Exception as e:
      print(e)

def main():
  try:
    print("""
  ___              _  _     _____  _               _        
  |_  |            (_)| |   /  ___|| |             | |       
    | | _   _  ___  _ | | __\ `--. | |_  _   _   __| | _   _ 
    | || | | |/ __|| || |/ / `--. \| __|| | | | / _` || | | |
/\__/ /| |_| |\__ \| ||   < /\__/ /| |_ | |_| || (_| || |_| |
\____/  \__,_||___/|_||_|\_\\____/  \__| \__,_| \__,_| \__, |
                                                        __/ |
                                                      |___/      
  """)
    sched = BackgroundScheduler(timezone='Asia/Seoul')
    sched.start()
    input_time = input("시각을 입력해주세요 ex) 09:10 : ")
    input_hour = input_time.split(":")[0]
    input_minute = input_time.split(":")[1]
    input_id = input("아이디를 입력해주세요 : ")
    input_pw = input("비밀번호를 입력해주세요 : ")
    input_term = input("작성 간격을(분) 입력해주세요 ex) 10 : ")
    try:
      sched.add_job(job, 'cron', hour=input_hour, minute=input_minute, id='communityPostN',args=[input_id,input_pw,input_term],misfire_grace_time=600)
    except:
      try:
        print("기존 Job 제거 후 새로 추가")
        sched.remove_all_jobs()
        sched.add_job(job, 'cron', hour=input_hour, minute=input_minute, id='communityPostN',args=[input_id,input_pw,input_term],misfire_grace_time=600)
      except JobLookupError as e:
        print("scheduler 오류 발생",e)
        return
    while True:
      try:
        print("Running main process............","| [time] ", str(time.localtime().tm_hour)+":"+str(time.localtime().tm_min)+":"+str(time.localtime().tm_sec))
        time.sleep(600)  
      except KeyboardInterrupt:
        import sys
        print("Ctrl + C 중지, Job 제거 후 프로그램 종료")
        sched.remove_all_jobs()
        sys.exit()
  except KeyboardInterrupt:
    print("Ctrl + C 중지")


if __name__ == "__main__":
  main()