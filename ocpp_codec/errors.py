# Copyright (c) Polyconseil SAS. All rights reserved.
"""This module contains OCPP error codes as Python exceptions.

These errors are representations of OCPP error codes, as specified in
OCPP JSON specification, section 4.2.3 (v16) or 4.3 (v20).
"""
from ocpp_codec import types


class BaseOCPPError(Exception):
    """Base error all OCPP errors should inherit from.

    Attributes:
        - msg: str, an error message
        - details: dict, a dict of error details in an unspecified format
        - code: specification.types.ErrorCodeEnum, the enum value the class represents
    """
    # The ErrorCodeEnum value that should be used as the 'code' of this exception, useful when the class name doesn't
    # match the enum value.
    __error_code_name__ = None

    def __init__(self, msg, *args, **kwargs):
        super().__init__(msg, *args)

        self.msg = msg
        self.details = kwargs

        # Get a reference to the proper enum value to ease CallError messages construction. Most classes are named
        # according to ErrorCodeEnum values, but in order to respect Python exception naming convention (i.e.: suffixing
        # them with 'Error'), some don't. Instead, they provide the correct enum value through __error_code_name__.
        # The class name or __error_code_name__ must be found in the ErrorCodeEnum enum, or a ValueError will be raised.
        self.code = types.ErrorCodeEnum(self.__error_code_name__ or self.__class__.__name__)


# Conflicts with Python builtin, but other modules access this through this module (i.e.: errors.NotImplementedError),
# and since we don't raise it from this module, no conflicts should occur
class NotImplementedError(BaseOCPPError):  # pylint: disable=redefined-builtin
    """Raised when the action is unknown to our server."""
    __error_code_name__ = 'NotImplemented'


class NotSupportedError(BaseOCPPError):
    """Raised when the action is not supported by our server."""
    __error_code_name__ = 'NotSupported'


class ProtocolError(BaseOCPPError):
    """Raised when payload is incomplete."""


class PropertyConstraintViolationError(BaseOCPPError):
    """Raised when a field contains an invalid value."""
    __error_code_name__ = 'PropertyConstraintViolation'


class TypeConstraintViolationError(BaseOCPPError):
    """Raised when a field violates a data type constraint."""
    __error_code_name__ = 'TypeConstraintViolation'


class GenericError(BaseOCPPError):
    """Raised when there aren't any other more appropriate error."""


# OCPP v20 only
class MessageTypeNotSupportedError(BaseOCPPError):
    """Raised when the message type number of a message is unknown or not supported."""
    __error_code_name__ = 'MessageTypeNotSupported'


class RpcFrameworkError(BaseOCPPError):
    """Raised when the message isn't a valid RPC request (e.g.: can't read the message type id)."""
