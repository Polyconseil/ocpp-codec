# Copyright (c) Polyconseil SAS. All rights reserved.
"""OCPP base typing elements common to all versions of the protocol."""
import enum

from ocpp_codec import utils


class OCPPType:
    """Base OCPP type, inherited by all others.

    Fields defined by inheriting dataclasses should be typed according to the JSON representation of the object. If the
    object is a datetime transmitted as a string, then the field should be typed as 'str' and not 'datetime.datetime'.
    The type is used to check we received the correct type from the remote connection, and that the associated validator
    returned the correct type before sending back a message.
    """


class SimpleType(OCPPType):
    """A type mapping directly to a Python type.

    These types represent the base building blocks of OCPP. They're used to make the message definition more
    understandable, and avoid repetitions.

    Simple types should define a single field, whose type will be used to match data against.

    The name of the field doesn't matter, as dataclass fields cannot be indexed by their name. The first defined field
    of the 'SimpleType' will be used.

    Example:

        @dataclass
        class CiString20Type(SimpleType):
            value: str = field(metadata={'validators': [validators.max_length_20]})

        When used as part of another type, CiString20Type is expected to be a string of length 20.
    """


class ComplexType(OCPPType):
    """A type composed of several 'SimpleType' fields.

    These types represent the more elaborate OCPP types.

    Example:

        @dataclass
        class IdTagInfo(ComplexType):
            expiryDate: DateTime
            parentIdTag: IdToken
            status: AuthorizationStatus
    """


class ErrorCodeEnum(utils.AutoNameEnum):
    """Every error codes we can encounter when exchanging OCPP messages.

    This enum isn't versioned based on OCPP protocol version because v20 only adds a few extra errors. It makes the
    serializer code simpler not having to wonder for which protocol version we're handling errors. We just have to be
    careful not to raise unsupported errors.

    Otherwise, we'd have to propagate the protocol version to modules that can raise errors (e.g.: validators.py, itself
    used by structure.py) and it quickly becomes a mess.
    """
    NotImplemented = enum.auto()
    NotSupported = enum.auto()
    InternalError = enum.auto()
    ProtocolError = enum.auto()
    SecurityError = enum.auto()
    FormationViolation = enum.auto()
    PropertyConstraintViolation = enum.auto()
    OccurenceConstraintViolation = enum.auto()
    TypeConstraintViolation = enum.auto()
    GenericError = enum.auto()
    # OCPP v20 only
    FormatViolation = enum.auto()  # slight change in meaning from FormationViolation
    MessageTypeNotSupported = enum.auto()
    RpcFrameworkError = enum.auto()
