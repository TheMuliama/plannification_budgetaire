"""Calcul de l'état réel des budgets et du solde disponible."""

from calendar import monthrange
from datetime import date
from typing import Any

from serveur.services.budget import GestionnaireBudget
from serveur.services.depenses import GestionnaireDepenses
from serveur.services.objectifs_epargne import GestionnaireObjectifsEpargne
from serveur.services.revenus import GestionnaireRevenus


class CalculateurBudget:
    """Calculer les états financiers à partir des modules métier de base.

    Le calculateur est l'unique point responsable du solde, des consommations,
    du budget flexible et de la capacité d'épargne. Il ne persiste rien, ne
    génère pas d'alerte et ne réalise pas de projection future.
    """

    def __init__(
        self,
        budgets: GestionnaireBudget | None = None,
        revenus: GestionnaireRevenus | None = None,
        depenses: GestionnaireDepenses | None = None,
        objectifs: GestionnaireObjectifsEpargne | None = None,
    ) -> None:
        """Initialiser le calculateur avec ses dépendances métier.

        Les dépendances restent facultatives afin de permettre l'utilisation
        isolée des fonctions de calcul pur.

        Args:
            budgets: Gestionnaire des allocations mensuelles.
            revenus: Gestionnaire des revenus prévus et reçus.
            depenses: Gestionnaire des dépenses prévues et réalisées.
            objectifs: Gestionnaire des objectifs et versements d'épargne.
        """
        self._budgets = budgets
        self._revenus = revenus
        self._depenses = depenses
        self._objectifs = objectifs

    def calculer_budget_restant(
        self,
        budget: dict[str, Any],
        revenus: list[dict[str, Any]],
        depenses: list[dict[str, Any]],
    ) -> float:
        """Calculer le montant restant pour une allocation donnée.

        Args:
            budget: Allocation mensuelle définie.
            revenus: Revenus du mois, conservés dans le contrat du module.
            depenses: Dépenses pertinentes.

        Returns:
            Le montant restant après les dépenses réalisées.
        """
        del revenus
        plafond = float(budget.get("montant_alloue", 0))
        depense = sum(
            float(element["montant"])
            for element in depenses
            if element.get("statut") == "realisee"
            and ("id" not in budget or element.get("budget_id") == budget["id"])
        )
        return round(plafond - depense, 2)

    def calculer_etat_categorie(
        self, budget: dict[str, Any], depenses: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Calculer l'état réel d'une allocation de catégorie.

        Args:
            budget: Allocation mensuelle définie.
            depenses: Dépenses susceptibles d'y être rattachées.

        Returns:
            Les montants et le taux de consommation de l'allocation.
        """
        alloue = float(budget.get("montant_alloue", 0))
        restant = self.calculer_budget_restant(budget, [], depenses)
        consomme = round(alloue - restant, 2)
        return {
            "budget_id": budget.get("id"),
            "categorie_id": budget.get("categorie_id"),
            "montant_alloue": alloue,
            "montant_depense": consomme,
            "montant_restant": restant,
            "pourcentage_consomme": round(consomme / alloue * 100, 2)
            if alloue
            else 0.0,
        }

    def calculer_budget_flexible(
        self, budget: dict[str, Any], depenses: list[dict[str, Any]]
    ) -> float:
        """Calculer le montant encore disponible dans une allocation flexible.

        Args:
            budget: Allocation mensuelle définie.
            depenses: Dépenses susceptibles d'y être rattachées.

        Returns:
            Zéro pour une allocation obligatoire, sinon son montant restant.
        """
        return (
            0.0
            if budget.get("obligatoire")
            else self.calculer_budget_restant(budget, [], depenses)
        )

    def calculer_enveloppes_hebdomadaires(
        self, budget: dict[str, Any], depenses: list[dict[str, Any]]
    ) -> list[float]:
        """Répartir le montant flexible restant sur quatre semaines.

        Args:
            budget: Allocation mensuelle définie.
            depenses: Dépenses susceptibles d'y être rattachées.

        Returns:
            Quatre enveloppes dont la somme égale le disponible positif.
        """
        disponible = max(0.0, self.calculer_budget_flexible(budget, depenses))
        return self._repartir_quatre_semaines(disponible)

    def obtenir_solde(self, identifiant_utilisateur: int) -> dict[str, float]:
        """Calculer le solde global à partir des opérations réalisées.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire des opérations.

        Returns:
            Les totaux de revenus, dépenses, épargne et le solde disponible.
        """
        self._exiger_dependances()
        assert self._revenus is not None
        assert self._depenses is not None
        assert self._objectifs is not None
        total_revenus = self._revenus.totaliser_revenus(
            identifiant_utilisateur, statut="recu"
        )
        total_depenses = round(
            sum(
                float(depense["montant"])
                for depense in self._depenses.consulter_depenses(
                    identifiant_utilisateur, "realisee"
                )
            ),
            2,
        )
        total_epargne = round(
            self._objectifs.total_versements(identifiant_utilisateur), 2
        )
        return {
            "revenus": total_revenus,
            "depenses": total_depenses,
            "epargne": total_epargne,
            "disponible": round(
                total_revenus - total_depenses - total_epargne, 2
            ),
        }

    def verifier_depense(
        self,
        identifiant_utilisateur: int,
        donnees: dict[str, Any],
        depense_ignoree: int | None = None,
    ) -> None:
        """Refuser une dépense réalisée qui rendrait le solde négatif.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire de la dépense.
            donnees: Informations de la dépense à créer ou modifier.
            depense_ignoree: Dépense remplacée lors d'une modification.
        """
        if donnees.get("statut") != "realisee":
            return
        try:
            montant = float(donnees["montant"])
        except (KeyError, TypeError, ValueError) as erreur:
            raise ValueError("Le montant de la dépense est invalide.") from erreur
        self._exiger_dependances()
        assert self._depenses is not None
        solde = self.obtenir_solde(identifiant_utilisateur)
        if depense_ignoree is not None:
            ancienne = self._depenses.consulter_depense(
                identifiant_utilisateur, depense_ignoree
            )
            if ancienne.get("statut") == "realisee":
                solde["disponible"] += float(ancienne["montant"])
        self._verifier_montant_disponible(montant, solde["disponible"])

    def verifier_versement(
        self, identifiant_utilisateur: int, montant: float
    ) -> None:
        """Refuser un versement supérieur au solde disponible.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire du versement.
            montant: Montant à verser sur un objectif.
        """
        self._verifier_montant_disponible(
            float(montant), self.obtenir_solde(identifiant_utilisateur)["disponible"]
        )

    def verifier_depenses_recurrentes(
        self,
        identifiant_utilisateur: int,
        depenses: list[dict[str, Any]],
    ) -> None:
        """Refuser un lot dont les occurrences réalisées créeraient un découvert.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire des dépenses.
            depenses: Série préparée par le gestionnaire des dépenses.
        """
        total = round(
            sum(
                float(depense["montant"])
                for depense in depenses
                if depense["statut"] == "realisee"
            ),
            2,
        )
        self._verifier_montant_disponible(
            total, self.obtenir_solde(identifiant_utilisateur)["disponible"]
        )

    def calculer_etat_mensuel(
        self, identifiant_utilisateur: int, annee: int, mois: int
    ) -> dict[str, Any]:
        """Calculer l'état complet du budget pour un mois.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire du budget.
            annee: Année étudiée.
            mois: Mois étudié.

        Returns:
            La structure budgétaire enrichie de ses consommations réelles.
        """
        self._exiger_dependances()
        assert self._budgets is not None
        assert self._depenses is not None
        structure = self._budgets.construire_budget_mensuel(
            identifiant_utilisateur, annee, mois
        )
        debut, fin = self.periode_mensuelle(annee, mois)
        depenses = [
            depense
            for depense in self._depenses.consulter_depenses(
                identifiant_utilisateur, "realisee"
            )
            if debut <= depense["date"] <= fin
        ]
        etats = []
        for allocation in structure["allocations"]:
            etat = self.calculer_etat_categorie(allocation, depenses)
            pourcentage = etat["pourcentage_consomme"]
            etats.append(
                {
                    **allocation,
                    **etat,
                    "plafond": etat["montant_alloue"],
                    "depense": etat["montant_depense"],
                    "restant": etat["montant_restant"],
                    "progression": pourcentage / 100,
                    "alerte": self._niveau_consommation(pourcentage),
                    "enveloppes_hebdomadaires": self.calculer_enveloppes_hebdomadaires(
                        allocation, depenses
                    ),
                }
            )
        total_depense = round(sum(etat["montant_depense"] for etat in etats), 2)
        total_alloue = float(structure["total_alloue"])
        budget_flexible = round(
            sum(
                max(0.0, etat["montant_restant"])
                for etat in etats
                if not etat.get("obligatoire")
            ),
            2,
        )
        return {
            **structure,
            "categories": etats,
            "total_depense": total_depense,
            "total_restant": round(total_alloue - total_depense, 2),
            "pourcentage_consomme": round(
                total_depense / total_alloue * 100, 2
            )
            if total_alloue
            else 0.0,
            "budget_flexible": budget_flexible,
            "enveloppes_hebdomadaires": self._repartir_quatre_semaines(
                budget_flexible
            ),
        }

    def analyser_objectifs(
        self, identifiant_utilisateur: int
    ) -> list[dict[str, Any]]:
        """Évaluer les objectifs avec la capacité réelle du mois courant.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire des objectifs.

        Returns:
            Les objectifs enrichis du plan, de l'écart et des scénarios.
        """
        self._exiger_dependances()
        assert self._revenus is not None
        assert self._depenses is not None
        assert self._objectifs is not None
        aujourd_hui = date.today()
        debut = aujourd_hui.replace(day=1).isoformat()
        fin = aujourd_hui.isoformat()
        total_revenus = self._revenus.totaliser_revenus(
            identifiant_utilisateur, debut, fin, "recu"
        )
        total_depenses = round(
            sum(
                float(depense["montant"])
                for depense in self._depenses.consulter_depenses(
                    identifiant_utilisateur, "realisee"
                )
                if debut <= depense["date"] <= fin
            ),
            2,
        )
        total_versements = round(
            self._objectifs.total_versements(identifiant_utilisateur, debut, fin),
            2,
        )
        epargne_maximale = max(
            0.0, round(total_revenus - total_depenses - total_versements, 2)
        )
        analyses = []
        versements = self._objectifs.consulter_versements(identifiant_utilisateur)
        for objectif in self._objectifs.consulter_objectifs(
            identifiant_utilisateur
        ):
            plan = self._objectifs.determiner_plan_epargne(
                {**objectif, "utilisateur_id": identifiant_utilisateur}
            )
            requis = float(plan["montant_periodique_recommande"])
            epargne_objectif = round(
                sum(
                    float(versement["montant"])
                    for versement in versements
                    if versement["objectif_id"] == objectif["id"]
                    and debut <= versement["date"] <= fin
                ),
                2,
            )
            ecart = self._objectifs.constater_ecart(plan, epargne_objectif)
            analyses.append(
                {
                    **objectif,
                    **plan,
                    "revenus_mois": total_revenus,
                    "depenses_mois": total_depenses,
                    "versements_mois": total_versements,
                    "epargne_maximale": epargne_maximale,
                    "revenu_utilisable": round(max(0.0, total_revenus - requis), 2),
                    "objectif_atteignable": requis <= epargne_maximale,
                    "ecart_plan": ecart,
                    "scenarios_reajustement": (
                        self._objectifs.preparer_scenarios_reajustement(
                            objectif, ecart
                        )
                    ),
                }
            )
        return analyses

    def construire_tableau_de_bord(
        self, identifiant_utilisateur: int, annee: int, mois: int
    ) -> dict[str, Any]:
        """Construire tous les indicateurs financiers du tableau de bord.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire des données.
            annee: Année du résumé courant.
            mois: Mois du résumé courant.

        Returns:
            Les indicateurs, répartitions et séries destinés à la vue.
        """
        self._exiger_dependances()
        assert self._depenses is not None
        etat = self.calculer_etat_mensuel(identifiant_utilisateur, annee, mois)
        solde = self.obtenir_solde(identifiant_utilisateur)
        repartition = [
            {"categorie": element["libelle"], "montant": element["depense"]}
            for element in etat["categories"]
            if element["depense"] > 0
        ]
        evolution = []
        toutes_depenses = self._depenses.consulter_depenses(
            identifiant_utilisateur, "realisee"
        )
        for decalage in range(5, -1, -1):
            indice = annee * 12 + mois - 1 - decalage
            annee_cible, mois_zero = divmod(indice, 12)
            mois_cible = mois_zero + 1
            debut, fin = self.periode_mensuelle(annee_cible, mois_cible)
            total = sum(
                float(depense["montant"])
                for depense in toutes_depenses
                if debut <= depense["date"] <= fin
            )
            evolution.append(
                {"mois": f"{mois_cible:02d}/{annee_cible}", "montant": round(total, 2)}
            )
        assert self._budgets is not None
        noms_budgets = {
            element["id"]: element["libelle"]
            for element in self._budgets.consulter_allocations_detaillees(
                identifiant_utilisateur
            )
        }
        dernieres = [
            {
                **depense,
                "libelle": depense.get("description") or "Dépense",
                "categorie": noms_budgets.get(
                    depense["budget_id"], "Sans catégorie"
                ),
                "date": date.fromisoformat(depense["date"]).strftime("%d/%m/%Y"),
            }
            for depense in toutes_depenses[:5]
        ]
        return {
            "mois": f"Résumé du mois {mois:02d}/{annee}",
            "budget_mois": etat["total_alloue"],
            "depense": etat["total_depense"],
            "restant": solde["disponible"],
            "repartition": repartition,
            "budgets": [
                {
                    "categorie": element["libelle"],
                    "categorie_parent": element["categorie"],
                    "plafond": element["plafond"],
                    "depense": element["depense"],
                    "pourcentage": element["pourcentage_consomme"],
                }
                for element in etat["categories"]
            ],
            "evolution": evolution,
            "dernieres_depenses": dernieres,
        }

    def _exiger_dependances(self) -> None:
        """Refuser un calcul agrégé sans tous les modules requis."""
        if any(
            dependance is None
            for dependance in (
                self._budgets,
                self._revenus,
                self._depenses,
                self._objectifs,
            )
        ):
            raise RuntimeError("Les dépendances du calculateur sont absentes.")

    @staticmethod
    def periode_mensuelle(annee: int, mois: int) -> tuple[str, str]:
        """Retourner les bornes ISO d'un mois valide.

        Args:
            annee: Année de la période.
            mois: Mois de la période.

        Returns:
            Les dates ISO du premier et du dernier jour.
        """
        if annee < 2000 or not 1 <= mois <= 12:
            raise ValueError("La période mensuelle est invalide.")
        return (
            f"{annee:04d}-{mois:02d}-01",
            f"{annee:04d}-{mois:02d}-{monthrange(annee, mois)[1]:02d}",
        )

    @staticmethod
    def _niveau_consommation(pourcentage: float) -> str:
        """Déterminer le niveau visuel à partir du seuil final de 80 %."""
        if pourcentage >= 90:
            return "risque"
        if pourcentage >= 80:
            return "attention"
        return "normal"

    @staticmethod
    def _repartir_quatre_semaines(disponible: float) -> list[float]:
        """Répartir exactement un montant sur quatre enveloppes."""
        valeur = max(0.0, disponible)
        base = round(valeur / 4, 2)
        return [base, base, base, round(valeur - base * 3, 2)]

    @staticmethod
    def _verifier_montant_disponible(montant: float, disponible: float) -> None:
        """Comparer un montant au disponible en tolérant les arrondis."""
        if montant > disponible + 1e-9:
            raise ValueError(f"Solde insuffisant : {disponible:.2f} € disponible(s).")
