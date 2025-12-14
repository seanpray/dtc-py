from enum import IntEnum
import struct
import json
import dataclasses
from dataclasses import dataclass, asdict, field
from enum import IntEnum
from typing import Optional, Dict, Type, Any

# =============================================================================
# CONSTANTS & MESSAGE TYPES
# =============================================================================

CURRENT_VERSION = 8

# Text string lengths
USERNAME_PASSWORD_LENGTH = 32
SYMBOL_EXCHANGE_DELIMITER_LENGTH = 4
SYMBOL_LENGTH = 64
EXCHANGE_LENGTH = 16
UNDERLYING_SYMBOL_LENGTH = 32
SYMBOL_DESCRIPTION_LENGTH = 64
EXCHANGE_DESCRIPTION_LENGTH = 48
ORDER_ID_LENGTH = 32
TRADE_ACCOUNT_LENGTH = 32
TEXT_DESCRIPTION_LENGTH = 96
TEXT_MESSAGE_LENGTH = 256
ORDER_FREE_FORM_TEXT_LENGTH = 48
CLIENT_SERVER_NAME_LENGTH = 48
GENERAL_IDENTIFIER_LENGTH = 64
CURRENCY_CODE_LENGTH = 8
ORDER_FILL_EXECUTION_LENGTH = 64
PRICE_STRING_LENGTH = 16


class MessageType(IntEnum):
    # Authentication and connection monitoring
    LOGON_REQUEST = 1
    LOGON_RESPONSE = 2
    HEARTBEAT = 3
    LOGOFF = 5
    ENCODING_REQUEST = 6
    ENCODING_RESPONSE = 7

    # Market data
    MARKET_DATA_REQUEST = 101
    MARKET_DATA_REJECT = 103
    MARKET_DATA_SNAPSHOT = 104
    MARKET_DATA_UPDATE_TRADE = 107
    MARKET_DATA_UPDATE_TRADE_COMPACT = 112
    MARKET_DATA_UPDATE_LAST_TRADE_SNAPSHOT = 134
    MARKET_DATA_UPDATE_TRADE_WITH_UNBUNDLED_INDICATOR = 137
    MARKET_DATA_UPDATE_TRADE_WITH_UNBUNDLED_INDICATOR_2 = 146
    MARKET_DATA_UPDATE_TRADE_NO_TIMESTAMP = 142
    MARKET_DATA_UPDATE_BID_ASK = 108
    MARKET_DATA_UPDATE_BID_ASK_COMPACT = 117
    MARKET_DATA_UPDATE_BID_ASK_NO_TIMESTAMP = 143
    MARKET_DATA_UPDATE_BID_ASK_FLOAT_WITH_MICROSECONDS = 144
    MARKET_DATA_UPDATE_SESSION_OPEN = 120
    MARKET_DATA_UPDATE_SESSION_HIGH = 114
    MARKET_DATA_UPDATE_SESSION_LOW = 115
    MARKET_DATA_UPDATE_SESSION_VOLUME = 113
    MARKET_DATA_UPDATE_OPEN_INTEREST = 124
    MARKET_DATA_UPDATE_SESSION_SETTLEMENT = 119
    MARKET_DATA_UPDATE_SESSION_NUM_TRADES = 135
    MARKET_DATA_UPDATE_TRADING_SESSION_DATE = 136
    MARKET_DEPTH_REQUEST = 102
    MARKET_DEPTH_REJECT = 121
    MARKET_DEPTH_SNAPSHOT_LEVEL = 122
    MARKET_DEPTH_SNAPSHOT_LEVEL_FLOAT = 145
    MARKET_DEPTH_UPDATE_LEVEL = 106
    MARKET_DEPTH_UPDATE_LEVEL_FLOAT_WITH_MILLISECONDS = 140
    MARKET_DEPTH_UPDATE_LEVEL_NO_TIMESTAMP = 141
    MARKET_DATA_FEED_STATUS = 100
    MARKET_DATA_FEED_SYMBOL_STATUS = 116
    TRADING_SYMBOL_STATUS = 138

    # Market Orders
    MARKET_ORDERS_REQUEST = 150
    MARKET_ORDERS_REJECT = 151
    MARKET_ORDERS_ADD = 152
    MARKET_ORDERS_MODIFY = 153
    MARKET_ORDERS_REMOVE = 154
    MARKET_ORDERS_SNAPSHOT_MESSAGE_BOUNDARY = 155

    # Order entry and modification
    SUBMIT_NEW_SINGLE_ORDER = 208
    SUBMIT_NEW_OCO_ORDER = 201
    SUBMIT_FLATTEN_POSITION_ORDER = 209
    FLATTEN_POSITIONS_FOR_TRADE_ACCOUNT = 210
    CANCEL_ORDER = 203
    CANCEL_REPLACE_ORDER = 204

    # Trading related
    OPEN_ORDERS_REQUEST = 300
    OPEN_ORDERS_REJECT = 302
    ORDER_UPDATE = 301
    HISTORICAL_ORDER_FILLS_REQUEST = 303
    HISTORICAL_ORDER_FILLS_REJECT = 308
    HISTORICAL_ORDER_FILL_RESPONSE = 304
    CURRENT_POSITIONS_REQUEST = 305
    CURRENT_POSITIONS_REJECT = 307
    POSITION_UPDATE = 306
    ADD_CORRECTING_ORDER_FILL = 309
    CORRECTING_ORDER_FILL_RESPONSE = 310

    # Account list
    TRADE_ACCOUNTS_REQUEST = 400
    TRADE_ACCOUNT_RESPONSE = 401

    # Symbol discovery and security definitions
    EXCHANGE_LIST_REQUEST = 500
    EXCHANGE_LIST_RESPONSE = 501
    SYMBOLS_FOR_EXCHANGE_REQUEST = 502
    UNDERLYING_SYMBOLS_FOR_EXCHANGE_REQUEST = 503
    SYMBOLS_FOR_UNDERLYING_REQUEST = 504
    SECURITY_DEFINITION_FOR_SYMBOL_REQUEST = 506
    SECURITY_DEFINITION_RESPONSE = 507
    SYMBOL_SEARCH_REQUEST = 508
    SECURITY_DEFINITION_REJECT = 509

    # Account Balance Data
    ACCOUNT_BALANCE_REQUEST = 601
    ACCOUNT_BALANCE_REJECT = 602
    ACCOUNT_BALANCE_UPDATE = 600
    ACCOUNT_BALANCE_ADJUSTMENT = 607
    ACCOUNT_BALANCE_ADJUSTMENT_REJECT = 608
    ACCOUNT_BALANCE_ADJUSTMENT_COMPLETE = 609
    HISTORICAL_ACCOUNT_BALANCES_REQUEST = 603
    HISTORICAL_ACCOUNT_BALANCES_REJECT = 604
    HISTORICAL_ACCOUNT_BALANCE_RESPONSE = 606

    # Logging
    USER_MESSAGE = 700
    GENERAL_LOG_MESSAGE = 701
    ALERT_MESSAGE = 702
    JOURNAL_ENTRY_ADD = 703
    JOURNAL_ENTRIES_REQUEST = 704
    JOURNAL_ENTRIES_REJECT = 705
    JOURNAL_ENTRY_RESPONSE = 706

    # Historical price data
    HISTORICAL_PRICE_DATA_REQUEST = 800
    HISTORICAL_PRICE_DATA_RESPONSE_HEADER = 801
    HISTORICAL_PRICE_DATA_REJECT = 802
    HISTORICAL_PRICE_DATA_RECORD_RESPONSE = 803
    HISTORICAL_PRICE_DATA_TICK_RECORD_RESPONSE = 804
    HISTORICAL_PRICE_DATA_RESPONSE_TRAILER = 807

    # Historical market depth data
    HISTORICAL_MARKET_DEPTH_DATA_REQUEST = 900
    HISTORICAL_MARKET_DEPTH_DATA_RESPONSE_HEADER = 901
    HISTORICAL_MARKET_DEPTH_DATA_REJECT = 902
    HISTORICAL_MARKET_DEPTH_DATA_RECORD_RESPONSE = 903


