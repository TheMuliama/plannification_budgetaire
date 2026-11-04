"""Tests isolés du hachage et de la vérification des mots de passe."""

import pytest
from argon2 import PasswordHasher

from serveur.securite.mots_de_passe import (
    hacher_mot_de_passe,
    verifier_mot_de_passe,
)


@pytest.fixture
def mot_de_passe_hache() -> str:
    """Produire un hachage réel à partir d'un mot de passe fictif."""
    return hacher_mot_de_passe("Exemple-fictif-302!")


def test_hacher_avec_argon2id(mot_de_passe_hache: str) -> None:
    """Produire un hachage Argon2id utilisable par la bibliothèque."""
    assert mot_de_passe_hache.startswith("$argon2id$")
    assert mot_de_passe_hache != "Exemple-fictif-302!"
    assert PasswordHasher().verify(mot_de_passe_hache, "Exemple-fictif-302!")


def test_verifier_le_bon_mot_de_passe(mot_de_passe_hache: str) -> None:
    """Accepter le mot de passe qui a servi au hachage."""
    assert verifier_mot_de_passe("Exemple-fictif-302!", mot_de_passe_hache) is True


@pytest.mark.parametrize("mot_de_passe", ["Incorrect-302!", "exemple-fictif-302!", ""])
def test_refuser_un_mauvais_mot_de_passe(
    mot_de_passe: str, mot_de_passe_hache: str
) -> None:
    """Refuser les mots de passe différents, y compris une différence de casse."""
    assert verifier_mot_de_passe(mot_de_passe, mot_de_passe_hache) is False


def test_utiliser_un_sel_aleatoire() -> None:
    """Obtenir deux hachages différents qui vérifient le même mot de passe."""
    premier_hachage = hacher_mot_de_passe("Exemple-fictif-302!")
    second_hachage = hacher_mot_de_passe("Exemple-fictif-302!")

    assert premier_hachage != second_hachage
    assert verifier_mot_de_passe("Exemple-fictif-302!", premier_hachage) is True
    assert verifier_mot_de_passe("Exemple-fictif-302!", second_hachage) is True


def test_preserver_unicode_et_espaces() -> None:
    """Vérifier le texte exact sans supprimer les espaces ni les accents."""
    mot_de_passe = "  Épargne-fictive-302! 🔐  "
    hachage = hacher_mot_de_passe(mot_de_passe)

    assert verifier_mot_de_passe(mot_de_passe, hachage) is True
    assert verifier_mot_de_passe(mot_de_passe.strip(), hachage) is False


@pytest.mark.parametrize(
    "hachage_invalide",
    ["", "Exemple-fictif-302!", "$argon2id$invalide", "hachage-invalide-é"],
)
def test_refuser_un_hachage_invalide(hachage_invalide: str) -> None:
    """Retourner False pour un hachage mal formé ou une valeur en clair."""
    assert verifier_mot_de_passe("Exemple-fictif-302!", hachage_invalide) is False


def test_refuser_un_hachage_tronque(mot_de_passe_hache: str) -> None:
    """Refuser un hachage réel dont la partie finale a été supprimée."""
    assert (
        verifier_mot_de_passe(
            "Exemple-fictif-302!", mot_de_passe_hache.rsplit("$", 1)[0]
        )
        is False
    )
