# IT Inventory System (Eskort IT)

An internal IT stock inventory system used by the Eskort IT team to monitor, control and track IT stock movements (stock-in, stock-out, transfers and obsolete items). The system uses a simple Excel workbook as its data store and a Tkinter GUI for interactive operations.

## Table of contents
- [Description](#description)
- [Features](#features)
- [Technologies](#technologies)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Code structure overview](#code-structure-overview)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)


## Description

This application provides the Eskort IT team a small, local inventory tool that:
- Tracks items in the IT department (computers, peripherals, consumables)
- Records stock movements (Stock In / Stock Out)
- Allows transfers between departments and marks items as obsolete
- Produces a dashboard view of low/critical/ok stock levels

The authoritative data store is a spreadsheet (`Inventory.xlsx`) that the app reads and writes using `openpyxl`.


## Features

- Add new products to Product Master
- Record Stock In (receive stock)
- Record Stock Out (issue stock)
- Transfer stock between departments (logs transfers)
- Mark/remove products as obsolete (Non Stock Items)
- Dashboard with Low / Critical / All-items views and info cards
- Lightweight programmatic API (data layer) for automated scripts or tests


## Technologies

- Python 3.10+
- Tkinter (standard library) — GUI
- openpyxl — read/write Excel (`Inventory.xlsx`)
- pytest (optional) — tests


## Installation

1. Clone or copy the repository into a folder on the machine where the app will run.
2. Create a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

4. Ensure the Excel workbook `Inventory.xlsx` is present in the same folder as `main.py`. If you don't have one yet, create a workbook with the expected sheets:
- `dB` (movement log)
- `Product Master` (product catalog)
- `Inventory` (summary table)
- `Non Stock Items` (obsolete items)


## Usage

- Start the application (launches the GUI):

```powershell
python main.py
```

- Run the lightweight unit tests (no pytest required):

```powershell
python run_tests.py
```

- If you installed `pytest`, run:

```powershell
pytest -q
```

- Programmatic examples (from Python code):

```python
from data.excel_store import log_movement, calculate_balance, get_all_products

# Record a stock in
log_movement('Stock In', 'Printer Model X', 'SN123', 'Model X', 1, 'IT', 'PC01')

# Check balance
print(calculate_balance('Printer Model X'))
```


## Configuration

- `config/settings.py` — main configuration for the application. Important values:
	- `EXCEL_PATH` — path to `Inventory.xlsx` (default: `Inventory.xlsx`)
	- UI color constants (brand colors) used by the GUI

If you need to point to a different Excel file, edit `config/settings.py` or set an absolute path there.


## Code structure overview

- [main.py](main.py) — Application entrypoint; creates the root window and launches the dashboard.
- [config/settings.py](config/settings.py) — App configuration values (colors, `EXCEL_PATH`).
- [data/excel_store.py](data/excel_store.py) — Data layer: loads the Excel workbook and exposes functions for reading/updating stock and logs.
- [services/ui_helpers.py](services/ui_helpers.py) — UI utilities (styles, hover helpers, window history, status computation).
- [ui/dashboard.py](ui/dashboard.py) — Dashboard GUI window and auto-refresh logic.
- [ui/dialogs/product_windows.py](ui/dialogs/product_windows.py) — Dialog windows for Add Product, Stock In, Stock Out, Transfer, Remove.
- [tests/test_ui_helpers.py](tests/test_ui_helpers.py) — Example unit tests for non-GUI logic.
- [run_tests.py](run_tests.py) — Simple test runner (useful if `pytest` is not installed).
- [requirements.txt](requirements.txt) — Python dependencies.


## Troubleshooting

- Error: "Could not load Inventory.xlsx"
	- Ensure `Inventory.xlsx` exists in the same folder as `main.py` or update `EXCEL_PATH` in `config/settings.py`.
- Permission errors writing Excel
	- Close the workbook in Excel (Excel locks files on Windows). Run the app again.
- UI appears broken or fonts differ
	- Tkinter will fall back on available fonts/themes. Ensure your system has standard Windows fonts (Segoe UI). The app is tolerant of style failures.
- openpyxl errors reading sheets
	- Verify required sheet names exist: `dB`, `Product Master`, `Inventory`, `Non Stock Items`.


## Contributing

Thanks for helping improve this tool. A suggested workflow:

1. Fork the repository.
2. Create a topic branch for your change: `feature/your-feature` or `fix/bug`.
3. Add tests for new logic (non-GUI) and run `python run_tests.py`.
4. Commit with clear messages and open a pull request. Provide screenshots or sample data when modifying UI behavior.

Coding style & notes:
- Keep business logic in `data/excel_store.py` and UI code in `ui/*`.
- Prefer small, testable functions. Avoid importing GUI modules from tests.


