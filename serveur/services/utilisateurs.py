"""Service de gestion des comptes utilisateurs."""

import sqlite3
from typing import Any

from persistance.repositories.utilisateurs import RepositoryUtilisateurs
from serveur.securite.mots_de_passe import hacher_mot_de_passe, verifier_mot_de_passe


class GestionnaireUtilisateurs:
    """Gérer les comptes utilisateurs et leur authentification.

    Cette classe gère les comptes et l'accès associé. Elle ne contient pas
    de logique financière.
    """

    def __init__(self, repository: RepositoryUtilisateurs) -> None:
        self._repository = repository

    def creer_compte(
        self,
        identifiant: str,
        mot_de_passe: str,
        donnees_compte: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Créer un compte utilisateur.

        Args:
            identifiant: Identifiant du compte.
            mot_de_passe: Mot de passe du compte.
            donnees_compte: Informations complémentaires du compte.

        Returns:
            Le compte créé.
        """
        identifiant_normalise = self._valider_identifiant(identifiant)
        self._valider_mot_de_passe(mot_de_passe)
        try:
            utilisateur = self._repository.creer_utilisateur(
                identifiant_normalise,
                hacher_mot_de_passe(mot_de_passe),
            )
        except sqlite3.IntegrityError as erreur:
            raise ValueError("Cet identifiant est déjà utilisé.") from erreur
        return self._sans_mot_de_passe(utilisateur)

    def authentifier_utilisateur(self, identifiant: str, mot_de_passe: str) -> bool:
        """Authentifier un utilisateur à partir de ses identifiants.

        Args:
            identifiant: Identifiant de l'utilisateur.
            mot_de_passe: Mot de passe fourni.

        Returns:
            Le résultat de l'authentification.
        """
        if not isinstance(identifiant, str) or not isinstance(mot_de_passe, str):
            return False
        utilisateur = self._repository.recuperer_par_identifiant(identifiant.strip())
        if utilisateur is None:
            return False
        return verifier_mot_de_passe(mot_de_passe, utilisateur["mot_de_passe"])

    def supprimer_compte(self, identifiant: str) -> None:
        """Supprimer le compte associé à un identifiant.

        Args:
            identifiant: Identifiant du compte à supprimer.

        Returns:
            None.
        """
        utilisateur = self._repository.recuperer_par_identifiant(
            self._valider_identifiant(identifiant)
        )
        if utilisateur is None or not self._repository.supprimer_utilisateur(utilisateur["id"]):
            raise ValueError("Compte utilisateur introuvable.")

    def recuperer_compte(self, identifiant: str) -> dict[str, Any]:
        """Récupérer les informations nécessaires d'un compte.

        Args:
            identifiant: Identifiant du compte recherché.

        Returns:
            Les informations du compte.
        """
        utilisateur = self._repository.recuperer_par_identifiant(
            self._valider_identifiant(identifiant)
        )
        if utilisateur is None:
            raise ValueError("Compte utilisateur introuvable.")
        return self._sans_mot_de_passe(utilisateur)

    @staticmethod
    def _valider_identifiant(identifiant: str) -> str:
        if not isinstance(identifiant, str) or not identifiant.strip():
            raise ValueError("L'identifiant est obligatoire.")
        return identifiant.strip()

    @staticmethod
    def _valider_mot_de_passe(mot_de_passe: str) -> None:
        if not isinstance(mot_de_passe, str) or len(mot_de_passe) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères.")

    @staticmethod
    def _sans_mot_de_passe(utilisateur: dict[str, Any]) -> dict[str, Any]:
        return {
            cle: valeur
            for cle, valeur in utilisateur.items()
            if cle != "mot_de_passe"
        }
