"""Contrat d'accès à la base de données."""

from typing import Any


class Database:
    """Définir l'accès à la base de données de l'application.

    Cette classe ne contient pas de modèle de données ni de requête SQL dans
    le squelette architectural.
    """

    def connecter(self, chemin: str) -> Any:
        """Établir une connexion à la base désignée.

        Args:
            chemin: Emplacement de la base de données.

        Returns:
            La connexion à la base de données.
        """
        pass

    def fermer(self) -> None:
        """Fermer la connexion à la base de données.

        Returns:
            None.
        """
        pass
