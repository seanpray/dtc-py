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


@dataclass(kw_only=True)
class EncodingRequest:
    # No inheritance from DTCMessage for this one to avoid JSON confusion
    # This struct is PURE binary in the handshake phase
    ProtocolVersion: int = 8
    Encoding: int = EncodingEnum.JSON_ENCODING
    ProtocolType: str = "DTC"
    Type: int = MessageType.ENCODING_REQUEST  # ENCODING_REQUEST = None

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
        # Format: < (Little Endian) H (Size) H (Type) i (Version) i (Encoding) 4s (ProtoType) = None
        fmt = "<HHi i 4s"
        size = struct.calcsize(fmt)

        # Ensure ProtocolType is bytes and exactly 4 chars
        proto_bytes = self.ProtocolType.encode("ascii")[:4].ljust(4, b"\x00")

        return struct.pack(
            fmt, size, self.Type, self.ProtocolVersion, self.Encoding, proto_bytes
        )


@dataclass(kw_only=True)
class EncodingResponse:
    ProtocolVersion: int = 8
    Encoding: int = EncodingEnum.BINARY_ENCODING
    ProtocolType: str = "DTC"
    Type: int = MessageType.ENCODING_RESPONSE  # ENCODING_RESPONSE = None

    @classmethod
    def from_binary(cls, data: bytes) -> "EncodingResponse":
        """Unpacks the binary C++ struct into a Python object."""
        fmt = "<HHi i 4s"

        # Basic validation
        if len(data) != struct.calcsize(fmt):
            raise ValueError(f"Expected {struct.calcsize(fmt)} bytes, got {len(data)}")

        size, msg_type, version, encoding, proto_bytes = struct.unpack(fmt, data)

        if msg_type != MessageType.ENCODING_RESPONSE:  # ENCODING_RESPONSE = None
            raise ValueError(f"Expected Message Type 7, got {msg_type}")

        return cls(
            ProtocolVersion=version,
            Encoding=encoding,
            ProtocolType=proto_bytes.decode("ascii").rstrip("\x00"),
        )


@dataclass(kw_only=True)
class LogonRequest(DTCMessage, type_id=MessageType.LOGON_REQUEST):
    ProtocolVersion: int = None
    Username: str = None
    Password: str = None
    GeneralTextData: str = None
    Integer_1: int = None
    Integer_2: int = None
    HeartbeatIntervalInSeconds: int = None
    TradeAccount: str = None
    HardwareIdentifier: str = None
    ClientName: str = None
    MarketDataTransmissionInterval: int = None


@dataclass(kw_only=True)
class LogonResponse(DTCMessage, type_id=MessageType.LOGON_RESPONSE):
    ProtocolVersion: int = None
    Result: int = None
    ResultText: str = None
    ReconnectAddress: str = None
    Integer_1: int = None
    ServerName: str = None
    MarketDepthUpdatesBestBidAndAsk: int = None
    TradingIsSupported: int = None
    OCOOrdersSupported: int = None
    OrderCancelReplaceSupported: int = None
    SymbolExchangeDelimiter: str = None
    SecurityDefinitionsSupported: int = None
    HistoricalPriceDataSupported: int = None
    ResubscribeWhenMarketDataFeedAvailable: int = None
    MarketDepthIsSupported: int = None
    OneHistoricalPriceDataRequestPerConnection: int = None
    BracketOrdersSupported: int = None
    UsesMultiplePositionsPerSymbolAndTradeAccount: int = None
    MarketDataSupported: int = None


@dataclass(kw_only=True)
class Heartbeat(DTCMessage, type_id=MessageType.HEARTBEAT):
    NumDroppedMessages: int = None
    CurrentDateTime: int = None


@dataclass(kw_only=True)
class Logoff(DTCMessage, type_id=MessageType.LOGOFF):
    Reason: str = None
    DoNotReconnect: int = None


# --- Market Data ---


@dataclass(kw_only=True)
class MarketDataRequest(DTCMessage, type_id=MessageType.MARKET_DATA_REQUEST):
    RequestAction: int = None
    SymbolID: int = None
    Symbol: str = None
    Exchange: str = None
    IntervalForSnapshotUpdatesInMilliseconds: int = None


@dataclass(kw_only=True)
class MarketDataSnapshot(DTCMessage, type_id=MessageType.MARKET_DATA_SNAPSHOT):
    SymbolID: int = None
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
    MarketDepthUpdateDateTime: Optional[float] = None


