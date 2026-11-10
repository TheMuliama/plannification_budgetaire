"""Service de gestion du budget mensuel."""

from math import isfinite
from typing import Any

from persistance.repositories.budgets import RepositoryBudgets
from serveur.services.categories import GestionnaireCategories
from serveur.services.objectifs_epargne import GestionnaireObjectifsEpargne
from serveur.services.revenus import GestionnaireRevenus


class GestionnaireBudget:
    """Construire et gérer le budget mensuel structuré.

    Cette classe gère les allocations, y compris l'épargne prévue comme
    catégorie spéciale. Elle ne calcule pas le budget restant ni les
    projections futures.
    """

    def __init__(
        self,
        repository: RepositoryBudgets,
        revenus: GestionnaireRevenus,
        objectifs: GestionnaireObjectifsEpargne,
        categories: GestionnaireCategories,
    ) -> None:
        """Initialiser le gestionnaire et ses dépendances métier.

        Args:
            repository: Accès persistant aux allocations budgétaires.
            revenus: Gestionnaire utilisé pour construire le budget mensuel.
            objectifs: Gestionnaire fournissant l'épargne prévue.
            categories: Gestionnaire validant et nommant les classements.
        """
        self._repository = repository
        self._revenus = revenus
        self._objectifs = objectifs
        self._categories = categories

    def creer_budget(self, budget: dict[str, Any]) -> dict[str, Any]:
        """Créer un budget mensuel structuré.

        Args:
            budget: Informations du budget, dont l'épargne prévue.

        Returns:
            Le budget créé.
        """
        donnees = self._valider(budget)
        self._verifier_classement(donnees)
        return self._repository.creer_budget(**donnees)

    def modifier_budget(
        self,
        identifiant_utilisateur: int,
        identifiant_budget: int,
        budget: dict[str, Any],
    ) -> dict[str, Any]:
        """Modifier un budget mensuel.

        Args:
            identifiant_budget: Identifiant du budget à modifier.
            budget: Nouvelles informations du budget.

        Returns:
            Le budget modifié.
        """
        donnees = self._valider({**budget, "utilisateur_id": identifiant_utilisateur})
        self._verifier_classement(donnees)
        resultat = self._repository.modifier_budget(
            identifiant_utilisateur,
            identifiant_budget,
            **{
                cle: valeur
                for cle, valeur in donnees.items()
                if cle != "utilisateur_id"
            },
        )
        if resultat is None:
            raise ValueError("Budget introuvable pour cet utilisateur.")
        return resultat

    def consulter_budget(
        self,
        identifiant_utilisateur: int,
        annee: int | None = None,
        mois: int | None = None,
    ) -> list[dict[str, Any]]:
        """Consulter le budget mensuel d'un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire du budget.

        Returns:
            Le budget mensuel structuré.
        """
        return self._repository.consulter_budgets(identifiant_utilisateur, annee, mois)

    def consulter_allocation(
        self, identifiant_utilisateur: int, identifiant_budget: int
    ) -> dict[str, Any]:
        """Consulter une allocation appartenant à un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire attendu.
            identifiant_budget: Identifiant de l'allocation.

        Returns:
            L'allocation demandée.

        Raises:
            ValueError: Si l'allocation est inaccessible.
        """
        resultat = self._repository.obtenir_budget(
            identifiant_utilisateur, identifiant_budget
        )
        if resultat is None:
            raise ValueError("Budget introuvable pour cet utilisateur.")
        return resultat

    def consulter_allocations_detaillees(
        self,
        identifiant_utilisateur: int,
        annee: int | None = None,
        mois: int | None = None,
    ) -> list[dict[str, Any]]:
        """Consulter des allocations enrichies de leurs libellés.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire des budgets.
            annee: Année facultative utilisée comme filtre.
            mois: Mois facultatif utilisé comme filtre.

        Returns:
            Les allocations avec leur catégorie et leur sous-catégorie.
        """
        return [
            self._nommer_allocation(identifiant_utilisateur, allocation)
            for allocation in self.consulter_budget(
                identifiant_utilisateur, annee, mois
            )
        ]

    def construire_budget_mensuel(
        self, identifiant_utilisateur: int, annee: int, mois: int
    ) -> dict[str, Any]:
        """Construire le budget mensuel à partir des modules de base.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire du budget.
            annee: Année à synthétiser.
            mois: Mois à synthétiser.

        Returns:
            Les revenus, l'épargne prévue et les allocations structurées.

        Raises:
            RuntimeError: Si les dépendances métier ne sont pas configurées.
            ValueError: Si la période est invalide.
        """
        if annee < 2000 or not 1 <= mois <= 12:
            raise ValueError("La période mensuelle du budget est invalide.")

        from calendar import monthrange

        debut = f"{annee:04d}-{mois:02d}-01"
        fin = f"{annee:04d}-{mois:02d}-{monthrange(annee, mois)[1]:02d}"
        revenus_prevus = self._revenus.totaliser_revenus(
            identifiant_utilisateur, debut, fin, "prevu"
        )
        revenus_recus = self._revenus.totaliser_revenus(
            identifiant_utilisateur, debut, fin, "recu"
        )
        epargne_prevue = round(
            sum(
                float(objectif.get("montant_periodique", 0))
                for objectif in self._objectifs.consulter_objectifs(
                    identifiant_utilisateur
                )
            ),
            2,
        )
        allocations = self.consulter_allocations_detaillees(
            identifiant_utilisateur, annee, mois
        )
        total_alloue = round(
            sum(float(allocation["montant_alloue"]) for allocation in allocations),
            2,
        )
        return {
            "annee": annee,
            "mois": mois,
            "revenus_prevus": revenus_prevus,
            "revenus_recus": revenus_recus,
            "epargne_prevue": epargne_prevue,
            "categorie_epargne": {
                "categorie": "Épargne",
                "montant_alloue": epargne_prevue,
                "obligatoire": True,
            },
            "allocations": allocations,
            "total_alloue": total_alloue,
            "budget_non_alloue_prevu": round(
                revenus_prevus + revenus_recus - epargne_prevue - total_alloue, 2
            ),
            "equilibre": (
                revenus_prevus + revenus_recus - epargne_prevue - total_alloue >= 0
            ),
        }

    def supprimer_budget(
        self, identifiant_utilisateur: int, identifiant_budget: int
    ) -> None:
        """Supprimer un budget appartenant à un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire du budget.
            identifiant_budget: Identifiant du budget à supprimer.

        Raises:
            ValueError: Si le budget n'appartient pas à l'utilisateur.
        """
        if not self._repository.supprimer_budget(
            identifiant_utilisateur, identifiant_budget
        ):
            raise ValueError("Budget introuvable pour cet utilisateur.")

    def _verifier_classement(self, donnees: dict[str, Any]) -> None:
        """Déléguer la validation d'un classement au module des catégories."""
        self._categories.verifier_classement(
            donnees["utilisateur_id"],
            donnees["categorie_id"],
            donnees["sous_categorie_id"],
        )

    def _nommer_allocation(
        self, identifiant_utilisateur: int, allocation: dict[str, Any]
    ) -> dict[str, Any]:
        """Ajouter les libellés de classement à une allocation."""
        categorie = self._categories.recuperer_categorie(
            identifiant_utilisateur, allocation["categorie_id"]
        )
        sous_categorie = None
        if allocation.get("sous_categorie_id") is not None:
            sous_categorie = self._categories.recuperer_sous_categorie(
                identifiant_utilisateur,
                allocation["categorie_id"],
                allocation["sous_categorie_id"],
            )
        return {
            **allocation,
            "categorie": categorie["nom"],
            "sous_categorie": sous_categorie["nom"] if sous_categorie else None,
            "libelle": categorie["nom"]
            + (f" · {sous_categorie['nom']}" if sous_categorie else ""),
        }

    @staticmethod
    def _valider(budget: dict[str, Any]) -> dict[str, Any]:
        try:
            donnees = {
                "utilisateur_id": int(budget["utilisateur_id"]),
                "annee": int(budget["annee"]),
                "mois": int(budget["mois"]),
                "categorie_id": int(budget["categorie_id"]),
                "sous_categorie_id": None
                if budget.get("sous_categorie_id") is None
                else int(budget["sous_categorie_id"]),
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
