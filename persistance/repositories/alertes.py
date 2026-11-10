"""Accès aux alertes persistées."""

import sqlite3
from typing import Any


class RepositoryAlertes:
    """Lire et écrire les alertes en les isolant par utilisateur."""

    def __init__(self, connexion: sqlite3.Connection) -> None:
        self._connexion = connexion

    def creer_alerte(
        self, utilisateur_id: int, budget_id: int, type_alerte: str, message: str
    ) -> dict[str, Any]:
        """Créer une alerte rattachée à un budget accessible.

        Args:
            utilisateur_id: Identifiant du propriétaire de l'alerte.
            budget_id: Identifiant du budget concerné.
            type_alerte: Niveau de l'alerte.
            message: Texte présenté à l'utilisateur.

        Returns:
            L'alerte enregistrée.

        Raises:
            ValueError: Si le budget n'appartient pas à l'utilisateur.
        """
        if (
            self._connexion.execute(
                "SELECT 1 FROM budgets WHERE id=? AND utilisateur_id=?",
                (budget_id, utilisateur_id),
            ).fetchone()
            is None
        ):
            raise ValueError("Budget introuvable pour cet utilisateur.")
        with self._connexion:
            curseur = self._connexion.execute(
                "INSERT INTO alertes (utilisateur_id,budget_id,type,message) VALUES (?,?,?,?)",
                (utilisateur_id, budget_id, type_alerte, message),
            )
        return self.obtenir_alerte(utilisateur_id, curseur.lastrowid)

    def obtenir_alerte(
        self, utilisateur_id: int, alerte_id: int
    ) -> dict[str, Any] | None:
        """Récupérer une alerte accessible à un utilisateur.

        Args:
            utilisateur_id: Identifiant du propriétaire de l'alerte.
            alerte_id: Identifiant de l'alerte recherchée.

        Returns:
            L'alerte trouvée, ou ``None`` si elle est inaccessible.
        """
        ligne = self._connexion.execute(
            "SELECT * FROM alertes WHERE utilisateur_id=? AND id=?",
            (utilisateur_id, alerte_id),
        ).fetchone()
        return dict(ligne) if ligne is not None else None

    def consulter_alertes(
        self, utilisateur_id: int, lue: bool | None = None
    ) -> list[dict[str, Any]]:
        """Consulter les alertes d'un utilisateur.

        Args:
            utilisateur_id: Identifiant du propriétaire des alertes.
            lue: État de lecture facultatif utilisé comme filtre.

        Returns:
            Les alertes correspondant au filtre.
        """
        requete = "SELECT * FROM alertes WHERE utilisateur_id=?"
        valeurs = [utilisateur_id]
        if lue is not None:
            requete += " AND lue=?"
            valeurs.append(int(lue))
        return [
            dict(l)
            for l in self._connexion.execute(
                requete + " ORDER BY date_creation DESC,id DESC", valeurs
            ).fetchall()
        ]

    def marquer_lue(self, utilisateur_id: int, alerte_id: int) -> bool:
        """Marquer une alerte accessible comme lue.

        Args:
            utilisateur_id: Identifiant du propriétaire de l'alerte.
            alerte_id: Identifiant de l'alerte à modifier.

        Returns:
            ``True`` si une alerte a été modifiée.
        """
        with self._connexion:
            curseur = self._connexion.execute(
                "UPDATE alertes SET lue=1 WHERE utilisateur_id=? AND id=?",
                (utilisateur_id, alerte_id),
            )
        return curseur.rowcount > 0
