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
        pass
