"""Service de gestion des dépenses."""

from typing import Any
from datetime import date
from math import isfinite
from persistance.repositories.depenses import RepositoryDepenses


class GestionnaireDepenses:
    """Gérer les dépenses prévues et réalisées.

    Cette classe associe les dépenses à des catégories, sans décider de leur
    acceptabilité financière.
    """

    def __init__(self, repository: RepositoryDepenses) -> None:
        self._repository = repository

    def ajouter_depense(self, depense: dict[str, Any]) -> dict[str, Any]:
        """Ajouter une dépense prévue ou réalisée.

        Args:
            depense: Informations de la dépense, dont sa catégorie éventuelle.

        Returns:
            La dépense enregistrée.
        """
        return self._repository.ajouter_depense(**self._valider(depense))

    def modifier_depense(self, identifiant_utilisateur: int, identifiant_depense: int,
                         depense: dict[str, Any]) -> dict[str, Any]:
        """Modifier une dépense existante.

        Args:
            identifiant_depense: Identifiant de la dépense à modifier.
            depense: Nouvelles informations de la dépense.

        Returns:
            La dépense modifiée.
        """
        donnees = self._valider({**depense, "utilisateur_id": identifiant_utilisateur})
        resultat = self._repository.modifier_depense(identifiant_utilisateur, identifiant_depense,
            **{c: v for c, v in donnees.items() if c != "utilisateur_id"})
        if resultat is None: raise ValueError("Dépense introuvable pour cet utilisateur.")
        return resultat

    def supprimer_depense(self, identifiant_utilisateur: int, identifiant_depense: int) -> None:
        """Supprimer une dépense.

        Args:
            identifiant_depense: Identifiant de la dépense à supprimer.

        Returns:
            None.
        """
        if not self._repository.supprimer_depense(identifiant_utilisateur, identifiant_depense):
            raise ValueError("Dépense introuvable pour cet utilisateur.")

    def consulter_depenses(self, identifiant_utilisateur: int,
                           statut: str | None = None) -> list[dict[str, Any]]:
        """Consulter l'historique des dépenses d'un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant de l'utilisateur concerné.

        Returns:
            La liste de ses dépenses.
        """
        if statut is not None and statut not in {"prevue", "realisee"}:
            raise ValueError("Statut de dépense invalide.")
        return self._repository.consulter_depenses(identifiant_utilisateur, statut)

    @staticmethod
    def _valider(depense: dict[str, Any]) -> dict[str, Any]:
        try:
            resultat = {"utilisateur_id": int(depense["utilisateur_id"]),
                "budget_id": int(depense["budget_id"]), "categorie_id": int(depense["categorie_id"]),
                "sous_categorie_id": None if depense.get("sous_categorie_id") is None else int(depense["sous_categorie_id"]),
                "montant": float(depense["montant"]), "date": depense["date"],
                "description": depense.get("description"), "statut": depense["statut"]}
        except (KeyError, TypeError, ValueError) as erreur:
            raise ValueError("Informations de dépense incomplètes.") from erreur
        if any(resultat[c] <= 0 for c in ("utilisateur_id","budget_id","categorie_id")):
            raise ValueError("Les identifiants de la dépense sont invalides.")
        if not isfinite(resultat["montant"]) or resultat["montant"] <= 0:
            raise ValueError("Le montant doit être strictement positif.")
        try: date.fromisoformat(resultat["date"])
        except (TypeError, ValueError) as erreur: raise ValueError("Date de dépense invalide.") from erreur
        if resultat["statut"] not in {"prevue","realisee"}: raise ValueError("Statut de dépense invalide.")
        if resultat["description"] is not None:
            resultat["description"] = str(resultat["description"]).strip() or None
        return resultat
