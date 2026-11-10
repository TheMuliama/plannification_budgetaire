"""Tests du gestionnaire des dépenses."""

from pathlib import Path

import pytest

from persistance.database import Database
from persistance.repositories.budgets import RepositoryBudgets
from persistance.repositories.categories import RepositoryCategories
from persistance.repositories.depenses import RepositoryDepenses
from persistance.repositories.objectifs_epargne import RepositoryObjectifsEpargne
from persistance.repositories.revenus import RepositoryRevenus
from serveur.services.budget import GestionnaireBudget
from serveur.services.categories import GestionnaireCategories
from serveur.services.depenses import GestionnaireDepenses
from serveur.services.objectifs_epargne import GestionnaireObjectifsEpargne
from serveur.services.revenus import GestionnaireRevenus


@pytest.fixture
def gestionnaire_depenses() -> GestionnaireDepenses:
    connexion = Database().connecter(":memory:")
    connexion.executescript(Path("persistance/schema.sql").read_text(encoding="utf-8"))
    connexion.executemany(
        "INSERT INTO utilisateurs (identifiant,mot_de_passe) VALUES (?,?)",
        (("u1", "h1"), ("u2", "h2")),
    )
    connexion.executemany(
        "INSERT INTO categories (utilisateur_id,nom) VALUES (?,?)",
        ((1, "Courses"), (2, "Privée")),
    )
    connexion.executemany(
        "INSERT INTO budgets (utilisateur_id,annee,mois,categorie_id,montant_alloue) VALUES (?,?,?,?,?)",
        ((1, 2026, 11, 1, 300), (2, 2026, 11, 2, 500)),
    )
    categories = GestionnaireCategories(RepositoryCategories(connexion))
    revenus = GestionnaireRevenus(RepositoryRevenus(connexion))
    objectifs = GestionnaireObjectifsEpargne(RepositoryObjectifsEpargne(connexion))
    budgets = GestionnaireBudget(
        RepositoryBudgets(connexion), revenus, objectifs, categories
    )
    yield GestionnaireDepenses(RepositoryDepenses(connexion), categories, budgets)
    connexion.close()


def test_gerer_une_depense(gestionnaire_depenses: GestionnaireDepenses) -> None:
    donnees = {
        "utilisateur_id": 1,
        "budget_id": 1,
        "categorie_id": 1,
        "montant": 42.5,
        "date": "2026-11-04",
        "description": " Courses ",
        "statut": "prevue",
    }
    depense = gestionnaire_depenses.ajouter_depense(donnees)
    assert depense["description"] == "Courses"
    modifiee = gestionnaire_depenses.modifier_depense(
        1, depense["id"], {**donnees, "montant": 45, "statut": "realisee"}
    )
    assert modifiee["statut"] == "realisee"
    assert gestionnaire_depenses.consulter_depenses(1, "realisee") == [modifiee]
    gestionnaire_depenses.supprimer_depense(1, depense["id"])
    assert gestionnaire_depenses.consulter_depenses(1) == []


def test_isoler_les_depenses(gestionnaire_depenses: GestionnaireDepenses) -> None:
    with pytest.raises(ValueError, match="Budget"):
        gestionnaire_depenses.ajouter_depense(
            {
                "utilisateur_id": 1,
                "budget_id": 2,
                "categorie_id": 2,
                "montant": 10,
                "date": "2026-11-04",
                "statut": "realisee",
            }
        )


@pytest.mark.parametrize(
    "champ,valeur", (("montant", 0), ("date", "04/11/2026"), ("statut", "payee"))
)
def test_refuser_une_depense_invalide(
    gestionnaire_depenses: GestionnaireDepenses, champ: str, valeur: object
) -> None:
    donnees = {
        "utilisateur_id": 1,
        "budget_id": 1,
        "categorie_id": 1,
        "montant": 10,
        "date": "2026-11-04",
        "statut": "prevue",
    }
    donnees[champ] = valeur
    with pytest.raises(ValueError):
        gestionnaire_depenses.ajouter_depense(donnees)
