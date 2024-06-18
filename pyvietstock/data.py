import time
import requests
from datetime import datetime, timedelta
from typing import Union, List, Dict, AnyStr, Optional

from cachetools.func import ttl_cache

from config import API_BASE_URL, API_DEFAULT_HEADERS, FINANCE_BASE_URL, _TOKENS, _HEADERS
from pyvietstock.params import HistoricalResolution, Period, DocumentType
from pyvietstock.utils import convert_to_epoch, to_time_s


@ttl_cache(maxsize=2048, ttl=10)
def historical_data(
        symbol: AnyStr, resolution: Union[HistoricalResolution, AnyStr] = HistoricalResolution.DEFAULT,
        from_time: Union[datetime, int, str, None] = None,
        to_time: Union[datetime, int, str, None] = None
) -> List[Dict[str, Union[datetime, float, int]]]:
    """
    Get historical data for a stock symbol. The data is resampled 1-day and 1-year in default
    :param symbol:
    :param resolution: any of the HistoricalResolution enum values or a string 1m, 1, 5m, 5, 15m, 30m, 1h, 1d, 1w, 1M,...
    :param from_time:
    :param to_time:
    :return: list of historical data with fields: time, open, high, low, close, volume
    """
    resolution = resolution if "m" not in resolution else resolution.replace("m", "")
    to_time = convert_to_epoch(to_time) if to_time is not None else int(time.time())
    from_time = convert_to_epoch(from_time) if from_time is not None else to_time - 31536000

    url = f'{API_BASE_URL}/tvnew/history'
    params = {
        'symbol': symbol,
        'resolution': resolution,
        'from': from_time,
        'to': to_time,
    }

    response = requests.get(url, headers=API_DEFAULT_HEADERS, params=params)
    response.raise_for_status()
    data = response.json()

    return [{
        "time": to_time_s(t, ns=1),
        "open": o,
        "high": h,
        "low": l,
        "close": c,
        "volume": v
    } for t, o, h, l, c, v in zip(data['t'], data['o'], data['h'], data['l'], data['c'], data['v'])]


def trading_info(symbol: AnyStr) -> Dict[str, Union[str, float, int]]:
    """
    :param symbol: stock symbol
    :return: trading info includes the following fields:
    - time, symbol, largest_trading_volume, total_volume_traded, prior_close_price, ceiling_price, floor_price,
    - total_vol, total_val, market_capital, highest_price, lowest_price, open_price, last_price, avr_price,
    - change, per_change, min_52w, max_52w, vol_52w, outstanding_buy, outstanding_sell, owned_ratio, dividend,
    - yield, beta, eps, pe, feps, bvps, pb, total_room, curr_room, remain_room,
    - f_buy_vol, f_buy_val, f_sell_vol, f_sell_val, f_buy_put_vol, f_buy_put_val, f_sell_put_vol, f_sell_put_val,
    - market_status, color_id, status_name, stock_status
    """
    url = f'{FINANCE_BASE_URL}/company/tradinginfo'
    payload = {
        'code': symbol,
        's': '1',
        '__RequestVerificationToken': _TOKENS
    }

    response = requests.post(url, headers=_HEADERS, data=payload)
    response.raise_for_status()
    data = response.json()

    return {
        "time": to_time_s(data["TradingDate"]),
        "symbol": data["StockCode"],
        "largest_trading_volume": data["KLCPLH"],
        "total_volume_traded": data["KLCPNY"],
        "prior_close_price": data["PriorClosePrice"],
        "ceiling_price": data["CeilingPrice"],
        "floor_price": data["FloorPrice"],
        "total_vol": data["TotalVol"],
        "total_val": data["TotalVal"],
        "market_capital": data["MarketCapital"],
        "highest_price": data["HighestPrice"],
        "lowest_price": data["LowestPrice"],
        "open_price": data["OpenPrice"],
        "last_price": data["LastPrice"],
        "avr_price": data["AvrPrice"],
        "change": data["Change"],
        "per_change": data["PerChange"],
        "min_52w": data["Min52W"],
        "max_52w": data["Max52W"],
        "vol_52w": data["Vol52W"],
        "outstanding_buy": data["OutstandingBuy"],
        "outstanding_sell": data["OutstandingSell"],
        "owned_ratio": data["OwnedRatio"],
        "dividend": data["Dividend"],
        "yield": data["Yield"],
        "beta": data["Beta"],
        "eps": data["EPS"],
        "pe": data["PE"],
        "feps": data["FEPS"],
        "bvps": data["BVPS"],
        "pb": data["PB"],
        "total_room": data["TotalRoom"],
        "curr_room": data["CurrRoom"],
        "remain_room": data["RemainRoom"],
        "f_buy_vol": data["F_BuyVol"],
        "f_buy_val": data["F_BuyVal"],
        "f_sell_vol": data["F_SellVol"],
        "f_sell_val": data["F_SellVal"],
        "f_buy_put_vol": data["F_BuyPutVol"],
        "f_buy_put_val": data["F_BuyPutVal"],
        "f_sell_put_vol": data["F_SellPutVol"],
        "f_sell_put_val": data["F_SellPutVal"],
        "market_status": data["MarketStatus"],
        "color_id": data["ColorId"],
        "status_name": data["StatusName"],
        "stock_status": data["StockStatus"]
    }


