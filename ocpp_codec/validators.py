# Copyright (c) Polyconseil SAS. All rights reserved.
"""Collection of functions and classes that can be used to validate OCPP input.

There exists two kinds of validators: simple functions and encoders.

The functions take an input and validate it without altering its typing, whereas encoders are expected to convert the
incoming value to another type (e.g.: from a string to a 'datetime.datetime'). Both should raise an appropriate instance
of a 'BaseOCPPError' if the input value does not meet the appropriate criteria. Validators are expected to return the
value unaltered so that their API matches encoders.

Simple functions validators shouldn't run any type checking, this is taken care of before they're called.

Encoders shouldn't run any type checking when parsing ('from_json'), but should when serializing ('to_json'). This is
because there might be several Python types that can be coerced into the correct OCPP-JSON type required. The validator
is responsible for raising a 'TypeConstraintViolationError' error if it cannot process the input.

Validators are assigned to a dataclass field through its metadata 'validators' key.
"""
import datetime
import decimal
import functools
import re
import typing

import dateutil.parser
import pytz

from ocpp_codec import errors


###########
# Utilities

def build_simple_validator(func: typing.Callable, *args, **kwargs) -> typing.Callable[[typing.Any], typing.Any]:
    """Build a ready-to-use simple validator out of a function.

    Args:
        - func: callable, the function to be called to validate an input
        - args: list, args to partially apply to func
        - kwargs: dict, kwargs to partially apply to func

    Returns:
        validator: functools.partial, a partial function based on ``func``, with ``args`` and ``kwargs`` partially
                   applied and run through functools.update_wrapper
    """
    validator = functools.partial(func, *args, **kwargs)
    return functools.update_wrapper(validator, func)


############
# Validators

def noop(value: typing.Any) -> typing.Any:
    """A no-op validator, used as a default validator when none is specified."""
    return value


def max_length(length: int, value: typing.Any) -> typing.Any:
    """Validates that an input doesn't exceed a given length."""
    actual_length = len(value)
    if actual_length > length:
        raise errors.PropertyConstraintViolationError(
            "Input is too long", max_length=length, actual_length=actual_length,
        )
    return value


# Common OCPP types length, see OCPP 1.6 specification, from section 7.15 to 7.19, and
# OCPP 1.6 JSON specification section 4.1.4.
max_length_4 = build_simple_validator(max_length, 4)
max_length_8 = build_simple_validator(max_length, 8)
max_length_20 = build_simple_validator(max_length, 20)
max_length_25 = build_simple_validator(max_length, 25)
max_length_36 = build_simple_validator(max_length, 36)
max_length_50 = build_simple_validator(max_length, 50)
max_length_128 = build_simple_validator(max_length, 128)
max_length_255 = build_simple_validator(max_length, 255)
max_length_500 = build_simple_validator(max_length, 500)
max_length_512 = build_simple_validator(max_length, 512)
max_length_1000 = build_simple_validator(max_length, 1000)
max_length_2500 = build_simple_validator(max_length, 2500)


def decimal_validator(precision: int, value: float) -> float:
    components = str(value).split('.')
    if len(components[-1]) > precision:
        raise errors.PropertyConstraintViolationError("Decimal value precision is too big", precision=precision)
    return value


decimal_precision_1 = build_simple_validator(decimal_validator, 1)


def is_positive(value: typing.Union[int, float]) -> typing.Union[int, float]:
    if value < 0:
        raise errors.PropertyConstraintViolationError("Input is negative")
    return value


def is_not_zero(value: typing.Union[int, float]) -> typing.Union[int, float]:
    if value == 0:
        raise errors.PropertyConstraintViolationError("Input is zero")
    return value


_IDENTIFIER_REGEXP = re.compile('[a-zA-Z0-9' + re.escape('*_=:+|@.-') + ']*')


def is_identifier(value: str) -> str:
    if not _IDENTIFIER_REGEXP.fullmatch(value):
        raise errors.PropertyConstraintViolationError(
            "Input is not a valid identifier",
            pattern=_IDENTIFIER_REGEXP.pattern,
        )
    return value


