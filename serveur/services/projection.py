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
        total=round(sum(float(d.get("montant",0)) for d in depenses_prevues),2)
        restant=round(float(etat_budget.get("budget_restant",0))-total,2)
        flexible=round(float(etat_budget.get("budget_flexible",restant))-total,2)
        capacite=max(0.0,round(float(objectif_epargne.get("montant_periodique",0))+min(0,flexible),2))
        return {**etat_budget,"depenses_prevues":total,"budget_restant_projete":restant,
                "budget_flexible_projete":flexible,"capacite_epargne_projetee":capacite}

    def simuler_ajout_depense(self, etat_budget: dict[str, Any], depense_prevue: dict[str, Any], objectif_epargne: dict[str, Any]) -> dict[str, Any]:
        """Simuler l'impact d'une dépense prévue ajoutée.

        Args:
            etat_budget: État courant du budget.
            depense_prevue: Dépense à ajouter à la simulation.
            objectif_epargne: Objectif d'épargne concerné.

        Returns:
            La situation projetée après l'ajout.
        """
        return self.realiser_projection(etat_budget,[depense_prevue],objectif_epargne)

    def determiner_consequences(self, situation_projetee: dict[str, Any]) -> dict[str, Any]:
        """Déterminer les conséquences d'une situation projetée.

        Args:
            situation_projetee: Situation financière future simulée.

        Returns:
            Les conséquences sur les catégories, la flexibilité et l'épargne.
        """
        restant=float(situation_projetee.get("budget_restant_projete",0))
        flexible=float(situation_projetee.get("budget_flexible_projete",0))
        return {"budget_depasse":restant<0,"budget_flexible_depasse":flexible<0,
                "impact_budget":round(-float(situation_projetee.get("depenses_prevues",0)),2),
                "capacite_epargne":float(situation_projetee.get("capacite_epargne_projetee",0))}
