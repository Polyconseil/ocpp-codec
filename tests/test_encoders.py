# Copyright (c) Polyconseil SAS. All rights reserved.
import datetime
import enum

import pytest
import pytz

from ocpp_codec import encoders
from ocpp_codec import errors


def test_datetime_encoder():
    encoder = encoders.DateTimeEncoder()

    with pytest.raises(errors.PropertyConstraintViolationError):
        encoder.from_json('well thats not a date')
    # Date must be UTC
    with pytest.raises(errors.PropertyConstraintViolationError):
        encoder.from_json('2019-03-21T12:00:00+01:00')
    dt = datetime.datetime(year=2019, month=3, day=21, hour=12, tzinfo=pytz.UTC)
    # Naive dates are considered UTC
    assert encoder.from_json('2019-03-21T12:00:00') == dt
    # Proper UTC formatting
    assert encoder.from_json('2019-03-21T12:00:00+00:00') == dt
    assert encoder.from_json('2019-03-21T12:00:00Z') == dt

    with pytest.raises(errors.TypeConstraintViolationError):
        encoder.to_json('well thats not a date')
    # Naive datetime
    with pytest.raises(errors.PropertyConstraintViolationError):
        encoder.to_json(datetime.datetime(year=2019, month=3, day=21, hour=12))
    # Wrong tzinfo
    with pytest.raises(errors.PropertyConstraintViolationError):
        encoder.to_json(
            datetime.datetime(year=2019, month=3, day=21, hour=12, tzinfo=pytz.timezone('Europe/Paris'))
        )
    assert (
        encoder.to_json(datetime.datetime(year=2019, month=3, day=21, hour=12, tzinfo=pytz.UTC))
        == '2019-03-21T12:00:00+00:00'
    )


def test_enum_encoder():
    class TestEnum(enum.Enum):
        A = 1
        B = 'b'

    encoder = encoders.EnumEncoder(TestEnum)

    with pytest.raises(errors.PropertyConstraintViolationError):
        encoder.from_json(123)
    assert encoder.from_json(1) == TestEnum.A
    assert encoder.from_json('b') == TestEnum.B

    with pytest.raises(errors.TypeConstraintViolationError):
        encoder.to_json('well thats not an enum')
    assert encoder.to_json(TestEnum.A) == 1
    assert encoder.to_json(TestEnum.B) == 'b'


def test_outgoing_message_decimal_encoder():
    encoder = encoders.OutgoingMessageDecimalEncoder()

    assert encoder.from_json(1.123456789) == 1.123456789

    with pytest.raises(errors.TypeConstraintViolationError):
        encoder.to_json('well thats not a float')
    with pytest.raises(errors.TypeConstraintViolationError):
        # Too big
        assert encoder.to_json('112345599999999994030193027055616.1234567890')

    assert encoder.to_json('1.12') == 1.12
    assert encoder.to_json('1.123456789') == 1.123456
    assert encoder.to_json('0.00001') == 1e-05
    assert encoder.to_json('1e-05') == 1e-05
