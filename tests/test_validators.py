# Copyright (c) Polyconseil SAS. All rights reserved.
import pytest

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


def test_is_identifier():
    with pytest.raises(errors.PropertyConstraintViolationError):
        validators.is_identifier('!#$%^&()')
    assert validators.is_identifier('Id06-@') == 'Id06-@'
