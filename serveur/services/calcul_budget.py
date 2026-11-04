"""Calcul de l'état courant du budget."""

from typing import Any


class CalculateurBudget:
    """Calculer l'état réel d'un budget à partir des revenus et dépenses.

    Cette classe produit les montants et états courants. Elle ne génère pas
    d'alertes et ne réalise pas de projections futures.
    """

    def calculer_budget_restant(self, budget: dict[str, Any], revenus: list[dict[str, Any]], depenses: list[dict[str, Any]]) -> float:
        """Calculer le montant restant pour un budget donné.

        Args:
            budget: Budget mensuel défini.
            revenus: Revenus prévisionnels ou réels pertinents.
            depenses: Dépenses prévues ou réalisées pertinentes.

        Returns:
            Le montant de budget restant.
        """
        plafond = float(budget.get("montant_alloue", 0))
        depense = sum(float(d["montant"]) for d in depenses
                      if d.get("statut") == "realisee" and
                      ("id" not in budget or d.get("budget_id") == budget["id"]))
        return round(plafond - depense, 2)

    def calculer_etat_categorie(self, budget: dict[str, Any], depenses: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculer l'état des catégories d'un budget.

        Args:
            budget: Budget mensuel défini.
            depenses: Dépenses associées aux catégories.

        Returns:
            L'état des catégories.
        """
        alloue=float(budget.get("montant_alloue",0)); restant=self.calculer_budget_restant(budget,[],depenses)
        consomme=round(alloue-restant,2)
        return {"budget_id":budget.get("id"),"categorie_id":budget.get("categorie_id"),
                "montant_alloue":alloue,"montant_depense":consomme,"montant_restant":restant,
                "pourcentage_consomme":round(consomme/alloue*100,2) if alloue else 0.0}

    def calculer_budget_flexible(self, budget: dict[str, Any], depenses: list[dict[str, Any]]) -> float:
        """Calculer le budget flexible disponible.

        Args:
            budget: Budget mensuel défini.
            depenses: Dépenses à prendre en compte.

        Returns:
            Le montant flexible disponible.
        """
        return 0.0 if budget.get("obligatoire") else self.calculer_budget_restant(budget,[],depenses)

    def calculer_enveloppes_hebdomadaires(self, budget: dict[str, Any], depenses: list[dict[str, Any]]) -> list[float]:
        """Calculer les enveloppes hebdomadaires du budget.

        Args:
            budget: Budget mensuel défini.
            depenses: Dépenses à prendre en compte.

        Returns:
            Les montants des enveloppes hebdomadaires.
        """
        disponible=max(0.0,self.calculer_budget_flexible(budget,depenses))
        base=round(disponible/4,2)
        return [base,base,base,round(disponible-base*3,2)]
