"""Accès aux données des objectifs d'épargne."""

import sqlite3
from typing import Any


class RepositoryObjectifsEpargne:
    """Lire et écrire les objectifs et leurs versements."""

    def __init__(self, connexion: sqlite3.Connection) -> None:
        self._connexion = connexion

    def creer_objectif(self, **donnees: Any) -> dict[str, Any]:
        """Créer un objectif d'épargne.

        Args:
            **donnees: Valeurs validées de l'objectif.

        Returns:
            L'objectif enregistré.
        """
        with self._connexion:
            curseur = self._connexion.execute(
                "INSERT INTO objectifs_epargne (utilisateur_id,nom,montant_cible,montant_actuel,"
                "montant_periodique,date_cible) VALUES (?,?,?,?,?,?)",
                tuple(
                    donnees[c]
                    for c in (
                        "utilisateur_id",
                        "nom",
                        "montant_cible",
                        "montant_actuel",
                        "montant_periodique",
                        "date_cible",
                    )
                ),
            )
        resultat = self.obtenir_objectif(donnees["utilisateur_id"], curseur.lastrowid)
        assert resultat is not None
        return resultat

    def obtenir_objectif(
        self, utilisateur_id: int, objectif_id: int
    ) -> dict[str, Any] | None:
        """Récupérer un objectif accessible à un utilisateur.

        Args:
            utilisateur_id: Identifiant du propriétaire de l'objectif.
            objectif_id: Identifiant de l'objectif recherché.

        Returns:
            L'objectif trouvé, ou ``None`` s'il est inaccessible.
        """
        ligne = self._connexion.execute(
            "SELECT * FROM objectifs_epargne WHERE utilisateur_id=? AND id=?",
            (utilisateur_id, objectif_id),
        ).fetchone()
        return dict(ligne) if ligne is not None else None

    def consulter_objectifs(self, utilisateur_id: int) -> list[dict[str, Any]]:
        """Consulter les objectifs d'un utilisateur.

        Args:
            utilisateur_id: Identifiant du propriétaire des objectifs.

        Returns:
            Les objectifs appartenant à l'utilisateur.
        """
        return [
            dict(ligne)
            for ligne in self._connexion.execute(
                "SELECT * FROM objectifs_epargne WHERE utilisateur_id=? ORDER BY date_cible,id",
                (utilisateur_id,),
            ).fetchall()
        ]

    def modifier_objectif(
        self, utilisateur_id: int, objectif_id: int, **donnees: Any
    ) -> dict[str, Any] | None:
        """Modifier un objectif accessible à un utilisateur.

        Args:
            utilisateur_id: Identifiant du propriétaire de l'objectif.
            objectif_id: Identifiant de l'objectif à modifier.
            **donnees: Nouvelles valeurs de l'objectif.

        Returns:
            L'objectif modifié, ou ``None`` s'il est inaccessible.
        """
        with self._connexion:
            curseur = self._connexion.execute(
                "UPDATE objectifs_epargne SET nom=?,montant_cible=?,montant_actuel=?,"
                "montant_periodique=?,date_cible=? WHERE utilisateur_id=? AND id=?",
                (
                    donnees["nom"],
                    donnees["montant_cible"],
                    donnees["montant_actuel"],
                    donnees["montant_periodique"],
                    donnees["date_cible"],
                    utilisateur_id,
                    objectif_id,
                ),
            )
        return (
            self.obtenir_objectif(utilisateur_id, objectif_id)
            if curseur.rowcount
            else None
        )

    def supprimer_objectif(self, utilisateur_id: int, objectif_id: int) -> bool:
        """Supprimer un objectif accessible à un utilisateur.

        Args:
            utilisateur_id: Identifiant du propriétaire de l'objectif.
            objectif_id: Identifiant de l'objectif à supprimer.

        Returns:
            ``True`` si un objectif a été supprimé.
        """
        with self._connexion:
            curseur = self._connexion.execute(
                "DELETE FROM objectifs_epargne WHERE utilisateur_id=? AND id=?",
                (utilisateur_id, objectif_id),
            )
        return curseur.rowcount > 0

    def ajouter_versement(
        self, utilisateur_id: int, objectif_id: int, montant: float, date_versement: str
    ) -> dict[str, Any]:
        """Ajouter un versement et augmenter l'objectif atomiquement.

        Args:
            utilisateur_id: Identifiant du propriétaire de l'objectif.
            objectif_id: Identifiant de l'objectif à alimenter.
            montant: Montant du versement.
            date_versement: Date du versement au format ISO.

        Returns:
            Le versement enregistré.

        """
        with self._connexion:
            curseur = self._connexion.execute(
                "INSERT INTO versements_epargne "
                "(utilisateur_id,objectif_id,montant,date) VALUES (?,?,?,?)",
                (utilisateur_id, objectif_id, montant, date_versement),
            )
            self._connexion.execute(
                "UPDATE objectifs_epargne SET montant_actuel=montant_actuel+? "
                "WHERE id=? AND utilisateur_id=?",
                (montant, objectif_id, utilisateur_id),
            )
        ligne = self._connexion.execute(
            "SELECT id,utilisateur_id,objectif_id,montant,date FROM versements_epargne "
            "WHERE id=?",
            (curseur.lastrowid,),
        ).fetchone()
        return dict(ligne)

    def consulter_versements(
        self, utilisateur_id: int, objectif_id: int | None = None
    ) -> list[dict[str, Any]]:
        """Consulter les versements d'un utilisateur.

        Args:
            utilisateur_id: Identifiant du propriétaire des versements.
            objectif_id: Objectif facultatif utilisé comme filtre.

        Returns:
            Les versements correspondant au filtre.
        """
        requete = (
            "SELECT id,utilisateur_id,objectif_id,montant,date "
            "FROM versements_epargne WHERE utilisateur_id=?"
        )
        valeurs: list[Any] = [utilisateur_id]
        if objectif_id is not None:
            requete += " AND objectif_id=?"
            valeurs.append(objectif_id)
        return [
            dict(ligne)
            for ligne in self._connexion.execute(
                requete + " ORDER BY date DESC,id DESC", valeurs
            ).fetchall()
        ]

    def total_versements(
        self, utilisateur_id: int, debut: str | None = None, fin: str | None = None
    ) -> float:
        """Calculer le total des versements sur une période.

        Args:
            utilisateur_id: Identifiant du propriétaire des versements.
            debut: Date de début facultative au format ISO.
            fin: Date de fin facultative au format ISO.

        Returns:
            Le total des versements correspondant aux filtres.
        """
        clauses = ["utilisateur_id=?"]
        valeurs: list[Any] = [utilisateur_id]
        if debut is not None:
            clauses.append("date>=?")
            valeurs.append(debut)
        if fin is not None:
            clauses.append("date<=?")
            valeurs.append(fin)
        ligne = self._connexion.execute(
            "SELECT COALESCE(SUM(montant),0) FROM versements_epargne WHERE "
            + " AND ".join(clauses),
            valeurs,
        ).fetchone()
        return float(ligne[0])
