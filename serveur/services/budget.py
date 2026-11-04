"""Service de gestion du budget mensuel."""

from typing import Any
from math import isfinite

from persistance.repositories.budgets import RepositoryBudgets


class GestionnaireBudget:
    """Construire et gérer le budget mensuel structuré.

    Cette classe gère les allocations, y compris l'épargne prévue comme
    catégorie spéciale. Elle ne calcule pas le budget restant ni les
    projections futures.
    """

    def __init__(self, repository: RepositoryBudgets) -> None:
        self._repository = repository

    def creer_budget(self, budget: dict[str, Any]) -> dict[str, Any]:
        """Créer un budget mensuel structuré.

        Args:
            budget: Informations du budget, dont l'épargne prévue.

        Returns:
            Le budget créé.
        """
        return self._repository.creer_budget(**self._valider(budget))

    def modifier_budget(self, identifiant_utilisateur: int, identifiant_budget: int,
                        budget: dict[str, Any]) -> dict[str, Any]:
        """Modifier un budget mensuel.

        Args:
            identifiant_budget: Identifiant du budget à modifier.
            budget: Nouvelles informations du budget.

        Returns:
            Le budget modifié.
        """
        donnees = self._valider({**budget, "utilisateur_id": identifiant_utilisateur})
        resultat = self._repository.modifier_budget(
            identifiant_utilisateur, identifiant_budget,
            **{cle: valeur for cle, valeur in donnees.items() if cle != "utilisateur_id"},
        )
        if resultat is None:
            raise ValueError("Budget introuvable pour cet utilisateur.")
        return resultat

    def consulter_budget(self, identifiant_utilisateur: int, annee: int | None = None,
                         mois: int | None = None) -> list[dict[str, Any]]:
        """Consulter le budget mensuel d'un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire du budget.

        Returns:
            Le budget mensuel structuré.
        """
        return self._repository.consulter_budgets(identifiant_utilisateur, annee, mois)

    def supprimer_budget(self, identifiant_utilisateur: int, identifiant_budget: int) -> None:
        if not self._repository.supprimer_budget(identifiant_utilisateur, identifiant_budget):
            raise ValueError("Budget introuvable pour cet utilisateur.")

    @staticmethod
    def _valider(budget: dict[str, Any]) -> dict[str, Any]:
        try:
            donnees = {
                "utilisateur_id": int(budget["utilisateur_id"]), "annee": int(budget["annee"]),
                "mois": int(budget["mois"]), "categorie_id": int(budget["categorie_id"]),
                "sous_categorie_id": None if budget.get("sous_categorie_id") is None else int(budget["sous_categorie_id"]),
                "montant_alloue": float(budget["montant_alloue"]),
                "obligatoire": bool(budget.get("obligatoire", False)),
            }
        except (KeyError, TypeError, ValueError) as erreur:
            raise ValueError("Les informations du budget sont incomplètes.") from erreur
        if donnees["utilisateur_id"] <= 0 or donnees["categorie_id"] <= 0:
            raise ValueError("Le propriétaire ou la catégorie est invalide.")
        if donnees["annee"] < 2000 or not 1 <= donnees["mois"] <= 12:
            raise ValueError("La période mensuelle du budget est invalide.")
        if not isfinite(donnees["montant_alloue"]) or donnees["montant_alloue"] < 0:
            raise ValueError("Le montant alloué est invalide.")
        return donnees

    def gerer_allocation(self, identifiant_budget: int, allocation: dict[str, Any]) -> dict[str, Any]:
        """Gérer une allocation par catégorie ou sous-catégorie.

        Args:
            identifiant_budget: Identifiant du budget concerné.
            allocation: Informations de l'allocation à gérer.

        Returns:
            L'allocation enregistrée.
        """
        raise NotImplementedError("Les allocations utilisent directement les lignes de budgets du schéma MVP.")