# =============================================================================
# ENUMS
# =============================================================================


class EncodingEnum(IntEnum):
    BINARY_ENCODING = 0
    BINARY_WITH_VARIABLE_LENGTH_STRINGS = 1
    JSON_ENCODING = 2
    JSON_COMPACT_ENCODING = 3
    PROTOCOL_BUFFERS = 4


class LogonStatusEnum(IntEnum):
    LOGON_SUCCESS = 1
    LOGON_ERROR = 2
    LOGON_ERROR_NO_RECONNECT = 3
    LOGON_RECONNECT_NEW_ADDRESS = 4


class RequestActionEnum(IntEnum):
    SUBSCRIBE = 1
    UNSUBSCRIBE = 2
    SNAPSHOT = 3
    SNAPSHOT_WITH_INTERVAL_UPDATES = 4


class UnbundledTradeIndicatorEnum(IntEnum):
    UNBUNDLED_TRADE_NONE = 0
    FIRST_SUB_TRADE_OF_UNBUNDLED_TRADE = 1
    LAST_SUB_TRADE_OF_UNBUNDLED_TRADE = 2


class OrderStatusEnum(IntEnum):
    ORDER_STATUS_UNSPECIFIED = 0
    ORDER_STATUS_ORDER_SENT = 1
    ORDER_STATUS_PENDING_OPEN = 2
    ORDER_STATUS_PENDING_CHILD = 3
    ORDER_STATUS_OPEN = 4
    ORDER_STATUS_PENDING_CANCEL_REPLACE = 5
    ORDER_STATUS_PENDING_CANCEL = 6
    ORDER_STATUS_FILLED = 7
    ORDER_STATUS_CANCELED = 8
    ORDER_STATUS_REJECTED = 9
    ORDER_STATUS_PARTIALLY_FILLED = 10


class OrderUpdateReasonEnum(IntEnum):
    ORDER_UPDATE_REASON_UNSET = 0
    OPEN_ORDERS_REQUEST_RESPONSE = 1
    NEW_ORDER_ACCEPTED = 2
    GENERAL_ORDER_UPDATE = 3
    ORDER_FILLED = 4
    ORDER_FILLED_PARTIALLY = 5
    ORDER_CANCELED = 6
    ORDER_CANCEL_REPLACE_COMPLETE = 7
    NEW_ORDER_REJECTED = 8
    ORDER_CANCEL_REJECTED = 9
    ORDER_CANCEL_REPLACE_REJECTED = 10


class AtBidOrAskEnum(IntEnum):
    BID_ASK_UNSET = 0
    AT_BID = 1
    AT_ASK = 2


class MarketDepthUpdateTypeEnum(IntEnum):
    MARKET_DEPTH_UNSET = 0
    MARKET_DEPTH_INSERT_UPDATE_LEVEL = 1
    MARKET_DEPTH_DELETE_LEVEL = 2


class FinalUpdateInBatchEnum(IntEnum):
    FINAL_UPDATE_UNSET = 0
    FINAL_UPDATE_TRUE = 1
    FINAL_UPDATE_FALSE = 2
    FINAL_UPDATE_BEGIN_BATCH = 3


class MessageSetBoundaryEnum(IntEnum):
    MESSAGE_SET_BOUNDARY_UNSET = 0
    MESSAGE_SET_BOUNDARY_BEGIN = 1
    MESSAGE_SET_BOUNDARY_END = 2


class OrderTypeEnum(IntEnum):
    ORDER_TYPE_UNSET = 0
    ORDER_TYPE_MARKET = 1
    ORDER_TYPE_LIMIT = 2
    ORDER_TYPE_STOP = 3
    ORDER_TYPE_STOP_LIMIT = 4
    ORDER_TYPE_MARKET_IF_TOUCHED = 5
    ORDER_TYPE_LIMIT_IF_TOUCHED = 6
    ORDER_TYPE_MARKET_LIMIT = 7


class TimeInForceEnum(IntEnum):
    TIF_UNSET = 0
    TIF_DAY = 1
    TIF_GOOD_TILL_CANCELED = 2
    TIF_GOOD_TILL_DATE_TIME = 3
    TIF_IMMEDIATE_OR_CANCEL = 4
    TIF_ALL_OR_NONE = 5
    TIF_FILL_OR_KILL = 6


class BuySellEnum(IntEnum):
    BUY_SELL_UNSET = 0
    BUY = 1
    SELL = 2


class OpenCloseTradeEnum(IntEnum):
    TRADE_UNSET = 0
    TRADE_OPEN = 1
    TRADE_CLOSE = 2


class PartialFillHandlingEnum(IntEnum):
    PARTIAL_FILL_UNSET = 0
    PARTIAL_FILL_HANDLING_REDUCE_QUANTITY = 1
    PARTIAL_FILL_HANDLING_IMMEDIATE_CANCEL = 2


class MarketDataFeedStatusEnum(IntEnum):
    MARKET_DATA_FEED_STATUS_UNSET = 0
    MARKET_DATA_FEED_UNAVAILABLE = 1
    MARKET_DATA_FEED_AVAILABLE = 2


class TradingStatusEnum(IntEnum):
    TRADING_STATUS_UNKNOWN = 0
    TRADING_STATUS_PRE_OPEN = 1
    TRADING_STATUS_OPEN = 2
    TRADING_STATUS_CLOSE = 3
    TRADING_STATUS_TRADING_HALT = 4


