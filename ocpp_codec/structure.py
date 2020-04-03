# Copyright (c) Polyconseil SAS. All rights reserved.
"""OCPP common message structure.

This module implements elements specified in OCPP 1.6 JSON specification, section 4.
"""
from dataclasses import dataclass
from dataclasses import field
import enum

from ocpp_codec import encoders
from ocpp_codec import types
from ocpp_codec import validators


class MessageTypeEnum(enum.Enum):
    CALL = 2
    CALLRESULT = 3
    CALLERROR = 4


@dataclass
class MessageType(types.SimpleType):
    """Field type coercing an integer to a MessageTypeEnum."""
    value: int = field(metadata={'encoder': encoders.EnumEncoder(MessageTypeEnum)})


@dataclass
class ErrorCode(types.SimpleType):
    """Field type coercing a string to a ErrorCodeEnum."""
    value: str = field(metadata={'encoder': encoders.EnumEncoder(types.ErrorCodeEnum)})


@dataclass
class OCPPMessage:
    """Base class every OCPP message should inherit from."""
    messageTypeId: MessageType = field(init=False)  # Let subclasses define that field
    uniqueId: str = field(metadata={'validators': validators.max_length_36})


@dataclass
class Call(OCPPMessage):
    """Representation of a Call message.

    The 'payload' field isn't enforced to a specific type as its parsing relies on the value of 'action'.
    """
    messageTypeId = MessageTypeEnum.CALL
    action: str
    payload: dict


@dataclass
class CallResult(OCPPMessage):
    """Representation of a CallResult message.

    The 'payload' field isn't enforced to a specific type as its parsing relies on the value of the associated request's
    'action'.
    """
    messageTypeId = MessageTypeEnum.CALLRESULT
    payload: dict


@dataclass
class CallError(OCPPMessage):
    """Representation of a CallResult message."""
    messageTypeId = MessageTypeEnum.CALLERROR
    errorCode: ErrorCode
    errorDescription: str
    errorDetails: dict
