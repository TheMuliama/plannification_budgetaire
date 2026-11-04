"""Tests du calcul budgétaire."""

from serveur.services.calcul_budget import CalculateurBudget


def test_calculer_etat_et_enveloppes() -> None:
    calcul = CalculateurBudget()
    budget = {"id": 1, "categorie_id": 2, "montant_alloue": 400, "obligatoire": 0}
    depenses = [
        {"budget_id": 1, "montant": 100, "statut": "realisee"},
        {"budget_id": 1, "montant": 50, "statut": "prevue"},
    ]
    assert calcul.calculer_budget_restant(budget, [], depenses) == 300
    assert (
        calcul.calculer_etat_categorie(budget, depenses)["pourcentage_consomme"] == 25
    )
    assert calcul.calculer_enveloppes_hebdomadaires(budget, depenses) == [
        75,
        75,
        75,
        75,
    ]


def test_exclure_depenses_autres_budgets() -> None:
    assert (
        CalculateurBudget().calculer_budget_restant(
            {"id": 1, "montant_alloue": 100},
            [],
            [{"budget_id": 2, "montant": 80, "statut": "realisee"}],
        )
        == 100
    )