class PriceDisplayFormatEnum(IntEnum):
    PRICE_DISPLAY_FORMAT_UNSET = -1
    PRICE_DISPLAY_FORMAT_DECIMAL_0 = 0
    PRICE_DISPLAY_FORMAT_DECIMAL_1 = 1
    PRICE_DISPLAY_FORMAT_DECIMAL_2 = 2
    PRICE_DISPLAY_FORMAT_DECIMAL_3 = 3
    PRICE_DISPLAY_FORMAT_DECIMAL_4 = 4
    PRICE_DISPLAY_FORMAT_DECIMAL_5 = 5
    PRICE_DISPLAY_FORMAT_DECIMAL_6 = 6
    PRICE_DISPLAY_FORMAT_DECIMAL_7 = 7
    PRICE_DISPLAY_FORMAT_DECIMAL_8 = 8
    PRICE_DISPLAY_FORMAT_DECIMAL_9 = 9
    PRICE_DISPLAY_FORMAT_DENOMINATOR_256 = 356
    PRICE_DISPLAY_FORMAT_DENOMINATOR_128 = 228
    PRICE_DISPLAY_FORMAT_DENOMINATOR_64 = 164
    PRICE_DISPLAY_FORMAT_DENOMINATOR_32_EIGHTHS = 140
    PRICE_DISPLAY_FORMAT_DENOMINATOR_32_QUARTERS = 136
    PRICE_DISPLAY_FORMAT_DENOMINATOR_32_HALVES = 134
    PRICE_DISPLAY_FORMAT_DENOMINATOR_32 = 132
    PRICE_DISPLAY_FORMAT_DENOMINATOR_16 = 116
    PRICE_DISPLAY_FORMAT_DENOMINATOR_8 = 108
    PRICE_DISPLAY_FORMAT_DENOMINATOR_4 = 104
    PRICE_DISPLAY_FORMAT_DENOMINATOR_2 = 102


class SecurityTypeEnum(IntEnum):
    SECURITY_TYPE_UNSET = 0
    SECURITY_TYPE_FUTURES = 1
    SECURITY_TYPE_STOCK = 2
    SECURITY_TYPE_FOREX = 3
    SECURITY_TYPE_INDEX = 4
    SECURITY_TYPE_FUTURES_STRATEGY = 5
    SECURITY_TYPE_FUTURES_OPTION = 7
    SECURITY_TYPE_STOCK_OPTION = 6
    SECURITY_TYPE_INDEX_OPTION = 8
    SECURITY_TYPE_BOND = 9
    SECURITY_TYPE_MUTUAL_FUND = 10


class PutCallEnum(IntEnum):
    PC_UNSET = 0
    PC_CALL = 1
    PC_PUT = 2


class SearchTypeEnum(IntEnum):
    SEARCH_TYPE_UNSET = 0
    SEARCH_TYPE_BY_SYMBOL = 1
    SEARCH_TYPE_BY_DESCRIPTION = 2


class HistoricalDataIntervalEnum(IntEnum):
    INTERVAL_TICK = 0
    INTERVAL_1_SECOND = 1
    INTERVAL_2_SECONDS = 2
    INTERVAL_4_SECONDS = 4
    INTERVAL_5_SECONDS = 5
    INTERVAL_10_SECONDS = 10
    INTERVAL_30_SECONDS = 30
    INTERVAL_1_MINUTE = 60
    INTERVAL_5_MINUTE = 300
    INTERVAL_10_MINUTE = 600
    INTERVAL_15_MINUTE = 900
    INTERVAL_30_MINUTE = 1800
    INTERVAL_1_HOUR = 3600
    INTERVAL_2_HOURS = 7200
    INTERVAL_1_DAY = 86400
    INTERVAL_1_WEEK = 604800


class HistoricalPriceDataRejectReasonCodeEnum(IntEnum):
    HPDR_UNSET = 0
    HPDR_UNABLE_TO_SERVE_DATA_RETRY_IN_SPECIFIED_SECONDS = 1
    HPDR_UNABLE_TO_SERVE_DATA_DO_NOT_RETRY = 2
    HPDR_DATA_REQUEST_OUTSIDE_BOUNDS_OF_AVAILABLE_DATA = 3
    HPDR_GENERAL_REJECT_ERROR = 4


class TradeConditionEnum(IntEnum):
    TRADE_CONDITION_NONE = 0
    TRADE_CONDITION_NON_LAST_UPDATE_EQUITY_TRADE = 1
    TRADE_CONDITION_ODD_LOT_EQUITY_TRADE = 2


# =============================================================================
# BASE MESSAGE & REGISTRY
# =============================================================================

MESSAGE_MAP: Dict[int, Type["DTCMessage"]] = {}


@dataclass
class DTCMessage:
    """Base class for all DTC messages."""

    def __init_subclass__(cls, type_id: int, **kwargs):
        super().__init_subclass__(**kwargs)
        if type_id is not None:
            MESSAGE_MAP[type_id] = cls
            cls.Type = type_id

    def to_json(self) -> bytes:
        data = asdict(self)
        if "Type" not in data:
            data["Type"] = getattr(self, "Type", 0)
        data.pop("Size", None)
        clean_data = {k: v for k, v in data.items() if v is not None}
        return json.dumps(clean_data).encode("utf-8") + b"\x00"

    @staticmethod
    def from_json(json_bytes: bytes) -> "DTCMessage":
        if json_bytes.endswith(b"\x00"):
            json_bytes = json_bytes[:-1]
        data = json.loads(json_bytes)
        msg_type = data.get("Type")

        if msg_type in MESSAGE_MAP:
            cls = MESSAGE_MAP[msg_type]
            valid_keys = {f.name for f in dataclasses.fields(cls)}
            filtered_data = {k: v for k, v in data.items() if k in valid_keys}
            return cls(**filtered_data)
        else:
            return GenericDTCMessage(**data)


@dataclass
class GenericDTCMessage(DTCMessage, type_id=None):
    Type: int

    def __post_init__(self):
        pass


# =============================================================================
# MESSAGE DEFINITIONS
# =============================================================================

# --- Authentication & Connection ---


@dataclass
class EncodingRequest:
    # NOTE: This does not inherit from DTCMessage because it must be packed in binary for the handshake
    ProtocolVersion: int = CURRENT_VERSION
    Encoding: int = EncodingEnum.JSON_ENCODING
    ProtocolType: str = "DTC"
    Type: int = 6

    def to_binary(self) -> bytes:
        # struct s_EncodingRequest { uint16 Size; uint16 Type; int32 Version; int32 Encoding; char Proto[4]; }
        fmt = "<HHi i 4s"
        size = struct.calcsize(fmt)
        proto_bytes = self.ProtocolType.encode("ascii")[:4].ljust(4, b"\x00")
        return struct.pack(
            fmt, size, self.Type, self.ProtocolVersion, self.Encoding, proto_bytes
        )


