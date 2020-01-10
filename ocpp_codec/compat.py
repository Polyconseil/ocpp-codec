# Copyright (c) Polyconseil SAS. All rights reserved.
"""Utilities to handle different versions of OCPP."""
import enum
import typing

from ocpp_codec import errors
from ocpp_codec.v16.messages import IMPLEMENTED as IMPLEMENTED_v16
from ocpp_codec.v20.messages import IMPLEMENTED as IMPLEMENTED_v20


class OcppJsonProtocol(enum.Enum):
    v16 = 16
    v20 = 20


def get_implemented_messages(protocol: OcppJsonProtocol) -> typing.Dict[
    str, typing.Union[messages_v16.Action, messages_v20.Action]
]:
    return {
        OcppJsonProtocol.v16: IMPLEMENTED_v16,
        OcppJsonProtocol.v20: IMPLEMENTED_v20,
    }[protocol]


def get_rpc_framework_error(msg: str, protocol: OcppJsonProtocol) -> errors.BaseOCPPError:
    if protocol is OcppJsonProtocol.v20:
        return errors.RpcFrameworkError(msg)
    return errors.GenericError(msg)


def get_message_type_not_supported_error(msg: str, protocol: OcppJsonProtocol) -> errors.BaseOCPPError:
    if protocol is OcppJsonProtocol.v20:
        return errors.MessageTypeNotSupportedError(msg)
    return errors.GenericError(msg)