@dataclass(kw_only=True)
class MarketDataUpdateTrade(DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_TRADE):
    SymbolID: int = None
    AtBidOrAsk: int = None
    Price: float = None
    Volume: float = None
    DateTime: float = None


@dataclass(kw_only=True)
class MarketDataUpdateBidAsk(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_BID_ASK
):
    SymbolID: int = None
    BidPrice: float = None
    BidQuantity: float = None
    AskPrice: float = None
    AskQuantity: float = None
    DateTime: int = None


# --- Order Entry ---


@dataclass(kw_only=True)
class SubmitNewSingleOrder(DTCMessage, type_id=MessageType.SUBMIT_NEW_SINGLE_ORDER):
    Symbol: str = None
    Exchange: str = None
    TradeAccount: str = None
    ClientOrderID: str = None
    OrderType: int = None
    BuySell: int = None
    Price1: float = None
    Price2: float = None
    Quantity: float = None
    TimeInForce: int = None
    GoodTillDateTime: int = None
    IsAutomatedOrder: int = None
    IsParentOrder: int = None
    FreeFormText: str = None
    OpenOrClose: int = None
    MaxShowQuantity: float = None
    Price1AsString: str = None
    Price2AsString: str = None
    IntendedPositionQuantity: float = None


@dataclass(kw_only=True)
class OrderUpdate(DTCMessage, type_id=MessageType.ORDER_UPDATE):
    RequestID: int = None
    TotalNumMessages: int = None
    MessageNumber: int = None
    Symbol: str = None
    Exchange: str = None
    PreviousServerOrderID: str = None
    ServerOrderID: str = None
    ClientOrderID: str = None
    ExchangeOrderID: str = None
    OrderStatus: int = None
    OrderUpdateReason: int = None
    OrderType: int = None
    BuySell: int = None
    Price1: float = None
    Price2: float = None
    TimeInForce: int = None
    GoodTillDateTime: int = None
    OrderQuantity: float = None
    FilledQuantity: float = None
    RemainingQuantity: float = None
    AverageFillPrice: float = None
    LastFillPrice: float = None
    LastFillDateTime: int = None
    LastFillQuantity: float = None
    LastFillExecutionID: str = None
    TradeAccount: str = None
    InfoText: str = None
    NoOrders: int = None
    ParentServerOrderID: str = None
    OCOLinkedOrderServerOrderID: str = None
    OpenOrClose: int = None
    PreviousClientOrderID: str = None
    FreeFormText: str = None
    OrderReceivedDateTime: int = None
    LatestTransactionDateTime: float = None
    Username: str = None


@dataclass(kw_only=True)
class MarketDataReject(DTCMessage, type_id=MessageType.MARKET_DATA_REJECT):
    SymbolID: int = None
    RejectText: str = None


@dataclass(kw_only=True)
class MarketDataFeedStatus(DTCMessage, type_id=MessageType.MARKET_DATA_FEED_STATUS):
    Status: int = None


@dataclass(kw_only=True)
class MarketDataFeedSymbolStatus(
    DTCMessage, type_id=MessageType.MARKET_DATA_FEED_SYMBOL_STATUS
):
    SymbolID: int = None
    Status: int = None


@dataclass(kw_only=True)
class TradingSymbolStatus(DTCMessage, type_id=MessageType.TRADING_SYMBOL_STATUS):
    SymbolID: int = None
    Status: int = None


@dataclass(kw_only=True)
class MarketDataUpdateTradeCompact(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_TRADE_COMPACT
):
    Price: float = None
    Volume: float = None
    DateTime: int = None
    SymbolID: int = None
    AtBidOrAsk: int = None


@dataclass(kw_only=True)
class MarketDataUpdateLastTradeSnapshot(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_LAST_TRADE_SNAPSHOT
):
    SymbolID: int = None
    LastTradePrice: float = None
    LastTradeVolume: float = None
    LastTradeDateTime: float = None


@dataclass(kw_only=True)
class MarketDataUpdateTradeWithUnbundledIndicator(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_TRADE_WITH_UNBUNDLED_INDICATOR
):
    SymbolID: int = None
    AtBidOrAsk: int = None
    UnbundledTradeIndicator: int = None
    TradeCondition: int = None
    Reserve_1: int = None
    Reserve_2: int = None
    Price: float = None
    Volume: int = None
    Reserve_3: int = None
    DateTime: float = None


