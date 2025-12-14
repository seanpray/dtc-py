from src.dtc_client import (
    DTCClient,
    Heartbeat,
    Logoff,
    LogonRequest,
    LogonStatusEnum,
    MarketDataRequest,
    MarketDataSnapshot,
    MarketDataUpdateTrade,
    MessageType,
    RequestActionEnum,
)

if __name__ == "__main__":
    client = DTCClient(host="127.0.0.1", port=11099)

    try:
        client.connect()

        logon = LogonRequest(
            Username="",
            Password="",
            HeartbeatIntervalInSeconds=10,
            ClientName="PythonClient",
        )
        client.send(logon)

        response = client.wait_for(MessageType.LOGON_RESPONSE)
        if response and response.Result == LogonStatusEnum.LOGON_SUCCESS:
            print("Logon Successful!")
            print(f"Server Name: {response.ServerName}")
        else:
            print("Logon Failed")
            exit()

        # md_req = MarketDataRequest(
        #     Symbol="ESZ5",
        #     Exchange="CME",
        #     RequestAction=RequestActionEnum.SUBSCRIBE,
        #     SymbolID=1001,
        # )
        # client.send(md_req)
        # print("Market Data Requested...")

        while True:
            msg = client.read_message()
            print(msg)
            if not msg:
                break

            if isinstance(msg, MarketDataUpdateTrade):
                print(f"Trade: Price={msg.Price} Vol={msg.Volume}")
            elif isinstance(msg, MarketDataSnapshot):
                print(f"Snapshot: Last={msg.LastTradePrice}")
            elif isinstance(msg, Heartbeat):
                print("Heartbeat received")
                # Depending on server config, you might need to send one back periodically

    except KeyboardInterrupt:
        print("Disconnecting...")
        client.send(Logoff(Reason="User Quit"))
        client.sock.close()
