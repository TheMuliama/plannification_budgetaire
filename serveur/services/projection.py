"""Service de projection de la situation budgétaire."""

from typing import Any

from serveur.services.calcul_budget import CalculateurBudget
from serveur.services.depenses import GestionnaireDepenses
from serveur.services.objectifs_epargne import GestionnaireObjectifsEpargne


class MoteurProjection:
    """Simuler l'évolution future du budget et de l'objectif d'épargne.

    Cette classe produit des situations projetées sans générer d'alertes,
    modifier automatiquement les données ni prendre de décision utilisateur.
    """

    def __init__(
        self,
        calculateur: CalculateurBudget | None = None,
        depenses: GestionnaireDepenses | None = None,
        objectifs: GestionnaireObjectifsEpargne | None = None,
    ) -> None:
        """Initialiser le moteur avec les modules dont il projette les données.

        Args:
            calculateur: Calculateur fournissant l'état réel du budget.
            depenses: Gestionnaire fournissant les dépenses prévues.
            objectifs: Gestionnaire fournissant l'objectif d'épargne.
        """
        self._calculateur = calculateur
        self._depenses = depenses
        self._objectifs = objectifs

    def realiser_projection(
        self,
        etat_budget: dict[str, Any],
        depenses_prevues: list[dict[str, Any]],
        objectif_epargne: dict[str, Any],
    ) -> dict[str, Any]:
        """Réaliser une projection de la situation financière future.

        Args:
            etat_budget: État courant du budget.
            depenses_prevues: Dépenses prévues à simuler.
            objectif_epargne: Objectif d'épargne à prendre en compte.

        Returns:
            La situation future projetée.
        """
        total = round(sum(float(d.get("montant", 0)) for d in depenses_prevues), 2)
        restant = round(float(etat_budget.get("budget_restant", 0)) - total, 2)
        flexible = round(float(etat_budget.get("budget_flexible", restant)) - total, 2)
        objectif_periodique = float(objectif_epargne.get("montant_periodique", 0))
        capacite = round(max(0.0, min(objectif_periodique, flexible)), 2)
        categories_projetees = []
        for categorie in etat_budget.get("categories", []):
            impact = round(
                sum(
                    float(depense.get("montant", 0))
                    for depense in depenses_prevues
                    if depense.get("budget_id") == categorie.get("id")
                ),
                2,
            )
            categories_projetees.append(
                {
                    **categorie,
                    "depenses_prevues": impact,
                    "montant_restant_projete": round(
                        float(categorie.get("montant_restant", 0)) - impact, 2
                    ),
                }
            )
        return {
            **etat_budget,
            "depenses_prevues": total,
            "budget_restant_projete": restant,
            "budget_flexible_projete": flexible,
            "capacite_epargne_projetee": capacite,
            "categories_projetees": categories_projetees,
        }

    def simuler_ajout_depense(
        self,
        etat_budget: dict[str, Any],
        depense_prevue: dict[str, Any],
        objectif_epargne: dict[str, Any],
    ) -> dict[str, Any]:
        """Simuler l'impact d'une dépense prévue ajoutée.

        Args:
            etat_budget: État courant du budget.
            depense_prevue: Dépense à ajouter à la simulation.
            objectif_epargne: Objectif d'épargne concerné.

        Returns:
            La situation projetée après l'ajout.
        """
        return self.realiser_projection(etat_budget, [depense_prevue], objectif_epargne)

    def determiner_consequences(
        self, situation_projetee: dict[str, Any]
    ) -> dict[str, Any]:
        """Déterminer les conséquences d'une situation projetée.

        Args:
            situation_projetee: Situation financière future simulée.

        Returns:
            Les conséquences sur les catégories, la flexibilité et l'épargne.
        """
        restant = float(situation_projetee.get("budget_restant_projete", 0))
        flexible = float(situation_projetee.get("budget_flexible_projete", 0))
        return {
            "budget_depasse": restant < 0,
            "budget_flexible_depasse": flexible < 0,
            "impact_budget": round(
                -float(situation_projetee.get("depenses_prevues", 0)), 2
            ),
            "capacite_epargne": float(
                situation_projetee.get("capacite_epargne_projetee", 0)
            ),
        }

    def projeter_mois(
        self,
        identifiant_utilisateur: int,
        annee: int,
        mois: int,
        montant_supplementaire: float = 0,
        identifiant_objectif: int | None = None,
        identifiant_budget: int | None = None,
    ) -> dict[str, Any]:
        """Projeter un mois depuis les données réelles de l'utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire des données.
            annee: Année à projeter.
            mois: Mois à projeter.
            montant_supplementaire: Dépense hypothétique facultative.
            identifiant_objectif: Objectif d'épargne facultatif à étudier.
            identifiant_budget: Budget facultatif de la dépense hypothétique.

        Returns:
            La situation projetée et ses conséquences.
        """
        if (
            self._calculateur is None
            or self._depenses is None
            or self._objectifs is None
        ):
            raise RuntimeError(
                "Les dépendances du moteur de projection sont absentes."
            )
        etat = self._calculateur.calculer_etat_mensuel(
            identifiant_utilisateur, annee, mois
        )
        debut, fin = self._calculateur.periode_mensuelle(annee, mois)
        depenses_prevues = [
            depense
            for depense in self._depenses.consulter_depenses(
                identifiant_utilisateur, "prevue"
            )
            if debut <= depense["date"] <= fin
        ]
        valeur_supplementaire = float(montant_supplementaire)
        if valeur_supplementaire < 0:
            raise ValueError("La dépense simulée ne peut pas être négative.")
        if valeur_supplementaire:
            depenses_prevues.append(
                {"montant": valeur_supplementaire, "budget_id": identifiant_budget}
            )

        objectifs = self._objectifs.consulter_objectifs(identifiant_utilisateur)
        if identifiant_objectif is not None:
            objectif = self._objectifs.consulter_objectif(
                identifiant_utilisateur, identifiant_objectif
            )
        else:
            objectif = objectifs[0] if objectifs else {"montant_periodique": 0}
        projection = self.realiser_projection(
            {
                "budget_restant": etat["total_restant"],
                "budget_flexible": etat["budget_flexible"],
                "categories": etat["categories"],
            },
            depenses_prevues,
            objectif,
        )
        return {**projection, "consequences": self.determiner_consequences(projection)}
