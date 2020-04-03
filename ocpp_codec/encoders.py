# Copyright (c) Polyconseil SAS. All rights reserved.
"""Collection of classes that can be used to encode and decode OCPP data.

Encoders are expected to convert the incoming value to another type (e.g.: from a string to a 'datetime.datetime').
They should raise an appropriate instance of a 'BaseOCPPError' if the input value does not meet the appropriate
criteria.

Encoders shouldn't run any type checking when parsing ('from_json'), but should when serializing ('to_json'). This is
because there might be several Python types that can be coerced into the correct OCPP-JSON type required. Encoders are
responsible for raising a 'TypeConstraintViolationError' error if they cannot process the input.

Encoders are assigned to a dataclass field through its metadata 'encoder' key. Only a single encoder is accepted.
"""
import datetime
import decimal
import typing

import dateutil.parser
import pytz

from ocpp_codec import errors


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