def market_prices() -> Union[List[Dict[str, Union[str, float, int]]], None]:
    """
    :return: all market prices including VN-Index, HNX-Index, VS 100, VN30F1M, Spot Gold, XAUUSDVN, Dầu,... as a list of dictionaries.
    fields are: time, symbol, name, price, change, per_change
    """
    url = f'{FINANCE_BASE_URL}/data/getmarketprice'
    payload = {
        # 'type': '2',
        '__RequestVerificationToken': _TOKENS
    }

    response = requests.post(url, headers=_HEADERS, data=payload)
    if response.status_code == 200:
        data = response.json()
        return [{
            "time": to_time_s(record["TradingDate"]),
            "symbol": record["Code"],
            "name": record["Name"],
            "price": record["Price"],
            "change": record["Change"],
            "per_change": record["PerChange"]
        } for record in data]
    else:
        print(f"Error: {response.status_code} - {response.reason}")
        return None


def stock_deal_detail(
        symbol: AnyStr
) -> Union[List[Dict[str, Union[str, float, int]]], None]:
    """
    Fetches stock deal details from current trading day.
    :param symbol: stock symbol
    :return: A list of dictionaries, each containing:
    - stock_code: Code of the stock.
    - package: Package identifier.
    - trading_date: Trading date in string format.
    - price: Price of the deal.
    - vol: Volume of the deal.
    - total_vol: Total volume traded for the day.
    - total_val: Total value traded for the day.
    - change: Change in price.
    - is_buy: buy (B) or sell (S) transaction.
    - per_change: Percentage change in price.
    """
    url = f'{FINANCE_BASE_URL}/data/getstockdealdetail'
    payload = {
        'code': symbol,
        'seq': 0,
        '__RequestVerificationToken': _TOKENS
    }

    response = requests.post(url, headers=_HEADERS, data=payload)
    if response.status_code == 200:
        data = response.json()
        formatted_data = [{
            "time": to_time_s(record["TradingDate"]),
            "symbol": record["Stockcode"],
            "package": record["Package"],
            "price": record["Price"],
            "vol": record["Vol"],
            "total_vol": record["TotalVol"],
            "total_val": record["TotalVal"],
            "change": record["Change"],
            "side": "B" if record["IsBuy"] else "S",
            "per_change": record["PerChange"]
        } for record in data]
        return formatted_data
    else:
        response.raise_for_status()  # Raise an exception for non-200 status codes
        return None


