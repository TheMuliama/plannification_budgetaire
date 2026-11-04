"""Accès aux alertes persistées."""
import sqlite3
from typing import Any


class RepositoryAlertes:
    def __init__(self, connexion: sqlite3.Connection) -> None:
        self._connexion=connexion

    def creer_alerte(self, utilisateur_id: int, budget_id: int, type_alerte: str,
                     message: str) -> dict[str, Any]:
        if self._connexion.execute("SELECT 1 FROM budgets WHERE id=? AND utilisateur_id=?",
                                   (budget_id,utilisateur_id)).fetchone() is None:
            raise ValueError("Budget introuvable pour cet utilisateur.")
        with self._connexion:
            curseur=self._connexion.execute(
                "INSERT INTO alertes (utilisateur_id,budget_id,type,message) VALUES (?,?,?,?)",
                (utilisateur_id,budget_id,type_alerte,message))
        return self.obtenir_alerte(utilisateur_id,curseur.lastrowid)

    def obtenir_alerte(self, utilisateur_id: int, alerte_id: int) -> dict[str, Any] | None:
        ligne=self._connexion.execute("SELECT * FROM alertes WHERE utilisateur_id=? AND id=?",
                                     (utilisateur_id,alerte_id)).fetchone()
        return dict(ligne) if ligne is not None else None

    def consulter_alertes(self, utilisateur_id: int, lue: bool | None=None) -> list[dict[str, Any]]:
        requete="SELECT * FROM alertes WHERE utilisateur_id=?"; valeurs=[utilisateur_id]
        if lue is not None: requete+=" AND lue=?"; valeurs.append(int(lue))
        return [dict(l) for l in self._connexion.execute(
            requete+" ORDER BY date_creation DESC,id DESC",valeurs).fetchall()]

    def marquer_lue(self, utilisateur_id: int, alerte_id: int) -> bool:
        with self._connexion:
            curseur=self._connexion.execute("UPDATE alertes SET lue=1 WHERE utilisateur_id=? AND id=?",
                                             (utilisateur_id,alerte_id))
        return curseur.rowcount>0
