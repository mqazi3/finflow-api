"""Money types shared by the request and response schemas.

Amounts are handled as Decimal end to end so cents never drift the way
floats do (0.1 + 0.2 != 0.3). JSON responses still render them as plain
numbers, so API clients see the same shape as before.
"""
from decimal import Decimal
from typing import Annotated

from pydantic import Field, PlainSerializer


# Incoming amounts: at most 2 decimal places and 12 digits in total,
# matching the Numeric(12, 2) database columns.
MoneyIn = Annotated[Decimal, Field(max_digits=12, decimal_places=2)]

# Outgoing amounts: exact Decimal internally, a JSON number on the wire.
Money = Annotated[
    Decimal,
    PlainSerializer(float, return_type=float, when_used="json"),
]