def statistics_by_date_range(
        symbol: AnyStr,
        from_date: Union[str, None] = None,
        to_date: Union[str, None] = None
) -> Union[Dict[str, Union[str, float, int]], None]:
    """
    Fetches statistics by period for a specific stock symbol within a date range.
    **Note**: You can only fetch data for a maximum of 1 year from the current date.
    :param symbol: Stock symbol.
    :param from_date: Start date in 'YYYY-MM-DD' format.
    :param to_date: End date in 'YYYY-MM-DD' format.
    :return: A list containing a single dictionary with statistical data:
    - f_date: Start date of the period.
    - t_date: End date of the period.
    - f_last_price: First price in the period.
    - f_total_vol: Total volume at the start of the period.
    - t_last_price: Last price in the period.
    - t_total_vol: Total volume at the end of the period.
    - no_tr: Number of trading sessions in the period.
    - change: Absolute change in price during the period.
    - per_change: Percentage change in price during the period.
    - max_price: Maximum price observed during the period.
    - min_price: Minimum price observed during the period.
    - avg_vol: Average volume traded per session during the period.
    - max_vol: Maximum volume traded in a session during the period.
    - min_vol: Minimum volume traded in a session during the period.
    - date_max_price: Date of maximum price in the period.
    - date_min_price: Date of minimum price in the period.
    - date_max_vol: Date of maximum volume in the period.
    - date_min_vol: Date of minimum volume in the period.
    """

    if not from_date:
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    if not to_date:
        to_date = (datetime.now()).strftime('%Y-%m-%d')

    url = f'{FINANCE_BASE_URL}/data/StatisticByDate'
    payload = {
        'code': symbol,
        'fromDate': from_date,
        'toDate': to_date,
        '__RequestVerificationToken': _TOKENS
    }
    response = requests.post(url, headers=_HEADERS, data=payload)
    if response.status_code == 200:
        data = response.json()
        if data:
            record = data['Data'][0]  # Assuming there is only one record in the response
            formatted_data = {
                "f_date": to_time_s(record["F_Date"]),
                "t_date": to_time_s(record["T_Date"]),
                "f_last_price": record["F_LastPrice"],
                "f_total_vol": record["F_TotalVol"],
                "t_last_price": record["T_LastPrice"],
                "t_total_vol": record["T_TotalVol"],
                "num_trading_days": record["NoTr"],
                "change": record["Change"],
                "per_change": record["PerChange"],
                "max_price": record["MaxPrice"],
                "min_price": record["MinPrice"],
                "avg_vol": record["AvgVol"],
                "max_vol": record["MaxVol"],
                "min_vol": record["MinVol"],
                "date_max_price": to_time_s(record["DateMaxPrice"]),
                "date_min_price": to_time_s(record["DateMinPrice"]),
                "date_max_vol": to_time_s(record["DateMaxVol"]),
                "date_min_vol": to_time_s(record["DateMinVol"])
            }
            return formatted_data
        else:
            print("No data found for the given period.")
            return None
    else:
        print(f"Error: {response.status_code} - {response.reason}")
        return None


def statistics_by_period(
        symbol: AnyStr,
        period: Union[Period, str] = Period.WEEK
) -> Union[Dict[str, Union[str, float, int]], None]:
    """
    Fetches statistics by period for a specific stock symbol within a date range.
    :param symbol: Stock symbol.
    :param period: Period type (W: Weekly, M: Monthly, Q: Quarterly, Y: Yearly).
    :return: A list containing a single dictionary with statistical data:
    - f_date: Start date of the period.
    - t_date: End date of the period.
    - f_last_price: First price in the period.
    - f_total_vol: Total volume at the start of the period.
    - t_last_price: Last price in the period.
    - t_total_vol: Total volume at the end of the period.
    - no_tr: Number of trading sessions in the period.
    - change: Absolute change in price during the period.
    - per_change: Percentage change in price during the period.
    - max_price: Maximum price observed during the period.
    - min_price: Minimum price observed during the period.
    - avg_vol: Average volume traded per session during the period.
    - max_vol: Maximum volume traded in a session during the period.
    - min_vol: Minimum volume traded in a session during the period.
    - date_max_price: Date of maximum price in the period.
    - date_min_price: Date of minimum price in the period.
    - date_max_vol: Date of maximum volume in the period.
    - date_min_vol: Date of minimum volume in the period.
    """

    url = f'{FINANCE_BASE_URL}/data/StatisticByPeriod'
    payload = {
        'code': symbol,
        'type': period,
        '__RequestVerificationToken': _TOKENS
    }
    response = requests.post(url, headers=_HEADERS, data=payload)
    if response.status_code == 200:
        data = response.json()
        if data:
            record = data[0]  # Assuming there is only one record in the response
            formatted_data = {
                "f_date": to_time_s(record["F_Date"]),
                "t_date": to_time_s(record["T_Date"]),
                "f_last_price": record["F_LastPrice"],
                "f_total_vol": record["F_TotalVol"],
                "t_last_price": record["T_LastPrice"],
                "t_total_vol": record["T_TotalVol"],
                "num_trading_days": record["NoTr"],
                "change": record["Change"],
                "per_change": record["PerChange"],
                "max_price": record["MaxPrice"],
                "min_price": record["MinPrice"],
                "avg_vol": record["AvgVol"],
                "max_vol": record["MaxVol"],
                "min_vol": record["MinVol"],
                "date_max_price": to_time_s(record["DateMaxPrice"]),
                "date_min_price": to_time_s(record["DateMinPrice"]),
                "date_max_vol": to_time_s(record["DateMaxVol"]),
                "date_min_vol": to_time_s(record["DateMinVol"])
            }
            return formatted_data
        else:
            print("No data found for the given period.")
            return None
    else:
        print(f"Error: {response.status_code} - {response.reason}")
        return None


