"""Service de gestion des catégories."""

from typing import Any


class GestionnaireCategories:
    """Gérer les catégories et sous-catégories des utilisateurs.

    Cette classe organise les catégories sans calcul budgétaire.
    """

    def creer_categorie(self, identifiant_utilisateur: int, categorie: dict[str, Any]) -> dict[str, Any]:
        """Créer une catégorie pour un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire.
            categorie: Informations de la catégorie.

        Returns:
            La catégorie créée.
        """
        pass

    def creer_sous_categorie(self, identifiant_categorie: int, sous_categorie: dict[str, Any]) -> dict[str, Any]:
        """Créer une sous-catégorie dans une catégorie.

        Args:
            identifiant_categorie: Identifiant de la catégorie parente.
            sous_categorie: Informations de la sous-catégorie.

        Returns:
            La sous-catégorie créée.
        """
        pass

    def modifier_categorie(self, identifiant_categorie: int, categorie: dict[str, Any]) -> dict[str, Any]:
        """Modifier une catégorie ou une sous-catégorie.

        Args:
            identifiant_categorie: Identifiant de l'élément à modifier.
            categorie: Nouvelles informations de l'élément.

        Returns:
            La catégorie modifiée.
        """
        pass

    def supprimer_categorie(self, identifiant_categorie: int) -> None:
        """Supprimer une catégorie.

        Args:
            identifiant_categorie: Identifiant de la catégorie à supprimer.

        Returns:
            None.
        """
        pass

    def recuperer_categories(self, identifiant_utilisateur: int) -> list[dict[str, Any]]:
        """Récupérer les catégories et sous-catégories d'un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire des catégories.

        Returns:
            La liste des catégories et sous-catégories.
        """
        pass
