"""Tests du gestionnaire de budgets."""

from pathlib import Path

import pytest

from persistance.database import Database
from persistance.repositories.budgets import RepositoryBudgets
from persistance.repositories.categories import RepositoryCategories
from persistance.repositories.objectifs_epargne import RepositoryObjectifsEpargne
from persistance.repositories.revenus import RepositoryRevenus
from serveur.services.budget import GestionnaireBudget
from serveur.services.categories import GestionnaireCategories
from serveur.services.objectifs_epargne import GestionnaireObjectifsEpargne
from serveur.services.revenus import GestionnaireRevenus


@pytest.fixture
def gestionnaire_budget() -> GestionnaireBudget:
    connexion = Database().connecter(":memory:")
    connexion.executescript(Path("persistance/schema.sql").read_text(encoding="utf-8"))
    connexion.executemany(
        "INSERT INTO utilisateurs (identifiant,mot_de_passe) VALUES (?,?)",
        (("u1", "h1"), ("u2", "h2")),
    )
    connexion.executemany(
        "INSERT INTO categories (utilisateur_id,nom) VALUES (?,?)",
        ((1, "Alimentation"), (2, "Privée")),
    )
    categories = GestionnaireCategories(RepositoryCategories(connexion))
    revenus = GestionnaireRevenus(RepositoryRevenus(connexion))
    objectifs = GestionnaireObjectifsEpargne(RepositoryObjectifsEpargne(connexion))
    yield GestionnaireBudget(
        RepositoryBudgets(connexion), revenus, objectifs, categories
    )
    connexion.close()


def test_gerer_un_budget_mensuel(gestionnaire_budget: GestionnaireBudget) -> None:
    donnees = {
        "utilisateur_id": 1,
        "annee": 2026,
        "mois": 11,
        "categorie_id": 1,
        "montant_alloue": 300,
        "obligatoire": True,
    }
    budget = gestionnaire_budget.creer_budget(donnees)
    assert budget["montant_alloue"] == 300
    assert gestionnaire_budget.consulter_budget(1, 2026, 11) == [budget]
    modifie = gestionnaire_budget.modifier_budget(
        1, budget["id"], {**donnees, "montant_alloue": 350}
    )
    assert modifie["montant_alloue"] == 350
    gestionnaire_budget.supprimer_budget(1, budget["id"])
    assert gestionnaire_budget.consulter_budget(1) == []


def test_isoler_les_budgets(gestionnaire_budget: GestionnaireBudget) -> None:
    with pytest.raises(ValueError, match="Catégorie"):
        gestionnaire_budget.creer_budget(
            {
                "utilisateur_id": 1,
                "annee": 2026,
                "mois": 11,
                "categorie_id": 2,
                "montant_alloue": 10,
            }
        )


@pytest.mark.parametrize(
    "champ,valeur", (("mois", 13), ("annee", 1999), ("montant_alloue", -1))
)
def test_refuser_un_budget_invalide(
    gestionnaire_budget: GestionnaireBudget, champ: str, valeur: int
) -> None:
    donnees = {
        "utilisateur_id": 1,
        "annee": 2026,
        "mois": 11,
        "categorie_id": 1,
        "montant_alloue": 300,
    }
    donnees[champ] = valeur
    with pytest.raises(ValueError):
        gestionnaire_budget.creer_budget(donnees)
