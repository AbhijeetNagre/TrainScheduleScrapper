# TrainScheduleScrapper

## Usage

Interactive mode:

```bash
python /home/runner/work/TrainScheduleScrapper/TrainScheduleScrapper/TrainScheduleScrapper.py
```

Argument-based mode:

```bash
python /home/runner/work/TrainScheduleScrapper/TrainScheduleScrapper/TrainScheduleScrapper.py --start 11001 --end 11003
```

The script writes a `TrainSchedule_*.csv` file in the current working directory and prints per-train status output to stdout.

## Tests

Run:

```bash
python -m unittest discover -s /home/runner/work/TrainScheduleScrapper/TrainScheduleScrapper/tests
```
