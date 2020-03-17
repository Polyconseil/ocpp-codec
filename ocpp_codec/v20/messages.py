# Copyright (c) Polyconseil SAS. All rights reserved.
"""OCPP messages definitions.

This module implements elements specified in OCPP 2.0 specification, section Messages.

Attributes:
    - IMPLEMENTED: dict, a mapping from action name to action classes for every implemented OCPP actions.
"""
from dataclasses import dataclass
import inspect
import sys
import typing

from . import types


class ActionMetaClass(type):
    """Simple metaclass that inserts a reference to the englobing 'Action' class inside nested Request/Response classes.

    This makes 'Action.Request' and 'Action.Response' classes able to know which 'Action' they refer to.
    """

    def __new__(cls, class_name, bases, attrs, **kwargs):
        klass = super().__new__(cls, class_name, bases, attrs)

        # Insert reference to the 'Action' class in both 'Action.Request' and 'Action.Response'
        setattr(klass.Request, '_action_class', klass)
        setattr(klass.Response, '_action_class', klass)

        return klass


class Action(metaclass=ActionMetaClass):
    """Base class representing an OCPP action.

    This indinstinctly represents messages coming from the charge point as well as messages coming from the central
    system.
    """

    @dataclass
    class Request:
        """Base class representing the request part of the message."""

    @dataclass
    class Response:
        """Base class representing the response part of the message."""



class Authorize(Action):
    @dataclass
    class Request:
        idToken: types.IdTokenType

        evseId: typing.List[int] = None
        certificateHashData: typing.List[types.OCSPRequestDataType] = types.ListCard4Field(default=None)

    @dataclass
    class Response:
        idTokenInfo: types.IdTokenInfoType

        certificateStatus: types.CertificateStatusEnumType = None
        evseId: typing.List[int] = None


class BootNotification(Action):
    @dataclass
    class Request:
        reason: types.BootReasonEnumType
        chargingStation: types.ChargingStationType

    @dataclass
    class Response:
        currentTime: types.DateTime
        interval: int
        status: types.RegistrationStatusEnumType


class ChangeAvailability(Action):
    @dataclass
    class Request:
        evseId: int
        operationalStatus: types.OperationalStatusEnumType

    @dataclass
    class Response:
        status: types.ChangeAvailabilityStatusEnumType


class GetVariables(Action):
    @dataclass
    class Request:
        getVariableData: typing.List[types.GetVariableDataType]

    @dataclass
    class Response:
        getVariableResult: typing.List[types.GetVariableResultType]


class Heartbeat(Action):
    @dataclass
    class Request:
        pass

    @dataclass
    class Response:
        currentTime: types.DateTime


class SetVariables(Action):
    @dataclass
    class Request:
        setVariableData: typing.List[types.SetVariableDataType]

    @dataclass
    class Response:
        setVariableResult: typing.List[types.SetVariableResultType]


class StatusNotification(Action):
    @dataclass
    class Request:
        timestamp: types.DateTime
        connectorStatus: types.ConnectorStatusEnumType
        evseId: int
        connectorId: int

    @dataclass
    class Response:
        pass


class TransactionEvent(Action):
    @dataclass
    class Request:
        eventType: types.TransactionEventEnumType
        timestamp: types.DateTime
        triggerReason: types.TriggerReasonEnumType
        seqNo: int
        transactionData: types.TransactionType

        offline: bool = None
        numberOfPhasesUsed: int = None
        cableMaxCurrent: types.Decimal = None
        reservationId: int = None
        idToken: types.IdTokenType = None
        evse: types.EVSEType = None
        meterValue: typing.List[types.MeterValueType] = None

    @dataclass
    class Response:
        pass


# Every defined Action regrouped in a dict, to easily check whether a specific action is implemented or not.
IMPLEMENTED = dict(inspect.getmembers(
    sys.modules[__name__],
    lambda m: inspect.isclass(m) and m is not Action and issubclass(m, Action),
))
