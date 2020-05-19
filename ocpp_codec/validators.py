# Copyright (c) Polyconseil SAS. All rights reserved.
"""Collection of functions that can be used to validate OCPP input.

Validators take an input and validate it without altering its typing. They should raise an appropriate instance of a
'BaseOCPPError' if the input value does not meet the appropriate criteria. Validators are written so that they return
their input, but there's no use for it for now.

Validators shouldn't run any type checking, this is taken care of before they're called.

Validators are responsible for raising a 'TypeConstraintViolationError' error if they cannot process the input.

Validators are assigned to a dataclass field through its metadata 'validators' key. A single validator can be provided,
or several in a list.
"""
import functools
import re
import typing

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
