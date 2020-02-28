# Copyright (c) Polyconseil SAS. All rights reserved.
"""OCPP messages definitions.

This module implements elements specified in OCPP 1.6 specification, section 6.

Attributes:
    - IMPLEMENTED: dict, a mapping from action name to action classes for every implemented OCPP actions.
"""
from dataclasses import dataclass
import inspect
import sys
import typing

from . import types


class ActionMetaClass(type):
    """Simple metaclass that inserts a reference to the englobing 'Action' class inside nested req and conf classes.

    This makes 'Action.req' and 'Action.conf' classes able to know which 'Action' they refer to.
    """

    def __new__(cls, class_name, bases, attrs, **kwargs):
        klass = super().__new__(cls, class_name, bases, attrs)

        # Insert reference to the 'Action' class in both 'Action.req' and 'Action.conf'
        setattr(klass.req, '_action_class', klass)
        setattr(klass.conf, '_action_class', klass)

        return klass


class Action(metaclass=ActionMetaClass):
    """Base class representing an OCPP action.

    This indinstinctly represents messages coming from the charge point as well as messages coming from the central
    system.
    """

    @dataclass
    class req:
        """Base class representing the request part of the message."""

    @dataclass
    class conf:
        """Base class representing the response part of the message."""


class Authorize(Action):
    @dataclass
    class req(Action.req):
        idTag: types.IdToken

    @dataclass
    class conf(Action.conf):
        idTagInfo: types.IdTagInfo


class BootNotification(Action):
    @dataclass
    class req(Action.req):
        chargePointModel: types.CiString20Type
        chargePointVendor: types.CiString20Type

        chargeBoxSerialNumber: types.CiString25Type = None
        chargePointSerialNumber: types.CiString25Type = None
        firmwareVersion: types.CiString50Type = None
        iccid: types.CiString20Type = None
        imsi: types.CiString20Type = None
        meterSerialNumber: types.CiString25Type = None
        meterType: types.CiString25Type = None

    @dataclass
    class conf(Action.conf):
        currentTime: types.DateTime
        interval: int
        status: types.RegistrationStatus


class ChangeAvailability(Action):
    @dataclass
    class req(Action.req):
        connectorId: types.PositiveInteger
        type: types.AvailabilityType

    @dataclass
    class conf(Action.conf):
        status: types.AvailabilityStatus


class ChangeConfiguration(Action):
    @dataclass
    class req(Action.req):
        key: types.CiString50Type
        value: types.CiString500Type

    @dataclass
    class conf(Action.conf):
        status: types.ConfigurationStatus


class DataTransfer(Action):
    @dataclass
    class req(Action.req):
        vendorId: types.CiString255Type
        messageId: types.CiString50Type = None
        data: str = None

    @dataclass
    class conf(Action.conf):
        status: types.DataTransferStatus
        data: str = None


class DiagnosticsStatusNotification(Action):
    @dataclass
    class req(Action.req):
        status: types.DiagnosticsStatus

    @dataclass
    class conf(Action.conf):
        pass


class FirmwareStatusNotification(Action):
    @dataclass
    class req(Action.req):
        status: types.FirmwareStatus

    @dataclass
    class conf(Action.conf):
        pass


class GetLocalListVersion(Action):
    @dataclass
    class req(Action.req):
        pass

    @dataclass
    class conf(Action.conf):
        listVersion: int


class Heartbeat(Action):
    @dataclass
    class req(Action.req):
        pass

    @dataclass
    class conf(Action.conf):
        currentTime: types.DateTime


class MeterValues(Action):
    @dataclass
    class req(Action.req):
        connectorId: types.PositiveInteger
        meterValue: typing.List[types.MeterValue]
        transactionId: int = None

    @dataclass
    class conf(Action.conf):
        pass


class RemoteStartTransaction(Action):
    @dataclass
    class req(Action.req):
        idTag: types.IdToken

        connectorId: types.PositiveIntegerNonNull = None
        chargingProfile: types.ChargingProfile = None

    @dataclass
    class conf(Action.conf):
        status: types.RemoteStartStopStatus


class RemoteStopTransaction(Action):
    @dataclass
    class req(Action.req):
        transactionId: int

    @dataclass
    class conf(Action.conf):
        status: types.RemoteStartStopStatus


class ReserveNow(Action):
    @dataclass
    class req(Action.req):
        connectorId: types.PositiveInteger
        expiryDate: types.DateTime
        idTag: types.IdToken
        reservationId: int

        parentIdTag: types.IdToken = None

    @dataclass
    class conf(Action.conf):
        status: types.ReservationStatus


class SendLocalList(Action):
    @dataclass
    class req(Action.req):
        listVersion: types.PositiveInteger
        updateType: types.UpdateType

        localAuthorizationList: typing.List[types.AuthorizationData] = None

    @dataclass
    class conf(Action.conf):
        status: types.UpdateStatus


class StartTransaction(Action):
    @dataclass
    class req(Action.req):
        connectorId: types.PositiveIntegerNonNull
        idTag: types.IdToken
        meterStart: int
        timestamp: types.DateTime

        reservationId: int = None

    @dataclass
    class conf(Action.conf):
        idTagInfo: types.IdTagInfo
        transactionId: int


class StatusNotification(Action):
    @dataclass
    class req(Action.req):
        connectorId: types.PositiveInteger
        errorCode: types.ChargePointErrorCode
        status: types.ChargePointStatus

        info: types.CiString50Type = None
        timestamp: types.DateTime = None
        vendorId: types.CiString255Type = None
        vendorErrorCode: types.CiString50Type = None

    @dataclass
    class conf(Action.conf):
        pass


class StopTransaction(Action):
    @dataclass
    class req(Action.req):
        meterStop: int
        timestamp: types.DateTime
        transactionId: int

        idTag: types.IdToken = None
        reason: types.Reason = None
        transactionData: typing.List[types.MeterValue] = None

    @dataclass
    class conf(Action.conf):
        idTagInfo: types.IdTagInfo = None


class UnlockConnector(Action):
    @dataclass
    class req(Action.req):
        connectorId: types.PositiveIntegerNonNull

    @dataclass
    class conf(Action.conf):
        status: types.UnlockStatus


# Every defined Action regrouped in a dict, to easily check whether a specific action is implemented or not.
IMPLEMENTED = dict(inspect.getmembers(
    sys.modules[__name__],
    lambda m: inspect.isclass(m) and m is not Action and issubclass(m, Action),
))