@dataclass(kw_only=True)
class MarketDataUpdateTradeWithUnbundledIndicator2(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_TRADE_WITH_UNBUNDLED_INDICATOR_2
):
    SymbolID: int = None
    Price: float = None
    Volume: int = None
    DateTime: int = None
    AtBidOrAsk: int = None
    UnbundledTradeIndicator: int = None
    TradeCondition: int = None


@dataclass(kw_only=True)
class MarketDataUpdateTradeNoTimestamp(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_TRADE_NO_TIMESTAMP
):
    SymbolID: int = None
    Price: float = None
    Volume: int = None
    AtBidOrAsk: int = None
    UnbundledTradeIndicator: int = None
    TradeCondition: int = None


@dataclass(kw_only=True)
class MarketDataUpdateBidAskCompact(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_BID_ASK_COMPACT
):
    BidPrice: float = None
    BidQuantity: float = None
    AskPrice: float = None
    AskQuantity: float = None
    DateTime: int = None
    SymbolID: int = None


@dataclass(kw_only=True)
class MarketDataUpdateBidAskNoTimeStamp(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_BID_ASK_NO_TIMESTAMP
):
    SymbolID: int = None
    BidPrice: float = None
    BidQuantity: int = None
    AskPrice: float = None
    AskQuantity: int = None


@dataclass(kw_only=True)
class MarketDataUpdateBidAskFloatWithMicroseconds(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_BID_ASK_FLOAT_WITH_MICROSECONDS
):
    SymbolID: int = None
    BidPrice: float = None
    BidQuantity: float = None
    AskPrice: float = None
    AskQuantity: float = None
    DateTime: int = None


@dataclass(kw_only=True)
class MarketDataUpdateSessionOpen(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_SESSION_OPEN
):
    SymbolID: int = None
    Price: float = None
    TradingSessionDate: int = None


@dataclass(kw_only=True)
class MarketDataUpdateSessionHigh(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_SESSION_HIGH
):
    SymbolID: int = None
    Price: float = None
    TradingSessionDate: int = None


@dataclass(kw_only=True)
class MarketDataUpdateSessionLow(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_SESSION_LOW
):
    SymbolID: int = None
    Price: float = None
    TradingSessionDate: int = None


@dataclass(kw_only=True)
class MarketDataUpdateSessionVolume(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_SESSION_VOLUME
):
    SymbolID: int = None
    Volume: float = None
    TradingSessionDate: int = None
    IsFinalSessionVolume: int = None


@dataclass(kw_only=True)
class MarketDataUpdateOpenInterest(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_OPEN_INTEREST
):
    SymbolID: int = None
    OpenInterest: int = None
    TradingSessionDate: int = None


@dataclass(kw_only=True)
class MarketDataUpdateSessionSettlement(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_SESSION_SETTLEMENT
):
    SymbolID: int = None
    Price: float = None
    DateTime: int = None


@dataclass(kw_only=True)
class MarketDataUpdateSessionNumTrades(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_SESSION_NUM_TRADES
):
    SymbolID: int = None
    NumTrades: int = None
    TradingSessionDate: int = None


@dataclass(kw_only=True)
class MarketDataUpdateTradingSessionDate(
    DTCMessage, type_id=MessageType.MARKET_DATA_UPDATE_TRADING_SESSION_DATE
):
    SymbolID: int = None
    Date: int = None


@dataclass(kw_only=True)
class MarketDepthRequest(DTCMessage, type_id=MessageType.MARKET_DEPTH_REQUEST):
    RequestAction: int = None
    SymbolID: int = None
    Symbol: str = None
    Exchange: str = None
    NumLevels: int = None


@dataclass(kw_only=True)
class MarketDepthReject(DTCMessage, type_id=MessageType.MARKET_DEPTH_REJECT):
    SymbolID: int = None
    RejectText: str = None


@dataclass(kw_only=True)
class MarketDepthSnapshotLevel(
    DTCMessage, type_id=MessageType.MARKET_DEPTH_SNAPSHOT_LEVEL
):
    SymbolID: int = None
    Side: int = None
    Price: float = None
    Quantity: float = None
    Level: int = None
    IsFirstMessageInBatch: int = None
    IsLastMessageInBatch: int = None
    DateTime: float = None
    NumOrders: int = None


@dataclass(kw_only=True)
class MarketDepthSnapshotLevelFloat(
    DTCMessage, type_id=MessageType.MARKET_DEPTH_SNAPSHOT_LEVEL_FLOAT
):
    SymbolID: int = None
    Price: float = None
    Quantity: float = None
    NumOrders: int = None
    Level: int = None
    Side: int = None
    FinalUpdateInBatch: int = None