@dataclass
class EncodingResponse:
    # NOTE: This does not inherit from DTCMessage because it is received in binary
    ProtocolVersion: int = CURRENT_VERSION
    Encoding: int = EncodingEnum.BINARY_ENCODING
    ProtocolType: str = "DTC"
    Type: int = 7

    @classmethod
    def from_binary(cls, data: bytes) -> "EncodingResponse":
        fmt = "<HHi i 4s"
        if len(data) != struct.calcsize(fmt):
            raise ValueError(f"Expected {struct.calcsize(fmt)} bytes, got {len(data)}")
        size, msg_type, version, encoding, proto_bytes = struct.unpack(fmt, data)
        return cls(
            ProtocolVersion=version,
            Encoding=encoding,
            ProtocolType=proto_bytes.decode("ascii").rstrip("\x00"),
        )


@dataclass
class LogonRequest(DTCMessage, type_id=MessageType.LOGON_REQUEST):
    ProtocolVersion: int = CURRENT_VERSION
    Username: str = ""
    Password: str = ""
    GeneralTextData: str = ""
    Integer_1: int = 0
    Integer_2: int = 0
    HeartbeatIntervalInSeconds: int = 10
    TradeAccount: str = ""
    HardwareIdentifier: str = ""
    ClientName: str = "PythonDTC"
    MarketDataTransmissionInterval: int = 0


@dataclass
class LogonResponse(DTCMessage, type_id=MessageType.LOGON_RESPONSE):
    ProtocolVersion: int = CURRENT_VERSION
    Result: int = LogonStatusEnum.LOGON_SUCCESS
    ResultText: str = ""
    ReconnectAddress: str = ""
    Integer_1: int = 0
    ServerName: str = ""
    MarketDepthUpdatesBestBidAndAsk: int = 0
    TradingIsSupported: int = 0
    OCOOrdersSupported: int = 0
    OrderCancelReplaceSupported: int = 1
    SymbolExchangeDelimiter: str = ""
    SecurityDefinitionsSupported: int = 0
    HistoricalPriceDataSupported: int = 0
    ResubscribeWhenMarketDataFeedAvailable: int = 0
    MarketDepthIsSupported: int = 1
    OneHistoricalPriceDataRequestPerConnection: int = 0
    BracketOrdersSupported: int = 0
    UsesMultiplePositionsPerSymbolAndTradeAccount: int = 0
    MarketDataSupported: int = 1


@dataclass
class Heartbeat(DTCMessage, type_id=MessageType.HEARTBEAT):
    NumDroppedMessages: int = 0
    CurrentDateTime: int = 0


@dataclass
class Logoff(DTCMessage, type_id=MessageType.LOGOFF):
    Reason: str = ""
    DoNotReconnect: int = 0


# --- Market Data ---


@dataclass
class MarketDataRequest(DTCMessage, type_id=MessageType.MARKET_DATA_REQUEST):
    RequestAction: int = RequestActionEnum.SUBSCRIBE
    SymbolID: int = 0
    Symbol: str = ""
    Exchange: str = ""
    IntervalForSnapshotUpdatesInMilliseconds: int = 0


@dataclass
class MarketDataReject(DTCMessage, type_id=MessageType.MARKET_DATA_REJECT):
    SymbolID: int = 0
    RejectText: str = ""


@dataclass
class MarketDataSnapshot(DTCMessage, type_id=MessageType.MARKET_DATA_SNAPSHOT):
    SymbolID: int = 0
    SessionSettlementPrice: Optional[float] = None
    SessionOpenPrice: Optional[float] = None
    SessionHighPrice: Optional[float] = None
    SessionLowPrice: Optional[float] = None
    SessionVolume: Optional[float] = None
    SessionNumTrades: Optional[int] = None
    OpenInterest: Optional[int] = None
    BidPrice: Optional[float] = None
    AskPrice: Optional[float] = None
    AskQuantity: Optional[float] = None
    BidQuantity: Optional[float] = None
    LastTradePrice: Optional[float] = None
    LastTradeVolume: Optional[float] = None
    LastTradeDateTime: Optional[float] = None
    BidAskDateTime: Optional[float] = None
    SessionSettlementDateTime: Optional[int] = None
    TradingSessionDate: Optional[int] = None
    TradingStatus: Optional[int] = None


@dataclass
class MarketDataUpdateTrade(DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_TRADE):
    SymbolID: int = 0
    AtBidOrAsk: int = 0
    Price: float = 0.0
    Volume: float = 0.0
    DateTime: float = 0.0


@dataclass
class MarketDataUpdateTradeCompact(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_TRADE_COMPACT
):
    Price: float = 0.0
    Volume: float = 0.0
    DateTime: int = 0
    SymbolID: int = 0
    AtBidOrAsk: int = 0


@dataclass
class MarketDataUpdateLastTradeSnapshot(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_LAST_TRADE_SNAPSHOT
):
    SymbolID: int = 0
    LastTradePrice: float = 0.0
    LastTradeVolume: float = 0.0
    LastTradeDateTime: float = 0.0


@dataclass
class MarketDataUpdateTradeWithUnbundledIndicator(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_TRADE_WITH_UNBUNDLED_INDICATOR
):
    SymbolID: int = 0
    AtBidOrAsk: int = 0
    UnbundledTradeIndicator: int = 0
    TradeCondition: int = 0
    Reserve_1: int = 0
    Reserve_2: int = 0
    Price: float = 0.0
    Volume: int = 0
    Reserve_3: int = 0
    DateTime: float = 0.0


@dataclass
class MarketDataUpdateTradeWithUnbundledIndicator2(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_TRADE_WITH_UNBUNDLED_INDICATOR_2
):
    SymbolID: int = 0
    Price: float = 0.0
    Volume: int = 0
    DateTime: int = 0
    AtBidOrAsk: int = 0
    UnbundledTradeIndicator: int = 0
    TradeCondition: int = 0


@dataclass
class MarketDataUpdateTradeNoTimestamp(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_TRADE_NO_TIMESTAMP
):
    SymbolID: int = 0
    Price: float = 0.0
    Volume: int = 0
    AtBidOrAsk: int = 0
    UnbundledTradeIndicator: int = 0
    TradeCondition: int = 0


@dataclass
class MarketDataUpdateBidAsk(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_BID_ASK
):
    SymbolID: int = 0
    BidPrice: float = 0.0
    BidQuantity: float = 0.0
    AskPrice: float = 0.0
    AskQuantity: float = 0.0
    DateTime: int = 0


@dataclass
class MarketDataUpdateBidAskCompact(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_BID_ASK_COMPACT
):
    BidPrice: float = 0.0
    BidQuantity: float = 0.0
    AskPrice: float = 0.0
    AskQuantity: float = 0.0
    DateTime: int = 0
    SymbolID: int = 0


@dataclass
class MarketDataUpdateBidAskNoTimeStamp(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_BID_ASK_NO_TIMESTAMP
):
    SymbolID: int = 0
    BidPrice: float = 0.0
    BidQuantity: int = 0
    AskPrice: float = 0.0
    AskQuantity: int = 0


@dataclass
class MarketDataUpdateBidAskFloatWithMicroseconds(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_BID_ASK_FLOAT_WITH_MICROSECONDS
):
    SymbolID: int = 0
    BidPrice: float = 0.0
    BidQuantity: float = 0.0
    AskPrice: float = 0.0
    AskQuantity: float = 0.0
    DateTime: int = 0


