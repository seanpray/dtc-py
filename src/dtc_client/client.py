import json
import socket
import time
from collections import deque
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
    def __init__(self, host: str = "127.0.0.1", port: int = 11099):
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False
        self.encoding = EncodingEnum.BINARY_ENCODING  # Default start state

        # Buffers
        self._buffer = b""
        self._message_queue = deque()

    def connect(self):
        """
        1. Connects to socket.
        2. Sends Binary Encoding Request.
        3. Receives Binary Encoding Response.
        4. Switches mode to JSON.
        """
        print(f"Connecting to {self.host}:{self.port}...")
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
            raise Exception(f"Server refused JSON encoding. Returned: {resp.Encoding}")

        print(
            f"Handshake Complete. Protocol Version: {resp.ProtocolVersion}. Switched to JSON."
        )

        self.connected = True
        self.encoding = EncodingEnum.JSON_ENCODING
        self.sock.settimeout(None)  # Reset timeout to blocking or handle differently

    def _recv_exact(self, n: int) -> bytes:
        """Helper to receive exactly n bytes (blocking)."""
        data = b""
        while len(data) < n:
            chunk = self.sock.recv(n - len(data))
            if not chunk:
                break
            data += chunk
        return data

    def send(self, message: DTCMessage):
        """Serializes and sends a DTCMessage (JSON mode)."""
        if not self.connected:
            raise Exception("Not connected")

        # We assume JSON encoding now
        json_data = message.to_json()
        # print(f"Sending: {json_data}") # Debug logging
        self.sock.sendall(json_data)

    def _read_socket(self):
        """Reads stream, parses JSON messages separated by null bytes."""
        try:
            # Read chunk
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

        except socket.error as e:
            print(f"Socket Error: {e}")
            self.connected = False

    def read_message(self, timeout=None) -> Optional[DTCMessage]:
        """
        Returns the next message from the queue.
        Reads from socket if queue is empty.
        """
        start_time = time.time()

        while self.connected:
            if self._message_queue:
                return self._message_queue.popleft()

            # If queue is empty, try to read more from socket
            self.sock.settimeout(1.0)  # Short timeout for loop check
            try:
                self._read_socket()
            except socket.timeout:
                pass
            except ConnectionError:
                return None

            if timeout and (time.time() - start_time > timeout):
                return None

        return None

    def wait_for(self, message_type: MessageType, timeout=5.0) -> Optional[DTCMessage]:
        """
        'Serial' helper.
        Waits specifically for a message of 'message_type'.
        Any other messages received in the meantime (e.g. Heartbeats) are ignored
        or handled (here just printed/queued could be an option).

        Note: In a production app, you might want to callback/queue the skipped messages.
        """
        start_time = time.time()
        skipped_messages = []
        found_msg = None

        while time.time() - start_time < timeout:
            msg = self.read_message(timeout=1.0)
            if not msg:
                continue

            if msg.Type == message_type:
                found_msg = msg
                break
            elif msg.Type == MessageType.HEARTBEAT:
                # Auto-reply to heartbeats? Usually client sends them on timer.
                # But here we just ignore incoming heartbeats during a specific wait
                pass
            else:
                print(f"Received async message while waiting: {msg}")
                # Ideally, put back in a secondary queue or handle via callback
                # For now, we unfortunately drop it or store it if you prefer

        return found_msg

    def heartbeat_loop(self):
        """Simple helper to send heartbeats if you were threading this."""
        hb = Heartbeat()
        self.send(hb)