@dataclass(kw_only=True)
class MarketDepthUpdateLevel(DTCMessage, type_id=MessageType.MARKET_DEPTH_UPDATE_LEVEL):
    SymbolID: int = None
    Side: int = None
    Price: float = None
    Quantity: float = None
    UpdateType: int = None
    DateTime: float = None
    NumOrders: int = None
    FinalUpdateInBatch: int = None
    Level: int = None


@dataclass(kw_only=True)
class MarketDepthUpdateLevelFloatWithMilliseconds(
    DTCMessage, type_id=MessageType.MARKET_DEPTH_UPDATE_LEVEL_FLOAT_WITH_MILLISECONDS
):
    SymbolID: int = None
    DateTime: int = None
    Price: float = None
    Quantity: float = None
    Side: int = None
    UpdateType: int = None
    NumOrders: int = None
    FinalUpdateInBatch: int = None
    Level: int = None


@dataclass(kw_only=True)
class MarketDepthUpdateLevelNoTimestamp(
    DTCMessage, type_id=MessageType.MARKET_DEPTH_UPDATE_LEVEL_NO_TIMESTAMP
):
    SymbolID: int = None
    Price: float = None
    Quantity: float = None
    NumOrders: int = None
    Side: int = None
    UpdateType: int = None
    FinalUpdateInBatch: int = None
    Level: int = None


@dataclass(kw_only=True)
class MarketOrdersRequest(DTCMessage, type_id=MessageType.MARKET_ORDERS_REQUEST):
    RequestAction: int = None
    SymbolID: int = None
    Symbol: str = None
    Exchange: str = None
    SendQuantitiesGreaterOrEqualTo: int = None


@dataclass(kw_only=True)
class MarketOrdersReject(DTCMessage, type_id=MessageType.MARKET_ORDERS_REJECT):
    SymbolID: int = None
    RejectText: str = None


@dataclass(kw_only=True)
class MarketOrdersAdd(DTCMessage, type_id=MessageType.MARKET_ORDERS_ADD):
    SymbolID: int = None
    Side: int = None
    Quantity: int = None
    Price: float = None
    OrderID: int = None
    DateTime: int = None


@dataclass(kw_only=True)
class MarketOrdersModify(DTCMessage, type_id=MessageType.MARKET_ORDERS_MODIFY):
    SymbolID: int = None
    Side: int = None
    Quantity: int = None
    Price: float = None
    OrderID: int = None
    PriorPrice: float = None
    PriorQuantity: int = None
    PriorOrderID: int = None
    DateTime: int = None


@dataclass(kw_only=True)
class MarketOrdersRemove(DTCMessage, type_id=MessageType.MARKET_ORDERS_REMOVE):
    SymbolID: int = None
    Quantity: int = None
    Price: float = None
    OrderID: int = None
    DateTime: int = None
    Side: int = None


@dataclass(kw_only=True)
class MarketOrdersSnapshotMessageBoundary(
    DTCMessage, type_id=MessageType.MARKET_ORDERS_SNAPSHOT_MESSAGE_BOUNDARY
):
    SymbolID: int = None
    MessageBoundary: int = None


@dataclass(kw_only=True)
class SubmitFlattenPositionOrder(
    DTCMessage, type_id=MessageType.SUBMIT_FLATTEN_POSITION_ORDER
):
    Symbol: str = None
    Exchange: str = None
    TradeAccount: str = None
    ClientOrderID: str = None
    FreeFormText: str = None
    IsAutomatedOrder: int = None


@dataclass(kw_only=True)
class CancelReplaceOrder(DTCMessage, type_id=MessageType.CANCEL_REPLACE_ORDER):
    ServerOrderID: str = None
    ClientOrderID: str = None
    Price1: float = None
    Price2: float = None
    Quantity: float = None
    Price1IsSet: int = None
    Price2IsSet: int = None
    Unused: int = None
    TimeInForce: int = None
    GoodTillDateTime: int = None
    UpdatePrice1OffsetToParent: int = None
    TradeAccount: str = None
    Price1AsString: str = None
    Price2AsString: str = None


@dataclass(kw_only=True)
class CancelOrder(DTCMessage, type_id=MessageType.CANCEL_ORDER):
    ServerOrderID: str = None
    ClientOrderID: str = None
    TradeAccount: str = None


