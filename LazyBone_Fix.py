import requests
import json
import os
import datetime
import csv
import socket
import time
import logging

#開機確定網路狀況
def checkNetwork():
    try:
        socket.gethostbyname("www.google.com")
        return True
    except Exception as e:
        print("Network error,Please check your network.")
        return False

def getToken():
    #用csv紀錄Token，Token有可能會過期，所以加上一個驗證機制
    global token, userid, filePath
    if os.path.isfile(filePath):
        with open(filePath, 'r') as csvfile:
            rows = csv.reader(csvfile)
            for i in rows:
                userid=i[1]
        print("Token失效，需重新取得")
    else:
        userid=input('請輸入學號')
        userid=userid.upper()
    password=input('請輸入密碼')
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'content-type': 'application/json',
        'Accept':'application/json',
    }
    data={
        'userId': userid,
        'password': password ,
        'remember': 'true'
    }
    loginJson=json.dumps(data)
    #url
    url='https://epidemicapi.ncut.edu.tw/api/login'
    # 獲取session
    session = requests.Session()
    #POST Data
    post = session.post(url, headers = headers, data = loginJson)
    #print(post)
    findToken = json.loads(post.text)
    token = findToken['token']
    #print(Token)
    if token:
        print("Succeed!")
        # 寫入資料
        with open(filePath, 'w', encoding='utf-8') as f:
            f.write(token)
            f.write(","+userid)
    else:
        print("Failed!, Confirm your userid & password")
        print("Your userid & password ", (userid, password))
        os.system("pause")

def date(n):
    date = datetime.datetime.today()+ datetime.timedelta(days=n)
    y=date.year
    m=date.month
    d=date.day
    if m<10:
        m='0'+str(m)
    if d<10:
        d='0'+str(d)
    y, m, d = str(y), str(m), str(d)
    return (y, m, d)

def getTargetUrl(y, m, d):
    global Headers, userid
    url = 'https://epidemicapi.ncut.edu.tw/api/temperatureSurveys/' + userid + '-' + y + '-' + m + '-' +d
    #print(url)
    return url
    
def upload():
    logging.debug("today info:")
    #抓取今天資料
    print(ty+" "+ tm +" "+td)
    todayData = session.get((getTargetUrl(ty, tm, td)), headers=Headers)
    print("-------------------------------------------------------------------")
    print(todayData.text)
    print("-------------------------------------------------------------------")
    # input ( " Waiting for enter input")
    #獲取上禮拜的資料
        
    id=userid+'-undefined'
    today=ty+'-'+tm+'-'+td
    
    morningActivity = "宿舍"
    noonActivity = "宿舍"
    nightActivity = "宿舍"
    className = "四訊三丙"
    departmentName = "40"
    #填入身體狀況資料
    bodyState = {
      "id": id,
      "saveDate": today,
      "morningTemp": None,
      "noonTemp": None,
      "nightTemp": None,
      "isValid": "true",
      "morningManner": "0",
      "noonManner": "0",
      "nightManner": "0",
      "isMorningFever": None,
      "isNoonFever": "false",
      "isNightFever": None,
      "morningActivity": morningActivity,
      "noonActivity": noonActivity,
      "nightActivity": nightActivity,
      "measureTime": "22:00",
      "userId": userid,
      "departmentId": "40",
      "className": className,
      "departmentName": departmentName,
      "type": "1"
    }
    #轉成Json格式
    defaultBodyStateJson=json.dumps(bodyState)
    #先檢查今天有沒有填報過，有用put傳資料，否則用post上傳第一筆資料
    if todayData.text:
        temp = json.loads(todayData.text)
        print(temp)
        #print(temp)
        morn = temp['morningActivity']
        noon = temp['noonActivity']
        night = temp['nightActivity']
        fever = temp['isNoonFever']
        print("今天已經填過資料，資料如下")
        print("--------------------------")
        print(f'{ty}-{tm}/{td}\nFever:{fever}\nmorningActivity:{morn}\nnoonActivity:{noon}\nnightActivity:{night}')
        print("--------------------------")
        override = input("覆蓋以上資料(y/n)")
        override = override.upper()
    else:        
        #第一次用post寫入資料
        logging.debug("Post")
        postResponse = session.post('https://epidemicapi.ncut.edu.tw/api/temperatureSurveys', headers=Headers, data=defaultBodyStateJson)
        #print(response)
        #如果post成功 response=200
        #print(response.text)
        if postResponse:
            #print("Post result : %s" % response)
            #抓取今天資料，如果有todayData有get到今天資料，表示上傳成功，否則重新上傳
            todayData = session.get((getLastWeekUrl(ty, tm, td)), headers=Headers)
            temp = json.loads(todayData.text)
            #print(temp)
            morn = temp['morningActivity']
            noon = temp['noonActivity']
            night = temp['nightActivity']
            fever = temp['isNoonFever']
            #print(todayDataJson)
            if todayData.text:
                print("Succeed")
                print("--------------------------")
                print(f'{ty}-{tm}/{td}\nFever:{fever}\nmorningActivity:{morn}\nnoonActivity:{noon}\nnightActivity:{night}')
                print("--------------------------")
                return False
            else:
                logging.debug("Post Failed")
                print("Failed")
                return True
        #put 失敗，重新post
        else:
            #print("Post eroor : %s " % response)
            #重新
            print("restart")
            updateData = session.post('https://epidemicapi.ncut.edu.tw/api/temperatureSurveys', headers=Headers, data=defaultBodyStateJson)
            todayData = session.get((getTargetUrl(ty, tm, td)), headers=Headers)
            temp = json.loads(todayData.text)
            #print(temp)
            morn = temp['morningActivity']
            noon = temp['noonActivity']
            night = temp['nightActivity']
            fever = temp['isNoonFever']
            if todayData.text:
                print("Succeed")
                print("--------------------------")
                print(f'{ty}-{tm}/{td}\nFever:{fever}\nmorningActivity:{morn}\nnoonActivity:{noon}\nnightActivity:{night}')
                print("--------------------------")
                return False
            else:
                print("Failed")
                return True


def getLastWeekUrl(y, m, d):
    global Headers, userid
    url = 'https://epidemicapi.ncut.edu.tw/api/temperatureSurveys/' + userid + '-' + y + '-' + m + '-' +d
    #print(url)
    print(y, m, d)
    return url


while True:
    logging.basicConfig(filename='error.log', level=logging.DEBUG)
    logTime = datetime.datetime.today()
    logging.info('Time : %s ' % logTime)
    if checkNetwork():
        pwd = os.getcwd()
        print(pwd)
        print("Network ok!")
        
        #Current  time 
        ty, tm, td = date(0)
        ly, lm, ld = date(-7)
        
        token, userid = None, None
        #設定session，讓所有的session都相同
        session = requests.Session()
        filePath=pwd+'\\token.csv'
        
        #檢查有沒有token.csv
        if os.path.isfile(filePath):
            with open(filePath, 'r') as csvfile:
                rows = csv.reader(csvfile)
                for i in rows:
                    token=i[0]
                    userid=i[1]
        else:
            print("新增資料......")
            getToken()
            
        #Token 資料格式為json
        Headers ={
            'authorization': 'Bearer '+token,
            'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
            'content-type': 'application/json; charset=utf-8',
            'Accept':'application/json',
        }

        print(f'Today is {ty}-{tm}/{td}')
        temp = True
        while temp:
            #print(lastWeekResponse.text)
            temp = upload()
            os.system("pause")
            logging.info("All Done")
        break
    else:
        time.sleep(1)