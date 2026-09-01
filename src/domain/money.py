"""Monetary arithmetic.

Money is never a float here. Binary floating point cannot represent most decimal
amounts exactly, and Python's built-in `round` breaks ties toward the even digit,
while invoicing rounds ties away from zero. Both effects are invisible on one line
and wrong by cents across an invoice.

Every amount entering the domain passes through `to_money`, so there is exactly one
place where the rounding policy is defined.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Union

CENTS = Decimal("0.01")

MoneyInput = Union[Decimal, int, float, str]


def to_money(value: MoneyInput) -> Decimal:
    """Returns the amount as a Decimal quantised to two places, rounding half up.

    A float is converted through its string form first: `Decimal(0.1)` inherits the
    binary approximation, `Decimal("0.1")` does not. Accepting floats at the boundary
    keeps existing callers working; the domain still stores Decimal.
    """
    if isinstance(value, float):
        value = repr(value)
    return Decimal(value).quantize(CENTS, rounding=ROUND_HALF_UP)


def multiply(amount: Decimal, quantity: int) -> Decimal:
    """Multiplies a unit price by a whole quantity and quantises once, at the end."""
    return to_money(amount * Decimal(quantity))


def apply_rate(base: Decimal, rate: Decimal) -> Decimal:
    """Applies a tax rate and quantises once, at the end.

    Quantising the operands before multiplying would round twice and drift.
    """
    return to_money(base * rate)