@dataclass(kw_only=True)
class SubmitNewOCOOrder(DTCMessage, type_id=MessageType.SUBMIT_NEW_OCO_ORDER):
    Symbol: str = None
    Exchange: str = None
    ClientOrderID_1: str = None
    OrderType_1: int = None
    BuySell_1: int = None
    Price1_1: float = None
    Price2_1: float = None
    Quantity_1: float = None
    ClientOrderID_2: str = None
    OrderType_2: int = None
    BuySell_2: int = None
    Price1_2: float = None
    Price2_2: float = None
    Quantity_2: float = None
    TimeInForce: int = None
    GoodTillDateTime: int = None
    TradeAccount: str = None
    IsAutomatedOrder: int = None
    ParentTriggerClientOrderID: str = None
    FreeFormText: str = None
    OpenOrClose: int = None
    PartialFillHandling: int = None
    UseOffsets: int = None
    OffsetFromParent1: float = None
    OffsetFromParent2: float = None
    MaintainSamePricesOnParentFill: int = None
    Price1_1AsString: str = None
    Price2_1AsString: str = None
    Price1_2AsString: str = None
    Price2_2AsString: str = None


@dataclass(kw_only=True)
class OpenOrdersRequest(DTCMessage, type_id=MessageType.OPEN_ORDERS_REQUEST):
    RequestID: int = None
    RequestAllOrders: int = None
    ServerOrderID: str = None
    TradeAccount: str = None


@dataclass(kw_only=True)
class OpenOrdersReject(DTCMessage, type_id=MessageType.OPEN_ORDERS_REJECT):
    RequestID: int = None
    RejectText: str = None


@dataclass(kw_only=True)
class HistoricalOrderFillsRequest(
    DTCMessage, type_id=MessageType.HISTORICAL_ORDER_FILLS_REQUEST
):
    RequestID: int = None
    ServerOrderID: str = None
    NumberOfDays: int = None
    TradeAccount: str = None
    StartDateTime: int = None


@dataclass(kw_only=True)
class HistoricalOrderFillsReject(
    DTCMessage, type_id=MessageType.HISTORICAL_ORDER_FILLS_REJECT
):
    RequestID: int = None
    RejectText: str = None


@dataclass(kw_only=True)
class HistoricalOrderFillResponse(
    DTCMessage, type_id=MessageType.HISTORICAL_ORDER_FILL_RESPONSE
):
    RequestID: int = None
    TotalNumberMessages: int = None
    MessageNumber: int = None
    Symbol: str = None
    Exchange: str = None
    ServerOrderID: str = None
    BuySell: int = None
    Price: float = None
    DateTime: int = None
    Quantity: float = None
    UniqueExecutionID: str = None
    TradeAccount: str = None
    OpenClose: int = None
    NoOrderFills: int = None
    InfoText: str = None
    HighPriceDuringPosition: float = None
    LowPriceDuringPosition: float = None
    PositionQuantity: float = None
    Username: str = None
    ExchangeOrderID: str = None
    SenderSubID: str = None


@dataclass(kw_only=True)
class CurrentPositionsRequest(
    DTCMessage, type_id=MessageType.CURRENT_POSITIONS_REQUEST
):
    RequestID: int = None
    TradeAccount: str = None


@dataclass(kw_only=True)
class CurrentPositionsReject(DTCMessage, type_id=MessageType.CURRENT_POSITIONS_REJECT):
    RequestID: int = None
    RejectText: str = None


@dataclass(kw_only=True)
class PositionUpdate(DTCMessage, type_id=MessageType.POSITION_UPDATE):
    RequestID: int = None
    TotalNumberMessages: int = None
    MessageNumber: int = None
    Symbol: str = None
    Exchange: str = None
    Quantity: float = None
    AveragePrice: float = None
    PositionIdentifier: str = None
    TradeAccount: str = None
    NoPositions: int = None
    Unsolicited: int = None
    MarginRequirement: float = None
    EntryDateTime: int = None
    OpenProfitLoss: float = None
    HighPriceDuringPosition: float = None
    LowPriceDuringPosition: float = None
    QuantityLimit: float = None
    MaxPotentialPostionQuantity: float = None


@dataclass(kw_only=True)
class AddCorrectingOrderFill(DTCMessage, type_id=MessageType.ADD_CORRECTING_ORDER_FILL):
    Symbol: str = None
    Exchange: str = None
    TradeAccount: str = None
    ClientOrderID: str = None
    BuySell: int = None
    FillPrice: float = None
    FillQuantity: float = None
    FreeFormText: str = None


