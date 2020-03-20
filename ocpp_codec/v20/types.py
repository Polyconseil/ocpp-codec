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


class AuthorizationStatusEnum(utils.AutoNameEnum):
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


class AttributeEnum(utils.AutoNameEnum):
    Actual = enum.auto()
    Target = enum.auto()
    MinSet = enum.auto()
    MaxSet = enum.auto()


class BootReasonEnum(utils.AutoNameEnum):
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


class CertificateStatusEnum(utils.AutoNameEnum):
    Accepted = enum.auto()
    SignatureError = enum.auto()
    CertificateExpired = enum.auto()
    CertificateRevoked = enum.auto()
    NoCertificateAvailable = enum.auto()
    CertChainError = enum.auto()
    ContractCancelled = enum.auto()


class ChangeAvailabilityStatusEnum(utils.AutoNameEnum):
    Accepted = enum.auto()
    Rejected = enum.auto()
    Scheduled = enum.auto()


class ConnectorStatusEnum(utils.AutoNameEnum):
    Available = enum.auto()
    Occupied = enum.auto()
    Reserved = enum.auto()
    Unavailable = enum.auto()
    Faulted = enum.auto()


class EncodingMethodEnum(utils.AutoNameEnum):
    Other = enum.auto()
    DLMSMessage = 'DLMS Message'
    COSEMProtectedData = 'COSEM Protected Data'
    EDL = enum.auto()


class GetVariableStatusEnum(utils.AutoNameEnum):
    Accepted = enum.auto()
    Rejected = enum.auto()
    UnknownComponent = enum.auto()
    UnknownVariable = enum.auto()
    NotSupportedAttributeType = enum.auto()


class HashAlgorithmEnum(utils.AutoNameEnum):
    SHA256 = enum.auto()
    SHA384 = enum.auto()
    SHA512 = enum.auto()


class IdTokenEnum(utils.AutoNameEnum):
    Central = enum.auto()
    eMAID = enum.auto()
    ISO14443 = enum.auto()
    KeyCode = enum.auto()
    Local = enum.auto()
    NoAuthorization = enum.auto()
    ISO15693 = enum.auto()
    Description = enum.auto()


class LocationEnum(utils.AutoNameEnum):
    Body = enum.auto()
    Cable = enum.auto()
    EV = enum.auto()
    Inlet = enum.auto()
    Outlet = enum.auto()


class MeasurandEnum(utils.AutoNameEnum):
    CurrentExport = 'Current.Export'
    CurrentImport = 'Current.Import'
    CurrentOffered = 'Current.Offered'
    EnergyActiveExportRegister = 'Energy.Active.Export.Register'
    EnergyActiveImportRegister = 'Energy.Active.Import.Register'
    EnergyReactiveExportRegister = 'Energy.Reactive.Export.Register'
    EnergyReactiveImportRegister = 'Energy.Reactive.Import.Register'
    EnergyActiveExportInterval = 'Energy.Active.Export.Interval'
    EnergyActiveImportInterval = 'Energy.Active.Import.Interval'
    EnergyActiveNet = 'Energy.Active.Net'
    EnergyReactiveExportInterval = 'Energy.Reactive.Export.Interval'
    EnergyReactiveImportInterval = 'Energy.Reactive.Import.Interval'
    EnergyReactiveNet = 'Energy.Reactive.Net'
    EnergyApparentNet = 'Energy.Apparent.Net'
    EnergyApparentImport = 'Energy.Apparent.Import'
    EnergyApparentExport = 'Energy.Apparent.Export'
    Frequency = enum.auto()
    PowerActiveExport = 'Power.Active.Export'
    PowerActiveImport = 'Power.Active.Import'
    PowerFactor = 'Power.Factor'
    PowerOffered = 'Power.Offered'
    PowerReactiveExport = 'Power.Reactive.Export'
    PowerReactiveImport = 'Power.Reactive.Import'
    SoC = enum.auto()
    Voltage = enum.auto()


class MessageFormatEnum(utils.AutoNameEnum):
    ASCII = enum.auto()
    HTML = enum.auto()
    URI = enum.auto()
    UTF8 = enum.auto()


class OperationalStatusEnum(utils.AutoNameEnum):
    Inoperative = enum.auto()
    Operative = enum.auto()


class PhaseEnum(utils.AutoNameEnum):
    L1 = enum.auto()
    L2 = enum.auto()
    L3 = enum.auto()
    N = enum.auto()
    L1N = 'L1-N'
    L2N = 'L2-N'
    L3N = 'L3-N'
    L1L2 = 'L1-L2'
    L2L3 = 'L2-L3'
    L3L1 = 'L3-L1'


class ReadingContextEnum(utils.AutoNameEnum):
    InterruptionBegin = 'Interruption.Begin'
    InterruptionEnd = 'Interruption.End'
    Other = enum.auto()
    SampleClock = 'Sample.Clock'
    SamplePeriodic = 'Sample.Periodic'
    TransactionBegin = 'Transaction.Begin'
    TransactionEnd = 'Transaction.End'
    Trigger = enum.auto()


class RegistrationStatusEnum(utils.AutoNameEnum):
    Accepted = enum.auto()
    Pending = enum.auto()
    Rejected = enum.auto()


class SetVariableStatusEnum(utils.AutoNameEnum):
    Accepted = enum.auto()
    Rejected = enum.auto()
    InvalidValue = enum.auto()
    UnknownComponent = enum.auto()
    UnknownVariable = enum.auto()
    NotSupportedAttributeType = enum.auto()
    OutOfRange = enum.auto()
    RebootRequired = enum.auto()


class SignatureMethodEnum(utils.AutoNameEnum):
    ECDSAP256SHA256 = enum.auto()
    ECDSAP384SHA384 = enum.auto()
    ECDSA192SHA256 = enum.auto()


