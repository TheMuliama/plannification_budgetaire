"""Tests du repository utilisateurs."""

import sqlite3
from pathlib import Path

import pytest

from persistance.database import Database
from persistance.repositories.utilisateurs import RepositoryUtilisateurs


@pytest.fixture
def repository_utilisateurs() -> RepositoryUtilisateurs:
    """Créer un repository connecté à une base isolée."""
    connexion = Database().connecter(":memory:")
    connexion.executescript(Path("persistance/schema.sql").read_text(encoding="utf-8"))
    yield RepositoryUtilisateurs(connexion)
    connexion.close()


def test_creer_et_recuperer_un_utilisateur(
    repository_utilisateurs: RepositoryUtilisateurs,
) -> None:
    utilisateur = repository_utilisateurs.creer_utilisateur(
        "etudiant@example.test",
        "hachage-fictif",
    )

    assert utilisateur["id"] > 0
    assert utilisateur["identifiant"] == "etudiant@example.test"
    assert utilisateur["mot_de_passe"] == "hachage-fictif"
    assert repository_utilisateurs.recuperer_par_id(utilisateur["id"]) == utilisateur
    assert repository_utilisateurs.recuperer_par_identifiant(
        "etudiant@example.test"
    ) == utilisateur


def test_refuser_un_identifiant_duplique(
    repository_utilisateurs: RepositoryUtilisateurs,
) -> None:
    repository_utilisateurs.creer_utilisateur("meme@example.test", "hachage-1")

    with pytest.raises(sqlite3.IntegrityError):
        repository_utilisateurs.creer_utilisateur("meme@example.test", "hachage-2")


def test_supprimer_un_utilisateur(
    repository_utilisateurs: RepositoryUtilisateurs,
) -> None:
    utilisateur = repository_utilisateurs.creer_utilisateur("a-supprimer", "hachage")

    assert repository_utilisateurs.supprimer_utilisateur(utilisateur["id"]) is True
    assert repository_utilisateurs.recuperer_par_id(utilisateur["id"]) is None
    assert repository_utilisateurs.supprimer_utilisateur(utilisateur["id"]) is False


def test_retourner_none_pour_un_utilisateur_absent(
    repository_utilisateurs: RepositoryUtilisateurs,
) -> None:
    assert repository_utilisateurs.recuperer_par_id(999) is None
    assert repository_utilisateurs.recuperer_par_identifiant("absent") is None