@dataclass
class MarketDataUpdateSessionOpen(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_SESSION_OPEN
):
    SymbolID: int = 0
    Price: float = 0.0
    TradingSessionDate: int = 0


@dataclass
class MarketDataUpdateSessionHigh(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_SESSION_HIGH
):
    SymbolID: int = 0
    Price: float = 0.0
    TradingSessionDate: int = 0


@dataclass
class MarketDataUpdateSessionLow(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_SESSION_LOW
):
    SymbolID: int = 0
    Price: float = 0.0
    TradingSessionDate: int = 0


@dataclass
class MarketDataUpdateSessionVolume(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_SESSION_VOLUME
):
    SymbolID: int = 0
    Volume: float = 0.0
    TradingSessionDate: int = 0
    IsFinalSessionVolume: int = 0


@dataclass
class MarketDataUpdateOpenInterest(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_OPEN_INTEREST
):
    SymbolID: int = 0
    OpenInterest: int = 0
    TradingSessionDate: int = 0


@dataclass
class MarketDataUpdateSessionSettlement(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_SESSION_SETTLEMENT
):
    SymbolID: int = 0
    Price: float = 0.0
    DateTime: int = 0


@dataclass
class MarketDataUpdateSessionNumTrades(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_SESSION_NUM_TRADES
):
    SymbolID: int = 0
    NumTrades: int = 0
    TradingSessionDate: int = 0


@dataclass
class MarketDataUpdateTradingSessionDate(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_TRADING_SESSION_DATE
):
    SymbolID: int = 0
    Date: int = 0


@dataclass
class MarketDataFeedStatus(DTCMessage, type_id=MessageType.MARKET_DATA_FEED_STATUS):
    Status: int = 0


@dataclass
class MarketDataFeedSymbolStatus(
    DTCMessage, type_id=MessageType.MARKET_DATA_FEED_SYMBOL_STATUS
):
    SymbolID: int = 0
    Status: int = 0


@dataclass
class TradingSymbolStatus(DTCMessage, type_id=MessageType.TRADING_SYMBOL_STATUS):
    SymbolID: int = 0
    Status: int = 0


# --- Market Depth ---


@dataclass
class MarketDepthRequest(DTCMessage, type_id=MessageType.MARKET_DEPTH_REQUEST):
    RequestAction: int = RequestActionEnum.SUBSCRIBE
    SymbolID: int = 0
    Symbol: str = ""
    Exchange: str = ""
    NumLevels: int = 0


@dataclass
class MarketDepthReject(DTCMessage, type_id=MessageType.MARKET_DEPTH_REJECT):
    SymbolID: int = 0
    RejectText: str = ""


@dataclass
class MarketDepthSnapshotLevel(
    DTCMessage, type_id=MessageType.MARKET_DEPTH_SNAPSHOT_LEVEL
):
    SymbolID: int = 0
    Side: int = 0
    Price: float = 0.0
    Quantity: float = 0.0
    Level: int = 0
    IsFirstMessageInBatch: int = 0
    IsLastMessageInBatch: int = 0
    DateTime: float = 0.0
    NumOrders: int = 0


@dataclass
class MarketDepthSnapshotLevelFloat(
    DTCMessage, type_id=MessageType.MARKET_DEPTH_SNAPSHOT_LEVEL_FLOAT
):
    SymbolID: int = 0
    Price: float = 0.0
    Quantity: float = 0.0
    NumOrders: int = 0
    Level: int = 0
    Side: int = 0
    FinalUpdateInBatch: int = 0


@dataclass
class MarketDepthUpdateLevel(DTCMessage, type_id=MessageType.MARKET_DEPTH_UPDATE_LEVEL):
    SymbolID: int = 0
    Side: int = 0
    Price: float = 0.0
    Quantity: float = 0.0
    UpdateType: int = 0
    DateTime: float = 0.0
    NumOrders: int = 0
    FinalUpdateInBatch: int = 0
    Level: int = 0


@dataclass
class MarketDepthUpdateLevelFloatWithMilliseconds(
    DTCMessage, type_id=MessageType.MARKET_DEPTH_UPDATE_LEVEL_FLOAT_WITH_MILLISECONDS
):
    SymbolID: int = 0
    DateTime: int = 0
    Price: float = 0.0
    Quantity: float = 0.0
    Side: int = 0
    UpdateType: int = 0
    NumOrders: int = 0
    FinalUpdateInBatch: int = 0
    Level: int = 0


@dataclass
class MarketDepthUpdateLevelNoTimestamp(
    DTCMessage, type_id=MessageType.MARKET_DEPTH_UPDATE_LEVEL_NO_TIMESTAMP
):
    SymbolID: int = 0
    Price: float = 0.0
    Quantity: float = 0.0
    NumOrders: int = 0
    Side: int = 0
    UpdateType: int = 0
    FinalUpdateInBatch: int = 0
    Level: int = 0


# --- Market Orders (MBO) ---


@dataclass
class MarketOrdersRequest(DTCMessage, type_id=MessageType.MARKET_ORDERS_REQUEST):
    RequestAction: int = RequestActionEnum.SUBSCRIBE
    SymbolID: int = 0
    Symbol: str = ""
    Exchange: str = ""
    SendQuantitiesGreaterOrEqualTo: int = 0


@dataclass
class MarketOrdersReject(DTCMessage, type_id=MessageType.MARKET_ORDERS_REJECT):
    SymbolID: int = 0
    RejectText: str = ""


@dataclass
class MarketOrdersAdd(DTCMessage, type_id=MessageType.MARKET_ORDERS_ADD):
    SymbolID: int = 0
    Side: int = 0
    Quantity: int = 0
    Price: float = 0.0
    OrderID: int = 0
    DateTime: int = 0


@dataclass
class MarketOrdersModify(DTCMessage, type_id=MessageType.MARKET_ORDERS_MODIFY):
    SymbolID: int = 0
    Side: int = 0
    Quantity: int = 0
    Price: float = 0.0
    OrderID: int = 0
    PriorPrice: float = 0.0
    PriorQuantity: int = 0
    PriorOrderID: int = 0
    DateTime: int = 0


@dataclass
class MarketOrdersRemove(DTCMessage, type_id=MessageType.MARKET_ORDERS_REMOVE):
    SymbolID: int = 0
    Quantity: int = 0
    Price: float = 0.0
    OrderID: int = 0
    DateTime: int = 0
    Side: int = 0


@dataclass
class MarketOrdersSnapshotMessageBoundary(
    DTCMessage, type_id=MessageType.MARKET_ORDERS_SNAPSHOT_MESSAGE_BOUNDARY
):
    SymbolID: int = 0
    MessageBoundary: int = 0


# --- Order Entry ---


