# Copyright (c) Polyconseil SAS. All rights reserved.
"""Test types used to define test messages."""
from dataclasses import dataclass
from dataclasses import field
import enum
import typing

from ocpp_codec import encoders
from ocpp_codec import types
from ocpp_codec import utils
from ocpp_codec import validators


class FooBarEnum(utils.AutoNameEnum):
    Foo = enum.auto()
    Bar = enum.auto()


@dataclass
class ValidatedType(types.SimpleType):
    value: str = field(metadata={'validators': [validators.max_length_20]})


@dataclass
class SeveralValidatorsType(types.SimpleType):
    value: float = field(metadata={'validators': [validators.is_positive, validators.decimal_precision_1]})


@dataclass
class DateTimeType(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.DateTimeEncoder()})


@dataclass
class EnumType(types.SimpleType):
    value: str = field(metadata={'encoder': encoders.EnumEncoder(FooBarEnum)})


@dataclass
class ComplexType(types.ComplexType):
    enumValue: EnumType
    validatedValue: ValidatedType


@dataclass
class ElementType(types.ComplexType):
    value: str
    optionalValue: EnumType = None


@dataclass
class ListElementType(types.ComplexType):
    datetimeValue: DateTimeType
    nestedListValue: typing.List[ElementType]
