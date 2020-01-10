# Copyright (c) Polyconseil SAS. All rights reserved.
"""OCPP types as defined in OCPP 2.0 specification, section Datatypes."""
from dataclasses import dataclass
from dataclasses import field
import enum
import functools
import typing

from ocpp_codec import types
from ocpp_codec import utils
from ocpp_codec import validators


# Enums
#######


class AuthorizationStatusEnumType(utils.AutoNameEnum):
    Accepted = enum.auto()
    Blocked = enum.auto()
    ConcurrentTx = enum.auto()
    Expired = enum.auto()
    Invalid = enum.auto()
    NoCredit = enum.auto()
    NotAllowedTypeEVSE = enum.auto()
    NotAtThisLocation = enum.auto()
    NotAtThisTime = enum.auto()
    Unknown = enum.auto()


class BootReasonEnumType(utils.AutoNameEnum):
    ApplicationReset = enum.auto()
    FirmwareUpdate = enum.auto()
    LocalReset = enum.auto()
    PowerUp = enum.auto()
    RemoteReset = enum.auto()
    ScheduledReset = enum.auto()
    Triggered = enum.auto()
    Unknown = enum.auto()
    Watchdog = enum.auto()
    Description = enum.auto()


class CertificateStatusEnumType(utils.AutoNameEnum):
    Accepted = enum.auto()
    SignatureError = enum.auto()
    CertificateExpired = enum.auto()
    CertificateRevoked = enum.auto()
    NoCertificateAvailable = enum.auto()
    CertChainError = enum.auto()
    ContractCancelled = enum.auto()


class HashAlgorithmEnumType(utils.AutoNameEnum):
    SHA256 = enum.auto()
    SHA384 = enum.auto()
    SHA512 = enum.auto()


class IdTokenEnumType(utils.AutoNameEnum):
    Central = enum.auto()
    eMAID = enum.auto()
    ISO14443 = enum.auto()
    KeyCode = enum.auto()
    Local = enum.auto()
    NoAuthorization = enum.auto()
    ISO15693 = enum.auto()
    Description = enum.auto()


class MessageFormatEnumType(utils.AutoNameEnum):
    ASCII = enum.auto()
    HTML = enum.auto()
    URI = enum.auto()
    UTF8 = enum.auto()


class RegistrationStatusEnumType(utils.AutoNameEnum):
    Accepted = enum.auto()
    Pending = enum.auto()
    Rejected = enum.auto()


# Commonly used primitive types aliases
#######################################

@dataclass
class _String8(types.SimpleType):
    value: str = field(metadata={'validator': validators.max_length_8})


@dataclass
class _String20(types.SimpleType):
    value: str = field(metadata={'validator': validators.max_length_20})


@dataclass
class _String50(types.SimpleType):
    value: str = field(metadata={'validator': validators.max_length_50})


@dataclass
class _String128(types.SimpleType):
    value: str = field(metadata={'validator': validators.max_length_128})


@dataclass
class _String512(types.SimpleType):
    value: str = field(metadata={'validator': validators.max_length_512})


@dataclass
class _IdentifierString20(types.SimpleType):
    value: str = field(metadata={
        'validator': validators.compound_validator(validators.max_length_20, validators.is_identifier),
    })


@dataclass
class _IdentifierString36(types.SimpleType):
    value: str = field(metadata={
        'validator': validators.compound_validator(validators.max_length_36, validators.is_identifier),
    })


@dataclass
class _IdentifierString128(types.SimpleType):
    value: str = field(metadata={
        'validator': validators.compound_validator(validators.max_length_128, validators.is_identifier),
    })


# Field definitions for tricky cases
####################################

# These two could not be defined as dataclasses, as it became tricky to handle a Generic dataclass using the limited
# typing API. Defining:
#
# @dataclass
# class ListCard4(typing.Generic[T]):
#     value: typing.List[T] = field(...)

# doesn't work because ListCard4[int] for example isn't considered a dataclass, while ListCard4 is, but extracting the
# type of the 'value' field yields, quite naturally, ~T. We'd like to be able to extract the concrete type of a
# ListCard4[int] along with the field validators.
ListCard4Field = functools.partial(field, metadata={'validator': validators.max_length_4})


# Simple types
##############

@dataclass
class DateTime(types.SimpleType):
    value: str = field(metadata={'validator': validators.DateTimeEncoder()})


# Complex types
###############

@dataclass
class ModemType(types.ComplexType):
    iccid: _IdentifierString20 = None
    imsi: _IdentifierString20 = None


@dataclass
class ChargingStationType(types.ComplexType):
    model: _String20
    vendorName: _String50

    serialNumber: _String20 = None
    firmwareVersion: _String50 = None
    modem: ModemType = None


@dataclass
class AdditionalInfoType(types.ComplexType):
    additionalIdToken: _IdentifierString36
    type_: _String50


@dataclass
class IdTokenType(types.ComplexType):
    idToken: _IdentifierString36
    type_: IdTokenEnumType

    additionalInfo: typing.List[AdditionalInfoType] = None


@dataclass
class GroupIdTokenType(types.ComplexType):
    idToken: _IdentifierString36
    type_: IdTokenEnumType


@dataclass
class MessageContentType(types.ComplexType):
    format_: MessageFormatEnumType
    content: _String512

    language: _String8 = None


@dataclass
class IdTokenInfoType(types.ComplexType):
    status: AuthorizationStatusEnumType

    cacheExpiryDateTime: DateTime = None
    chargingPriority: int = None
    language1: _String8 = None
    language2: _String8 = None
    groupIdToken: GroupIdTokenType = None
    personalMessage: MessageContentType = None


@dataclass
class OCSPRequestDataType(types.ComplexType):
    hashAlgorithm: HashAlgorithmEnumType
    issuerNameHash: _IdentifierString128
    issuerKeyHash: _String128
    serialNumber: _String20

    responderUrl: _String512 = None