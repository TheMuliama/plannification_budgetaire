"""Service de gestion du budget mensuel."""

from typing import Any


class GestionnaireBudget:
    """Construire et gérer le budget mensuel structuré.

    Cette classe gère les allocations, y compris l'épargne prévue comme
    catégorie spéciale. Elle ne calcule pas le budget restant ni les
    projections futures.
    """

    def creer_budget(self, budget: dict[str, Any]) -> dict[str, Any]:
        """Créer un budget mensuel structuré.

        Args:
            budget: Informations du budget, dont l'épargne prévue.

        Returns:
            Le budget créé.
        """
        pass

    def modifier_budget(self, identifiant_budget: int, budget: dict[str, Any]) -> dict[str, Any]:
        """Modifier un budget mensuel.

        Args:
            identifiant_budget: Identifiant du budget à modifier.
            budget: Nouvelles informations du budget.

        Returns:
            Le budget modifié.
        """
        pass

    def consulter_budget(self, identifiant_utilisateur: int) -> dict[str, Any]:
        """Consulter le budget mensuel d'un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire du budget.

        Returns:
            Le budget mensuel structuré.
        """
        pass

    def gerer_allocation(self, identifiant_budget: int, allocation: dict[str, Any]) -> dict[str, Any]:
        """Gérer une allocation par catégorie ou sous-catégorie.

        Args:
            identifiant_budget: Identifiant du budget concerné.
            allocation: Informations de l'allocation à gérer.

        Returns:
            L'allocation enregistrée.
        """
        pass