def company_relation_filter(
    symbol: AnyStr,
    page: int = 1,
    page_size: int = 20,
) -> Union[List[Dict[str, Union[AnyStr, int, float]]], None]:
    """
    Fetches company relations filter based on provided parameters.
    :param symbol: symbol code.
    :param page: Page number (default: 1).
    :param page_size: Number of items per page (default: 10).
    :return: A list containing dictionaries with company relation details.
    """
    url = f'{FINANCE_BASE_URL}/company/GetCompanyRelationFilter'
    payload = {
        'Code': symbol,
        'Page': page,
        'PageSize': page_size,
        '__RequestVerificationToken': _TOKENS
    }
    response = requests.post(url, headers=_HEADERS, data=payload)

    if response.status_code == 200:
        data = response.json()
        return [{
            "symbol": item.get("StockCode", ""),
            "cat_id": item.get("CatID", 0),
            "last_price": item.get("LastPrice", 0),
            "change": item.get("Change", 0),
            "per_change": item.get("PerChange", 0.0),
            "highest_price": item.get("HighestPrice", 0),
            "lowest_price": item.get("LowestPrice", 0),
            "total_vol": item.get("TotalVol", 0),
            "total_val": item.get("TotalVal", 0),
            "foreign_buy_vol": item.get("ForeignBuyVol", 0),
            "foreign_sell_vol": item.get("ForeignSellVol", 0),
            "market_capital": item.get("MarketCapital", 0),
            "pe": item.get("PE", 0.0),
            "pb": item.get("PB", 0.0),
            "url": item.get("Url", ""),
        } for item in data]
    else:
        print(f"Error: {response.status_code} - {response.reason}")
        return None


def documents(
    symbol: AnyStr,
    page: int = 1,
    document_type: DocumentType = DocumentType.ALL,
) -> Union[List[Dict[str, AnyStr]], None]:
    """
    Fetches documents based on provided parameters.
    :param symbol: symbol code.
    :param page: Page number (default: 1).
    :param document_type: Document type ID. If None, fetches all document types.
    :return: A list containing dictionaries with document details.
    """
    url = f'{FINANCE_BASE_URL}/data/getdocument'
    payload = {
        'code': symbol,
        'page': page,
        '__RequestVerificationToken': _TOKENS
    }
    if document_type is not None:
        payload['type'] = document_type
    response = requests.post(url, headers=_HEADERS, data=payload)

    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            formatted_data = []
            for document in data:
                formatted_document = {
                    "file_ext": document.get("FileExt", ""),
                    "update_time": document.get("UpdateTime"),
                    "total_row": document.get("TotalRow", 0),
                    "file_info_id": document.get("FileInfoID", 0),
                    "url": document.get("Url", ""),
                    "title": document.get("Title", ""),
                    "full_name": document.get("FullName", ""),
                    "last_update": to_time_s(document.get("LastUpdate"))
                }
                formatted_data.append(formatted_document)
            return formatted_data
    else:
        print(f"Error: {response.status_code} - {response.reason}")
        return None


def header_news(
        page_size: int = 10,
) -> Union[List[Dict[str, Union[str, int]]], None]:
    """
    Fetches header news based on provided parameters.
    :param page_size: Number of news items per page (default: 4).
    :return: A list containing dictionaries with news details.
    """
    url = f'{FINANCE_BASE_URL}/data/headernews'
    payload = {
        'type': 1,
        'pageSize': page_size,
    }

    response = requests.post(url, params=payload, headers=_HEADERS)

    if response.status_code == 200:
        data = response.json()
        return [
            {
                "title": news_item.get("Title", ""),
                "url": f"https://finance.vietstock.vn{news_item.get('URL', '')}",
                "publish_time": to_time_s(news_item.get("PublishTime", ""))
            }
            for news_item in data
        ]
    else:
        print(f"Error: {response.status_code} - {response.reason}")
        return None


