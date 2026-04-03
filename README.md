# TrainScheduleScrapper

## Usage

Interactive mode:

```bash
python TrainScheduleScrapper.py
```

Argument-based mode:

```bash
python TrainScheduleScrapper.py --start 11001 --end 11003
```

The script writes a `TrainSchedule_*.csv` file in the current working directory and prints per-train status output to stdout.

## Tests

Run:

```bash
python -m unittest discover -s tests
```

## Publish

Generate a Windows executable from the project root with:

```powershell
.venv\Scripts\python.exe -m PyInstaller --onefile TrainScheduleScrapper.py
```

If `PyInstaller` is not installed yet, install it first:

```powershell
.venv\Scripts\python.exe -m pip install pyinstaller
```

The generated executable will be created at `dist\TrainScheduleScrapper.exe`.
