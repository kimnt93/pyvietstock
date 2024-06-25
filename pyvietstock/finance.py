import re
import time
from datetime import datetime, timedelta
from functools import lru_cache
from typing import AnyStr, Union, List, Dict
import logging
import requests
from babel.messages.pofile import read_po

from pyvietstock.account import login
from pyvietstock.config import API_BASE_URL, FINANCE_BASE_URL, DEFAULT_API_HEADERS
from pyvietstock.params import HistoricalResolution, DocumentType, Period, TransferTypeID, EventType, \
    FinancialPeriod, FinancialReportType
from pyvietstock.schema import (
    EventTransferData, HistoricalData, TradingInfo, MarketPrice, StockDealDetail,
    StatisticsData, CompanyRelation, Document, HeaderNews, BondRelated, NewsArticle, ChannelNewsArticle, CompanyEvent,
    EventSameIndustry, IncomeStatementData
)
from pyvietstock.utils import convert_to_epoch, to_time_s


class VietStockFinance:
    def __init__(self):
        self._user_name = self.password = None
        self._headers = None
        self._token = None
        self._logged_in = False
        self.api_base_url = API_BASE_URL
        self.finance_base_url = FINANCE_BASE_URL
        self.home_url = "https://finance.vietstock.vn"

    def set_user_name(self, user_name):
        self._user_name = user_name
        return self

    def set_password(self, password):
        self.password = password
        return self

    def login(self):
        self._headers, self._token = login(self._user_name, self.password)
        self._logged_in = True
        return self

    def historical_data(
            self,
            symbol: AnyStr, resolution: Union[HistoricalResolution, AnyStr] = HistoricalResolution.DEFAULT,
            from_time: Union[datetime, int, str, None] = None,
            to_time: Union[datetime, int, str, None] = None
    ) -> Union[List[HistoricalData], None]:
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

        url = f'{self.api_base_url}/tvnew/history'
        params = {
            'symbol': symbol,
            'resolution': resolution,
            'from': from_time,
            'to': to_time,
        }

        response = requests.get(url, headers=DEFAULT_API_HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        if response.status_code == 200:
            return [HistoricalData(
                time=to_time_s(t, ns=1),
                open=o,
                high=h,
                low=l,
                close=c,
                volume=v
            ) for t, o, h, l, c, v in zip(data['t'], data['o'], data['h'], data['l'], data['c'], data['v'])]
        else:
            response.raise_for_status()  # Raise an exception for non-200 status codes
            return None

    def trading_info(
            self, symbol: AnyStr
    ) -> Union[TradingInfo, None]:
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
        url = f'{self.finance_base_url}/company/tradinginfo'
        payload = {
            'code': symbol,
            's': '1',
            '__RequestVerificationToken': self._token
        }

        response = requests.post(url, headers=self._headers, data=payload)
        response.raise_for_status()
        data = response.json()
        if response.status_code == 200:
            return TradingInfo(
                time=to_time_s(data["TradingDate"]),
                symbol=data["StockCode"],
                largest_trading_volume=data["KLCPLH"],
                total_volume_traded=data["KLCPNY"],
                prior_close_price=data["PriorClosePrice"],
                ceiling_price=data["CeilingPrice"],
                floor_price=data["FloorPrice"],
                total_vol=data["TotalVol"],
                total_val=data["TotalVal"],
                market_capital=data["MarketCapital"],
                highest_price=data["HighestPrice"],
                lowest_price=data["LowestPrice"],
                open_price=data["OpenPrice"],
                last_price=data["LastPrice"],
                avr_price=data["AvrPrice"],
                change=data["Change"],
                per_change=data["PerChange"],
                min_52w=data["Min52W"],
                max_52w=data["Max52W"],
                vol_52w=data["Vol52W"],
                outstanding_buy=data["OutstandingBuy"],
                outstanding_sell=data["OutstandingSell"],
                owned_ratio=data["OwnedRatio"],
                dividend=data["Dividend"],
                yield_=data["Yield"],
                beta=data["Beta"],
                eps=data["EPS"],
                pe=data["PE"],
                feps=data["FEPS"],
                bvps=data["BVPS"],
                pb=data["PB"],
                total_room=data["TotalRoom"],
                curr_room=data["CurrRoom"],
                remain_room=data["RemainRoom"],
                f_buy_vol=data["F_BuyVol"],
                f_buy_val=data["F_BuyVal"],
                f_sell_vol=data["F_SellVol"],
                f_sell_val=data["F_SellVal"],
                f_buy_put_vol=data["F_BuyPutVol"],
                f_buy_put_val=data["F_BuyPutVal"],
                f_sell_put_vol=data["F_SellPutVol"],
                f_sell_put_val=data["F_SellPutVal"],
                market_status=data["MarketStatus"],
                color_id=data["ColorId"],
                status_name=data["StatusName"],
                stock_status=data["StockStatus"]
            )
        else:
            response.raise_for_status()  # Raise an exception for non-200 status codes
            return None

    def market_prices(self) -> Union[List[MarketPrice], None]:
        """
        :return: all market prices including VN-Index, HNX-Index, VS 100, VN30F1M, Spot Gold, XAUUSDVN, Dầu,... as a list of dictionaries.
        fields are: time, symbol, name, price, change, per_change
        """
        url = f'{self.finance_base_url}/data/getmarketprice'
        payload = {
            # 'type': '2',
            '__RequestVerificationToken': self._token
        }

        response = requests.post(url, headers=self._headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            return [
                MarketPrice(
                    time=to_time_s(record["TradingDate"]),
                    symbol=record["Code"],
                    name=record["Name"],
                    price=record["Price"],
                    change=record["Change"],
                    per_change=record["PerChange"]
                ) for record in data
            ]
        else:
            response.raise_for_status()  # Raise an exception for non-200 status codes
            return None

    def stock_deal_detail(
            self,
            symbol: AnyStr
    ) -> Union[List[StockDealDetail], None]:
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
        url = f'{self.finance_base_url}/data/getstockdealdetail'
        payload = {
            'code': symbol,
            'seq': 0,
            '__RequestVerificationToken': self._token
        }

        response = requests.post(url, headers=self._headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            return [
                StockDealDetail(
                    time=to_time_s(record["TradingDate"]),
                    symbol=record["Stockcode"],
                    package=record["Package"],
                    price=record["Price"],
                    vol=record["Vol"],
                    total_vol=record["TotalVol"],
                    total_val=record["TotalVal"],
                    change=record["Change"],
                    side="B" if record["IsBuy"] else "S",
                    per_change=record["PerChange"]
                ) for record in data
            ]
        else:
            response.raise_for_status()  # Raise an exception for non-200 status codes
            return None

    def statistics_by_date_range(
            self,
            symbol: AnyStr,
            from_date: Union[str, None] = None,
            to_date: Union[str, None] = None
    ) -> Union[StatisticsData, None]:
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

        url = f'{self.finance_base_url}/data/StatisticByDate'
        payload = {
            'code': symbol,
            'fromDate': from_date,
            'toDate': to_date,
            '__RequestVerificationToken': self._token
        }
        response = requests.post(url, headers=self._headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            if data:
                record = data['Data'][0]  # Assuming there is only one record in the response
                return StatisticsData(
                    f_date=to_time_s(record["F_Date"]),
                    t_date=to_time_s(record["T_Date"]),
                    f_last_price=record["F_LastPrice"],
                    f_total_vol=record["F_TotalVol"],
                    t_last_price=record["T_LastPrice"],
                    t_total_vol=record["T_TotalVol"],
                    num_trading_days=record["NoTr"],
                    change=record["Change"],
                    per_change=record["PerChange"],
                    max_price=record["MaxPrice"],
                    min_price=record["MinPrice"],
                    avg_vol=record["AvgVol"],
                    max_vol=record["MaxVol"],
                    min_vol=record["MinVol"],
                    date_max_price=to_time_s(record["DateMaxPrice"]),
                    date_min_price=to_time_s(record["DateMinPrice"]),
                    date_max_vol=to_time_s(record["DateMaxVol"]),
                    date_min_vol=to_time_s(record["DateMinVol"])
                )
            else:
                logging.warning("No data found for the given period.")
                return None
        else:
            response.raise_for_status()
            return None

    def statistics_by_period(
            self,
            symbol: AnyStr,
            period: Union[Period, str] = Period.WEEK
    ) -> Union[StatisticsData, None]:
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

        url = f'{self.finance_base_url}/data/StatisticByPeriod'
        payload = {
            'code': symbol,
            'type': period,
            '__RequestVerificationToken': self._token
        }
        response = requests.post(url, headers=self._headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            if data:
                record = data[0]  # Assuming there is only one record in the response
                return StatisticsData(
                    f_date=to_time_s(record["F_Date"]),
                    t_date=to_time_s(record["T_Date"]),
                    f_last_price=record["F_LastPrice"],
                    f_total_vol=record["F_TotalVol"],
                    t_last_price=record["T_LastPrice"],
                    t_total_vol=record["T_TotalVol"],
                    num_trading_days=record["NoTr"],
                    change=record["Change"],
                    per_change=record["PerChange"],
                    max_price=record["MaxPrice"],
                    min_price=record["MinPrice"],
                    avg_vol=record["AvgVol"],
                    max_vol=record["MaxVol"],
                    min_vol=record["MinVol"],
                    date_max_price=to_time_s(record["DateMaxPrice"]),
                    date_min_price=to_time_s(record["DateMinPrice"]),
                    date_max_vol=to_time_s(record["DateMaxVol"]),
                    date_min_vol=to_time_s(record["DateMinVol"])
                )
            else:
                logging.warning("No data found for the given period.")
                return None
        else:
            response.raise_for_status()
            return None

    def company_relation_filter(
        self,
        symbol: AnyStr,
        page: int = 1,
        page_size: int = 20,
    ) -> Union[List[CompanyRelation], None]:
        """
        Fetches company relations filter based on provided parameters.
        :param symbol: symbol code.
        :param page: Page number (default: 1).
        :param page_size: Number of items per page (default: 10).
        :return: A list containing dictionaries with company relation details.
        """
        url = f'{self.finance_base_url}/company/GetCompanyRelationFilter'
        payload = {
            'Code': symbol,
            'Page': page,
            'PageSize': page_size,
            '__RequestVerificationToken': self._token
        }
        response = requests.post(url, headers=self._headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return [
                CompanyRelation(
                    symbol=item.get("StockCode", ""),
                    cat_id=item.get("CatID", 0),
                    last_price=item.get("LastPrice", 0),
                    change=item.get("Change", 0),
                    per_change=item.get("PerChange", 0.0),
                    highest_price=item.get("HighestPrice", 0),
                    lowest_price=item.get("LowestPrice", 0),
                    total_vol=item.get("TotalVol", 0),
                    total_val=item.get("TotalVal", 0),
                    foreign_buy_vol=item.get("ForeignBuyVol", 0),
                    foreign_sell_vol=item.get("ForeignSellVol", 0),
                    market_capital=item.get("MarketCapital", 0),
                    pe=item.get("PE", 0.0),
                    pb=item.get("PB", 0.0),
                    url=item.get("Url", ""),
                ) for item in data
            ]
        else:
            response.raise_for_status()
            return None

    def documents(
            self,
            symbol: AnyStr,
            page: int = 1,
            document_type: DocumentType = DocumentType.ALL,
    ) -> Union[List[Document], None]:
        """
        Fetches documents based on provided parameters.
        :param symbol: symbol code.
        :param page: Page number (default: 1).
        :param document_type: Document type ID. If None, fetches all document types.
        :return: A list containing dictionaries with document details.
        """
        url = f'{self.finance_base_url}/data/getdocument'
        payload = {
            'code': symbol,
            'page': page,
            '__RequestVerificationToken': self._token
        }
        if document_type is not None:
            payload['type'] = document_type
        response = requests.post(url, headers=self._headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                formatted_data = []
                return [
                    Document(
                        file_ext=document.get("FileExt", ""),
                        update_time=document.get("UpdateTime"),
                        total_row=document.get("TotalRow", 0),
                        file_info_id=document.get("FileInfoID", 0),
                        url=document.get("Url", ""),
                        title=document.get("Title", ""),
                        full_name=document.get("FullName", ""),
                        last_update=to_time_s(document.get("LastUpdate"))
                    ) for document in data
                ]
        else:
            response.raise_for_status()
            return None

    def header_news(
            self,
            page_size: int = 10,
    ) -> Union[List[HeaderNews], None]:
        """
        Fetches header news based on provided parameters.
        :param page_size: Number of news items per page (default: 10).
        :return: A list containing dictionaries with news details.
        """
        url = f'{self.finance_base_url}/data/headernews'
        payload = {
            'type': 1,
            'pageSize': page_size,
        }

        response = requests.post(url, params=payload, headers=self._headers)

        if response.status_code == 200:
            data = response.json()
            return [
                HeaderNews(
                    title=news_item.get("Title", ""),
                    url=f"https://finance.vietstock.vn{news_item.get('URL', '')}",
                    publish_time=to_time_s(news_item.get("PublishTime", ""))
                ) for news_item in data
            ]
        else:
            response.raise_for_status()
            return None

    def event_transfer_data(
            self, symbol: AnyStr,
            f_date: AnyStr = None, t_date: AnyStr = None,
            page: int = 1, page_size: int = 20,
            order_by: str = "EventID", order_dir: str = "DESC",
            transfer_type_id: TransferTypeID = TransferTypeID.ALL
    ) -> Union[List[EventTransferData], None]:

        # Set default f_date and t_date if not provided
        if not f_date or not t_date:
            today = datetime.now().date()
            three_months_ago = today - timedelta(days=3 * 30)  # Assuming 30 days per month for simplicity
            f_date = three_months_ago.strftime("%Y-%m-%d")
            t_date = today.strftime("%Y-%m-%d")

        url = f"{self.finance_base_url}/data/eventstransferdata"
        payload = {
            "transferTypeID": transfer_type_id,
            "stockCode": symbol,
            "fDate": f_date,
            "tDate": t_date,
            "page": page,
            "pageSize": page_size,
            "orderBy": order_by,
            "orderDir": order_dir,
            "__RequestVerificationToken": self._token
        }

        response = requests.post(url, data=payload, headers=self._headers)
        data = response.json()

        if response.status_code == 200:
            return [
                EventTransferData(
                    event_id=item["EventID"],
                    symbol=item["StockCode"],
                    finance_url=item["FinanceURL"],
                    content=item["Content"],
                    title=item["Title"],
                    file_url=item["FileUrl"],
                    type_name=item["TypeName"],
                    transfer_type_id=item["TransferTypeID"],
                    position_cd=item["PositionCD"],
                    extra_position_nlq=item["ExtraPositionNLQ"],
                    extra_position_nlq_ex=item["ExtraPositionNLQEx"],
                    extra_position_nn=item["ExtraPositionNN"],
                    relationship_type=item["RelationShipType"],
                    dtthcd=item["DTTHCD"],
                    dtthlq=item["DTTHLQ"],
                    dtlqlq=item["DTLQLQ"],
                    nvth=item["NVTH"],
                    register_buy_volume=item["RegisterBuyVolume"],
                    buy_volume=item["BuyVolume"],
                    register_sell_volume=item["RegisterSellVolume"],
                    sell_volume=item["SellVolume"],
                    register_volume_before=item["RegisterVolumeBefore"],
                    register_volume_after=item["RegisterVolumeAfter"],
                    volume_before=item["VolumeBefore"],
                    volume_after=item["VolumeAfter"],
                    date_buy_expected=item["DateBuyExpected"],
                    date_sell_expected=item["DateSellExpected"],
                    date_action_to=item["DateActionTo"],
                    position_cd_ex=item["PositionCDEx"],
                    extra_position_id_nn_ex=item["ExtraPositionIDNNEx"],
                    date_action_from=item["DateActionFrom"],
                    ndd_title=item["NDDTitle"],
                    nddth=item["NDDTH"],
                    ndd_position=item["NDDPosition"],
                    ndd_extra_position=item["NDDExtraPosition"],
                    transfer_title_type_id=item["TransferTitleTypeID"],
                    register_buy_volume_percent=item["RegisterBuyVolumePercent"],
                    buy_volume_percent=item["BuyVolumePercent"],
                    register_sell_volume_percent=item["RegisterSellVolumePercent"],
                    sell_volume_percent=item["SellVolumePercent"],
                    register_volume_before_percent=item["RegisterVolumeBeforePercent"],
                    register_volume_after_percent=item["RegisterVolumeAfterPercent"],
                    volume_before_percent=item["VolumeBeforePercent"],
                    volume_after_percent=item["VolumeAfterPercent"],
                    status_name=item["StatusName"],
                    total_record=item["TotalRecord"],
                    row=item["Row"]
                ) for item in data]
        else:
            response.raise_for_status()
            return None

    def bond_related(
            self,
            symbol: str,
            order_by: str = 'ReleaseDate',
            order_dir: str = 'DESC',
            page: int = 1,
            page_size: int = 20,
    ) -> Union[List[BondRelated], None]:
        """
        Fetches bond-related data based on provided parameters.
        :param symbol: Stock code.
        :param order_by: Field to order by (default: 'ReleaseDate').
        :param order_dir: Ordering direction ('ASC' or 'DESC', default: 'DESC').
        :param page: Page number (default: 1).
        :param page_size: Number of items per page (default: 20).
        :return: A list containing instances of BondRelated dataclass with bond details.
        """
        url = f'{self.finance_base_url}/Data/GetBondRelated'
        payload = {
            '__RequestVerificationToken': self._token,
            'code': symbol,
            'orderBy': order_by,
            'orderDir': order_dir,
            'page': page,
            'pageSize': page_size
        }

        response = requests.post(url, headers=self._headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return [
                    BondRelated(
                        key_code=bond.get("KeyCode", ""),
                        stock_code=bond.get("StockCode", ""),
                        bond_code=bond.get("BondCode", ""),
                        release_date=to_time_s(bond.get("ReleaseDate")),
                        due_date=to_time_s(bond.get("DueDate")),
                        face_value=bond.get("FaceValue", 0),
                        issue_rate=bond.get("IssueRate", 0.0),
                        issue_volume=bond.get("IssuaVolume", 0),
                        outstanding_shares=bond.get("OutstandingShares", 0),
                        company_code=bond.get("CompanyCode"),
                        company_name=bond.get("CompanyName"),
                        company_url=bond.get("CompanyURL"),
                        interest_rate_type=bond.get("InterestRateType", ""),
                        interest_period=bond.get("InterestPeriod", ""),
                        total_record=bond.get("TotalRecord", 0)
                    ) for bond in data
                ]
            else:
                logging.warning("Error: Data received is not in expected list format.")
                return None
        else:
            response.raise_for_status()
            return None

    def news_by_code(
            self,
            symbol: str,
            page: int = 1,
            page_size: int = 5
    ) -> Union[List[NewsArticle], None]:
        """
        Fetches news articles based on provided parameters.
        :param symbol:
        :param page:
        :param page_size:
        :return:
        """
        url = f"{self.finance_base_url}/data/getnewsbycode"
        params = {
            'code': symbol,
            'types[]': [-1, 3, 4, 5, 6, 7],
            'page': page,
            'pageSize': page_size,
            '__RequestVerificationToken': self._token
        }

        response = requests.post(url, data=params, headers=self._headers)
        if response.status_code == 200:
            articles = []
            response_data = response.json()
            for group in response_data:
                for item in group:
                    article = NewsArticle(
                        symbol=item.get('StockCode'),
                        channel_id=item.get('ChannelID'),
                        head=item.get('Head'),
                        article_id=item.get('ArticleID'),
                        title=item.get('Title'),
                        publish_time=to_time_s(item.get('PublishTime')),
                        content=item.get('Content'),
                        url=item.get('URL'),
                        total_row=item.get('TotalRow')
                    )
                    articles.append(article)
            return articles
        else:
            response.raise_for_status()
            return None

    def news_by_channel(
            self,
            symbol: str,
            news_type: int = 1,
            page: int = 1,
            page_size: int = 10
    ) -> Union[List[ChannelNewsArticle], None]:
        """
        Fetches news articles based on provided parameters.
        :param symbol:
        :param news_type:
        :param page:
        :param page_size:
        :return:
        """
        url = f"{self.finance_base_url}/data/getnewsbychannel3"
        params = {
            'code': symbol,
            'type': news_type,
            'page': page,
            'pageSize': page_size,
            '__RequestVerificationToken': self._token
        }

        response = requests.post(url, data=params, headers=self._headers)
        if response.status_code == 200:
            articles = []
            response_data = response.json()
            for item in response_data:
                article = ChannelNewsArticle(
                    article_id=item.get('ArticleID'),
                    title=item.get('Title'),
                    head=item.get('Head'),
                    head_image_url=item.get('HeadImageUrl'),
                    publish_time=to_time_s(item.get('PublishTime')),
                    channel_id=item.get('ChannelID'),
                    url=item.get('URL'),
                    row=item.get('Row'),
                    total_row=item.get('TotalRow')
                )
                articles.append(article)
            return articles
        else:
            response.raise_for_status()
            return None

    def events_by_type(
        self,
        symbol: str,
        from_date: str = '',
        to_date: str = '',
        page: int = 1,
        page_size: int = 5,
        order_by: str = 'Date1',
        order_dir: str = 'DESC'
    ) -> Union[List[CompanyEvent], None]:
        """
        Fetches events based on provided parameters.
        :param symbol:
        :param from_date:
        :param to_date:
        :param page:
        :param page_size:
        :param order_by:
        :param order_dir:
        :return:
        """
        url = f"{self.finance_base_url}/data/eventstypedata"

        events = []  # return this
        for event_type_id in EventType.ALL:
            params = {
                'eventTypeID': event_type_id,
                'channelID': 0,
                'code': symbol,
                'catID': -1,
                'fDate': from_date,
                'tDate': to_date,
                'page': page,
                'pageSize': page_size,
                'orderBy': order_by,
                'orderDir': order_dir,
                '__RequestVerificationToken': self._token
            }

            response = requests.post(url, data=params, headers=self._headers)
            if response.status_code == 200:
                response_data = response.json()
                response_data = response_data[0]
                for item in response_data:
                    events.append(CompanyEvent(
                        symbol=item.get('Code'),
                        event_id=item.get('EventID'),
                        event_type_id=item.get('EventTypeID'),
                        channel_id=item.get('ChannelID'),
                        company_name=item.get('CompanyName'),
                        cat_id=item.get('CatID'),
                        gdkhq_date=to_time_s(item.get('GDKHQDate')),
                        ndkcc_date=to_time_s(item.get('NDKCCDate')),
                        event_time=item.get('Time'),
                        note=item.get('Note'),
                        name=item.get('Name'),
                        exchange=item.get('Exchange'),
                        title=item.get('Title'),
                        content=item.get('Content'),
                        file_url=item.get('FileUrl'),
                        date_order=to_time_s(item.get('DateOrder')),
                        row=item.get('Row')
                    ))
            else:
                response.raise_for_status()

        return events if len(events) > 0 else None

    def events_same_industry(
        self,
        symbol: str,
        from_date: str = '',
        to_date: str = '',
        page: int = 1,
        page_size: int = 5,
        order_by: str = 'Date1',
        order_dir: str = 'DESC'
    ) -> Union[List[EventSameIndustry], None]:
        """
        Fetches events based on provided parameters for companies in the same industry.
        :param symbol: Stock symbol of the company.
        :param from_date: Starting date for event search.
        :param to_date: Ending date for event search.
        :param page: Page number for pagination.
        :param page_size: Number of records per page.
        :param order_by: Column to order the results by.
        :param order_dir: Direction of the order (ASC/DESC).
        :return: List of EventSameIndustry or None if no events are found.
        """
        url = f"{self.finance_base_url}/data/eventstypedatasameindustry"
        events = []  # return this
        for event_type_id in EventType.ALL:
            params = {
                'eventTypeID': event_type_id,
                'channelID': 0,
                'code': symbol,
                'catID': -1,
                'fDate': from_date,
                'tDate': to_date,
                'page': page,
                'pageSize': page_size,
                'orderBy': order_by,
                'orderDir': order_dir,
                '__RequestVerificationToken': self._token
            }

            response = requests.post(url, data=params, headers=self._headers)
            if response.status_code == 200:
                response_data = response.json()
                response_data = response_data[0]

                events = []
                for item in response_data:
                    events.append(EventSameIndustry(
                        symbol=item.get('Code'),
                        event_id=item.get('EventID'),
                        event_type_id=item.get('EventTypeID'),
                        channel_id=item.get('ChannelID'),
                        company_name=item.get('CompanyName'),
                        cat_id=item.get('CatID'),
                        gdkhq_date=to_time_s(item.get('GDKHQDate')),
                        ndkcc_date=to_time_s(item.get('NDKCCDate')),
                        event_time=to_time_s(item.get('Time')),
                        note=item.get('Note'),
                        name=item.get('Name'),
                        exchange=item.get('Exchange'),
                        title=item.get('Title'),
                        content=item.get('Content'),
                        file_url=item.get('FileUrl'),
                        date_order=to_time_s(item.get('DateOrder')),
                        place=item.get('Place'),
                        time_action=item.get('TimeAction'),
                        from_date=to_time_s(item.get('FromDate')),
                        row=item.get('Row')
                    ))

            else:
                response.raise_for_status()

        return events if len(events) > 0 else None

    def financial_plan(self, symbol):
        raise NotImplementedError()

    def income_statement(self, symbol: str, period: Union[FinancialPeriod, AnyStr] = FinancialPeriod.DEFAULT) -> Union[List[IncomeStatementData], None]:
        """
        Get income statement data for a stock code.
        :param symbol: Stock code to fetch report data for.
        :param period: Period type (QUY: Quarterly, NAM: Yearly). Default is quarterly.
        :return: List of dictionaries containing report data.
        """

        url = f'{self.finance_base_url}/data/KQKD_GetListReportData'
        payload = {
            'StockCode': symbol,
            'UnitedId': -1,
            'AuditedStatusId': -1,
            'Unit': 1000000000,
            'IsNamDuongLich': False,
            'PeriodType': period,
            'SortTimeType': 'Time_ASC',
            '__RequestVerificationToken': self._token,
        }

        response = requests.post(url, data=payload, headers=self._headers)
        datas = list()
        if response.status_code == 200:
            data = response.json().get('data', [])
            data = data[0]['data'] if data else []
            datas = [
                IncomeStatementData(
                    row_number=item['RowNumber'],
                    report_data_id=item['ReportDataID'],
                    year_period=item['YearPeriod'],
                    report_term_id=item['ReportTermID'],
                    audit_opinion=item['YKienKiemToan'],
                    audit_firm=item['CtyKiemToan'],
                    is_united=item['IsUnited'],
                    united_name=item['UnitedName'],
                    audit_status_id=item['AuditStatusID'],
                    audit_status_name=item['AuditStatusName'],
                    period_begin=item['PeriodBegin'],
                    period_end=item['PeriodEnd'],
                    base_period_begin=item['BasePeriodBegin'],
                    base_period_end=item['BasePeriodEnd'],
                    is_show_data_permission=item['IsShowData_Permission']
                ) for item in data
            ]
        else:
            response.raise_for_status()  # Raise an exception for non-200 status codes

        return None if len(datas) == 0 else datas

    def balance_sheet(self, symbol: str):
        raise NotImplementedError()

    def cash_flow_statement(self, symbol: str):
        raise NotImplementedError()
    def financial_ratios(self, symbol: str):
        raise NotImplementedError()

    @lru_cache(maxsize=2048)
    def _get_report_norm(self, report_type: FinancialReportType, symbol=None):
        if report_type == FinancialReportType.FINANCIAL_SUMMARY:
            url = f"{self.finance_base_url}/data/GetListReportNorm_BCTT_ByStockCode"
        elif report_type == FinancialReportType.BALANCE_SHEET:
            url = f"{self.finance_base_url}/data/GetListReportNormByStockCode"
        elif report_type == FinancialReportType.INCOME_STATEMENT:
            url = f"{self.finance_base_url}/data/GetListReportNorm_KQKD_ByStockCode"
        elif report_type == FinancialReportType.CASH_FLOW_STATEMENT:
            url = f"{self.finance_base_url}/data/GetListReportNorm_LCTT_ByStockCode"
        elif report_type == FinancialReportType.FINANCIAL_RATIOS:
            url = f"{self.finance_base_url}/data/GetListReportNorm_CSTC_ByStockCode"
        elif report_type == FinancialReportType.FINANCIAL_PLAN:
            url = f"{self.finance_base_url}/data/GetListReportNorm_CTKH"
        else:
            raise ValueError(f"Invalid report type {report_type}")

        payload = {
            "__RequestVerificationToken": self._token
        }
        if symbol is not None:
            payload['stockCode'] = symbol

        response = requests.post(url, data=payload, headers=self._headers)
        if response.status_code == 200:
            pattern = r'\d+\.'
            data = response.json()
            if 'error' in data:
                logging.error(f"Error fetching report period data: {data['error']}")
                return None

            data = data['data']
            report_norms = list()
            if isinstance(data, dict):
                for _, values in data.items():
                    report_norms.extend(values) if isinstance(values, list) else report_norms.append(values)

            return {
                row['ReportNormId']: re.sub(pattern, '', row['ReportNormName']).strip() for row in report_norms
            }
        else:
            response.raise_for_status()
            return dict()

    @lru_cache(maxsize=2048)
    def _get_report_period(
        self,
        report_type: FinancialReportType,
        symbol: str,
        period: FinancialPeriod = FinancialPeriod.DEFAULT,
        financial_year: bool = False
   ):
        if report_type == FinancialReportType.FINANCIAL_SUMMARY:
            url = f"{self.finance_base_url}/data/BCTT_GetListReportData"
        elif report_type == FinancialReportType.BALANCE_SHEET:
            url = f"{self.finance_base_url}/data/CDKT_GetListReportData"
        elif report_type == FinancialReportType.INCOME_STATEMENT:
            url = f"{self.finance_base_url}/data/KQKD_GetListReportData"
        elif report_type == FinancialReportType.CASH_FLOW_STATEMENT:
            url = f"{self.finance_base_url}/data/LCTT_GetListReportData_Quarter_VSTTinh"
        elif report_type == FinancialReportType.FINANCIAL_RATIOS:
            url = f"{self.finance_base_url}/data/CSTC_GetListTerms"
        elif report_type == FinancialReportType.FINANCIAL_PLAN:
            url = f"{self.finance_base_url}/data/CTKH_GetListYearPeriods"
        else:
            raise ValueError(f"Invalid report type {report_type}")

        payload = {
            "stockCode": symbol,
            "UnitedId": -1,
            "AuditedStatusId": -1,
            "Unit": 1000000000,
            "IsNamDuongLich": not financial_year,
            "PeriodType": period,
            "SortTimeType": "Time_ASC",
            "__RequestVerificationToken": self._token
        }
        response = requests.post(url, data=payload, headers=self._headers)
        if response.status_code == 200:
            data = response.json()
            if 'error' in data:
                logging.error(f"Error fetching report period data: {data['error']}")
                return None

            data = data['data']

            return [
                {
                    "year": item['YearPeriod'],
                    "quarter": item.get('ReportTermID', 1) - 1,  # 0 if report type is yearly
                } for item in data[-5:]  # Get the last 5 years/quarters
            ]
        else:
            response.raise_for_status()
            return dict()
