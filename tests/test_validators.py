# Copyright (c) Polyconseil SAS. All rights reserved.
import datetime
import enum

import pytest
import pytz

from ocpp_codec import errors
from ocpp_codec import validators


def test_build_simple_validator():
    def validator_func(arg, value):
        return arg, value

    validator = validators.build_simple_validator(validator_func, 'arg')
    assert validator.__name__ == 'validator_func'
    assert validator('test') == ('arg', 'test')


def test_noop():
    assert validators.noop('value') == 'value'


def test_max_length_validators():
    with pytest.raises(errors.PropertyConstraintViolationError):
        validators.max_length(10, 'a' * 11)
    assert validators.max_length(10, 'a' * 10) == 'a' * 10

    # Make sure the prepared validators were correctly defined
    # 20
    with pytest.raises(errors.PropertyConstraintViolationError):
        validators.max_length_20('a' * 21)
    assert validators.max_length_20('a' * 20) == 'a' * 20
    # 25
    with pytest.raises(errors.PropertyConstraintViolationError):
        validators.max_length_25('a' * 26)
    assert validators.max_length_25('a' * 25) == 'a' * 25
    # 36
    with pytest.raises(errors.PropertyConstraintViolationError):
        validators.max_length_36('a' * 37)
    assert validators.max_length_36('a' * 36) == 'a' * 36
    # 50
    with pytest.raises(errors.PropertyConstraintViolationError):
        validators.max_length_50('a' * 51)
    assert validators.max_length_50('a' * 50) == 'a' * 50
    # 255
    with pytest.raises(errors.PropertyConstraintViolationError):
        validators.max_length_255('a' * 256)
    assert validators.max_length_255('a' * 255) == 'a' * 255
    # 500
    with pytest.raises(errors.PropertyConstraintViolationError):
        validators.max_length_500('a' * 501)
    assert validators.max_length_500('a' * 500) == 'a' * 500


def test_decimal_precision_validators():
    with pytest.raises(errors.PropertyConstraintViolationError):
        validators.decimal_validator(1, 1.23)
    assert validators.decimal_validator(1, 1.2) == 1.2

    # Make sure the prepared validators were correctly defined
    with pytest.raises(errors.PropertyConstraintViolationError):
        validators.decimal_precision_1(1.23)
    assert validators.decimal_precision_1(1.2) == 1.2


def test_is_positive_validators():
    with pytest.raises(errors.PropertyConstraintViolationError):
        validators.is_positive(-1)
    assert validators.is_positive(0) == 0
    assert validators.is_positive(1) == 1

    with pytest.raises(errors.PropertyConstraintViolationError):
        assert validators.is_not_zero(0)
    assert validators.is_not_zero(-1) == -1
    assert validators.is_not_zero(1) == 1

    with pytest.raises(errors.PropertyConstraintViolationError):
        validators.is_strictly_positive(-1)
    with pytest.raises(errors.PropertyConstraintViolationError):
        validators.is_strictly_positive(0)
    assert validators.is_strictly_positive(1) == 1


def test_is_identifier():
    with pytest.raises(errors.PropertyConstraintViolationError):
        validators.is_identifier('!#$%^&()')
    assert validators.is_identifier('Id06-@') == 'Id06-@'


def test_datetime_encoder():
    encoder = validators.DateTimeEncoder()

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

    encoder = validators.EnumEncoder(TestEnum)

    with pytest.raises(errors.PropertyConstraintViolationError):
        encoder.from_json(123)
    assert encoder.from_json(1) == TestEnum.A
    assert encoder.from_json('b') == TestEnum.B

    with pytest.raises(errors.TypeConstraintViolationError):
        encoder.to_json('well thats not an enum')
    assert encoder.to_json(TestEnum.A) == 1
    assert encoder.to_json(TestEnum.B) == 'b'


def test_outgoing_message_decimal_encoder():
    encoder = validators.OutgoingMessageDecimalEncoder()

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


def test_compound_validator():
    validator = validators.compound_validator(validators.is_positive, validators.decimal_precision_1)
    with pytest.raises(errors.PropertyConstraintViolationError):
        validator(-2.1)
    with pytest.raises(errors.PropertyConstraintViolationError):
        validator(2.12)
    assert validator(2.1) == 2.1
