
# -*- coding: utf-8 -*-
import requests as r
import json
import os
from datetime import datetime

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = 'https://www.irctc.co.in/eticketing/protected/mapps1/trnscheduleenquiry/'
    
headrs = {'Referer': 'https://www.irctc.co.in/nget/booking/train-list' , 
                  'Sec-Fetch-Site': 'same-origin',
                  'Connection': 'keep-alive',
                  'Sec-Fetch-Mode': 'cors',
                  'DNT': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    'greq': '1570176943805',
    'Content-Language': 'en',
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Sec-Fetch-Site': 'same-origin',
    'Referer': 'https://www.irctc.co.in/nget/booking/train-list',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,mr;q=0.8,hi;q=0.7'}
    

cooky = {'_ga' :  'GA1.3.945583488.1570170656' , '_gid' :  'GA1.3.1894108909.1570170656' , '__gads' :  'ID=2cf276bd7ee49021:T=1570170661:S=ALNI_MaDXoeOY_7iBqY9sz6PAVyQPaCMzg' , 'et_app' :  '40daa3d667a2540eb029ab1136edff520ed293aa1e98ecf225e1c85029f22579ebba9d1a' , 'JSESSIONID' :  '4uibdzT9uYsjdVuExU6QGLZueAC1phHtxkbHOVT8bhQynR5VM-Z-!-55696307'}


def getFilePath() :
    
    dirpath = os.getcwd()

    now = datetime.now()

    filename = filename = f'TrainSchedule_{now.year}{now.month:02}{now.day:02}_{now.hour:02}{now.minute:02}.csv'
    filepath = os.path.join(dirpath, filename)
    
    return filepath


def getTrainScheduleJson(trainNumber):
    
    trainUrl = url + str(trainNumber)
    
    t = r.get(trainUrl, verify=False, headers= headrs, cookies=cooky)
    
    schedule = json.loads(t.text)
    
    return schedule
   

def saveScheduleToFile(scheduleJson, file,trainNumber, saveHeaders) :
    
    if(saveHeaders) :
        keys = list(scheduleJson['stationList'][0].keys())
        keys = ['Train Number', 'Serial number'] + keys   # prepend trainNumber
    
        s = ','.join(keys)
        file.write(s + '\n')        
        
    for idx, st in enumerate(scheduleJson['stationList']) :     
        vals = list(st.values())
        vals = [str(trainNumber), str(idx)] + vals   # prepend trainNumber
        
        s = ','.join(vals)        
        file.write(s + '\n')
        
def getInputs() :
    start = input('Enter start range (Default is 11000) : ')
    end = input("Enter end range (Default is 26200) : ")

    start = int(11000 if bool(start.strip()) == False else start)
    end = int(26200 if bool(end.strip()) == False else end)
    
    print(start)
    print(end)
    
    return start,end

def fetchSchedules(start,end) :
    
    firstTrain = True
    
    elapsedBefore = 0    
    startTime = datetime.now()
    
    for t in range(start,end + 1) :
        
        #print(f'Fetching schedule for Train {t}.')
        
        scheduleJson = getTrainScheduleJson(t)        
        
        if('stationList' in scheduleJson) :
            #print(f'Saving schedule for Train {t}.')
            saveScheduleToFile(scheduleJson,f,t, firstTrain) 
            firstTrain = False
            
        currentTime = datetime.now()
        elapsed = int((currentTime - startTime).total_seconds() / 60)
        
        if(elapsed > elapsedBefore) :
            percentComplete = round(( t - start) * 100 / (end - start),1)
            print(f'Train {t} done. {percentComplete}%     Elapsed : {elapsed} mins.')
            elapsedBefore = elapsed 
            
            f.flush()

start,end = getInputs()

filepath = getFilePath()
with open(filepath, "w+") as f :
    
    fetchSchedules(start,end) 