@dataclass
class SubmitNewSingleOrder(DTCMessage, type_id=MessageType.SUBMIT_NEW_SINGLE_ORDER):
    Symbol: str = ""
    Exchange: str = ""
    TradeAccount: str = ""
    ClientOrderID: str = ""
    OrderType: int = OrderTypeEnum.ORDER_TYPE_MARKET
    BuySell: int = BuySellEnum.BUY
    Price1: float = 0.0
    Price2: float = 0.0
    Quantity: float = 0.0
    TimeInForce: int = TimeInForceEnum.TIF_DAY
    GoodTillDateTime: int = 0
    IsAutomatedOrder: int = 0
    IsParentOrder: int = 0
    FreeFormText: str = ""


@dataclass
class SubmitFlattenPositionOrder(
    DTCMessage, type_id=MessageType.SUBMIT_FLATTEN_POSITION_ORDER
):
    Symbol: str = ""
    Exchange: str = ""
    TradeAccount: str = ""
    ClientOrderID: str = ""
    FreeFormText: str = ""
    IsAutomatedOrder: int = 0


@dataclass
class CancelReplaceOrder(DTCMessage, type_id=MessageType.CANCEL_REPLACE_ORDER):
    ServerOrderID: str = ""
    ClientOrderID: str = ""
    Price1: float = 0.0
    Price2: float = 0.0
    Quantity: float = 0.0
    Price1IsSet: int = 1
    Price2IsSet: int = 1
    Unused: int = 0
    TimeInForce: int = 0
    GoodTillDateTime: int = 0
    UpdatePrice1OffsetToParent: int = 0
    TradeAccount: str = ""
    Price1AsString: str = ""
    Price2AsString: str = ""


@dataclass
class CancelOrder(DTCMessage, type_id=MessageType.CANCEL_ORDER):
    ServerOrderID: str = ""
    ClientOrderID: str = ""
    TradeAccount: str = ""


@dataclass
class SubmitNewOCOOrder(DTCMessage, type_id=MessageType.SUBMIT_NEW_OCO_ORDER):
    Symbol: str = ""
    Exchange: str = ""
    ClientOrderID_1: str = ""
    OrderType_1: int = 0
    BuySell_1: int = 0
    Price1_1: float = 0.0
    Price2_1: float = 0.0
    Quantity_1: float = 0.0
    ClientOrderID_2: str = ""
    OrderType_2: int = 0
    BuySell_2: int = 0
    Price1_2: float = 0.0
    Price2_2: float = 0.0
    Quantity_2: float = 0.0
    TimeInForce: int = 0
    GoodTillDateTime: int = 0
    TradeAccount: str = ""
    IsAutomatedOrder: int = 0
    ParentTriggerClientOrderID: str = ""
    FreeFormText: str = ""
    OpenOrClose: int = 0
    PartialFillHandling: int = 0
    UseOffsets: int = 0
    OffsetFromParent1: float = 0.0
    OffsetFromParent2: float = 0.0
    MaintainSamePricesOnParentFill: int = 0
    Price1_1AsString: str = ""
    Price2_1AsString: str = ""
    Price1_2AsString: str = ""
    Price2_2AsString: str = ""


@dataclass
class OpenOrdersRequest(DTCMessage, type_id=MessageType.OPEN_ORDERS_REQUEST):
    RequestID: int = 0
    RequestAllOrders: int = 1
    ServerOrderID: str = ""
    TradeAccount: str = ""


@dataclass
class OpenOrdersReject(DTCMessage, type_id=MessageType.OPEN_ORDERS_REJECT):
    RequestID: int = 0
    RejectText: str = ""


@dataclass
class OrderUpdate(DTCMessage, type_id=MessageType.ORDER_UPDATE):
    RequestID: int = 0
    TotalNumMessages: int = 0
    MessageNumber: int = 0
    Symbol: str = ""
    Exchange: str = ""
    PreviousServerOrderID: str = ""
    ServerOrderID: str = ""
    ClientOrderID: str = ""
    ExchangeOrderID: str = ""
    OrderStatus: int = 0
    OrderUpdateReason: int = 0
    OrderType: int = 0
    BuySell: int = 0
    Price1: float = 0.0
    Price2: float = 0.0
    TimeInForce: int = 0
    GoodTillDateTime: int = 0
    OrderQuantity: float = 0.0
    FilledQuantity: float = 0.0
    RemainingQuantity: float = 0.0
    AverageFillPrice: float = 0.0
    LastFillPrice: float = 0.0
    LastFillDateTime: int = 0
    LastFillQuantity: float = 0.0
    LastFillExecutionID: str = ""
    TradeAccount: str = ""
    InfoText: str = ""
    NoOrders: int = 0
    ParentServerOrderID: str = ""


@dataclass
class HistoricalOrderFillsRequest(
    DTCMessage, type_id=MessageType.HISTORICAL_ORDER_FILLS_REQUEST
):
    RequestID: int = 0
    ServerOrderID: str = ""
    NumberOfDays: int = 0
    TradeAccount: str = ""
    StartDateTime: int = 0


@dataclass
class HistoricalOrderFillsReject(
    DTCMessage, type_id=MessageType.HISTORICAL_ORDER_FILLS_REJECT
):
    RequestID: int = 0
    RejectText: str = ""


@dataclass
class HistoricalOrderFillResponse(
    DTCMessage, type_id=MessageType.HISTORICAL_ORDER_FILL_RESPONSE
):
    RequestID: int = 0
    TotalNumberMessages: int = 0
    MessageNumber: int = 0
    Symbol: str = ""
    Exchange: str = ""
    ServerOrderID: str = ""
    BuySell: int = 0
    Price: float = 0.0
    DateTime: int = 0
    Quantity: float = 0.0
    UniqueExecutionID: str = ""
    TradeAccount: str = ""
    OpenClose: int = 0
    NoOrderFills: int = 0
    InfoText: str = ""
    HighPriceDuringPosition: float = 0.0
    LowPriceDuringPosition: float = 0.0
    PositionQuantity: float = 0.0
    Username: str = ""
    ExchangeOrderID: str = ""
    SenderSubID: str = ""


@dataclass
class CurrentPositionsRequest(
    DTCMessage, type_id=MessageType.CURRENT_POSITIONS_REQUEST
):
    RequestID: int = 0
    TradeAccount: str = ""


@dataclass
class CurrentPositionsReject(DTCMessage, type_id=MessageType.CURRENT_POSITIONS_REJECT):
    RequestID: int = 0
    RejectText: str = ""


@dataclass
class PositionUpdate(DTCMessage, type_id=MessageType.POSITION_UPDATE):
    RequestID: int = 0
    TotalNumberMessages: int = 0
    MessageNumber: int = 0
    Symbol: str = ""
    Exchange: str = ""
    Quantity: float = 0.0
    AveragePrice: float = 0.0
    PositionIdentifier: str = ""
    TradeAccount: str = ""
    NoPositions: int = 0
    Unsolicited: int = 0
    MarginRequirement: float = 0.0
    EntryDateTime: int = 0
    OpenProfitLoss: float = 0.0
    HighPriceDuringPosition: float = 0.0
    LowPriceDuringPosition: float = 0.0
    QuantityLimit: float = 0.0
    MaxPotentialPostionQuantity: float = 0.0


