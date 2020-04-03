# Copyright (c) Polyconseil SAS. All rights reserved.
"""OCPP types as defined in OCPP 1.6 specification, section 7."""
from dataclasses import dataclass
from dataclasses import field
import enum
import typing

from ocpp_codec import encoders
from ocpp_codec import types
from ocpp_codec import utils
from ocpp_codec import validators


# Enums
#######

class AuthorizationStatusEnum(utils.AutoNameEnum):
    Accepted = enum.auto()
    Blocked = enum.auto()
    Expired = enum.auto()
    Invalid = enum.auto()
    ConcurrentTx = enum.auto()


class AvailabilityStatusEnum(utils.AutoNameEnum):
    Accepted = enum.auto()
    Rejected = enum.auto()
    Scheduled = enum.auto()


class AvailabilityTypeEnum(utils.AutoNameEnum):
    Inoperative = enum.auto()
    Operative = enum.auto()


class ConfigurationStatusEnum(utils.AutoNameEnum):
    Accepted = enum.auto()
    Rejected = enum.auto()
    RebootRequired = enum.auto()
    NotSupported = enum.auto()


class ChargePointErrorCodeEnum(utils.AutoNameEnum):
    ConnectorLockFailure = enum.auto()
    EVCommunicationError = enum.auto()
    GroundFailure = enum.auto()
    HighTemperature = enum.auto()
    InternalError = enum.auto()
    LocalListConflict = enum.auto()
    Central = enum.auto()
    LocalAuthorizationList = enum.auto()
    NoError = enum.auto()
    OtherError = enum.auto()
    OverCurrentFailure = enum.auto()
    OverVoltage = enum.auto()
    PowerMeterFailure = enum.auto()
    PowerSwitchFailure = enum.auto()
    ReaderFailure = enum.auto()
    ResetFailure = enum.auto()
    UnderVoltage = enum.auto()
    WeakSignal = enum.auto()


class ChargePointStatusEnum(utils.AutoNameEnum):
    Available = enum.auto()
    Preparing = enum.auto()
    Charging = enum.auto()
    SuspendedEVSE = enum.auto()
    SuspendedEV = enum.auto()
    Finishing = enum.auto()
    Reserved = enum.auto()
    Unavailable = enum.auto()
    Faulted = enum.auto()


class ChargingProfileKindTypeEnum(utils.AutoNameEnum):
    Absolute = enum.auto()
    Recurring = enum.auto()
    Relative = enum.auto()


class ChargingProfilePurposeTypeEnum(utils.AutoNameEnum):
    ChargePointMaxProfile = enum.auto()
    TxDefaultProfile = enum.auto()
    TxProfile = enum.auto()


class ChargingRateUnitTypeEnum(utils.AutoNameEnum):
    W = enum.auto()
    A = enum.auto()


class DataTransferStatusEnum(utils.AutoNameEnum):
    Accepted = enum.auto()
    Rejected = enum.auto()
    UnknownMessageId = enum.auto()
    UnknownVendorId = enum.auto()


class DiagnosticsStatusEnum(utils.AutoNameEnum):
    Idle = enum.auto()
    Uploaded = enum.auto()
    UploadFailed = enum.auto()
    Uploading = enum.auto()


class FirmwareStatusEnum(utils.AutoNameEnum):
    Downloaded = enum.auto()
    DownloadFailed = enum.auto()
    Downloading = enum.auto()
    Idle = enum.auto()
    InstallationFailed = enum.auto()
    Installing = enum.auto()
    Installed = enum.auto()


class LocationEnum(utils.AutoNameEnum):
    Body = enum.auto()
    Cable = enum.auto()
    EV = enum.auto()
    Inlet = enum.auto()
    Outlet = enum.auto()