@dataclass(kw_only=True)
class CorrectingOrderFillResponse(
    DTCMessage, type_id=MessageType.CORRECTING_ORDER_FILL_RESPONSE
):
    ClientOrderID: str = None
    ResultText: str = None
    IsError: int = None


@dataclass(kw_only=True)
class TradeAccountsRequest(DTCMessage, type_id=MessageType.TRADE_ACCOUNTS_REQUEST):
    RequestID: int = None


@dataclass(kw_only=True)
class TradeAccountResponse(DTCMessage, type_id=MessageType.TRADE_ACCOUNT_RESPONSE):
    TotalNumberMessages: int = None
    MessageNumber: int = None
    TradeAccount: str = None
    RequestID: int = None
    TradingIsDisabled: int = None


@dataclass(kw_only=True)
class ExchangeListRequest(DTCMessage, type_id=MessageType.EXCHANGE_LIST_REQUEST):
    RequestID: int = None


@dataclass(kw_only=True)
class ExchangeListResponse(DTCMessage, type_id=MessageType.EXCHANGE_LIST_RESPONSE):
    RequestID: int = None
    Exchange: str = None
    IsFinalMessage: int = None
    Description: str = None


@dataclass(kw_only=True)
class SymbolsForExchangeRequest(
    DTCMessage, type_id=MessageType.SYMBOLS_FOR_EXCHANGE_REQUEST
):
    RequestID: int = None
    Exchange: str = None
    SecurityType: int = None
    RequestAction: int = None
    Symbol: str = None


@dataclass(kw_only=True)
class UnderlyingSymbolsForExchangeRequest(
    DTCMessage, type_id=MessageType.UNDERLYING_SYMBOLS_FOR_EXCHANGE_REQUEST
):
    RequestID: int = None
    Exchange: str = None
    SecurityType: int = None


@dataclass(kw_only=True)
class SymbolsForUnderlyingRequest(
    DTCMessage, type_id=MessageType.SYMBOLS_FOR_UNDERLYING_REQUEST
):
    RequestID: int = None
    UnderlyingSymbol: str = None
    Exchange: str = None
    SecurityType: int = None


@dataclass(kw_only=True)
class SecurityDefinitionForSymbolRequest(
    DTCMessage, type_id=MessageType.SECURITY_DEFINITION_FOR_SYMBOL_REQUEST
):
    RequestID: int = None
    Symbol: str = None
    Exchange: str = None


@dataclass(kw_only=True)
class SecurityDefinitionResponse(
    DTCMessage, type_id=MessageType.SECURITY_DEFINITION_RESPONSE
):
    RequestID: int = None
    Symbol: str = None
    Exchange: str = None
    SecurityType: int = None
    Description: str = None
    MinPriceIncrement: float = None
    PriceDisplayFormat: int = None
    CurrencyValuePerIncrement: float = None
    IsFinalMessage: int = None
    FloatToIntPriceMultiplier: float = None
    IntToFloatPriceDivisor: float = None
    UnderlyingSymbol: str = None
    UpdatesBidAskOnly: int = None
    StrikePrice: float = None
    PutOrCall: int = None
    ShortInterest: int = None
    SecurityExpirationDate: int = None
    BuyRolloverInterest: float = None
    SellRolloverInterest: float = None
    EarningsPerShare: float = None
    SharesOutstanding: int = None
    IntToFloatQuantityDivisor: float = None
    HasMarketDepthData: int = None
    DisplayPriceMultiplier: float = None
    ExchangeSymbol: str = None
    InitialMarginRequirement: float = None
    MaintenanceMarginRequirement: float = None
    Currency: str = None
    ContractSize: float = None
    OpenInterest: int = None
    RolloverDate: int = None
    IsDelayed: int = None
    SecurityIdentifier: int = None
    ProductIdentifier: str = None


@dataclass(kw_only=True)
class SecurityDefinitionReject(
    DTCMessage, type_id=MessageType.SECURITY_DEFINITION_REJECT
):
    RequestID: int = None
    RejectText: str = None


@dataclass(kw_only=True)
class SymbolSearchRequest(DTCMessage, type_id=MessageType.SYMBOL_SEARCH_REQUEST):
    RequestID: int = None
    SearchText: str = None
    Exchange: str = None
    SecurityType: int = None
    SearchType: int = None


