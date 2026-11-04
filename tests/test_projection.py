"""Tests du moteur de projection."""

from serveur.services.projection import MoteurProjection


def test_projeter_depense_sans_modifier_etat() -> None:
    etat = {"budget_restant": 100, "budget_flexible": 80}
    moteur = MoteurProjection()
    resultat = moteur.simuler_ajout_depense(
        etat, {"montant": 120}, {"montant_periodique": 50}
    )
    assert resultat["budget_restant_projete"] == -20
    assert moteur.determiner_consequences(resultat)["budget_depasse"] is True
    assert etat == {"budget_restant": 100, "budget_flexible": 80}
