# pyvietstock

## Overview
**pyvietstock** is a Python library aimed at providing tools and functionalities for working with Vietstock Finance data (https://finance.vietstock.vn/). The library is currently under construction and is intended to offer a comprehensive suite of features for data retrieval, analysis, and visualization tailored for the Vietnamese stock market.

## Features (Planned)
- Retrieve historical data from Vietstock
- Fetch detailed information about stock symbols
- Support for various financial indicators and metrics

## Implemented Functions Checklist
The function prototypes can be found under `pyvietstock/finance.py`. The response schemas are under `pyvietstock/schema.py`.
### Data Retrieval
- [x] **historical_data**: Fetches historical price and volume data for a stock symbol within a specified date range.
- [x] **trading_info**: Retrieves detailed trading information for a stock symbol, including various financial metrics and market status.
- [x] **market_prices**: Retrieves current market prices for various financial instruments like VN-Index, HNX-Index, etc.
- [x] **stock_deal_detail**: Fetches detailed stock deal information from the current trading day.

### Statistics
- [x] **statistics_by_date_range**: Fetches statistical data by date range for a specific stock symbol, including price changes, trading volumes, and extrema.
- [x] **statistics_by_period**: Retrieves statistical data by predefined periods (weekly, monthly, etc.) for a specific stock symbol.

### Company Information
- [x] **company_relation_filter**: Retrieves filtered company relations based on the provided stock symbol, including financial metrics and market performance.
- [x] **event_transfer_data**: Retrieves event transfer data for a stock symbol, including various event details and transfers.
- [x] **bond_related**: Fetches bond-related data for a stock, including details like release date, due date, and interest rates.
- [x] **documents**: Fetches documents related to a stock symbol, such as financial reports or disclosures.

### News
- [x] **header_news**: Fetches headline news from Vietstock, providing titles, URLs, and publication timestamps.

## Installation
The library is not yet available for installation as it is still under active development. Once completed, it will be available via PyPI. You can install the library locally by running the following command:

```bash
pip install .
```

## Usage

```python
from pyvietstock.finance import VietStockFinance

vf = VietStockFinance().login()
print(vf.documents("FPT"))
print(vf.historical_data("FPT"))
print(vf.event_transfer_data("FPT"))
print(vf.bond_related("VIC"))
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact
For any questions or feedback, please open an issue or contact us directly at [kimnt93@gmail.com].

---

## Project Status
**Note:** This project is currently under construction. Please check back later for updates.

---

## Acknowledgments
- Thanks to the contributors and the open-source community for their support.