##########
# Encoders


class BaseEncoder:
    """Base encoder from type A to B."""

    def from_json(self, json_value: typing.Any) -> typing.Any:
        """Encoding function handling conversion from OCPP-JSON to Python types."""
        raise NotImplementedError

    def to_json(self, value: typing.Any) -> typing.Any:
        """Encoding function handling conversion from Python types to OCPP-JSON."""
        raise NotImplementedError


class DateTimeEncoder(BaseEncoder):
    """Encoder for ISO 8601 UTC datetime values.

    This encoder parses strings to 'datetime.datetime' elements, making sure the timezone information is provided and
    is UTC. It expects any kind of ISO 8601 compatible strings, of any precision.

    This encoder serializes 'datetime.datetime' elements in ISO 8601 compatible strings, with the most precision
    available.
    """

    def from_json(self, json_value: str) -> datetime.datetime:
        try:
            dt = dateutil.parser.isoparse(json_value)
        except (ValueError, OverflowError) as exc:
            raise errors.PropertyConstraintViolationError(
                f"Date input isn't formatted appropriately",
                value=json_value,
            ) from exc
        else:
            # Assume naive datetime are UTC, so that we don't reject charge points who expect to speak UTC by default
            if not dt.tzinfo:
                dt = dt.replace(tzinfo=pytz.UTC)
            if dt.tzinfo.tzname(dt) != 'UTC':  # type: ignore # mypy doesn't catch that dt.replace call sets tzinfo
                raise errors.PropertyConstraintViolationError(
                    f"Date input must use the UTC timezone, not '{dt.tzinfo}'",
                    value=dt,
                )
            return dt

    def to_json(self, value: datetime.datetime) -> str:
        if not isinstance(value, datetime.datetime):
            raise errors.TypeConstraintViolationError(
                f"Input '{value}' is not a datetime.datetime instance",
                value=value,
            )

        if not value.tzinfo or value.tzinfo.tzname(value) != 'UTC':
            raise errors.PropertyConstraintViolationError(
                f"Date input must use the UTC timezone, not '{value.tzinfo}'",
                value=value,
            )

        return value.isoformat()


class EnumEncoder(BaseEncoder):
    """Encoder for a kind of 'Enum' class.

    This encoder parses strings to 'Enum' instances, based on the provided 'enum_class'.

    This encoder serializes 'Enum' instances to strings.
    """

    def __init__(self, enum_class):
        self.enum_class = enum_class

    def from_json(self, json_value):
        try:
            enum_instance = self.enum_class(json_value)
        except ValueError as exc:
            raise errors.PropertyConstraintViolationError(
                f"Input '{json_value}' is not a valid entry of enum {self.enum_class.__name__}",
                value=json_value, enum_class=self.enum_class,
            ) from exc
        else:
            return enum_instance

    def to_json(self, value):
        if not isinstance(value, self.enum_class):
            raise errors.TypeConstraintViolationError(
                f"Input '{value}' is not an instance of '{self.enum_class.__name__}",
                value=value, enum_class=self.enum_class.__name__,
            )
        return value.value


class OutgoingMessageDecimalEncoder(BaseEncoder):
    """Encoder to limit the precision of decimal values sent to charge points.

    This encoder doesn't restricts the precision of float values received from the charge point, as we *must* keep the
    full resolution, but limits it to 6 places when sending a value, as required by OCPP 2.0 spec (section 2.1.3).
    """

    def from_json(self, json_value):
        return json_value

    def to_json(self, value):
        try:
            float_value = float(value)
        except ValueError:
            raise errors.TypeConstraintViolationError(f"Input '{value}' cannot be cast to float", value=value)

        six_places = decimal.Decimal('1.000000')
        try:
            truncated_value = float(decimal.Decimal(float_value).quantize(six_places, rounding=decimal.ROUND_DOWN))
        except decimal.DecimalException as exc:
            raise errors.TypeConstraintViolationError(
                f"Input '{value}' could not be truncated to six decimal places",
                value=value,
            ) from exc

        return truncated_value
