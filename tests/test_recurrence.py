"""Tests de génération des transactions récurrentes."""

from datetime import date

import pytest

from client.recurrence import dates_recurrentes


def test_generer_recurrence_mensuelle_en_fin_de_mois() -> None:
    assert dates_recurrentes(date(2026, 1, 31), "Mensuelle", date(2026, 4, 30)) == [
        date(2026, 1, 31), date(2026, 2, 28), date(2026, 3, 31), date(2026, 4, 30)
    ]


def test_generer_recurrence_hebdomadaire() -> None:
    assert dates_recurrentes(date(2026, 11, 1), "Hebdomadaire", date(2026, 11, 20)) == [
        date(2026, 11, 1), date(2026, 11, 8), date(2026, 11, 15)
    ]


def test_refuser_recurrence_sans_fin() -> None:
    with pytest.raises(ValueError, match="date de fin"):
        dates_recurrentes(date(2026, 11, 1), "Mensuelle", None)
