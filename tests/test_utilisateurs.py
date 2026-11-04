"""Tests du repository utilisateurs."""

import sqlite3
from pathlib import Path

import pytest

from persistance.database import Database
from persistance.repositories.utilisateurs import RepositoryUtilisateurs
from serveur.services.utilisateurs import GestionnaireUtilisateurs


@pytest.fixture
def repository_utilisateurs() -> RepositoryUtilisateurs:
    """Créer un repository connecté à une base isolée."""
    connexion = Database().connecter(":memory:")
    connexion.executescript(Path("persistance/schema.sql").read_text(encoding="utf-8"))
    yield RepositoryUtilisateurs(connexion)
    connexion.close()


@pytest.fixture
def gestionnaire_utilisateurs(
    repository_utilisateurs: RepositoryUtilisateurs,
) -> GestionnaireUtilisateurs:
    return GestionnaireUtilisateurs(repository_utilisateurs)


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
    assert (
        repository_utilisateurs.recuperer_par_identifiant("etudiant@example.test")
        == utilisateur
    )


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


def test_creer_et_authentifier_un_compte(
    gestionnaire_utilisateurs: GestionnaireUtilisateurs,
    repository_utilisateurs: RepositoryUtilisateurs,
) -> None:
    compte = gestionnaire_utilisateurs.creer_compte(
        " etudiant@example.test ",
        "mot-de-passe-solide",
    )

    assert compte["identifiant"] == "etudiant@example.test"
    assert "mot_de_passe" not in compte
    utilisateur_stocke = repository_utilisateurs.recuperer_par_identifiant(
        "etudiant@example.test"
    )
    assert utilisateur_stocke is not None
    assert utilisateur_stocke["mot_de_passe"].startswith("$argon2id$")
    assert (
        gestionnaire_utilisateurs.authentifier_utilisateur(
            "etudiant@example.test",
            "mot-de-passe-solide",
        )
        is True
    )
    assert (
        gestionnaire_utilisateurs.authentifier_utilisateur(
            "etudiant@example.test",
            "mot-de-passe-incorrect",
        )
        is False
    )


def test_refuser_un_compte_duplique(
    gestionnaire_utilisateurs: GestionnaireUtilisateurs,
) -> None:
    gestionnaire_utilisateurs.creer_compte("etudiant", "mot-de-passe-1")

    with pytest.raises(ValueError, match="déjà utilisé"):
        gestionnaire_utilisateurs.creer_compte("etudiant", "mot-de-passe-2")


@pytest.mark.parametrize(
    ("identifiant", "mot_de_passe"),
    (("", "mot-de-passe"), ("etudiant", "court")),
)
def test_refuser_des_identifiants_invalides(
    gestionnaire_utilisateurs: GestionnaireUtilisateurs,
    identifiant: str,
    mot_de_passe: str,
) -> None:
    with pytest.raises(ValueError):
        gestionnaire_utilisateurs.creer_compte(identifiant, mot_de_passe)


def test_recuperer_et_supprimer_un_compte(
    gestionnaire_utilisateurs: GestionnaireUtilisateurs,
) -> None:
    gestionnaire_utilisateurs.creer_compte("etudiant", "mot-de-passe")

    compte = gestionnaire_utilisateurs.recuperer_compte("etudiant")
    assert compte["identifiant"] == "etudiant"
    assert "mot_de_passe" not in compte

    gestionnaire_utilisateurs.supprimer_compte("etudiant")
    assert (
        gestionnaire_utilisateurs.authentifier_utilisateur(
            "etudiant",
            "mot-de-passe",
        )
        is False
    )
    with pytest.raises(ValueError, match="introuvable"):
        gestionnaire_utilisateurs.recuperer_compte("etudiant")


def test_changer_le_mot_de_passe(
    gestionnaire_utilisateurs: GestionnaireUtilisateurs,
) -> None:
    compte = gestionnaire_utilisateurs.creer_compte("etudiant", "ancien-secret")

    gestionnaire_utilisateurs.changer_mot_de_passe(
        compte["id"], "ancien-secret", "nouveau-secret"
    )

    assert (
        gestionnaire_utilisateurs.authentifier_utilisateur("etudiant", "ancien-secret")
        is False
    )
    assert (
        gestionnaire_utilisateurs.authentifier_utilisateur("etudiant", "nouveau-secret")
        is True
    )


def test_refuser_changement_avec_mauvais_secret(
    gestionnaire_utilisateurs: GestionnaireUtilisateurs,
) -> None:
    compte = gestionnaire_utilisateurs.creer_compte("etudiant", "ancien-secret")
    with pytest.raises(ValueError, match="incorrect"):
        gestionnaire_utilisateurs.changer_mot_de_passe(
            compte["id"], "mauvais-secret", "nouveau-secret"
        )


def test_supprimer_compte_apres_verification(
    gestionnaire_utilisateurs: GestionnaireUtilisateurs,
) -> None:
    compte = gestionnaire_utilisateurs.creer_compte("etudiant", "mot-de-passe")
    gestionnaire_utilisateurs.supprimer_compte_authentifie(compte["id"], "mot-de-passe")
    assert (
        gestionnaire_utilisateurs.authentifier_utilisateur("etudiant", "mot-de-passe")
        is False
    )
