"""Service de gestion des dépenses."""

from collections.abc import Callable
from datetime import date
from math import isfinite
from typing import Any

from persistance.repositories.depenses import RepositoryDepenses
from serveur.services.budget import GestionnaireBudget
from serveur.services.categories import GestionnaireCategories
from serveur.services.recurrence import generer_dates_recurrence


class GestionnaireDepenses:
    """Gérer les dépenses prévues et réalisées.

    Cette classe associe les dépenses aux catégories et allocations qui leur
    appartiennent. Elle délègue l'acceptabilité financière au calculateur
    injecté par l'application lors d'une écriture utilisateur.
    """

    def __init__(
        self,
        repository: RepositoryDepenses,
        categories: GestionnaireCategories,
        budgets: GestionnaireBudget,
    ) -> None:
        """Initialiser le gestionnaire et ses dépendances de classement.

        Args:
            repository: Accès persistant aux dépenses.
            categories: Gestionnaire validant les catégories.
            budgets: Gestionnaire validant les allocations mensuelles.
        """
        self._repository = repository
        self._categories = categories
        self._budgets = budgets

    def ajouter_depense(
        self,
        depense: dict[str, Any],
        verifier_disponibilite: Callable[[int, dict[str, Any], int | None], None]
        | None = None,
    ) -> dict[str, Any]:
        """Ajouter une dépense prévue ou réalisée.

        Args:
            depense: Informations de la dépense, dont sa catégorie éventuelle.
            verifier_disponibilite: Règle financière fournie par le calculateur.

        Returns:
            La dépense enregistrée.
        """
        donnees = self._valider(depense)
        self._verifier_liens(donnees)
        if verifier_disponibilite is not None:
            verifier_disponibilite(donnees["utilisateur_id"], donnees, None)
        return self._repository.ajouter_depense(**donnees)

    def preparer_depenses_recurrentes(
        self,
        identifiant_utilisateur: int,
        depense: dict[str, Any],
        *,
        creer_budgets_manquants: bool = False,
    ) -> list[dict[str, Any]]:
        """Préparer et valider une série avant toute écriture.

        Chaque occurrence est associée au budget de son mois. Les budgets
        manquants peuvent être préparés à partir du budget de référence.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire des dépenses.
            depense: Dépense commune et paramètres de récurrence.
            creer_budgets_manquants: Autoriser la création des budgets absents.

        Returns:
            Les occurrences validées avec le budget propre à chaque mois
            et les éventuels budgets à créer.

        Raises:
            ValueError: Si les dates, le budget ou le classement sont invalides.
            ValueError: Si un budget manque et que sa création est interdite.
        """
        try:
            debut = date.fromisoformat(depense["date"])
            fin = (
                date.fromisoformat(depense["date_fin"])
                if depense.get("date_fin")
                else None
            )
        except (KeyError, TypeError, ValueError) as erreur:
            raise ValueError("Les dates de récurrence sont invalides.") from erreur

        occurrences = generer_dates_recurrence(
            debut, depense.get("frequence", "Aucune"), fin
        )

        try:
            categorie_id = int(depense["categorie_id"])
            sous_categorie_id = (
                int(depense["sous_categorie_id"])
                if depense.get("sous_categorie_id") is not None
                else None
            )

            budget_source = self._budgets.consulter_allocation(
                identifiant_utilisateur, int(depense["budget_id"])
            )
        except (KeyError, TypeError, ValueError) as erreur:
            raise ValueError(
                "Le budget servant de modèle à la récurrence est invalide."
            ) from erreur

        if (
            budget_source["categorie_id"] != categorie_id
            or budget_source.get("sous_categorie_id") != sous_categorie_id
        ):
            raise ValueError(
                "Le budget sélectionné ne correspond pas au classement."
            )

        aujourd_hui = date.today()
        resultat = []

        for occurrence in occurrences:
            correspondances = [
                budget
                for budget in self._budgets.consulter_budget(
                    identifiant_utilisateur,
                    occurrence.year,
                    occurrence.month,
                )
                if budget["categorie_id"] == categorie_id
                and budget.get("sous_categorie_id") == sous_categorie_id
            ]

            if not correspondances and not creer_budgets_manquants:
                raise ValueError(
                    "Aucun budget compatible pour le mois "
                    f"{occurrence.month:02d}/{occurrence.year}."
                )

            budget = correspondances[0] if correspondances else budget_source

            donnees = self._valider(
                {
                    **depense,
                    "utilisateur_id": identifiant_utilisateur,
                    "budget_id": budget["id"],
                    "date": occurrence.isoformat(),
                    "statut": (
                        "realisee"
                        if occurrence <= aujourd_hui
                        else "prevue"
                    ),
                }
            )

            self._verifier_liens(donnees)

            if not correspondances:
                donnees["_budget_a_creer"] = {
                    "utilisateur_id": identifiant_utilisateur,
                    "annee": occurrence.year,
                    "mois": occurrence.month,
                    "categorie_id": budget_source["categorie_id"],
                    "sous_categorie_id": budget_source.get("sous_categorie_id"),
                    "montant_alloue": budget_source["montant_alloue"],
                    "obligatoire": bool(budget_source.get("obligatoire")),
                }

            resultat.append(donnees)

        return resultat

    def enregistrer_depenses_preparees(
        self, depenses: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Persister une série de dépenses déjà validées.

        Les budgets manquants et les dépenses sont enregistrés dans une
        transaction SQLite unique afin d'éviter toute création partielle.

        Args:
            depenses: Occurrences produites par
                :meth:`preparer_depenses_recurrentes`.

        Returns:
            Les dépenses enregistrées avec leurs identifiants définitifs.

        Raises:
            sqlite3.Error: Si une opération de persistance échoue.
        """
        return self._repository.ajouter_depenses_recurrentes(depenses)

    def modifier_depense(
        self,
        identifiant_utilisateur: int,
        identifiant_depense: int,
        depense: dict[str, Any],
        verifier_disponibilite: Callable[[int, dict[str, Any], int | None], None]
        | None = None,
    ) -> dict[str, Any]:
        """Modifier une dépense existante.

        Args:
            identifiant_depense: Identifiant de la dépense à modifier.
            depense: Nouvelles informations de la dépense.
            verifier_disponibilite: Règle financière fournie par le calculateur.

        Returns:
            La dépense modifiée.
        """
        statut = depense.get("statut")
        if statut is None:
            try:
                statut = (
                    "realisee"
                    if date.fromisoformat(depense["date"]) <= date.today()
                    else "prevue"
                )
            except (KeyError, TypeError, ValueError) as erreur:
                raise ValueError("Date de dépense invalide.") from erreur
        donnees = self._valider(
            {
                **depense,
                "utilisateur_id": identifiant_utilisateur,
                "statut": statut,
            }
        )
        self._verifier_liens(donnees)
        self.consulter_depense(identifiant_utilisateur, identifiant_depense)
        if verifier_disponibilite is not None:
            verifier_disponibilite(
                identifiant_utilisateur, donnees, identifiant_depense
            )
        resultat = self._repository.modifier_depense(
            identifiant_utilisateur,
            identifiant_depense,
            **{c: v for c, v in donnees.items() if c != "utilisateur_id"},
        )
        if resultat is None:
            raise ValueError("Dépense introuvable pour cet utilisateur.")
        return resultat

    def supprimer_depense(
        self, identifiant_utilisateur: int, identifiant_depense: int
    ) -> None:
        """Supprimer une dépense.

        Args:
            identifiant_depense: Identifiant de la dépense à supprimer.

        Returns:
            None.
        """
        if not self._repository.supprimer_depense(
            identifiant_utilisateur, identifiant_depense
        ):
            raise ValueError("Dépense introuvable pour cet utilisateur.")

    def consulter_depenses(
        self, identifiant_utilisateur: int, statut: str | None = None
    ) -> list[dict[str, Any]]:
        """Consulter l'historique des dépenses d'un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant de l'utilisateur concerné.

        Returns:
            La liste de ses dépenses.
        """
        if statut is not None and statut not in {"prevue", "realisee"}:
            raise ValueError("Statut de dépense invalide.")
        return self._repository.consulter_depenses(identifiant_utilisateur, statut)

    def consulter_depense(
        self, identifiant_utilisateur: int, identifiant_depense: int
    ) -> dict[str, Any]:
        """Consulter une dépense accessible à l'utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire attendu.
            identifiant_depense: Identifiant de la dépense.

        Returns:
            La dépense demandée.
        """
        resultat = self._repository.obtenir_depense(
            identifiant_utilisateur, identifiant_depense
        )
        if resultat is None:
            raise ValueError("Dépense introuvable pour cet utilisateur.")
        return resultat

    def _verifier_liens(self, donnees: dict[str, Any]) -> None:
        """Vérifier les relations métier d'une dépense."""
        budget = self._budgets.consulter_allocation(
            donnees["utilisateur_id"], donnees["budget_id"]
        )
        if budget["categorie_id"] != donnees["categorie_id"]:
            raise ValueError("La catégorie ne correspond pas au budget.")
        if budget.get("sous_categorie_id") != donnees.get("sous_categorie_id"):
            raise ValueError("La sous-catégorie ne correspond pas au budget.")
        self._categories.verifier_classement(
            donnees["utilisateur_id"],
            donnees["categorie_id"],
            donnees.get("sous_categorie_id"),
        )

    @staticmethod
    def _valider(depense: dict[str, Any]) -> dict[str, Any]:
        try:
            resultat = {
                "utilisateur_id": int(depense["utilisateur_id"]),
                "budget_id": int(depense["budget_id"]),
                "categorie_id": int(depense["categorie_id"]),
                "sous_categorie_id": None
                if depense.get("sous_categorie_id") is None
                else int(depense["sous_categorie_id"]),
                "montant": float(depense["montant"]),
                "date": depense["date"],
                "description": depense.get("description"),
                "statut": depense["statut"],
            }
        except (KeyError, TypeError, ValueError) as erreur:
            raise ValueError("Informations de dépense incomplètes.") from erreur
        if any(
            resultat[c] <= 0 for c in ("utilisateur_id", "budget_id", "categorie_id")
        ):
            raise ValueError("Les identifiants de la dépense sont invalides.")
        if not isfinite(resultat["montant"]) or resultat["montant"] <= 0:
            raise ValueError("Le montant doit être strictement positif.")
        try:
            date.fromisoformat(resultat["date"])
        except (TypeError, ValueError) as erreur:
            raise ValueError("Date de dépense invalide.") from erreur
        if resultat["statut"] not in {"prevue", "realisee"}:
            raise ValueError("Statut de dépense invalide.")
        if resultat["description"] is not None:
            resultat["description"] = str(resultat["description"]).strip() or None
        return resultat
