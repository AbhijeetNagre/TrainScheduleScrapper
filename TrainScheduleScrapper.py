# -*- coding: utf-8 -*-
import csv
import os
from datetime import datetime

import requests as r
import urllib3
from requests import Response
from requests.exceptions import RequestException

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SCHEDULE_API_URL = 'https://www.irctc.co.in/eticketing/protected/mapps1/trnscheduleenquiry/'
BOOKING_PAGE_URL = 'https://www.irctc.co.in/nget/booking/check-train-schedule'
REQUEST_TIMEOUT_SECONDS = 30

BASE_HEADERS = {
    "Accept-Language": "en-US,en;q=0.9",
    "DNT": "1",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/135.0.0.0 Safari/537.36"
    ),
}

API_HEADERS = {
    **BASE_HEADERS,
    "Accept": "application/json, text/plain, */*",
    "Content-Language": "en",
    "Referer": BOOKING_PAGE_URL,
}


def createSession():
    session = r.Session()
    session.headers.update(BASE_HEADERS)
    session.get(BOOKING_PAGE_URL, timeout=REQUEST_TIMEOUT_SECONDS, verify=False)
    return session


def getFilePath():
    dirpath = os.getcwd()
    now = datetime.now()

    filename = f'TrainSchedule_{now.year}{now.month:02}{now.day:02}_{now.hour:02}{now.minute:02}.csv'
    filepath = os.path.join(dirpath, filename)

    return filepath


def parseTrainScheduleResponse(response: Response, trainNumber):
    try:
        schedule = response.json()
    except ValueError as exc:
        snippet = response.text.strip().replace('\n', ' ')[:200]
        raise RuntimeError(
            f'IRCTC returned a non-JSON response for train {trainNumber}: {snippet}'
        ) from exc

    if not isinstance(schedule, dict):
        raise RuntimeError(f'IRCTC returned an unexpected payload for train {trainNumber}.')

    return schedule


def getTrainScheduleJson(session, trainNumber):
    trainUrl = SCHEDULE_API_URL + str(trainNumber)

    try:
        response = session.get(
            trainUrl,
            headers=API_HEADERS,
            timeout=REQUEST_TIMEOUT_SECONDS,
            verify=False,
        )
        response.raise_for_status()
    except RequestException as exc:
        raise RuntimeError(f'Unable to fetch train {trainNumber}: {exc}') from exc

    return parseTrainScheduleResponse(response, trainNumber)


def saveScheduleToFile(scheduleJson, writer, trainNumber, saveHeaders):
    stationList = scheduleJson['stationList']

    if saveHeaders:
        keys = list(stationList[0].keys())
        keys = ['Train Number', 'Train Name', 'Serial number'] + keys + [
            'Schedule', 'From', 'To', 'Train Owner', 'Duration',
            'RunsOnMon', 'RunsOnTue', 'RunsOnWed', 'RunsOnThu', 'RunsOnFri', 'RunsOnSat', 'RunsOnSun'
        ]

        writer.writerow(keys)

    for idx, st in enumerate(stationList):
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

        writer.writerow(vals)


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


def getInputs():
    start = input('Enter start range (Default is 11000) : ')
    end = input("Enter end range (Default is 26200) : ")

    try:
        start = int(11000 if not start.strip() else start)
        end = int(26200 if not end.strip() else end)
    except ValueError:
        print('Start and end ranges must be whole numbers.')
        return None, None

    if start > end:
        print('Start range cannot be greater than end range.')
        return None, None

    print(start)
    print(end)

    return start, end


def fetchSchedules(session, writer, start, end):
    firstTrain = True
    savedTrainCount = 0
    skippedTrainCount = 0
    failures = []

    elapsedBefore = 0
    startTime = datetime.now()
    totalRange = max(end - start + 1, 1)

    for trainNumber in range(start, end + 1):
        try:
            scheduleJson = getTrainScheduleJson(session, trainNumber)
        except RuntimeError as exc:
            failures.append(str(exc))
            print(exc)
            continue

        if scheduleJson.get('stationList'):
            saveScheduleToFile(scheduleJson, writer, trainNumber, firstTrain)
            firstTrain = False
            savedTrainCount += 1
        elif 'stationList' in scheduleJson:
            skippedTrainCount += 1
            print(f'Train {trainNumber} returned an empty station list and was skipped.')

        currentTime = datetime.now()
        elapsed = int((currentTime - startTime).total_seconds() / 60)

        if elapsed > elapsedBefore:
            percentComplete = round((trainNumber - start) * 100 / totalRange, 1)
            print(f'Train {trainNumber} done. {percentComplete}%     Elapsed : {elapsed} mins.')
            elapsedBefore = elapsed

    return savedTrainCount, skippedTrainCount, failures


def main():
    start, end = getInputs()
    if start is None or end is None:
        return 1

    filepath = getFilePath()

    try:
        session = createSession()
    except RequestException as exc:
        print(f'Unable to start an IRCTC session: {exc}')
        return 1

    with open(filepath, "w+", newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        savedTrainCount, skippedTrainCount, failures = fetchSchedules(session, writer, start, end)

    if savedTrainCount == 0:
        os.remove(filepath)
        print('No train schedules were saved, so the empty CSV file was removed.')
    else:
        print(f'Saved {savedTrainCount} train schedules to {filepath}.')

    if failures:
        print(f'Failed to fetch {len(failures)} train numbers.')

    if skippedTrainCount:
        print(f'Skipped {skippedTrainCount} train numbers with empty station lists.')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