@dataclass(kw_only=True)
class AccountBalanceRequest(DTCMessage, type_id=MessageType.ACCOUNT_BALANCE_REQUEST):
    RequestID: int = None
    TradeAccount: str = None


@dataclass(kw_only=True)
class AccountBalanceReject(DTCMessage, type_id=MessageType.ACCOUNT_BALANCE_REJECT):
    RequestID: int = None
    RejectText: str = None


@dataclass(kw_only=True)
class AccountBalanceUpdate(DTCMessage, type_id=MessageType.ACCOUNT_BALANCE_UPDATE):
    RequestID: int = None
    CashBalance: float = None
    BalanceAvailableForNewPositions: float = None
    AccountCurrency: str = None
    TradeAccount: str = None
    SecuritiesValue: float = None
    MarginRequirement: float = None
    TotalNumberMessages: int = None
    MessageNumber: int = None
    NoAccountBalances: int = None
    Unsolicited: int = None
    OpenPositionsProfitLoss: float = None
    DailyProfitLoss: float = None
    InfoText: str = None
    TransactionIdentifier: int = None
    DailyNetLossLimit: float = None
    TrailingAccountValueToLimitPositions: float = None
    DailyNetLossLimitReached: int = None
    IsUnderRequiredMargin: int = None
    ClosePositionsAtEndOfDay: int = None
    TradingIsDisabled: int = None
    Description: str = None
    IsUnderRequiredAccountValue: int = None
    TransactionDateTime: int = None
    MarginRequirementFull: float = None
    MarginRequirementFullPositionsOnly: float = None
    PeakMarginRequirement: float = None
    IntroducingBroker: str = None


@dataclass(kw_only=True)
class AccountBalanceAdjustment(
    DTCMessage, type_id=MessageType.ACCOUNT_BALANCE_ADJUSTMENT
):
    RequestID: int = None
    TradeAccount: str = None
    CreditAmount: float = None
    DebitAmount: float = None
    Currency: str = None
    Reason: str = None
    RecalculateDailyLossLimit: int = None


@dataclass(kw_only=True)
class AccountBalanceAdjustmentReject(
    DTCMessage, type_id=MessageType.ACCOUNT_BALANCE_ADJUSTMENT_REJECT
):
    RequestID: int = None
    RejectText: str = None
    TradeAccount: str = None


@dataclass(kw_only=True)
class AccountBalanceAdjustmentComplete(
    DTCMessage, type_id=MessageType.ACCOUNT_BALANCE_ADJUSTMENT_COMPLETE
):
    RequestID: int = None
    TransactionID: int = None
    TradeAccount: str = None
    NewBalance: float = None


@dataclass(kw_only=True)
class HistoricalAccountBalancesRequest(
    DTCMessage, type_id=MessageType.HISTORICAL_ACCOUNT_BALANCES_REQUEST
):
    RequestID: int = None
    TradeAccount: str = None
    StartDateTime: int = None


@dataclass(kw_only=True)
class HistoricalAccountBalancesReject(
    DTCMessage, type_id=MessageType.HISTORICAL_ACCOUNT_BALANCES_REJECT
):
    RequestID: int = None
    RejectText: str = None


@dataclass(kw_only=True)
class HistoricalAccountBalanceResponse(
    DTCMessage, type_id=MessageType.HISTORICAL_ACCOUNT_BALANCE_RESPONSE
):
    RequestID: int = None
    DateTime: float = None
    CashBalance: float = None
    AccountCurrency: str = None
    TradeAccount: str = None
    IsFinalResponse: int = None
    NoAccountBalances: int = None
    InfoText: str = None
    TransactionId: str = None


@dataclass(kw_only=True)
class HistoricalPriceDataRequest(
    DTCMessage, type_id=MessageType.HISTORICAL_PRICE_DATA_REQUEST
):
    RequestID: int = None
    Symbol: str = None
    Exchange: str = None
    RecordInterval: int = None
    StartDateTime: int = None
    EndDateTime: int = None
    MaxDaysToReturn: int = None
    UseZLibCompression: int = None
    RequestDividendAdjustedStockData: int = None
    Integer_1: int = None


@dataclass(kw_only=True)
class HistoricalPriceDataResponseHeader(
    DTCMessage, type_id=MessageType.HISTORICAL_PRICE_DATA_RESPONSE_HEADER
):
    RequestID: int = None
    RecordInterval: int = None
    UseZLibCompression: int = None
    NoRecordsToReturn: int = None
    IntToFloatPriceDivisor: float = None


