from dataclasses import dataclass



class ReportTermType:
    BY_YEAR = 1
    BY_QUARTER = 2


class ReportType:
    BCTQ = "BCTQ"


@dataclass(frozen=True)
class HistoricalResolution:
    ONE_MINUTE: str = "1"
    THREE_MINUTES: str = "3"
    FIVE_MINUTES: str = "5"
    FIFTEEN_MINUTES: str = "15"
    THIRTY_MINUTES: str = "30"
    FORTY_FIVE_MINUTES: str = "45"
    ONE_HOUR: str = "60"
    ONE_DAY: str = "1D"
    ONE_WEEK: str = "1W"
    ONE_MONTH: str = "1M"
    DEFAULT: str = ONE_DAY


@dataclass(frozen=True)
class Period:
    DAY = "D"
    WEEK = "W"
    MONTH = "M"
    QUARTER = "Q"
    YEAR = "Y"
    DEFAULT = DAY


@dataclass(frozen=True)
class DocumentType:
    ALL = None
    FINANCIAL_STATEMENT = 1
    BOARD_OF_MANAGEMENT = 23
    EXPLANATION_FOR_FINANCIAL_STATEMENT = 8
    CORPORATE_GOVERNANCE_REPORT = 9
    ANNUAL_REPORT = 2
    RESOLUTION_OF_SHAREHOLDERS_MEETING = 4
    SHAREHOLDERS_MEETING_DOCUMENTS = 5
    PROSPECTUS = 3
    LIQUIDITY_RATIO_REPORT = 10
    REGULATIONS = 6