class MeasurandEnum(utils.AutoNameEnum):
    Current_Export = 'Current.Export'
    Current_Import = 'Current.Import'
    Current_Offered = 'Current.Offered'
    Energy_Active_Export_Register = 'Energy.Active.Export.Register'
    Energy_Active_Import_Register = 'Energy.Active.Import.Register'
    Energy_Reactive_Export_Register = 'Energy.Reactive.Export.Register'
    Energy_Reactive_Import_Register = 'Energy.Reactive.Import.Register'
    Energy_Active_Export_Interval = 'Energy.Active.Export.Interval'
    Energy_Active_Import_Interval = 'Energy.Active.Import.Interval'
    Energy_Reactive_Export_Interval = 'Energy.Reactive.Export.Interval'
    Energy_Reactive_Import_Interval = 'Energy.Reactive.Import.Interval'
    Power_Active_Export = 'Power.Active.Export'
    Power_Active_Import = 'Power.Active.Import'
    Power_Factor = 'Power.Factor'
    Power_Offered = 'Power.Offered'
    Power_Reactive_Export = 'Power.Reactive.Export'
    Power_Reactive_Import = 'Power.Reactive.Import'
    RPM = enum.auto()
    SoC = enum.auto()
    Temperature = enum.auto()
    Voltage = enum.auto()


class PhaseEnum(utils.AutoNameEnum):
    L1 = enum.auto()
    L2 = enum.auto()
    L3 = enum.auto()
    N = enum.auto()
    L1_N = 'L1-N'
    L2_N = 'L2-N'
    L3_N = 'L3-N'
    L1_L2 = 'L1-L2'
    L2_L3 = 'L2-L3'
    L3_L1 = 'L3-L1'


class ReadingContextEnum(utils.AutoNameEnum):
    Interruption_Begin = 'Interruption.Begin'
    Interruption_End = 'Interruption.End'
    Other = enum.auto()
    Sample_Clock = 'Sample.Clock'
    Sample_Periodic = 'Sample.Periodic'
    Transaction_Begin = 'Transaction.Begin'
    Transaction_End = 'Transaction.End'
    Trigger = enum.auto()


class ReasonEnum(utils.AutoNameEnum):
    EmergencyStop = enum.auto()
    EVDisconnected = enum.auto()
    HardReset = enum.auto()
    Local = enum.auto()
    Charge = enum.auto()
    Other = enum.auto()
    PowerLoss = enum.auto()
    Reboot = enum.auto()
    Remote = enum.auto()
    SoftReset = enum.auto()
    UnlockCommand = enum.auto()
    DeAuthorized = enum.auto()


class RecurrencyKindTypeEnum(utils.AutoNameEnum):
    Daily = enum.auto()
    Weekly = enum.auto()


class RegistrationStatusEnum(utils.AutoNameEnum):
    Accepted = enum.auto()
    Pending = enum.auto()
    Rejected = enum.auto()


class RemoteStartStopStatusEnum(utils.AutoNameEnum):
    Accepted = enum.auto()
    Rejected = enum.auto()


class ReservationStatusEnum(utils.AutoNameEnum):
    Accepted = enum.auto()
    Faulted = enum.auto()
    Occupied = enum.auto()
    Rejected = enum.auto()
    Unavailable = enum.auto()


class UnitOfMeasureEnum(utils.AutoNameEnum):
    Wh = enum.auto()
    kWh = enum.auto()
    varh = enum.auto()
    kvarh = enum.auto()
    W = enum.auto()
    kW = enum.auto()
    VA = enum.auto()
    kVA = enum.auto()
    var = enum.auto()
    kvar = enum.auto()
    A = enum.auto()
    V = enum.auto()
    Celsius = enum.auto()
    Fahrenheit = enum.auto()
    K = enum.auto()
    Percent = enum.auto()


class UnlockStatusEnum(utils.AutoNameEnum):
    Unlocked = enum.auto()
    UnlockFailed = enum.auto()
    NotSupported = enum.auto()


class UpdateStatusEnum(utils.AutoNameEnum):
    Accepted = enum.auto()
    Failed = enum.auto()
    NotSupported = enum.auto()
    VersionMismatch = enum.auto()


class UpdateTypeEnum(utils.AutoNameEnum):
    Differential = enum.auto()
    Full = enum.auto()


class ValueFormatEnum(utils.AutoNameEnum):
    Raw = enum.auto()
    SignedData = enum.auto()


# Simple types
##############

@dataclass
class AuthorizationStatus(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(AuthorizationStatusEnum)})


@dataclass
class AvailabilityStatus(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(AvailabilityStatusEnum)})


@dataclass
class AvailabilityType(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(AvailabilityTypeEnum)})


@dataclass
class ConfigurationStatus(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(ConfigurationStatusEnum)})


@dataclass
class ChargePointErrorCode(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(ChargePointErrorCodeEnum)})


@dataclass
class ChargePointStatus(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(ChargePointStatusEnum)})


