"""Service de projection de la situation budgétaire."""

from typing import Any


class MoteurProjection:
    """Simuler l'évolution future du budget et de l'objectif d'épargne.

    Cette classe produit des situations projetées sans générer d'alertes,
    modifier automatiquement les données ni prendre de décision utilisateur.
    """

    def realiser_projection(self, etat_budget: dict[str, Any], depenses_prevues: list[dict[str, Any]], objectif_epargne: dict[str, Any]) -> dict[str, Any]:
        """Réaliser une projection de la situation financière future.

        Args:
            etat_budget: État courant du budget.
            depenses_prevues: Dépenses prévues à simuler.
            objectif_epargne: Objectif d'épargne à prendre en compte.

        Returns:
            La situation future projetée.
        """
        pass

    def simuler_ajout_depense(self, etat_budget: dict[str, Any], depense_prevue: dict[str, Any], objectif_epargne: dict[str, Any]) -> dict[str, Any]:
        """Simuler l'impact d'une dépense prévue ajoutée.

        Args:
            etat_budget: État courant du budget.
            depense_prevue: Dépense à ajouter à la simulation.
            objectif_epargne: Objectif d'épargne concerné.

        Returns:
            La situation projetée après l'ajout.
        """
        pass

    def determiner_consequences(self, situation_projetee: dict[str, Any]) -> dict[str, Any]:
        """Déterminer les conséquences d'une situation projetée.

        Args:
            situation_projetee: Situation financière future simulée.

        Returns:
            Les conséquences sur les catégories, la flexibilité et l'épargne.
        """
        pass
