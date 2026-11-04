import sqlite3
from typing import Any


class RepositoryRevenus:
    """Lire et écrire les revenus en limitant chaque accès au propriétaire."""

    def __init__(self, connexion: sqlite3.Connection) -> None:
        self.connexion = connexion

    def ajouter_revenu(
        self,
        utilisateur_id: int,
        montant: float,
        date: str,
        description: str | None,
        statut: str,
        categorie: str = "Salaire",
    ) -> int:
        """Enregistrer un revenu.

        Args:
            utilisateur_id: Identifiant du propriétaire du revenu.
            montant: Montant positif du revenu.
            date: Date du revenu au format ISO.
            description: Description facultative du revenu.
            statut: Statut prévisionnel ou reçu.
            categorie: Catégorie du revenu.

        Returns:
            L'identifiant du revenu enregistré.
        """
        with self.connexion:
            curseur = self.connexion.execute(
                "INSERT INTO revenus "
                "(utilisateur_id, montant, date, description, statut, categorie) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (utilisateur_id, montant, date, description, statut, categorie),
            )
            identifiant = curseur.lastrowid
            assert identifiant is not None
            return identifiant

    def obtenir_revenu(
        self,
        utilisateur_id: int,
        revenu_id: int,
    ) -> dict[str, Any] | None:
        """Récupérer un revenu accessible à un utilisateur.

        Args:
            utilisateur_id: Identifiant du propriétaire du revenu.
            revenu_id: Identifiant du revenu recherché.

        Returns:
            Le revenu trouvé, ou ``None`` s'il est inaccessible.
        """
        curseur = self.connexion.execute(
            "SELECT id, utilisateur_id, montant, date, description, statut, categorie "
            "FROM revenus WHERE utilisateur_id = ? AND id = ?",
            (utilisateur_id, revenu_id),
        )
        ligne = curseur.fetchone()
        return self._dictionnaire(curseur, ligne) if ligne is not None else None

    def consulter_revenus(
        self,
        utilisateur_id: int,
        debut: str | None = None,
        fin: str | None = None,
        statut: str | None = None,
    ) -> list[dict[str, Any]]:
        """Consulter les revenus d'un utilisateur.

        Args:
            utilisateur_id: Identifiant du propriétaire des revenus.
            debut: Date de début facultative au format ISO.
            fin: Date de fin facultative au format ISO.
            statut: Statut facultatif utilisé comme filtre.

        Returns:
            Les revenus triés par date décroissante.
        """
        filtre, valeurs = self._filtre(utilisateur_id, debut, fin, statut)
        curseur = self.connexion.execute(
            "SELECT id, utilisateur_id, montant, date, description, statut, categorie "
            "FROM revenus WHERE " + filtre + " ORDER BY date DESC, id DESC",
            valeurs,
        )
        return [self._dictionnaire(curseur, ligne) for ligne in curseur.fetchall()]

    def modifier_revenu(
        self,
        utilisateur_id: int,
        revenu_id: int,
        montant: float,
        date: str,
        description: str | None,
        statut: str,
        categorie: str = "Salaire",
    ) -> bool:
        """Modifier un revenu accessible à un utilisateur.

        Args:
            utilisateur_id: Identifiant du propriétaire du revenu.
            revenu_id: Identifiant du revenu à modifier.
            montant: Nouveau montant du revenu.
            date: Nouvelle date au format ISO.
            description: Nouvelle description facultative.
            statut: Nouveau statut du revenu.
            categorie: Nouvelle catégorie du revenu.

        Returns:
            ``True`` si un revenu a été modifié.
        """
        with self.connexion:
            curseur = self.connexion.execute(
                "UPDATE revenus SET montant = ?, date = ?, description = ?, "
                "statut = ?, categorie = ? WHERE utilisateur_id = ? AND id = ?",
                (
                    montant,
                    date,
                    description,
                    statut,
                    categorie,
                    utilisateur_id,
                    revenu_id,
                ),
            )
            return curseur.rowcount > 0

    def supprimer_revenu(self, utilisateur_id: int, revenu_id: int) -> bool:
        """Supprimer un revenu accessible à un utilisateur.

        Args:
            utilisateur_id: Identifiant du propriétaire du revenu.
            revenu_id: Identifiant du revenu à supprimer.

        Returns:
            ``True`` si un revenu a été supprimé.
        """
        with self.connexion:
            curseur = self.connexion.execute(
                "DELETE FROM revenus WHERE utilisateur_id = ? AND id = ?",
                (utilisateur_id, revenu_id),
            )
            return curseur.rowcount > 0

    def total_revenus(
        self,
        utilisateur_id: int,
        debut: str | None = None,
        fin: str | None = None,
        statut: str | None = None,
    ) -> float:
        """Calculer le total des revenus d'un utilisateur.

        Args:
            utilisateur_id: Identifiant du propriétaire des revenus.
            debut: Date de début facultative au format ISO.
            fin: Date de fin facultative au format ISO.
            statut: Statut facultatif utilisé comme filtre.

        Returns:
            La somme des revenus correspondant aux filtres, ou zéro.
        """
        filtre, valeurs = self._filtre(utilisateur_id, debut, fin, statut)
        ligne = self.connexion.execute(
            "SELECT COALESCE(SUM(montant), 0) FROM revenus WHERE " + filtre,
            valeurs,
        ).fetchone()
        return float(ligne[0])

    @staticmethod
    def _filtre(
        utilisateur_id: int,
        debut: str | None,
        fin: str | None,
        statut: str | None,
    ) -> tuple[str, list[Any]]:
        # Les fragments SQL sont constants ; toutes les données sont paramétrées.
        clauses = ["utilisateur_id = ?"]
        valeurs: list[Any] = [utilisateur_id]
        for clause, valeur in (
            ("date >= ?", debut),
            ("date <= ?", fin),
            ("statut = ?", statut),
        ):
            if valeur is not None:
                clauses.append(clause)
                valeurs.append(valeur)
        return " AND ".join(clauses), valeurs

    @staticmethod
    def _dictionnaire(curseur: sqlite3.Cursor, ligne: Any) -> dict[str, Any]:
        """Convertir une ligne SQLite standard ou sqlite3.Row en dictionnaire."""
        return dict(zip((colonne[0] for colonne in curseur.description), ligne))