@dataclass
class AddCorrectingOrderFill(DTCMessage, type_id=MessageType.ADD_CORRECTING_ORDER_FILL):
    Symbol: str = ""
    Exchange: str = ""
    TradeAccount: str = ""
    ClientOrderID: str = ""
    BuySell: int = 0
    FillPrice: float = 0.0
    FillQuantity: float = 0.0
    FreeFormText: str = ""


@dataclass
class CorrectingOrderFillResponse(
    DTCMessage, type_id=MessageType.CORRECTING_ORDER_FILL_RESPONSE
):
    ClientOrderID: str = ""
    ResultText: str = ""
    IsError: int = 0


# --- Symbol Discovery & Security Definitions ---


@dataclass
class TradeAccountsRequest(DTCMessage, type_id=MessageType.TRADE_ACCOUNTS_REQUEST):
    RequestID: int = 0


@dataclass
class TradeAccountResponse(DTCMessage, type_id=MessageType.TRADE_ACCOUNT_RESPONSE):
    TotalNumberMessages: int = 0
    MessageNumber: int = 0
    TradeAccount: str = ""
    RequestID: int = 0
    TradingIsDisabled: int = 0


@dataclass
class ExchangeListRequest(DTCMessage, type_id=MessageType.EXCHANGE_LIST_REQUEST):
    RequestID: int = 0


@dataclass
class ExchangeListResponse(DTCMessage, type_id=MessageType.EXCHANGE_LIST_RESPONSE):
    RequestID: int = 0
    Exchange: str = ""
    IsFinalMessage: int = 0
    Description: str = ""


@dataclass
class SymbolsForExchangeRequest(
    DTCMessage, type_id=MessageType.SYMBOLS_FOR_EXCHANGE_REQUEST
):
    RequestID: int = 0
    Exchange: str = ""
    SecurityType: int = 0
    RequestAction: int = 1
    Symbol: str = ""


@dataclass
class UnderlyingSymbolsForExchangeRequest(
    DTCMessage, type_id=MessageType.UNDERLYING_SYMBOLS_FOR_EXCHANGE_REQUEST
):
    RequestID: int = 0
    Exchange: str = ""
    SecurityType: int = 0


@dataclass
class SymbolsForUnderlyingRequest(
    DTCMessage, type_id=MessageType.SYMBOLS_FOR_UNDERLYING_REQUEST
):
    RequestID: int = 0
    UnderlyingSymbol: str = ""
    Exchange: str = ""
    SecurityType: int = 0


@dataclass
class SecurityDefinitionForSymbolRequest(
    DTCMessage, type_id=MessageType.SECURITY_DEFINITION_FOR_SYMBOL_REQUEST
):
    RequestID: int = 0
    Symbol: str = ""
    Exchange: str = ""


@dataclass
class SecurityDefinitionResponse(
    DTCMessage, type_id=MessageType.SECURITY_DEFINITION_RESPONSE
):
    RequestID: int = 0
    Symbol: str = ""
    Exchange: str = ""
    SecurityType: int = 0
    Description: str = ""
    MinPriceIncrement: float = 0.0
    PriceDisplayFormat: int = 0
    CurrencyValuePerIncrement: float = 0.0
    IsFinalMessage: int = 0
    FloatToIntPriceMultiplier: float = 1.0
    IntToFloatPriceDivisor: float = 1.0
    UnderlyingSymbol: str = ""
    UpdatesBidAskOnly: int = 0
    StrikePrice: float = 0.0
    PutOrCall: int = 0
    ShortInterest: int = 0
    SecurityExpirationDate: int = 0
    BuyRolloverInterest: float = 0.0
    SellRolloverInterest: float = 0.0
    EarningsPerShare: float = 0.0
    SharesOutstanding: int = 0
    IntToFloatQuantityDivisor: float = 0.0
    HasMarketDepthData: int = 1
    DisplayPriceMultiplier: float = 1.0
    ExchangeSymbol: str = ""
    InitialMarginRequirement: float = 0.0
    MaintenanceMarginRequirement: float = 0.0
    Currency: str = ""
    ContractSize: float = 0.0
    OpenInterest: int = 0
    RolloverDate: int = 0
    IsDelayed: int = 0
    SecurityIdentifier: int = 0
    ProductIdentifier: str = ""


@dataclass
class SecurityDefinitionReject(
    DTCMessage, type_id=MessageType.SECURITY_DEFINITION_REJECT
):
    RequestID: int = 0
    RejectText: str = ""


@dataclass
class SymbolSearchRequest(DTCMessage, type_id=MessageType.SYMBOL_SEARCH_REQUEST):
    RequestID: int = 0
    SearchText: str = ""
    Exchange: str = ""
    SecurityType: int = 0
    SearchType: int = 0


# --- Account Balance ---


@dataclass
class AccountBalanceRequest(DTCMessage, type_id=MessageType.ACCOUNT_BALANCE_REQUEST):
    RequestID: int = 0
    TradeAccount: str = ""


@dataclass
class AccountBalanceReject(DTCMessage, type_id=MessageType.ACCOUNT_BALANCE_REJECT):
    RequestID: int = 0
    RejectText: str = ""


@dataclass
class AccountBalanceUpdate(DTCMessage, type_id=MessageType.ACCOUNT_BALANCE_UPDATE):
    RequestID: int = 0
    CashBalance: float = 0.0
    BalanceAvailableForNewPositions: float = 0.0
    AccountCurrency: str = ""
    TradeAccount: str = ""
    SecuritiesValue: float = 0.0
    MarginRequirement: float = 0.0
    TotalNumberMessages: int = 0
    MessageNumber: int = 0
    NoAccountBalances: int = 0
    Unsolicited: int = 0
    OpenPositionsProfitLoss: float = 0.0
    DailyProfitLoss: float = 0.0
    InfoText: str = ""
    TransactionIdentifier: int = 0
    DailyNetLossLimit: float = 0.0
    TrailingAccountValueToLimitPositions: float = 0.0
    DailyNetLossLimitReached: int = 0
    IsUnderRequiredMargin: int = 0
    ClosePositionsAtEndOfDay: int = 0
    TradingIsDisabled: int = 0
    Description: str = ""
    IsUnderRequiredAccountValue: int = 0
    TransactionDateTime: int = 0
    MarginRequirementFull: float = 0.0
    MarginRequirementFullPositionsOnly: float = 0.0
    PeakMarginRequirement: float = 0.0
    IntroducingBroker: str = ""


@dataclass
class AccountBalanceAdjustment(
    DTCMessage, type_id=MessageType.ACCOUNT_BALANCE_ADJUSTMENT
):
    RequestID: int = 0
    TradeAccount: str = ""
    CreditAmount: float = 0.0
    DebitAmount: float = 0.0
    Currency: str = ""
    Reason: str = ""
    RecalculateDailyLossLimit: int = 0


