"""Contrats de gestion des mots de passe."""


def hacher_mot_de_passe(mot_de_passe: str) -> str:
    """Produire la représentation sécurisée d'un mot de passe.

    Args:
        mot_de_passe: Mot de passe à protéger.

    Returns:
        La représentation sécurisée du mot de passe.
    """
    pass


def verifier_mot_de_passe(mot_de_passe: str, mot_de_passe_hache: str) -> bool:
    """Vérifier un mot de passe contre sa représentation sécurisée.

    Args:
        mot_de_passe: Mot de passe fourni.
        mot_de_passe_hache: Représentation sécurisée de référence.

    Returns:
        Le résultat de la vérification.
    """
    pass
