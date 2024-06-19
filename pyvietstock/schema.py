from dataclasses import dataclass
from datetime import datetime
from typing import Union


@dataclass
class HistoricalData:
    time: Union[datetime, str]
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class EventTransferData:
    event_id: int
    symbol: str
    finance_url: str
    content: str
    title: str
    file_url: str
    type_name: str
    transfer_type_id: int
    position_cd: str
    extra_position_nlq: str
    extra_position_nlq_ex: str
    extra_position_nn: str
    relationship_type: str
    dtthcd: str
    dtthlq: str
    dtlqlq: str
    nvth: str
    register_buy_volume: int
    buy_volume: int
    register_sell_volume: int
    sell_volume: int
    register_volume_before: int
    register_volume_after: int
    volume_before: int
    volume_after: int
    date_buy_expected: str
    date_sell_expected: str
    date_action_to: str
    position_cd_ex: str
    extra_position_id_nn_ex: int
    date_action_from: str
    ndd_title: int
    nddth: str
    ndd_position: int
    ndd_extra_position: int
    transfer_title_type_id: int
    register_buy_volume_percent: float
    buy_volume_percent: float
    register_sell_volume_percent: float
    sell_volume_percent: float
    register_volume_before_percent: float
    register_volume_after_percent: float
    volume_before_percent: float
    volume_after_percent: float
    status_name: str
    total_record: int
    row: int


@dataclass
class TradingInfo:
    time: Union[datetime, str]
    symbol: str
    largest_trading_volume: float
    total_volume_traded: float
    prior_close_price: float
    ceiling_price: float
    floor_price: float
    total_vol: float
    total_val: float
    market_capital: float
    highest_price: float
    lowest_price: float
    open_price: float
    last_price: float
    avr_price: float
    change: float
    per_change: float
    min_52w: float
    max_52w: float
    vol_52w: float
    outstanding_buy: float
    outstanding_sell: float
    owned_ratio: float
    dividend: float
    yield_: float  # 'yield' is a reserved keyword in Python, so using 'yield_'
    beta: float
    eps: float
    pe: float
    feps: float
    bvps: float
    pb: float
    total_room: float
    curr_room: float
    remain_room: float
    f_buy_vol: float
    f_buy_val: float
    f_sell_vol: float
    f_sell_val: float
    f_buy_put_vol: float
    f_buy_put_val: float
    f_sell_put_vol: float
    f_sell_put_val: float
    market_status: str
    color_id: int
    status_name: str
    stock_status: str


@dataclass
class MarketPrice:
    time: Union[datetime, str]
    symbol: str
    name: str
    price: float
    change: float
    per_change: float


@dataclass
class StockDealDetail:
    time: Union[str, float, int]
    symbol: str
    package: str
    price: float
    vol: float
    total_vol: float
    total_val: float
    change: float
    side: str
    per_change: float


@dataclass
class StatisticsData:
    f_date: Union[str, float, int]
    t_date: Union[str, float, int]
    f_last_price: float
    f_total_vol: float
    t_last_price: float
    t_total_vol: float
    num_trading_days: int
    change: float
    per_change: float
    max_price: float
    min_price: float
    avg_vol: float
    max_vol: float
    min_vol: float
    date_max_price: Union[str, float, int]
    date_min_price: Union[str, float, int]
    date_max_vol: Union[str, float, int]
    date_min_vol: Union[str, float, int]


@dataclass
class CompanyRelation:
    symbol: str
    cat_id: int
    last_price: float
    change: float
    per_change: float
    highest_price: float
    lowest_price: float
    total_vol: int
    total_val: float
    foreign_buy_vol: int
    foreign_sell_vol: int
    market_capital: float
    pe: float
    pb: float
    url: str


@dataclass
class Document:
    file_ext: str
    update_time: str
    total_row: int
    file_info_id: int
    url: str
    title: str
    full_name: str
    last_update: Union[str, None]


@dataclass
class HeaderNews:
    title: str
    url: str
    publish_time: Union[str, None]


@dataclass
class BondRelated:
    key_code: str
    stock_code: str
    bond_code: str
    release_date: Union[str, None]
    due_date: Union[str, None]
    face_value: int
    issue_rate: float
    issue_volume: int
    outstanding_shares: int
    company_code: Union[str, None]
    company_name: Union[str, None]
    company_url: Union[str, None]
    interest_rate_type: str
    interest_period: str
    total_record: int
