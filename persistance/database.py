"""Accès à la base de données SQLite."""

import sqlite3


class Database:
    """Gérer les connexions SQLite de l'application.

    Cette classe fournit une connexion configurée pour préserver les relations
    entre les données. Elle ne contient pas de logique métier.
    """

    def connecter(self, chemin: str) -> sqlite3.Connection:
        """Ouvrir une connexion SQLite au chemin indiqué.

        Args:
            chemin: Chemin de la base SQLite à ouvrir.

        Returns:
            La connexion SQLite configurée.
        """
        connexion = sqlite3.connect(chemin)
        connexion.row_factory = sqlite3.Row
        connexion.execute("PRAGMA foreign_keys = ON")
        return connexion

    def fermer(self, connexion: sqlite3.Connection) -> None:
        """Fermer la connexion à la base de données.

        Args:
            connexion: Connexion SQLite à fermer.

        Returns:
            None.
        """
        connexion.close()
