"""Accès aux données des budgets mensuels."""

import sqlite3
from typing import Any

class RepositoryBudgets:
    def __init__(self, connexion: sqlite3.Connection) -> None:
        self._connexion = connexion

    def creer_budget(self, utilisateur_id: int, annee: int, mois: int,
                     categorie_id: int, sous_categorie_id: int | None,
                     montant_alloue: float, obligatoire: bool) -> dict[str, Any]:
        self._verifier_classement(utilisateur_id, categorie_id, sous_categorie_id)
        with self._connexion:
            curseur = self._connexion.execute(
                "INSERT INTO budgets (utilisateur_id, annee, mois, categorie_id, "
                "sous_categorie_id, montant_alloue, obligatoire) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (utilisateur_id, annee, mois, categorie_id, sous_categorie_id,
                 montant_alloue, int(obligatoire)),
            )
        resultat = self.obtenir_budget(utilisateur_id, curseur.lastrowid)
        assert resultat is not None
        return resultat

    def obtenir_budget(self, utilisateur_id: int, budget_id: int) -> dict[str, Any] | None:
        ligne = self._connexion.execute(
            "SELECT id, utilisateur_id, annee, mois, categorie_id, sous_categorie_id, "
            "montant_alloue, obligatoire FROM budgets WHERE utilisateur_id = ? AND id = ?",
            (utilisateur_id, budget_id),
        ).fetchone()
        return dict(ligne) if ligne is not None else None

    def consulter_budgets(self, utilisateur_id: int, annee: int | None = None,
                          mois: int | None = None) -> list[dict[str, Any]]:
        clauses, valeurs = ["utilisateur_id = ?"], [utilisateur_id]
        if annee is not None:
            clauses.append("annee = ?"); valeurs.append(annee)
        if mois is not None:
            clauses.append("mois = ?"); valeurs.append(mois)
        lignes = self._connexion.execute(
            "SELECT id, utilisateur_id, annee, mois, categorie_id, sous_categorie_id, "
            "montant_alloue, obligatoire FROM budgets WHERE " + " AND ".join(clauses) +
            " ORDER BY annee DESC, mois DESC, id", valeurs,
        ).fetchall()
        return [dict(ligne) for ligne in lignes]

    def modifier_budget(self, utilisateur_id: int, budget_id: int, **donnees: Any) -> dict[str, Any] | None:
        self._verifier_classement(utilisateur_id, donnees["categorie_id"], donnees["sous_categorie_id"])
        with self._connexion:
            curseur = self._connexion.execute(
                "UPDATE budgets SET annee=?, mois=?, categorie_id=?, sous_categorie_id=?, "
                "montant_alloue=?, obligatoire=? WHERE utilisateur_id=? AND id=?",
                (donnees["annee"], donnees["mois"], donnees["categorie_id"],
                 donnees["sous_categorie_id"], donnees["montant_alloue"],
                 int(donnees["obligatoire"]), utilisateur_id, budget_id),
            )
        return self.obtenir_budget(utilisateur_id, budget_id) if curseur.rowcount else None

    def supprimer_budget(self, utilisateur_id: int, budget_id: int) -> bool:
        with self._connexion:
            curseur = self._connexion.execute(
                "DELETE FROM budgets WHERE utilisateur_id=? AND id=?", (utilisateur_id, budget_id)
            )
        return curseur.rowcount > 0

    def _verifier_classement(self, utilisateur_id: int, categorie_id: int,
                             sous_categorie_id: int | None) -> None:
        categorie = self._connexion.execute(
            "SELECT 1 FROM categories WHERE id=? AND utilisateur_id=?",
            (categorie_id, utilisateur_id),
        ).fetchone()
        if categorie is None:
            raise ValueError("Catégorie introuvable pour cet utilisateur.")
        if sous_categorie_id is not None and self._connexion.execute(
            "SELECT 1 FROM sous_categories WHERE id=? AND categorie_id=?",
            (sous_categorie_id, categorie_id),
        ).fetchone() is None:
            raise ValueError("Sous-catégorie incompatible avec la catégorie.")
