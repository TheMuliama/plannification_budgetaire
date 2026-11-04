"""Hachage et vérification des mots de passe avec Argon2id."""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from argon2.low_level import Type


_hacheur = PasswordHasher(type=Type.ID)


def hacher_mot_de_passe(mot_de_passe: str) -> str:
    """Hacher un mot de passe avec un sel aléatoire généré par Argon2.

    La chaîne retournée contient les paramètres, le sel et le hachage.
    Elle peut être conservée dans le champ TEXT prévu en base de données.
    Les règles de validité du mot de passe relèvent du service utilisateurs.

    Args:
        mot_de_passe: Mot de passe à protéger.

    Returns:
        La représentation sécurisée du mot de passe.
    """
    return _hacheur.hash(mot_de_passe)


def verifier_mot_de_passe(mot_de_passe: str, mot_de_passe_hache: str) -> bool:
    """Vérifier un mot de passe contre sa représentation sécurisée.

    Args:
        mot_de_passe: Mot de passe fourni.
        mot_de_passe_hache: Représentation sécurisée de référence.

    Returns:
        True si le mot de passe correspond, False s'il ne correspond pas
        ou si le hachage de référence est invalide.
    """
    try:
        return _hacheur.verify(mot_de_passe_hache, mot_de_passe)
    except (VerificationError, InvalidHashError, UnicodeEncodeError):
        return False
