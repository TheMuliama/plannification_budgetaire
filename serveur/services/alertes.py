"""Service de détection des alertes budgétaires."""

from typing import Any

from serveur.services.calcul_budget import CalculateurBudget
from serveur.services.projection import MoteurProjection


class GestionnaireAlertes:
    """Détecter les situations nécessitant une alerte et les produire.

    Cette classe interprète les états du budget et les projections. Les autres
    services ne sont pas responsables de générer les alertes.
    """

    def __init__(
        self,
        calculateur: CalculateurBudget | None = None,
        projection: MoteurProjection | None = None,
    ) -> None:
        """Initialiser le gestionnaire avec les sources d'états financiers.

        Args:
            calculateur: Calculateur des consommations réelles.
            projection: Moteur des situations futures.
        """
        self._calculateur = calculateur
        self._projection = projection

    def generer_alertes(
        self,
        etat_budget: dict[str, Any],
        resultat_projection: dict[str, Any],
        seuils: dict[str, Any],
        minima_utilisateur: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Générer les alertes correspondant à une situation donnée.

        Args:
            etat_budget: État courant du budget.
            resultat_projection: Résultat éventuel de projection.
            seuils: Seuils de consommation applicables.
            minima_utilisateur: Minima définis par l'utilisateur.

        Returns:
            Les alertes générées.
        """
        alertes = []
        pourcentage = float(etat_budget.get("pourcentage_consomme", 0))
        seuil_80 = float(seuils.get("attention", 80))
        if pourcentage >= 100:
            alertes.append(
                {"type": "depassement", "message": "Le budget est dépassé."}
            )
        elif pourcentage >= seuil_80:
            alertes.append(
                {
                    "type": "attention",
                    "message": f"Le budget est consommé à {pourcentage:.0f} %.",
                }
            )
        minimum = float(minima_utilisateur.get("budget_restant", 0))
        if float(etat_budget.get("montant_restant", 0)) < minimum:
            alertes.append(
                {
                    "type": "minimum",
                    "message": "Le budget restant est sous le minimum défini.",
                }
            )
        if resultat_projection.get("budget_restant_projete", 0) < 0:
            alertes.append(
                {
                    "type": "projection",
                    "message": "Une dépense prévue entraînerait un dépassement.",
                }
            )
        return alertes

    def lister_alertes(
        self,
        identifiant_utilisateur: int,
        annee: int,
        mois: int,
        seuil_attention: float = 80,
    ) -> list[dict[str, Any]]:
        """Produire les alertes actives d'un utilisateur pour un mois.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire du budget.
            annee: Année étudiée.
            mois: Mois étudié.
            seuil_attention: Seuil minimal, fixé à 80 % par défaut.

        Returns:
            Les alertes de consommation et de projection prêtes à afficher.
        """
        if self._calculateur is None or self._projection is None:
            raise RuntimeError(
                "Les dépendances du gestionnaire d'alertes sont absentes."
            )
        if seuil_attention < 80 or seuil_attention > 100:
            raise ValueError("Le seuil d'alerte doit être compris entre 80 et 100 %.")
        etat = self._calculateur.calculer_etat_mensuel(
            identifiant_utilisateur, annee, mois
        )
        resultat = []
        for categorie in etat["categories"]:
            pourcentage = float(categorie["pourcentage_consomme"])
            if pourcentage < seuil_attention:
                continue
            niveau = "risque" if pourcentage >= 90 else "attention"
            if pourcentage > 100:
                message = (
                    f"Le budget {categorie['libelle']} est dépassé : "
                    f"{pourcentage:.1f} % ont été utilisés."
                )
            elif pourcentage >= 100:
                message = f"Le budget {categorie['libelle']} a atteint sa limite."
            else:
                message = (
                    f"Le budget {categorie['libelle']} est utilisé à "
                    f"{pourcentage:.1f} %."
                )
            resultat.append(
                {
                    "id": f"budget:{categorie['id']}",
                    "titre": f"Budget {categorie['libelle']}",
                    "categorie": categorie["libelle"],
                    "type": niveau,
                    "message": message,
                    "pourcentage": pourcentage,
                    "statut": "active",
                }
            )
        projection = self._projection.projeter_mois(
            identifiant_utilisateur, annee, mois
        )
        if projection["budget_restant_projete"] < 0:
            resultat.append(
                {
                    "id": f"projection:{annee:04d}-{mois:02d}",
                    "titre": "Projection mensuelle",
                    "categorie": "Budget global",
                    "type": "risque",
                    "message": (
                        "Les dépenses prévues entraîneraient un dépassement."
                    ),
                    "pourcentage": 100.0,
                    "statut": "active",
                }
            )
        return sorted(
            resultat,
            key=lambda alerte: (
                0 if alerte["type"] == "risque" else 1,
                -float(alerte["pourcentage"]),
            ),
        )
