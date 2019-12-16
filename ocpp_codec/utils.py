# Copyright (c) Polyconseil SAS. All rights reserved.
import enum


class AutoNameEnum(enum.Enum):
    """Modifies the behaviour of 'enum.auto()' to return the enum's name.

    Example:

        class PizzaTopping(AutoNameEnum):
            pineapple = enum.auto()

        >>> PizzaTopping('pineapple')
        <PizzaTopping.pineapple: 'pineapple'>
    """
    # Copied from https://docs.python.org/3/library/enum.html#using-automatic-values
    # pylint: disable=no-self-argument
    def _generate_next_value_(name, start, count, last_values):
        return name
