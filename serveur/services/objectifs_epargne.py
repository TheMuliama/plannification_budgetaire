"""Service de gestion des objectifs d'épargne."""

from typing import Any


class GestionnaireObjectifsEpargne:
    """Gérer les objectifs d'épargne et leurs plans associés.

    Cette classe prépare le suivi et les scénarios de réajustement sans
    prendre de décision automatique à la place de l'utilisateur.
    """

    def creer_objectif(self, objectif: dict[str, Any]) -> dict[str, Any]:
        """Créer un objectif d'épargne.

        Args:
            objectif: Paramètres de l'objectif à créer.

        Returns:
            L'objectif créé.
        """
        pass

    def modifier_objectif(self, identifiant_objectif: int, objectif: dict[str, Any]) -> dict[str, Any]:
        """Modifier un objectif d'épargne.

        Args:
            identifiant_objectif: Identifiant de l'objectif à modifier.
            objectif: Nouvelles informations de l'objectif.

        Returns:
            L'objectif modifié.
        """
        pass

    def supprimer_objectif(self, identifiant_objectif: int) -> None:
        """Supprimer un objectif d'épargne.

        Args:
            identifiant_objectif: Identifiant de l'objectif à supprimer.

        Returns:
            None.
        """
        pass

    def consulter_objectif(self, identifiant_objectif: int) -> dict[str, Any]:
        """Consulter un objectif d'épargne.

        Args:
            identifiant_objectif: Identifiant de l'objectif recherché.

        Returns:
            Les informations de l'objectif.
        """
        pass

    def determiner_plan_epargne(self, objectif: dict[str, Any]) -> dict[str, Any]:
        """Déterminer le plan d'épargne associé à un objectif.

        Args:
            objectif: Paramètres de l'objectif d'épargne.

        Returns:
            Le plan d'épargne proposé.
        """
        pass

    def constater_ecart(self, plan: dict[str, Any], epargne_realisee: float) -> dict[str, Any]:
        """Constater l'écart entre un plan et l'épargne réalisée.

        Args:
            plan: Plan d'épargne prévu.
            epargne_realisee: Montant d'épargne effectivement réalisé.

        Returns:
            Les informations relatives à l'écart constaté.
        """
        pass

    def preparer_scenarios_reajustement(self, objectif: dict[str, Any], ecart: dict[str, Any]) -> list[dict[str, Any]]:
        """Préparer des scénarios de réajustement à soumettre à l'utilisateur.

        Args:
            objectif: Objectif d'épargne concerné.
            ecart: Écart constaté entre le plan et la réalisation.

        Returns:
            Les scénarios possibles, sans décision automatique.
        """
        pass
