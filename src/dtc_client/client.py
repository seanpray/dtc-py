import json
import socket
import time
from collections import deque
from threading import Thread, Lock
from time import sleep
from typing import Optional

from .protocol import (
    DTCMessage,
    EncodingEnum,
    EncodingRequest,
    EncodingResponse,
    Heartbeat,
    MessageType,
)


class DTCClient:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 11099,
        heartbeat_interval_sec: int = 10,
    ):
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False
        self.encoding = EncodingEnum.BINARY_ENCODING  # Default start state
        self.heartbeat_interval_sec = heartbeat_interval_sec
        # this must increment unique ids
        self.current_request_id = 1
        self.current_order_id = 1  # For unique ClientOrderID generation

        # Thread safety lock for socket operations
        self._socket_lock = Lock()

        # Buffers
        self._buffer = b""
        self._message_queue = deque()

        # Start heartbeat thread (will wait for connection)
        self.heartbeat_thread = Thread(target=self.heartbeat_loop)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()

    def connect(self):
        """
        1. Connects to socket.
        2. Sends Binary Encoding Request.
        3. Receives Binary Encoding Response.
        4. Switches mode to JSON.
        """
        print(f"Connecting to {self.host}:{self.port}...")
        with self._socket_lock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5.0)  # Set timeout for handshake
            self.sock.connect((self.host, self.port))

            # --- Step 1: Binary Handshake ---
            print("Performing Binary Encoding Handshake...")

            # Create and Send Request
            req = EncodingRequest(Encoding=EncodingEnum.JSON_ENCODING)
            bin_data = req.to_binary()
            self.sock.sendall(bin_data)

            # Receive Fixed-Size Response (16 bytes)
            # We read exactly 16 bytes because s_EncodingResponse is fixed size
            response_data = self._recv_exact(16)

            if not response_data:
                raise ConnectionError("Failed to receive Encoding Response")

            resp = EncodingResponse.from_binary(response_data)

            if resp.Encoding != EncodingEnum.JSON_ENCODING:
                raise Exception(
                    f"Server refused JSON encoding. Returned: {resp.Encoding}"
                )

            print(
                f"Handshake Complete. Protocol Version: {resp.ProtocolVersion}. Switched to JSON."
            )

            self.encoding = EncodingEnum.JSON_ENCODING
            # Set socket to non-blocking mode with a reasonable timeout
            self.sock.settimeout(0.5)  # 500ms timeout for reads

        # Mark as connected AFTER lock is released so heartbeat can start
        self.connected = True
        print("[DTC] Connection established, heartbeat thread active")

    def _recv_exact(self, n: int) -> bytes:
        """Helper to receive exactly n bytes (blocking)."""
        data = b""
        while len(data) < n:
            chunk = self.sock.recv(n - len(data))
            if not chunk:
                break
            data += chunk
        return data

    def send(
        self,
        message: DTCMessage,
        set_request_id: bool = False,
        set_order_id: bool = False,
    ):
        """Serializes and sends a DTCMessage (JSON mode)."""
        if not self.connected:
            raise Exception("Not connected")

        if set_request_id and hasattr(message, "RequestID"):
            message.RequestID = self.current_request_id
            self.current_request_id += 1

        if set_order_id and hasattr(message, "ClientOrderID"):
            # Generate unique ClientOrderID
            message.ClientOrderID = (
                f"ORDER_{int(time.time() * 1000)}_{self.current_order_id}"
            )
            self.current_order_id += 1

        # We assume JSON encoding now
        json_data = message.to_json()

        with self._socket_lock:
            if not self.connected:
                raise ConnectionError("Connection lost before send")
            try:
                self.sock.sendall(json_data)
            except socket.error as e:
                self.connected = False
                raise ConnectionError(f"Failed to send message: {e}")

    def _read_socket(self):
        """Reads stream, parses JSON messages separated by null bytes."""
        try:
            # Read chunk with lock
            with self._socket_lock:
                if not self.connected:
                    return
                chunk = self.sock.recv(4096)

            if not chunk:
                self.connected = False
                raise ConnectionError("Socket closed")

            self._buffer += chunk

            # JSON Logic: Split by null terminator
            while b"\x00" in self._buffer:
                msg_data, self._buffer = self._buffer.split(b"\x00", 1)
                if msg_data:
                    try:
                        parsed = DTCMessage.from_json(msg_data)
                        self._message_queue.append(parsed)
                    except Exception as e:
                        print(f"JSON Decode Error: {e} | Data: {msg_data}")

        except socket.timeout:
            # Timeout is normal, just return
            pass
        except socket.error as e:
            if self.connected:  # Only print if we weren't already disconnected
                print(f"Socket Error: {e}")
            self.connected = False

    def read_message(self, timeout=None) -> Optional[DTCMessage]:
        """
        Returns the next message from the queue.
        Reads from socket if queue is empty.
        """
        start_time = time.time()
        timeout = 15.0 if timeout is None else timeout

        while self.connected:
            if self._message_queue:
                return self._message_queue.popleft()

            # If queue is empty, try to read more from socket
            try:
                self._read_socket()
            except ConnectionError:
                return None

            if timeout and (time.time() - start_time > timeout):
                return None

            # Small sleep to prevent busy waiting
            time.sleep(0.01)

        return None

    def wait_for(self, message_type: MessageType, timeout=5.0) -> Optional[DTCMessage]:
        """
        'Serial' helper.
        Waits specifically for a message of 'message_type'.
        Any other messages received in the meantime (e.g. Heartbeats) are ignored
        or handled (here just printed/queued could be an option).
        """
        start_time = time.time()
        skipped_messages = []
        found_msg = None

        while time.time() - start_time < timeout:
            msg = self.read_message(timeout)
            if not msg:
                continue

            if msg.Type == message_type:
                found_msg = msg
                break
            elif msg.Type == MessageType.HEARTBEAT:
                pass
            else:
                pass
                # self._message_queue.extend(msg)

        return found_msg

    def heartbeat_loop(self):
        """Background thread that sends periodic heartbeats to keep connection alive."""
        while True:
            sleep(self.heartbeat_interval_sec)
            if self.connected:
                try:
                    hb = Heartbeat()
                    self.send(hb, set_request_id=False)
                except Exception as e:
                    print(f"[HEARTBEAT] Failed to send heartbeat: {e}")
                    self.connected = False
                    break

    def disconnect(self):
        """Cleanly disconnect from the server."""
        self.connected = False
        with self._socket_lock:
            if self.sock:
                try:
                    self.sock.close()
                except:
                    pass
                self.sock = None
        print("[DTC] Disconnected")
