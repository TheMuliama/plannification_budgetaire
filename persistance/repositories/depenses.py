"""Accès aux données des dépenses."""

import sqlite3
from typing import Any

class RepositoryDepenses:
    def __init__(self, connexion: sqlite3.Connection) -> None:
        self._connexion = connexion

    def ajouter_depense(self, **donnees: Any) -> dict[str, Any]:
        self._verifier_liens(donnees)
        with self._connexion:
            curseur = self._connexion.execute(
                "INSERT INTO depenses (utilisateur_id,budget_id,categorie_id,sous_categorie_id,"
                "montant,date,description,statut) VALUES (?,?,?,?,?,?,?,?)",
                tuple(donnees[cle] for cle in ("utilisateur_id","budget_id","categorie_id",
                    "sous_categorie_id","montant","date","description","statut")),
            )
        resultat = self.obtenir_depense(donnees["utilisateur_id"], curseur.lastrowid)
        assert resultat is not None
        return resultat

    def obtenir_depense(self, utilisateur_id: int, depense_id: int) -> dict[str, Any] | None:
        ligne = self._connexion.execute(
            "SELECT * FROM depenses WHERE utilisateur_id=? AND id=?", (utilisateur_id, depense_id)
        ).fetchone()
        return dict(ligne) if ligne is not None else None

    def consulter_depenses(self, utilisateur_id: int, statut: str | None = None) -> list[dict[str, Any]]:
        requete, valeurs = "SELECT * FROM depenses WHERE utilisateur_id=?", [utilisateur_id]
        if statut is not None:
            requete += " AND statut=?"; valeurs.append(statut)
        lignes = self._connexion.execute(requete + " ORDER BY date DESC,id DESC", valeurs).fetchall()
        return [dict(ligne) for ligne in lignes]

    def modifier_depense(self, utilisateur_id: int, depense_id: int, **donnees: Any) -> dict[str, Any] | None:
        donnees["utilisateur_id"] = utilisateur_id
        self._verifier_liens(donnees)
        with self._connexion:
            curseur = self._connexion.execute(
                "UPDATE depenses SET budget_id=?,categorie_id=?,sous_categorie_id=?,montant=?,"
                "date=?,description=?,statut=? WHERE utilisateur_id=? AND id=?",
                (donnees["budget_id"],donnees["categorie_id"],donnees["sous_categorie_id"],
                 donnees["montant"],donnees["date"],donnees["description"],donnees["statut"],
                 utilisateur_id,depense_id),
            )
        return self.obtenir_depense(utilisateur_id, depense_id) if curseur.rowcount else None

    def supprimer_depense(self, utilisateur_id: int, depense_id: int) -> bool:
        with self._connexion:
            curseur = self._connexion.execute("DELETE FROM depenses WHERE utilisateur_id=? AND id=?",
                                              (utilisateur_id, depense_id))
        return curseur.rowcount > 0

    def _verifier_liens(self, donnees: dict[str, Any]) -> None:
        budget = self._connexion.execute(
            "SELECT categorie_id,sous_categorie_id FROM budgets WHERE id=? AND utilisateur_id=?",
            (donnees["budget_id"], donnees["utilisateur_id"]),
        ).fetchone()
        if budget is None:
            raise ValueError("Budget introuvable pour cet utilisateur.")
        if budget["categorie_id"] != donnees["categorie_id"]:
            raise ValueError("La catégorie ne correspond pas au budget.")
        if donnees["sous_categorie_id"] is not None and self._connexion.execute(
            "SELECT 1 FROM sous_categories WHERE id=? AND categorie_id=?",
            (donnees["sous_categorie_id"], donnees["categorie_id"]),
        ).fetchone() is None:
            raise ValueError("Sous-catégorie incompatible avec la catégorie.")
