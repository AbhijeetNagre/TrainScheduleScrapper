import argparse
import json
import os
import sys
from datetime import datetime

import requests as r
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


def writeStatus(statusStream, message):
    if statusStream is None:
        return

    print(message, file=statusStream)

    if hasattr(statusStream, 'flush'):
        statusStream.flush()


def getFilePath():
    dirpath = os.getcwd()
    now = datetime.now()
    filename = f'TrainSchedule_{now.year}{now.month:02}{now.day:02}_{now.hour:02}{now.minute:02}.csv'
    filepath = os.path.join(dirpath, filename)

    return filepath


def getTrainScheduleJson(trainNumber):
    trainUrl = url + str(trainNumber)
    t = r.get(trainUrl, verify=False, headers=headrs, cookies=cooky)
    schedule = json.loads(t.text)

    return schedule


def isValidSchedule(scheduleJson):
    return bool(scheduleJson.get('stationList'))


def saveScheduleToFile(scheduleJson, file, trainNumber, saveHeaders):
    if saveHeaders:
        keys = list(scheduleJson['stationList'][0].keys())
        keys = ['Train Number', 'Train Name', 'Serial number'] + keys + [
            'Schedule', 'From', 'To', 'Train Owner', 'Duration',
            'RunsOnMon', 'RunsOnTue', 'RunsOnWed', 'RunsOnThu', 'RunsOnFri', 'RunsOnSat', 'RunsOnSun'
        ]

        s = ','.join(keys)
        file.write(s + '\n')

    for idx, st in enumerate(scheduleJson['stationList']):
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

        s = ','.join(str(val) for val in vals)
        file.write(s + '\n')


def getTrainSchedule(scheduleJson, serialNumber):
    if serialNumber != 0:
        return ''

    scheduleAsString = ''
    if scheduleJson['trainRunsOnMon'] == 'Y':
        scheduleAsString += ' MON '
    if scheduleJson['trainRunsOnTue'] == 'Y':
        scheduleAsString += ' TUE '
    if scheduleJson['trainRunsOnWed'] == 'Y':
        scheduleAsString += ' WED '
    if scheduleJson['trainRunsOnThu'] == 'Y':
        scheduleAsString += ' THU '
    if scheduleJson['trainRunsOnFri'] == 'Y':
        scheduleAsString += ' FRI '
    if scheduleJson['trainRunsOnSat'] == 'Y':
        scheduleAsString += ' SAT '
    if scheduleJson['trainRunsOnSun'] == 'Y':
        scheduleAsString += ' SUN'

    return scheduleAsString


def parseArgs(argv=None):
    parser = argparse.ArgumentParser(description='Download train schedule data for a train range.')
    parser.add_argument('--start', type=int, help='Train number to start from')
    parser.add_argument('--end', type=int, help='Train number to end at')
    return parser.parse_args(argv)


def getInputs(start=None, end=None, inputFunc=input):
    if start is None:
        start = inputFunc('Enter start range (Default is 11000) : ')
        start = int(11000 if not start.strip() else start)

    if end is None:
        end = inputFunc('Enter end range (Default is 26200) : ')
        end = int(26200 if not end.strip() else end)

    return start, end


def fetchSchedules(start, end, file, statusStream=None, fetchScheduleFunc=None):
    firstTrain = True
    elapsedBefore = 0
    startTime = datetime.now()
    fetchScheduleFunc = getTrainScheduleJson if fetchScheduleFunc is None else fetchScheduleFunc

    validTrains = []
    invalidTrains = []

    writeStatus(statusStream, f'Processing trains from {start} to {end}.')

    for trainNumber in range(start, end + 1):
        scheduleJson = fetchScheduleFunc(trainNumber)

        if isValidSchedule(scheduleJson):
            saveScheduleToFile(scheduleJson, file, trainNumber, firstTrain)
            firstTrain = False
            validTrains.append(trainNumber)
            writeStatus(statusStream, f'Train {trainNumber} valid.')
        else:
            invalidTrains.append(trainNumber)
            writeStatus(statusStream, f'Train {trainNumber} invalid.')

        currentTime = datetime.now()
        elapsed = int((currentTime - startTime).total_seconds() / 60)

        if elapsed > elapsedBefore:
            percentComplete = round((trainNumber - start) * 100 / (end - start), 1) if end != start else 100.0
            writeStatus(statusStream, f'Train {trainNumber} done. {percentComplete}%     Elapsed : {elapsed} mins.')
            elapsedBefore = elapsed

            if hasattr(file, 'flush'):
                file.flush()

    writeStatus(
        statusStream,
        f'Completed. Valid trains: {len(validTrains)}. Invalid trains: {len(invalidTrains)}.'
    )

    return {
        'start': start,
        'end': end,
        'validTrains': validTrains,
        'invalidTrains': invalidTrains
    }


def runScraper(start, end, outputFile=None, statusStream=None, fetchScheduleFunc=None):
    if outputFile is not None:
        result = fetchSchedules(start, end, outputFile, statusStream, fetchScheduleFunc)
        result['outputPath'] = None
        return result

    filepath = getFilePath()
    with open(filepath, "w+") as file:
        result = fetchSchedules(start, end, file, statusStream, fetchScheduleFunc)

    result['outputPath'] = filepath
    writeStatus(statusStream, f'Output file: {filepath}')

    return result


def main(argv=None, outputFile=None, statusStream=None, fetchScheduleFunc=None, inputFunc=input):
    args = parseArgs(argv)
    start, end = getInputs(args.start, args.end, inputFunc)
    return runScraper(start, end, outputFile, statusStream, fetchScheduleFunc)


if __name__ == '__main__':
    main(statusStream=sys.stdout)
