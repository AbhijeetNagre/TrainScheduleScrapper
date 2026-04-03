import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import TrainScheduleScrapper as scraper


def make_schedule(train_number):
    return {
        'trainName': f'Train {train_number}',
        'stationFrom': 'AAA',
        'stationTo': 'BBB',
        'trainOwner': 'NR',
        'duration': '01:00',
        'trainRunsOnMon': 'Y',
        'trainRunsOnTue': 'N',
        'trainRunsOnWed': 'Y',
        'trainRunsOnThu': 'N',
        'trainRunsOnFri': 'Y',
        'trainRunsOnSat': 'N',
        'trainRunsOnSun': 'Y',
        'stationList': [
            {
                'stationCode': 'AAA',
                'stationName': 'Alpha',
                'arrivalTime': 'SOURCE',
                'departureTime': '10:00',
                'routeNumber': '1',
                'haltTime': '00:00',
                'distance': '0',
                'dayCount': '1',
                'stnSerialNumber': '1'
            },
            {
                'stationCode': 'BBB',
                'stationName': 'Beta',
                'arrivalTime': '11:00',
                'departureTime': 'DEST',
                'routeNumber': '1',
                'haltTime': '00:05',
                'distance': '100',
                'dayCount': '1',
                'stnSerialNumber': '2'
            }
        ]
    }


class TrainScheduleScrapperTests(unittest.TestCase):
    def test_invalid_range_reports_no_valid_trains(self):
        output = io.StringIO()
        status = io.StringIO()

        def fail_if_prompted(_message):
            raise AssertionError('input() should not be called when args are provided')

        def fake_fetch(_train_number):
            return {}

        result = scraper.main(
            ['--start', '10990', '--end', '10992'],
            outputFile=output,
            statusStream=status,
            fetchScheduleFunc=fake_fetch,
            inputFunc=fail_if_prompted
        )

        self.assertEqual(result['validTrains'], [])
        self.assertEqual(result['invalidTrains'], [10990, 10991, 10992])
        self.assertEqual(output.getvalue(), '')

        status_text = status.getvalue()
        self.assertIn('Processing trains from 10990 to 10992.', status_text)
        self.assertIn('Train 10990 invalid.', status_text)
        self.assertIn('Train 10991 invalid.', status_text)
        self.assertIn('Train 10992 invalid.', status_text)
        self.assertIn('Completed. Valid trains: 0. Invalid trains: 3.', status_text)

    def test_invalid_range_reports_no_valid_train_Without_fakes(self):
        output = io.StringIO()
        status = io.StringIO()

        def fail_if_prompted(_message):
            raise AssertionError('input() should not be called when args are provided')

        def fake_fetch(_train_number):
            return {}

        result = scraper.main(
            ['--start', '10990', '--end', '10990'],
            outputFile=output,
            statusStream=status,
            fetchScheduleFunc=scraper.getTrainScheduleJson,
            inputFunc=fail_if_prompted
        )

        self.assertEqual(result['validTrains'], [])
        self.assertEqual(result['invalidTrains'], [10990])
        self.assertEqual(output.getvalue(), '')

        status_text = status.getvalue()
        self.assertIn('Processing trains from 10990 to 10990.', status_text)
        self.assertIn('Train 10990 invalid.', status_text)
        self.assertIn('Completed. Valid trains: 0. Invalid trains: 1.', status_text)


    def test_valid_range_reports_three_valid_trains(self):
        output = io.StringIO()
        status = io.StringIO()

        schedules = {
            11001: make_schedule(11001),
            11002: make_schedule(11002),
            11003: make_schedule(11003)
        }

        def fail_if_prompted(_message):
            raise AssertionError('input() should not be called when args are provided')

        def fake_fetch(train_number):
            return schedules[train_number]

        result = scraper.main(
            ['--start', '11001', '--end', '11003'],
            outputFile=output,
            statusStream=status,
            fetchScheduleFunc=fake_fetch,
            inputFunc=fail_if_prompted
        )

        self.assertEqual(result['validTrains'], [11001, 11002, 11003])
        self.assertEqual(result['invalidTrains'], [])

        output_text = output.getvalue()
        self.assertIn('11001', output_text)
        self.assertIn('11002', output_text)
        self.assertIn('11003', output_text)

        status_text = status.getvalue()
        self.assertIn('Processing trains from 11001 to 11003.', status_text)
        self.assertIn('Train 11001 valid.', status_text)
        self.assertIn('Train 11002 valid.', status_text)
        self.assertIn('Train 11003 valid.', status_text)
        self.assertIn('Completed. Valid trains: 3. Invalid trains: 0.', status_text)

    def test_valid_range_reports_valid_train_Without_fakes(self):
        output = io.StringIO()
        status = io.StringIO()

        def fail_if_prompted(_message):
            raise AssertionError('input() should not be called when args are provided')

        result = scraper.main(
            ['--start', '11001', '--end', '11001'],
            outputFile=output,
            statusStream=status,
            fetchScheduleFunc=scraper.getTrainScheduleJson,
            inputFunc=fail_if_prompted
        )

        self.assertEqual(result['validTrains'], [11001])
        self.assertEqual(result['invalidTrains'], [])

        output_text = output.getvalue()
        self.assertIn('11001', output_text)

        status_text = status.getvalue()
        self.assertIn('Processing trains from 11001 to 11001.', status_text)
        self.assertIn('Train 11001 valid.', status_text)
        self.assertIn('Completed. Valid trains: 1. Invalid trains: 0.', status_text)

if __name__ == '__main__':
    unittest.main()
