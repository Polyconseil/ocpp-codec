# Copyright (c) Polyconseil SAS. All rights reserved.
"""Test messages that use the whole set of features."""
from dataclasses import dataclass
from dataclasses import field
import typing

from ocpp_codec import validators

from . import types


class SimpleAction:
    @dataclass
    class req:
        value: str
        validatedValue: types.ValidatedType
        enumValue: types.EnumType

    @dataclass
    class conf:
        value: int
        datetimeValue: types.DateTimeType


class ComplexAction:
    @dataclass
    class req:
        complexValue: types.ComplexType
        listValue: typing.List[types.ListElementType] = field(metadata={'validators': [validators.max_length_4]})

        optionalValue: str = None

    @dataclass
    class conf:
        optionalListValue: typing.List[str] = None
        optionalComplexListValue: typing.List[types.ComplexType] = field(
            default=None, metadata={'validators': [validators.max_length_4]},
        )


class NoPayloadAction:
    @dataclass
    class req:
        pass

    @dataclass
    class conf:
        pass


IMPLEMENTED = {'SimpleAction': SimpleAction, 'ComplexAction': ComplexAction, 'NoPayloadAction': NoPayloadAction}