@dataclass(kw_only=True)
class HistoricalPriceDataReject(
    DTCMessage, type_id=MessageType.HISTORICAL_PRICE_DATA_REJECT
):
    RequestID: int = None
    RejectText: str = None
    RejectReasonCode: int = None
    RetryTimeInSeconds: int = None


@dataclass(kw_only=True)
class HistoricalPriceDataRecordResponse(
    DTCMessage, type_id=MessageType.HISTORICAL_PRICE_DATA_RECORD_RESPONSE
):
    RequestID: int = None
    StartDateTime: int = None
    OpenPrice: float = None
    HighPrice: float = None
    LowPrice: float = None
    LastPrice: float = None
    Volume: float = None
    # Union handled by including both fields as optional/standard
    OpenInterest: int = None
    NumTrades: int = None
    BidVolume: float = None
    AskVolume: float = None
    IsFinalRecord: int = None


@dataclass(kw_only=True)
class HistoricalPriceDataTickRecordResponse(
    DTCMessage, type_id=MessageType.HISTORICAL_PRICE_DATA_TICK_RECORD_RESPONSE
):
    RequestID: int = None
    DateTime: float = None
    AtBidOrAsk: int = None
    Price: float = None
    Volume: float = None
    IsFinalRecord: int = None


@dataclass(kw_only=True)
class HistoricalPriceDataResponseTrailer(
    DTCMessage, type_id=MessageType.HISTORICAL_PRICE_DATA_RESPONSE_TRAILER
):
    RequestID: int = None
    FinalRecordLastDateTime: int = None


@dataclass(kw_only=True)
class HistoricalMarketDepthDataRequest(
    DTCMessage, type_id=MessageType.HISTORICAL_MARKET_DEPTH_DATA_REQUEST
):
    RequestID: int = None
    Symbol: str = None
    Exchange: str = None
    StartDateTime: int = None
    EndDateTime: int = None
    UseZLibCompression: int = None
    Integer_1: int = None


@dataclass(kw_only=True)
class HistoricalMarketDepthDataResponseHeader(
    DTCMessage, type_id=MessageType.HISTORICAL_MARKET_DEPTH_DATA_RESPONSE_HEADER
):
    RequestID: int = None
    UseZLibCompression: int = None
    NoRecordsToReturn: int = None


@dataclass(kw_only=True)
class HistoricalMarketDepthDataReject(
    DTCMessage, type_id=MessageType.HISTORICAL_MARKET_DEPTH_DATA_REJECT
):
    RequestID: int = None
    RejectText: str = None
    RejectReasonCode: int = None


@dataclass(kw_only=True)
class HistoricalMarketDepthDataRecordResponse(
    DTCMessage, type_id=MessageType.HISTORICAL_MARKET_DEPTH_DATA_RECORD_RESPONSE
):
    RequestID: int = None
    StartDateTime: int = None
    Command: int = None
    Flags: int = None
    NumOrders: int = None
    Price: float = None
    Quantity: int = None
    IsFinalRecord: int = None


@dataclass(kw_only=True)
class UserMessage(DTCMessage, type_id=MessageType.USER_MESSAGE):
    UserMessage: str = None
    IsPopupMessage: int = None


@dataclass(kw_only=True)
class GeneralLogMessage(DTCMessage, type_id=MessageType.GENERAL_LOG_MESSAGE):
    MessageText: str = None


@dataclass(kw_only=True)
class AlertMessage(DTCMessage, type_id=MessageType.ALERT_MESSAGE):
    MessageText: str = None
    TradeAccount: str = None


@dataclass(kw_only=True)
class JournalEntryAdd(DTCMessage, type_id=MessageType.JOURNAL_ENTRY_ADD):
    JournalEntry: str = None
    DateTime: int = None


@dataclass(kw_only=True)
class JournalEntriesRequest(DTCMessage, type_id=MessageType.JOURNAL_ENTRIES_REQUEST):
    RequestID: int = None
    StartDateTime: int = None


@dataclass(kw_only=True)
class JournalEntriesReject(DTCMessage, type_id=MessageType.JOURNAL_ENTRIES_REJECT):
    RequestID: int = None
    RejectText: str = None


@dataclass(kw_only=True)
class JournalEntryResponse(DTCMessage, type_id=MessageType.JOURNAL_ENTRY_RESPONSE):
    JournalEntry: str = None
    DateTime: int = None
    IsFinalResponse: int = None
