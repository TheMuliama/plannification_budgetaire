import sqlite3
from typing import Any


class RepositoryRevenus:
    """Lire et écrire les revenus en limitant chaque accès au propriétaire."""

    def __init__(self, connexion: sqlite3.Connection) -> None:
        self.connexion = connexion

    def ajouter_revenu(
        self, utilisateur_id: int, montant: float, date: str,
        description: str | None, statut: str,
    ) -> int:
        """Enregistrer un revenu et retourner son identifiant.

        Le service valide la date et le montant. Le schéma impose également
        montant > 0 et un statut parmi 'prevu' et 'recu'. Les erreurs SQLite
        remontent au service et la transaction est annulée en cas d'échec.
        """
        with self.connexion:
            curseur = self.connexion.execute(
                "INSERT INTO revenus "
                "(utilisateur_id, montant, date, description, statut) "
                "VALUES (?, ?, ?, ?, ?)",
                (utilisateur_id, montant, date, description, statut),
            )
            identifiant = curseur.lastrowid
            assert identifiant is not None
            return identifiant

    def obtenir_revenu(
        self, utilisateur_id: int, revenu_id: int,
    ) -> dict[str, Any] | None:
        """Retourner le revenu du propriétaire, ou None s'il est introuvable."""
        curseur = self.connexion.execute(
            "SELECT id, utilisateur_id, montant, date, description, statut "
            "FROM revenus WHERE utilisateur_id = ? AND id = ?",
            (utilisateur_id, revenu_id),
        )
        ligne = curseur.fetchone()
        return self._dictionnaire(curseur, ligne) if ligne is not None else None

    def consulter_revenus(
        self, utilisateur_id: int, debut: str | None = None,
        fin: str | None = None, statut: str | None = None,
    ) -> list[dict[str, Any]]:
        """Lister par date décroissante, avec bornes inclusives et statut optionnel."""
        filtre, valeurs = self._filtre(utilisateur_id, debut, fin, statut)
        curseur = self.connexion.execute(
            "SELECT id, utilisateur_id, montant, date, description, statut "
            "FROM revenus WHERE " + filtre + " ORDER BY date DESC, id DESC",
            valeurs,
        )
        return [self._dictionnaire(curseur, ligne) for ligne in curseur.fetchall()]

    def modifier_revenu(
        self, utilisateur_id: int, revenu_id: int, montant: float,
        date: str, description: str | None, statut: str,
    ) -> bool:
        """Remplacer les champs ; retourner False si le revenu est inaccessible."""
        with self.connexion:
            curseur = self.connexion.execute(
                "UPDATE revenus SET montant = ?, date = ?, description = ?, "
                "statut = ? WHERE utilisateur_id = ? AND id = ?",
                (montant, date, description, statut, utilisateur_id, revenu_id),
            )
            return curseur.rowcount > 0

    def supprimer_revenu(self, utilisateur_id: int, revenu_id: int) -> bool:
        """Supprimer le revenu du propriétaire ; indiquer si une ligne a été supprimée."""
        with self.connexion:
            curseur = self.connexion.execute(
                "DELETE FROM revenus WHERE utilisateur_id = ? AND id = ?",
                (utilisateur_id, revenu_id),
            )
            return curseur.rowcount > 0

    def total_revenus(
        self, utilisateur_id: int, debut: str | None = None,
        fin: str | None = None, statut: str | None = None,
    ) -> float:
        """Retourner la somme en euros, zéro si vide.

        Sans filtre de statut, inclut tous les revenus. Pour le budget actuel,
        le service doit demander explicitement statut='recu'. Les valeurs REAL
        peuvent présenter des approximations binaires ; l'arrondi d'affichage
        relève du service ou de l'interface.
        """
        filtre, valeurs = self._filtre(utilisateur_id, debut, fin, statut)
        ligne = self.connexion.execute(
            "SELECT COALESCE(SUM(montant), 0) FROM revenus WHERE " + filtre,
            valeurs,
        ).fetchone()
        return float(ligne[0])

    @staticmethod
    def _filtre(
        utilisateur_id: int, debut: str | None, fin: str | None,
        statut: str | None,
    ) -> tuple[str, list[Any]]:
        # Les fragments SQL sont constants ; toutes les données sont paramétrées.
        clauses = ["utilisateur_id = ?"]
        valeurs: list[Any] = [utilisateur_id]
        for clause, valeur in (
            ("date >= ?", debut), ("date <= ?", fin), ("statut = ?", statut),
        ):
            if valeur is not None:
                clauses.append(clause)
                valeurs.append(valeur)
        return " AND ".join(clauses), valeurs

    @staticmethod
    def _dictionnaire(curseur: sqlite3.Cursor, ligne: Any) -> dict[str, Any]:
        """Convertir une ligne SQLite standard ou sqlite3.Row en dictionnaire."""
        return dict(zip((colonne[0] for colonne in curseur.description), ligne))

