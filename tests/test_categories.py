"""Tests du service de gestion des catégories."""

from pathlib import Path

import pytest

from persistance.database import Database
from persistance.repositories.categories import RepositoryCategories
from serveur.services.categories import GestionnaireCategories


@pytest.fixture
def gestionnaire_categories() -> GestionnaireCategories:
    """Créer un gestionnaire connecté à une base SQLite en mémoire.

    Yields:
        Un gestionnaire de catégories prêt pour les tests.
    """
    connexion = Database().connecter(":memory:")
    schema = Path("persistance/schema.sql").read_text(encoding="utf-8")
    connexion.executescript(schema)
    yield GestionnaireCategories(RepositoryCategories(connexion))
    connexion.close()


def test_creer_et_recuperer_une_categorie(gestionnaire_categories: GestionnaireCategories) -> None:
    """Vérifier qu'une catégorie créée peut être récupérée par son propriétaire."""
    categorie = gestionnaire_categories.creer_categorie(1, "Alimentation")

    categorie_recuperee = gestionnaire_categories.recuperer_categorie(1, categorie["id"])

    assert categorie_recuperee == categorie


def test_recuperer_les_categories_d_un_utilisateur(gestionnaire_categories: GestionnaireCategories) -> None:
    """Vérifier que la liste retourne toutes les catégories du propriétaire."""
    gestionnaire_categories.creer_categorie(1, "Alimentation")
    gestionnaire_categories.creer_categorie(1, "Transport")

    categories = gestionnaire_categories.recuperer_categories(1)

    assert [categorie["nom"] for categorie in categories] == ["Alimentation", "Transport"]


def test_modifier_une_categorie(gestionnaire_categories: GestionnaireCategories) -> None:
    """Vérifier que le nom d'une catégorie peut être modifié."""
    categorie = gestionnaire_categories.creer_categorie(1, "Courses")

    categorie_modifiee = gestionnaire_categories.modifier_categorie(1, categorie["id"], "Alimentation")

    assert categorie_modifiee["nom"] == "Alimentation"


def test_supprimer_une_categorie(gestionnaire_categories: GestionnaireCategories) -> None:
    """Vérifier qu'une catégorie supprimée n'est plus récupérable."""
    categorie = gestionnaire_categories.creer_categorie(1, "Loisirs")

    gestionnaire_categories.supprimer_categorie(1, categorie["id"])

    with pytest.raises(ValueError):
        gestionnaire_categories.recuperer_categorie(1, categorie["id"])


def test_creer_et_recuperer_des_sous_categories(gestionnaire_categories: GestionnaireCategories) -> None:
    """Vérifier que les sous-catégories sont rattachées à leur catégorie."""
    categorie = gestionnaire_categories.creer_categorie(1, "Alimentation")
    gestionnaire_categories.creer_sous_categorie(1, categorie["id"], "Marché")
    gestionnaire_categories.creer_sous_categorie(1, categorie["id"], "Restaurant")

    sous_categories = gestionnaire_categories.recuperer_sous_categories(1, categorie["id"])

    assert [sous_categorie["nom"] for sous_categorie in sous_categories] == ["Marché", "Restaurant"]


def test_modifier_une_sous_categorie(gestionnaire_categories: GestionnaireCategories) -> None:
    """Vérifier que le nom d'une sous-catégorie peut être modifié."""
    categorie = gestionnaire_categories.creer_categorie(1, "Transport")
    sous_categorie = gestionnaire_categories.creer_sous_categorie(1, categorie["id"], "Bus")

    sous_categorie_modifiee = gestionnaire_categories.modifier_sous_categorie(
        1,
        categorie["id"],
        sous_categorie["id"],
        "Train",
    )

    assert sous_categorie_modifiee["nom"] == "Train"


def test_supprimer_une_sous_categorie(gestionnaire_categories: GestionnaireCategories) -> None:
    """Vérifier qu'une sous-catégorie supprimée n'est plus listée."""
    categorie = gestionnaire_categories.creer_categorie(1, "Logement")
    sous_categorie = gestionnaire_categories.creer_sous_categorie(1, categorie["id"], "Loyer")

    gestionnaire_categories.supprimer_sous_categorie(1, categorie["id"], sous_categorie["id"])

    assert gestionnaire_categories.recuperer_sous_categories(1, categorie["id"]) == []


def test_isoler_les_categories_par_utilisateur(gestionnaire_categories: GestionnaireCategories) -> None:
    """Vérifier qu'un utilisateur ne récupère pas les catégories d'un autre."""
    categorie_utilisateur_un = gestionnaire_categories.creer_categorie(1, "Alimentation")
    categorie_utilisateur_deux = gestionnaire_categories.creer_categorie(2, "Voyages")

    assert gestionnaire_categories.recuperer_categories(1) == [categorie_utilisateur_un]
    assert gestionnaire_categories.recuperer_categories(2) == [categorie_utilisateur_deux]
    with pytest.raises(ValueError):
        gestionnaire_categories.recuperer_categorie(2, categorie_utilisateur_un["id"])