@dataclass
class AccountBalanceAdjustmentReject(
    DTCMessage, type_id=MessageType.ACCOUNT_BALANCE_ADJUSTMENT_REJECT
):
    RequestID: int = 0
    RejectText: str = ""
    TradeAccount: str = ""


@dataclass
class AccountBalanceAdjustmentComplete(
    DTCMessage, type_id=MessageType.ACCOUNT_BALANCE_ADJUSTMENT_COMPLETE
):
    RequestID: int = 0
    TransactionID: int = 0
    TradeAccount: str = ""
    NewBalance: float = 0.0


@dataclass
class HistoricalAccountBalancesRequest(
    DTCMessage, type_id=MessageType.HISTORICAL_ACCOUNT_BALANCES_REQUEST
):
    RequestID: int = 0
    TradeAccount: str = ""
    StartDateTime: int = 0


@dataclass
class HistoricalAccountBalancesReject(
    DTCMessage, type_id=MessageType.HISTORICAL_ACCOUNT_BALANCES_REJECT
):
    RequestID: int = 0
    RejectText: str = ""


@dataclass
class HistoricalAccountBalanceResponse(
    DTCMessage, type_id=MessageType.HISTORICAL_ACCOUNT_BALANCE_RESPONSE
):
    RequestID: int = 0
    DateTime: float = 0.0
    CashBalance: float = 0.0
    AccountCurrency: str = ""
    TradeAccount: str = ""
    IsFinalResponse: int = 0
    NoAccountBalances: int = 0
    InfoText: str = ""
    TransactionId: str = ""


# --- Logging ---


@dataclass
class UserMessage(DTCMessage, type_id=MessageType.USER_MESSAGE):
    UserMessage: str = ""
    IsPopupMessage: int = 1


@dataclass
class GeneralLogMessage(DTCMessage, type_id=MessageType.GENERAL_LOG_MESSAGE):
    MessageText: str = ""


@dataclass
class AlertMessage(DTCMessage, type_id=MessageType.ALERT_MESSAGE):
    MessageText: str = ""
    TradeAccount: str = ""


@dataclass
class JournalEntryAdd(DTCMessage, type_id=MessageType.JOURNAL_ENTRY_ADD):
    JournalEntry: str = ""
    DateTime: int = 0


@dataclass
class JournalEntriesRequest(DTCMessage, type_id=MessageType.JOURNAL_ENTRIES_REQUEST):
    RequestID: int = 0
    StartDateTime: int = 0


@dataclass
class JournalEntriesReject(DTCMessage, type_id=MessageType.JOURNAL_ENTRIES_REJECT):
    RequestID: int = 0
    RejectText: str = ""


@dataclass
class JournalEntryResponse(DTCMessage, type_id=MessageType.JOURNAL_ENTRY_RESPONSE):
    JournalEntry: str = ""
    DateTime: int = 0
    IsFinalResponse: int = 0


# --- Historical Price Data ---


@dataclass
class HistoricalPriceDataRequest(
    DTCMessage, type_id=MessageType.HISTORICAL_PRICE_DATA_REQUEST
):
    RequestID: int = 0
    Symbol: str = ""
    Exchange: str = ""
    RecordInterval: int = 0
    StartDateTime: int = 0
    EndDateTime: int = 0
    MaxDaysToReturn: int = 0
    UseZLibCompression: int = 0
    RequestDividendAdjustedStockData: int = 0
    Integer_1: int = 0


@dataclass
class HistoricalPriceDataResponseHeader(
    DTCMessage, type_id=MessageType.HISTORICAL_PRICE_DATA_RESPONSE_HEADER
):
    RequestID: int = 0
    RecordInterval: int = 0
    UseZLibCompression: int = 0
    NoRecordsToReturn: int = 0
    IntToFloatPriceDivisor: float = 0.0


@dataclass
class HistoricalPriceDataReject(
    DTCMessage, type_id=MessageType.HISTORICAL_PRICE_DATA_REJECT
):
    RequestID: int = 0
    RejectText: str = ""
    RejectReasonCode: int = 0
    RetryTimeInSeconds: int = 0


@dataclass
class HistoricalPriceDataRecordResponse(
    DTCMessage, type_id=MessageType.HISTORICAL_PRICE_DATA_RECORD_RESPONSE
):
    RequestID: int = 0
    StartDateTime: int = 0
    OpenPrice: float = 0.0
    HighPrice: float = 0.0
    LowPrice: float = 0.0
    LastPrice: float = 0.0
    Volume: float = 0.0
    OpenInterest: int = 0
    NumTrades: int = 0
    BidVolume: float = 0.0
    AskVolume: float = 0.0
    IsFinalRecord: int = 0


@dataclass
class HistoricalPriceDataTickRecordResponse(
    DTCMessage, type_id=MessageType.HISTORICAL_PRICE_DATA_TICK_RECORD_RESPONSE
):
    RequestID: int = 0
    DateTime: float = 0.0
    AtBidOrAsk: int = 0
    Price: float = 0.0
    Volume: float = 0.0
    IsFinalRecord: int = 0


@dataclass
class HistoricalPriceDataResponseTrailer(
    DTCMessage, type_id=MessageType.HISTORICAL_PRICE_DATA_RESPONSE_TRAILER
):
    RequestID: int = 0
    FinalRecordLastDateTime: int = 0


# --- Historical Market Depth Data ---


@dataclass
class HistoricalMarketDepthDataRequest(
    DTCMessage, type_id=MessageType.HISTORICAL_MARKET_DEPTH_DATA_REQUEST
):
    RequestID: int = 0
    Symbol: str = ""
    Exchange: str = ""
    StartDateTime: int = 0
    EndDateTime: int = 0
    UseZLibCompression: int = 0
    Integer_1: int = 0


@dataclass
class HistoricalMarketDepthDataResponseHeader(
    DTCMessage, type_id=MessageType.HISTORICAL_MARKET_DEPTH_DATA_RESPONSE_HEADER
):
    RequestID: int = 0
    UseZLibCompression: int = 0
    NoRecordsToReturn: int = 0


@dataclass
class HistoricalMarketDepthDataReject(
    DTCMessage, type_id=MessageType.HISTORICAL_MARKET_DEPTH_DATA_REJECT
):
    RequestID: int = 0
    RejectText: str = ""
    RejectReasonCode: int = 0


@dataclass
class HistoricalMarketDepthDataRecordResponse(
    DTCMessage, type_id=MessageType.HISTORICAL_MARKET_DEPTH_DATA_RECORD_RESPONSE
):
    RequestID: int = 0
    StartDateTime: int = 0
    Command: int = 0
    Flags: int = 0
    NumOrders: int = 0
    Price: float = 0.0
    Quantity: int = 0
    IsFinalRecord: int = 0
