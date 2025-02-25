
# -*- coding: utf-8 -*-
import requests as r
import json
import os
from datetime import datetime

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = 'https://www.irctc.co.in/eticketing/protected/mapps1/trnscheduleenquiry/'
    
headrs = {
    "Host": "www.irctc.co.in",
    "Connection": "keep-alive",
    "greq": "1740131289744",
    "sec-ch-ua-platform": "\"Windows\"",
    "bmirak": "webbm",
    "Accept-Language": "en-US,en;q=0.0",
    "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
    "bmiyek": "E984274AF71D3FA1AB85FC66A0BC8D90",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "DNT": "1",
    "Content-Language": "en",
    "Content-Type": "application/x-www-form-urlencoded",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.irctc.co.in/nget/booking/check-train-schedule",
    "Accept-Encoding": "gzip, deflate, br, zstd"
}
    

cooky = {
    "et_appVIP1": "771902986.16671.0000",
    "_ga_SHTZYKNHG2": "GS1.1.1740131290.1.0.1740131290.0.0.0",
    "_gid": "GA1.3.2047262707.1740131290",
    "_ga": "GA1.1.1641348256.1740131290",
    "_ga_JSTMKS9Y3J": "GS1.1.1740131291.1.0.1740131291.0.0.0",
    "_ga_NFN218243Z": "GS1.1.1740131290.1.1.1740131314.0.0.0",
    "_ga_7K0RMWL72E": "GS1.1.1740131290.1.1.1740131314.0.0.0",
    "_ga_8J9SC9WB3T": "GS1.1.1740131290.1.1.1740131314.36.0.0",
    "_ga_HXEC5QES15": "GS1.1.1740131291.1.1.1740131314.0.0.0",
    "ngetAppId": "MBMn8lOjMZVhILNoDdzAD7gCj069GC_HynHSqcxlQ0tiRQQJ7igq!-822774871",
    "__gads": "ID=bb875e629d12d9d6:T=1727788888:RT=1740133762:S=ALNI_Ma0kdawu4C94aH5zGPheKhvbArpMg",
    "__gpi": "UID=00000f2dc154f158:T=1727788888:RT=1740133762:S=ALNI_MYYzdonH37wOVgxOhWVN0rjvs7J6g",
    "__eoi": "ID=8a75c8728a310d38:T=1727788888:RT=1740133762:S=AA-AfjaXoL4ukaJwZhUOLRtvvRJA",
    "TS018d84e5": "01d83d9ce731cb0b2ab808c4dc48b084daa50f5a9ff2a8a29afe44c89c848ad7c134a1412b231259cad118e8005c99de5ab4e419ba"
}


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
        keys = ['Train Number', 'Train Name', 'Serial number'] + keys + [
            'Schedule', 'From', 'To', 'Train Owner','Duration',
            'RunsOnMon', 'RunsOnTue', 'RunsOnWed', 'RunsOnThu', 'RunsOnFri', 'RunsOnSat', 'RunsOnSun'
        ]
    
        s = ','.join(keys)
        file.write(s + '\n')        
        
    for idx, st in enumerate(scheduleJson['stationList']) :     
        vals = list(st.values())
        vals = [str(trainNumber), scheduleJson['trainName'], str(idx)] + vals + [
            getTrainSchedule(scheduleJson, idx),  
            scheduleJson['stationFrom'], 
            scheduleJson['stationTo'],
            scheduleJson['trainOwner'], 
            scheduleJson['duration'],
            scheduleJson['trainRunsOnMon'], 
            scheduleJson['trainRunsOnTue'], 
            scheduleJson['trainRunsOnWed'], 
            scheduleJson['trainRunsOnThu'], 
            scheduleJson['trainRunsOnFri'], 
            scheduleJson['trainRunsOnSat'],
            scheduleJson['trainRunsOnSun']
        ]

        s = ','.join(vals)
        file.write(s + '\n')

def getTrainSchedule(scheduleJson, serialNumber) :

    if(serialNumber != 0) :
        return ''
    
    scheduleAsString = ''
    if(scheduleJson['trainRunsOnMon'] == 'Y') :
        scheduleAsString += ' MON '
    if(scheduleJson['trainRunsOnTue'] == 'Y') :
        scheduleAsString += ' TUE '
    if(scheduleJson['trainRunsOnWed'] == 'Y') :
        scheduleAsString += ' WED '
    if(scheduleJson['trainRunsOnThu'] == 'Y') :
        scheduleAsString += ' THU '
    if(scheduleJson['trainRunsOnFri'] == 'Y') :
        scheduleAsString += ' FRI '
    if(scheduleJson['trainRunsOnSat'] == 'Y') :
        scheduleAsString += ' SAT '
    if(scheduleJson['trainRunsOnSun'] == 'Y') :
        scheduleAsString += ' SUN'

    return scheduleAsString     

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
