"""Service de détection des alertes budgétaires."""

from typing import Any


class GestionnaireAlertes:
    """Détecter les situations nécessitant une alerte et les produire.

    Cette classe interprète les états du budget et les projections. Les autres
    services ne sont pas responsables de générer les alertes.
    """

    def generer_alertes(self, etat_budget: dict[str, Any], resultat_projection: dict[str, Any], seuils: dict[str, Any], minima_utilisateur: dict[str, Any]) -> list[dict[str, Any]]:
        """Générer les alertes correspondant à une situation donnée.

        Args:
            etat_budget: État courant du budget.
            resultat_projection: Résultat éventuel de projection.
            seuils: Seuils de consommation applicables.
            minima_utilisateur: Minima définis par l'utilisateur.

        Returns:
            Les alertes générées.
        """
        alertes=[]
        pourcentage=float(etat_budget.get("pourcentage_consomme",0))
        seuil_50=float(seuils.get("information",50)); seuil_80=float(seuils.get("attention",80))
        if pourcentage >= 100:
            alertes.append({"type":"depassement","message":"Le budget est dépassé."})
        elif pourcentage >= seuil_80:
            alertes.append({"type":"attention","message":f"Le budget est consommé à {pourcentage:.0f} %."})
        elif pourcentage >= seuil_50:
            alertes.append({"type":"information","message":f"Le budget est consommé à {pourcentage:.0f} %."})
        minimum=float(minima_utilisateur.get("budget_restant",0))
        if float(etat_budget.get("montant_restant",0)) < minimum:
            alertes.append({"type":"minimum","message":"Le budget restant est sous le minimum défini."})
        if resultat_projection.get("budget_restant_projete",0) < 0:
            alertes.append({"type":"projection","message":"Une dépense prévue entraînerait un dépassement."})
        return alertes
