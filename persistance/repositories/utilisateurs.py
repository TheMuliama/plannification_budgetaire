"""Accès aux données des utilisateurs."""

import sqlite3
from typing import Any


class RepositoryUtilisateurs:
    """Persister les comptes sans appliquer les règles d'authentification."""

    def __init__(self, connexion: sqlite3.Connection) -> None:
        self._connexion = connexion

    def creer_utilisateur(self, identifiant: str, mot_de_passe_hache: str) -> dict[str, Any]:
        """Créer un utilisateur et retourner la ligne enregistrée."""
        with self._connexion:
            curseur = self._connexion.execute(
                "INSERT INTO utilisateurs (identifiant, mot_de_passe) VALUES (?, ?)",
                (identifiant, mot_de_passe_hache),
            )
        identifiant_utilisateur = curseur.lastrowid
        assert identifiant_utilisateur is not None
        utilisateur = self.recuperer_par_id(identifiant_utilisateur)
        assert utilisateur is not None
        return utilisateur

    def recuperer_par_id(self, identifiant_utilisateur: int) -> dict[str, Any] | None:
        """Récupérer un utilisateur par sa clé primaire."""
        ligne = self._connexion.execute(
            "SELECT id, identifiant, mot_de_passe, date_creation "
            "FROM utilisateurs WHERE id = ?",
            (identifiant_utilisateur,),
        ).fetchone()
        return dict(ligne) if ligne is not None else None

    def recuperer_par_identifiant(self, identifiant: str) -> dict[str, Any] | None:
        """Récupérer un utilisateur par son identifiant de connexion."""
        ligne = self._connexion.execute(
            "SELECT id, identifiant, mot_de_passe, date_creation "
            "FROM utilisateurs WHERE identifiant = ?",
            (identifiant,),
        ).fetchone()
        return dict(ligne) if ligne is not None else None

    def supprimer_utilisateur(self, identifiant_utilisateur: int) -> bool:
        """Supprimer un utilisateur et indiquer si une ligne existait."""
        with self._connexion:
            curseur = self._connexion.execute(
                "DELETE FROM utilisateurs WHERE id = ?",
                (identifiant_utilisateur,),
            )
        return curseur.rowcount > 0

    def modifier_mot_de_passe(self, identifiant_utilisateur: int,
                              mot_de_passe_hache: str) -> bool:
        """Remplacer le hachage du mot de passe d'un utilisateur."""
        with self._connexion:
            curseur = self._connexion.execute(
                "UPDATE utilisateurs SET mot_de_passe = ? WHERE id = ?",
                (mot_de_passe_hache, identifiant_utilisateur),
            )
        return curseur.rowcount > 0