# Commonly used primitive types aliases
#######################################

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
class _String1000(types.SimpleType):
    value: str = field(metadata={'validator': validators.max_length_1000})


@dataclass
class _String2500(types.SimpleType):
    value: str = field(metadata={'validator': validators.max_length_2500})


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
class AuthorizationStatusEnumType(types.SimpleType):
    value: str = field(metadata={'validator': validators.EnumEncoder(AuthorizationStatusEnum)})


@dataclass
class AttributeEnumType(types.SimpleType):
    value: str = field(metadata={'validator': validators.EnumEncoder(AttributeEnum)})


@dataclass
class BootReasonEnumType(types.SimpleType):
    value: str = field(metadata={'validator': validators.EnumEncoder(BootReasonEnum)})


@dataclass
class CertificateStatusEnumType(types.SimpleType):
    value: str = field(metadata={'validator': validators.EnumEncoder(CertificateStatusEnum)})


@dataclass
class ChangeAvailabilityStatusEnumType(types.SimpleType):
    value: str = field(metadata={'validator': validators.EnumEncoder(ChangeAvailabilityStatusEnum)})


@dataclass
class ConnectorStatusEnumType(types.SimpleType):
    value: str = field(metadata={'validator': validators.EnumEncoder(ConnectorStatusEnum)})


@dataclass
class Decimal(types.SimpleType):
    value: float = field(metadata={'validator': validators.decimal_precision_1})


@dataclass
class DateTime(types.SimpleType):
    value: str = field(metadata={'validator': validators.DateTimeEncoder()})


@dataclass
class EncodingMethodEnumType(types.SimpleType):
    value: str = field(metadata={'validator': validators.EnumEncoder(EncodingMethodEnum)})


@dataclass
class GetVariableStatusEnumType(types.SimpleType):
    value: str = field(metadata={'validator': validators.EnumEncoder(GetVariableStatusEnum)})


@dataclass
class HashAlgorithmEnumType(types.SimpleType):
    value: str = field(metadata={'validator': validators.EnumEncoder(HashAlgorithmEnum)})


@dataclass
class IdTokenEnumType(types.SimpleType):
    value: str = field(metadata={'validator': validators.EnumEncoder(IdTokenEnum)})


@dataclass
class LocationEnumType(types.SimpleType):
    value: str = field(metadata={'validator': validators.EnumEncoder(LocationEnum)})


@dataclass
class MeasurandEnumType(types.SimpleType):
    value: str = field(metadata={'validator': validators.EnumEncoder(MeasurandEnum)})


@dataclass
class MessageFormatEnumType(types.SimpleType):
    value: str = field(metadata={'validator': validators.EnumEncoder(MessageFormatEnum)})


@dataclass
class OperationalStatusEnumType(types.SimpleType):
    value: str = field(metadata={'validator': validators.EnumEncoder(OperationalStatusEnum)})


@dataclass
class PhaseEnumType(types.SimpleType):
    value: str = field(metadata={'validator': validators.EnumEncoder(PhaseEnum)})


@dataclass
class ReadingContextEnumType(types.SimpleType):
    value: str = field(metadata={'validator': validators.EnumEncoder(ReadingContextEnum)})


@dataclass
class RegistrationStatusEnumType(types.SimpleType):
    value: str = field(metadata={'validator': validators.EnumEncoder(RegistrationStatusEnum)})


@dataclass
class SetVariableStatusEnumType(types.SimpleType):
    value: str = field(metadata={'validator': validators.EnumEncoder(SetVariableStatusEnum)})


@dataclass
class SignatureMethodEnumType(types.SimpleType):
    value: str = field(metadata={'validator': validators.EnumEncoder(SignatureMethodEnum)})


@dataclass
class UnitOfMeasureType(types.SimpleType):
    value: str = field(metadata={'validator': validators.max_length_20})


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


@dataclass
class EVSEType(types.ComplexType):
    id: int

    connectorId: int = None


@dataclass
class ComponentType(types.ComplexType):
    name: _String50

    instance: _String50 = None
    evse: EVSEType = None


@dataclass
class VariableType(types.ComplexType):
    name: _String50

    instance: _String50 = None


@dataclass
class GetVariableDataType(types.ComplexType):
    component: ComponentType
    variable: VariableType

    attributeType: AttributeEnumType = None


@dataclass
class GetVariableResultType(types.ComplexType):
    attributeStatus: GetVariableStatusEnumType
    component: ComponentType
    variable: VariableType

    attributeType: AttributeEnumType = None
    attributeValue: _String1000 = None


@dataclass
class SignedMeterValueType(types.ComplexType):
    meterValueSignature: _String2500
    signatureMethod: SignatureMethodEnumType
    encodingMethod: EncodingMethodEnumType
    encodedMeterValue: _String512


@dataclass
class SampledValueType(types.ComplexType):
    value: Decimal

    context: ReadingContextEnumType = None
    measurand: MeasurandEnumType = None
    phase: PhaseEnumType = None
    location: LocationEnumType = None
    signedMeterValue: SignedMeterValueType = None
    unitOfMeasure: UnitOfMeasureType = None


@dataclass
class MeterValueType(types.ComplexType):
    timestamp: DateTime
    sampledValue: typing.List[SampledValueType]


@dataclass
class SetVariableDataType(types.ComplexType):
    attributeValue: _String1000
    component: ComponentType
    variable: VariableType

    attributeType: AttributeEnumType = None


@dataclass
class SetVariableResultType(types.ComplexType):
    attributeStatus: SetVariableStatusEnumType
    component: ComponentType
    variable: VariableType

    attributeType: AttributeEnumType = None
