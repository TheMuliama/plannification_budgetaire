"""Accès aux données des budgets mensuels."""

import sqlite3
from typing import Any


class RepositoryBudgets:
    """Lire et écrire les budgets mensuels d'un utilisateur."""

    def __init__(self, connexion: sqlite3.Connection) -> None:
        self._connexion = connexion

    def creer_budget(
        self,
        utilisateur_id: int,
        annee: int,
        mois: int,
        categorie_id: int,
        sous_categorie_id: int | None,
        montant_alloue: float,
        obligatoire: bool,
    ) -> dict[str, Any]:
        """Créer une allocation budgétaire mensuelle.

        Args:
            utilisateur_id: Identifiant du propriétaire du budget.
            annee: Année de l'allocation.
            mois: Mois de l'allocation.
            categorie_id: Catégorie financée.
            sous_categorie_id: Sous-catégorie facultative financée.
            montant_alloue: Montant affecté au budget.
            obligatoire: Indique si l'allocation est obligatoire.

        Returns:
            Le budget enregistré.
        """
        with self._connexion:
            curseur = self._connexion.execute(
                "INSERT INTO budgets (utilisateur_id, annee, mois, categorie_id, "
                "sous_categorie_id, montant_alloue, obligatoire) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    utilisateur_id,
                    annee,
                    mois,
                    categorie_id,
                    sous_categorie_id,
                    montant_alloue,
                    int(obligatoire),
                ),
            )
        resultat = self.obtenir_budget(utilisateur_id, curseur.lastrowid)
        assert resultat is not None
        return resultat

    def obtenir_budget(
        self, utilisateur_id: int, budget_id: int
    ) -> dict[str, Any] | None:
        """Récupérer un budget accessible à un utilisateur.

        Args:
            utilisateur_id: Identifiant du propriétaire du budget.
            budget_id: Identifiant du budget recherché.

        Returns:
            Le budget trouvé, ou ``None`` s'il est inaccessible.
        """
        ligne = self._connexion.execute(
            "SELECT id, utilisateur_id, annee, mois, categorie_id, sous_categorie_id, "
            "montant_alloue, obligatoire FROM budgets WHERE utilisateur_id = ? AND id = ?",
            (utilisateur_id, budget_id),
        ).fetchone()
        return dict(ligne) if ligne is not None else None

    def consulter_budgets(
        self, utilisateur_id: int, annee: int | None = None, mois: int | None = None
    ) -> list[dict[str, Any]]:
        """Consulter les budgets d'un utilisateur sur une période.

        Args:
            utilisateur_id: Identifiant du propriétaire des budgets.
            annee: Année facultative utilisée comme filtre.
            mois: Mois facultatif utilisé comme filtre.

        Returns:
            Les budgets correspondant à la période.
        """
        clauses, valeurs = ["utilisateur_id = ?"], [utilisateur_id]
        if annee is not None:
            clauses.append("annee = ?")
            valeurs.append(annee)
        if mois is not None:
            clauses.append("mois = ?")
            valeurs.append(mois)
        lignes = self._connexion.execute(
            "SELECT id, utilisateur_id, annee, mois, categorie_id, sous_categorie_id, "
            "montant_alloue, obligatoire FROM budgets WHERE "
            + " AND ".join(clauses)
            + " ORDER BY annee DESC, mois DESC, id",
            valeurs,
        ).fetchall()
        return [dict(ligne) for ligne in lignes]

    def modifier_budget(
        self, utilisateur_id: int, budget_id: int, **donnees: Any
    ) -> dict[str, Any] | None:
        """Modifier un budget accessible à un utilisateur.

        Args:
            utilisateur_id: Identifiant du propriétaire du budget.
            budget_id: Identifiant du budget à modifier.
            **donnees: Nouvelles valeurs du budget.

        Returns:
            Le budget modifié, ou ``None`` s'il est inaccessible.
        """
        with self._connexion:
            curseur = self._connexion.execute(
                "UPDATE budgets SET annee=?, mois=?, categorie_id=?, sous_categorie_id=?, "
                "montant_alloue=?, obligatoire=? WHERE utilisateur_id=? AND id=?",
                (
                    donnees["annee"],
                    donnees["mois"],
                    donnees["categorie_id"],
                    donnees["sous_categorie_id"],
                    donnees["montant_alloue"],
                    int(donnees["obligatoire"]),
                    utilisateur_id,
                    budget_id,
                ),
            )
        return (
            self.obtenir_budget(utilisateur_id, budget_id) if curseur.rowcount else None
        )

    def supprimer_budget(self, utilisateur_id: int, budget_id: int) -> bool:
        """Supprimer un budget accessible à un utilisateur.

        Args:
            utilisateur_id: Identifiant du propriétaire du budget.
            budget_id: Identifiant du budget à supprimer.

        Returns:
            ``True`` si un budget a été supprimé.
        """
        with self._connexion:
            curseur = self._connexion.execute(
                "DELETE FROM budgets WHERE utilisateur_id=? AND id=?",
                (utilisateur_id, budget_id),
            )
        return curseur.rowcount > 0