@dataclass
class ChargingProfileKindType(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(ChargingProfileKindTypeEnum)})


@dataclass
class ChargingProfilePurposeType(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(ChargingProfilePurposeTypeEnum)})


@dataclass
class ChargingRateUnitType(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(ChargingRateUnitTypeEnum)})


@dataclass
class CiString20Type(types.SimpleType):
    value: str = field(metadata={'validators': validators.max_length_20})


@dataclass
class CiString25Type(types.SimpleType):
    value: str = field(metadata={'validators': validators.max_length_25})


@dataclass
class CiString50Type(types.SimpleType):
    value: str = field(metadata={'validators': validators.max_length_50})


@dataclass
class CiString255Type(types.SimpleType):
    value: str = field(metadata={'validators': validators.max_length_255})


@dataclass
class CiString500Type(types.SimpleType):
    value: str = field(metadata={'validators': validators.max_length_500})


@dataclass
class DataTransferStatus(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(DataTransferStatusEnum)})


@dataclass
class DiagnosticsStatus(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(DiagnosticsStatusEnum)})


@dataclass
class DateTime(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.DateTimeEncoder()})


@dataclass
class Decimal(types.SimpleType):
    value: float = field(metadata={'validators': validators.decimal_precision_1})


@dataclass
class FirmwareStatus(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(FirmwareStatusEnum)})


@dataclass
class IdToken(CiString20Type):
    """A simple renaming of CiString20Type."""


@dataclass
class Location(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(LocationEnum)})


@dataclass
class Measurand(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(MeasurandEnum)})


@dataclass
class PositiveInteger(types.SimpleType):
    value: int = field(metadata={'validators': validators.is_positive})


@dataclass
class PositiveIntegerNonNull(types.SimpleType):
    value: int = field(metadata={'validators': [validators.is_positive, validators.is_not_zero]})


@dataclass
class Phase(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(PhaseEnum)})


@dataclass
class ReadingContext(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(ReadingContextEnum)})


@dataclass
class Reason(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(ReasonEnum)})


@dataclass
class RecurrencyKindType(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(RecurrencyKindTypeEnum)})


@dataclass
class RegistrationStatus(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(RegistrationStatusEnum)})


@dataclass
class RemoteStartStopStatus(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(RemoteStartStopStatusEnum)})


@dataclass
class ReservationStatus(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(ReservationStatusEnum)})


@dataclass
class UnitOfMeasure(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(UnitOfMeasureEnum)})


@dataclass
class UnlockStatus(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(UnlockStatusEnum)})


@dataclass
class UpdateStatus(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(UpdateStatusEnum)})


@dataclass
class UpdateType(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(UpdateTypeEnum)})


@dataclass
class ValueFormat(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(ValueFormatEnum)})


# Complex types
###############


@dataclass
class ChargingSchedulePeriod(types.ComplexType):
    startPeriod: int
    limit: Decimal

    numberPhases: int = None


@dataclass
class ChargingSchedule(types.ComplexType):
    chargingRateUnit: ChargingRateUnitType
    chargingSchedulePeriod: typing.List[ChargingSchedulePeriod]

    duration: int = None
    startSchedule: DateTime = None
    minChargingRate: Decimal = None


@dataclass
class ChargingProfile(types.ComplexType):
    chargingProfileId: int
    stackLevel: PositiveInteger
    chargingProfilePurpose: ChargingProfilePurposeType
    chargingProfileKind: ChargingProfileKindType
    chargingSchedule: ChargingSchedule

    transactionId: int = None
    recurrencyKind: RecurrencyKindType = None
    validFrom: DateTime = None
    validTo: DateTime = None


@dataclass
class IdTagInfo(types.ComplexType):
    status: AuthorizationStatus

    expiryDate: DateTime = None
    parentIdTag: IdToken = None


@dataclass
class AuthorizationData(types.ComplexType):
    idTag: IdToken
    idTagInfo: IdTagInfo = None


@dataclass
class SampledValue(types.ComplexType):
    value: str

    context: ReadingContext = None
    format: ValueFormat = None
    measurand: Measurand = None
    phase: Phase = None
    location: Location = None
    unit: UnitOfMeasure = None


@dataclass
class MeterValue(types.ComplexType):
    timestamp: DateTime
    sampledValue: typing.List[SampledValue]
