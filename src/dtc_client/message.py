import dataclasses
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional, Type

# Registry to map Type ID back to Class
MESSAGE_MAP: Dict[int, Type["DTCMessage"]] = {}


@dataclass
class DTCMessage:
    """Base class for all DTC messages."""

    def __init_subclass__(cls, type_id: int, **kwargs):
        """Auto-register subclasses into the MESSAGE_MAP."""
        super().__init_subclass__(**kwargs)
        if type_id is not None:
            MESSAGE_MAP[type_id] = cls
            # Inject the Type field automatically so instances have it
            cls.Type = type_id

    def to_json(self) -> bytes:
        """
        Converts the dataclass to a JSON string bytes with NULL terminator.
        Removes keys with None values to keep payload small.
        IMPORTANT: Type field must be first for Sierra Chart compatibility.
        """
        # Convert dataclass to dict
        data = asdict(self)

        # Get the Type value
        type_value = data.get("Type") or getattr(self, "Type", 0)
        
        # Remove 'Size' if it exists (only for binary)
        data.pop("Size", None)

        # Filter out None values
        clean_data = {k: v for k, v in data.items() if v is not None}

        # Create new dict with Type first (required by Sierra Chart)
        ordered_data = {"Type": type_value}
        ordered_data.update({k: v for k, v in clean_data.items() if k != "Type"})

        # Serialize to JSON and append null terminator
        # Use ASCII encoding as required by Sierra Chart DTC protocol
        return (json.dumps(ordered_data) + "\x00").encode("ascii")

    @staticmethod
    def from_json(json_bytes: bytes) -> "DTCMessage":
        """Parses a JSON byte string into the specific DTCMessage subclass."""
        # Strip null terminator if present
        if json_bytes.endswith(b"\x00"):
            json_bytes = json_bytes[:-1]

        data = json.loads(json_bytes)
        msg_type = data.get("Type")

        if msg_type in MESSAGE_MAP:
            cls = MESSAGE_MAP[msg_type]
            # Filter the dict to only keys that exist in the dataclass fields
            # to prevent errors if the server sends extra fields (forward compatibility)
            valid_keys = {f.name for f in dataclasses.fields(cls)}
            filtered_data = {k: v for k, v in data.items() if k in valid_keys}
            return cls(**filtered_data)
        else:
            # Fallback for unknown messages
            return GenericDTCMessage(**data)


@dataclass
class GenericDTCMessage(DTCMessage, type_id=None):
    """Fallback for messages we haven't implemented definitions for yet."""

    Type: int

    def __post_init__(self):
        # Allow dynamic attributes for generic messages
        pass
