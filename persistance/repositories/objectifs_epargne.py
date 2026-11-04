"""Accès aux données des objectifs d'épargne."""

import sqlite3
from typing import Any

class RepositoryObjectifsEpargne:
    def __init__(self, connexion: sqlite3.Connection) -> None:
        self._connexion = connexion

    def creer_objectif(self, **donnees: Any) -> dict[str, Any]:
        with self._connexion:
            curseur = self._connexion.execute(
                "INSERT INTO objectifs_epargne (utilisateur_id,nom,montant_cible,montant_actuel,"
                "montant_periodique,date_cible) VALUES (?,?,?,?,?,?)",
                tuple(donnees[c] for c in ("utilisateur_id","nom","montant_cible",
                    "montant_actuel","montant_periodique","date_cible")),
            )
        resultat = self.obtenir_objectif(donnees["utilisateur_id"], curseur.lastrowid)
        assert resultat is not None
        return resultat

    def obtenir_objectif(self, utilisateur_id: int, objectif_id: int) -> dict[str, Any] | None:
        ligne = self._connexion.execute(
            "SELECT * FROM objectifs_epargne WHERE utilisateur_id=? AND id=?",
            (utilisateur_id, objectif_id),
        ).fetchone()
        return dict(ligne) if ligne is not None else None

    def consulter_objectifs(self, utilisateur_id: int) -> list[dict[str, Any]]:
        return [dict(ligne) for ligne in self._connexion.execute(
            "SELECT * FROM objectifs_epargne WHERE utilisateur_id=? ORDER BY date_cible,id",
            (utilisateur_id,),
        ).fetchall()]

    def modifier_objectif(self, utilisateur_id: int, objectif_id: int,
                          **donnees: Any) -> dict[str, Any] | None:
        with self._connexion:
            curseur = self._connexion.execute(
                "UPDATE objectifs_epargne SET nom=?,montant_cible=?,montant_actuel=?,"
                "montant_periodique=?,date_cible=? WHERE utilisateur_id=? AND id=?",
                (donnees["nom"],donnees["montant_cible"],donnees["montant_actuel"],
                 donnees["montant_periodique"],donnees["date_cible"],utilisateur_id,objectif_id),
            )
        return self.obtenir_objectif(utilisateur_id, objectif_id) if curseur.rowcount else None

    def supprimer_objectif(self, utilisateur_id: int, objectif_id: int) -> bool:
        with self._connexion:
            curseur = self._connexion.execute(
                "DELETE FROM objectifs_epargne WHERE utilisateur_id=? AND id=?",
                (utilisateur_id, objectif_id),
            )
        return curseur.rowcount > 0
