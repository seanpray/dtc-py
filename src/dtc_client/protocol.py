import struct
from dataclasses import dataclass
from typing import Optional

from .constants import (
    CURRENT_VERSION,
    BuySellEnum,
    EncodingEnum,
    LogonStatusEnum,
    MessageType,
    OrderTypeEnum,
    RequestActionEnum,
    TimeInForceEnum,
)
from .message import DTCMessage


@dataclass
class EncodingRequest:
    # No inheritance from DTCMessage for this one to avoid JSON confusion
    # This struct is PURE binary in the handshake phase
    ProtocolVersion: int = 8  # CURRENT_VERSION
    Encoding: int = EncodingEnum.JSON_ENCODING
    ProtocolType: str = "DTC"
    Type: int = MessageType.ENCODING_REQUEST  # ENCODING_REQUEST

    def to_binary(self) -> bytes:
        """
        Packs the class into the C++ struct binary format.
        struct s_EncodingRequest {
            uint16_t Size;
            uint16_t Type;
            int32_t ProtocolVersion;
            EncodingEnum Encoding;
            char ProtocolType[4];
        };
        """
        # Format: < (Little Endian) H (Size) H (Type) i (Version) i (Encoding) 4s (ProtoType)
        fmt = "<HHi i 4s"
        size = struct.calcsize(fmt)

        # Ensure ProtocolType is bytes and exactly 4 chars
        proto_bytes = self.ProtocolType.encode("ascii")[:4].ljust(4, b"\x00")

        return struct.pack(
            fmt, size, self.Type, self.ProtocolVersion, self.Encoding, proto_bytes
        )


@dataclass
class EncodingResponse:
    ProtocolVersion: int = 8
    Encoding: int = EncodingEnum.BINARY_ENCODING
    ProtocolType: str = "DTC"
    Type: int = MessageType.ENCODING_RESPONSE  # ENCODING_RESPONSE

    @classmethod
    def from_binary(cls, data: bytes) -> "EncodingResponse":
        """Unpacks the binary C++ struct into a Python object."""
        fmt = "<HHi i 4s"

        # Basic validation
        if len(data) != struct.calcsize(fmt):
            raise ValueError(f"Expected {struct.calcsize(fmt)} bytes, got {len(data)}")

        size, msg_type, version, encoding, proto_bytes = struct.unpack(fmt, data)

        if msg_type != MessageType.ENCODING_RESPONSE:  # ENCODING_RESPONSE
            raise ValueError(f"Expected Message Type 7, got {msg_type}")

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
class MarketDataUpdateBidAsk(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_BID_ASK
):
    SymbolID: int = 0
    BidPrice: float = 0.0
    BidQuantity: float = 0.0
    AskPrice: float = 0.0
    AskQuantity: float = 0.0
    DateTime: int = 0


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


@dataclass
class MarketDataReject(DTCMessage, type_id=MessageType.MARKET_DATA_REJECT):
    SymbolID: int = 0
    RejectText: str = ""


@dataclass
class MarketDataFeedStatus(DTCMessage, type_id=MessageType.MARKET_DATA_FEED_STATUS):
    Status: int = 0  # MarketDataFeedStatusEnum


@dataclass
class MarketDataFeedSymbolStatus(
    DTCMessage, type_id=MessageType.MARKET_DATA_FEED_SYMBOL_STATUS
):
    SymbolID: int = 0
    Status: int = 0  # MarketDataFeedStatusEnum


@dataclass
class TradingSymbolStatus(DTCMessage, type_id=MessageType.TRADING_SYMBOL_STATUS):
    SymbolID: int = 0
    Status: int = 0  # TradingStatusEnum


@dataclass
class MarketDataUpdateTradeCompact(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_TRADE_COMPACT
):
    Price: float = 0.0
    Volume: float = 0.0
    DateTime: int = 0
    SymbolID: int = 0
    AtBidOrAsk: int = 0  # AtBidOrAskEnum


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
    DateTime: int = 0  # MicrosecondsInt
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
    DateTime: int = 0  # MicrosecondsInt


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
    Side: int = 0  # AtBidOrAskEnum
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
    UpdateType: int = 0  # MarketDepthUpdateTypeEnum
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
    SecurityType: int = 0  # SecurityTypeEnum
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
    PriceDisplayFormat: int = 0  # PriceDisplayFormatEnum
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


@dataclass
class HistoricalPriceDataRequest(
    DTCMessage, type_id=MessageType.HISTORICAL_PRICE_DATA_REQUEST
):
    RequestID: int = 0
    Symbol: str = ""
    Exchange: str = ""
    RecordInterval: int = 0  # HistoricalDataIntervalEnum
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
    StartDateTime: int = 0  # MicrosecondsInt
    OpenPrice: float = 0.0
    HighPrice: float = 0.0
    LowPrice: float = 0.0
    LastPrice: float = 0.0
    Volume: float = 0.0
    # Union handled by including both fields as optional/standard
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
