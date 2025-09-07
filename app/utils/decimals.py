# app/utils/decimals.py
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Tuple, Union

NumberLike = Union[Decimal, float, int, str]


def to_dec(x: NumberLike) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))


def field_quant_and_limit(model, field_name: str) -> Tuple[Decimal, Decimal]:
    """
    Возвращает (квант, лимит) для DecimalField.
    квант = 10^-decimal_places
    лимит = 10^(max_digits - decimal_places)  (т.е. |value| < лимит)
    """
    f = model._meta.fields_map[field_name]  # DecimalField
    quant = Decimal(1).scaleb(-f.decimal_places)
    limit = Decimal(10) ** (f.max_digits - f.decimal_places)
    return quant, limit


def quantize_to_field(model, field_name: str, value: NumberLike) -> Decimal:
    quant, _ = field_quant_and_limit(model, field_name)
    return to_dec(value).quantize(quant, rounding=ROUND_HALF_UP)
