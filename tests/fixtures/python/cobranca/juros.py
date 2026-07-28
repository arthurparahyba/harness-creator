"""Cálculo de encargos de cobrança."""

from __future__ import annotations

from decimal import Decimal


def juros_simples(principal: Decimal, taxa: Decimal, dias: int) -> Decimal:
    """Juros pro rata die sobre o principal."""
    return principal * taxa * Decimal(dias) / Decimal(30)


def multa_por_atraso(principal: Decimal, dias: int) -> Decimal:
    if dias <= 0:
        return Decimal(0)
    return principal * Decimal("0.02")
