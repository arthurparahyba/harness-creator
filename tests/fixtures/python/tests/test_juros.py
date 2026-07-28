from decimal import Decimal

from cobranca.juros import multa_por_atraso


def test_multa_zero_sem_atraso() -> None:
    assert multa_por_atraso(Decimal(100), 0) == Decimal(0)
