# Copyright (c) Polyconseil SAS. All rights reserved.
"""Utilities to handle different versions of OCPP."""
import enum
import typing

from ocpp_codec import errors
from ocpp_codec.v16 import messages as messages_v16
from ocpp_codec.v20 import messages as messages_v20


class OcppJsonProtocol(enum.Enum):
    v16 = 16
    v20 = 20


def get_implemented_messages(protocol: OcppJsonProtocol) -> typing.Dict[
    str, typing.Union[messages_v16.Action, messages_v20.Action]
]:
    return {
        OcppJsonProtocol.v16: messages_v16.IMPLEMENTED,
        OcppJsonProtocol.v20: messages_v20.IMPLEMENTED,
    }[protocol]


def get_rpc_framework_error(msg: str, protocol: OcppJsonProtocol) -> errors.BaseOCPPError:
    if protocol is OcppJsonProtocol.v20:
        return errors.RpcFrameworkError(msg)
    return errors.GenericError(msg)


def get_message_type_not_supported_error(msg: str, protocol: OcppJsonProtocol) -> errors.BaseOCPPError:
    if protocol is OcppJsonProtocol.v20:
        return errors.MessageTypeNotSupportedError(msg)
    return errors.GenericError(msg)


def get_request_payload_dataclass(action: typing.Union[messages_v16.Action, messages_v20.Action]):
    if issubclass(action, messages_v20.Action):
        return action.Request
    return action.req


def get_response_payload_dataclass(action: typing.Union[messages_v16.Action, messages_v20.Action]):
    if issubclass(action, messages_v20.Action):
        return action.Response
    return action.conf
