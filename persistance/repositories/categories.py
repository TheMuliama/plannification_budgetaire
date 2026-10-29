"""Accès aux données des catégories et sous-catégories."""

import sqlite3


class RepositoryCategories:
    """Persister les catégories et sous-catégories.

    Ce repository exécute uniquement les opérations de stockage et de lecture.
    Il ne porte aucune règle métier sur les catégories.
    """

    def __init__(self, connexion: sqlite3.Connection) -> None:
        """Initialiser le repository avec une connexion SQLite.

        Args:
            connexion: Connexion SQLite utilisée pour la persistance.
        """
        self._connexion = connexion

    def creer_categorie(self, identifiant_utilisateur: int, nom: str) -> dict[str, int | str]:
        """Enregistrer une catégorie pour un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire.
            nom: Nom de la catégorie.

        Returns:
            Les données de la catégorie enregistrée.
        """
        curseur = self._connexion.execute(
            "INSERT INTO categories (utilisateur_id, nom) VALUES (?, ?)",
            (identifiant_utilisateur, nom),
        )
        self._connexion.commit()
        return self.recuperer_categorie(identifiant_utilisateur, curseur.lastrowid)

    def recuperer_categorie(self, identifiant_utilisateur: int, identifiant_categorie: int) -> dict[str, int | str] | None:
        """Lire une catégorie appartenant à un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire attendu.
            identifiant_categorie: Identifiant de la catégorie recherchée.

        Returns:
            Les données de la catégorie, ou None lorsqu'elle est absente.
        """
        ligne = self._connexion.execute(
            "SELECT id, utilisateur_id, nom FROM categories WHERE id = ? AND utilisateur_id = ?",
            (identifiant_categorie, identifiant_utilisateur),
        ).fetchone()
        return dict(ligne) if ligne is not None else None

    def recuperer_categories(self, identifiant_utilisateur: int) -> list[dict[str, int | str]]:
        """Lire les catégories d'un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire des catégories.

        Returns:
            Les catégories appartenant à cet utilisateur.
        """
        lignes = self._connexion.execute(
            "SELECT id, utilisateur_id, nom FROM categories WHERE utilisateur_id = ? ORDER BY id",
            (identifiant_utilisateur,),
        ).fetchall()
        return [dict(ligne) for ligne in lignes]

    def modifier_categorie(self, identifiant_utilisateur: int, identifiant_categorie: int, nom: str) -> dict[str, int | str] | None:
        """Mettre à jour le nom d'une catégorie d'un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire attendu.
            identifiant_categorie: Identifiant de la catégorie à modifier.
            nom: Nouveau nom de la catégorie.

        Returns:
            La catégorie modifiée, ou None lorsqu'elle est absente.
        """
        curseur = self._connexion.execute(
            "UPDATE categories SET nom = ? WHERE id = ? AND utilisateur_id = ?",
            (nom, identifiant_categorie, identifiant_utilisateur),
        )
        self._connexion.commit()
        if curseur.rowcount == 0:
            return None
        return self.recuperer_categorie(identifiant_utilisateur, identifiant_categorie)

    def supprimer_categorie(self, identifiant_utilisateur: int, identifiant_categorie: int) -> bool:
        """Supprimer une catégorie appartenant à un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire attendu.
            identifiant_categorie: Identifiant de la catégorie à supprimer.

        Returns:
            True si une catégorie a été supprimée, sinon False.
        """
        curseur = self._connexion.execute(
            "DELETE FROM categories WHERE id = ? AND utilisateur_id = ?",
            (identifiant_categorie, identifiant_utilisateur),
        )
        self._connexion.commit()
        return curseur.rowcount > 0

    def creer_sous_categorie(self, identifiant_categorie: int, nom: str) -> dict[str, int | str]:
        """Enregistrer une sous-catégorie pour une catégorie.

        Args:
            identifiant_categorie: Identifiant de la catégorie parente.
            nom: Nom de la sous-catégorie.

        Returns:
            Les données de la sous-catégorie enregistrée.
        """
        curseur = self._connexion.execute(
            "INSERT INTO sous_categories (categorie_id, nom) VALUES (?, ?)",
            (identifiant_categorie, nom),
        )
        self._connexion.commit()
        return self.recuperer_sous_categorie(identifiant_categorie, curseur.lastrowid)

    def recuperer_sous_categorie(self, identifiant_categorie: int, identifiant_sous_categorie: int) -> dict[str, int | str] | None:
        """Lire une sous-catégorie appartenant à une catégorie.

        Args:
            identifiant_categorie: Identifiant de la catégorie parente attendue.
            identifiant_sous_categorie: Identifiant de la sous-catégorie recherchée.

        Returns:
            Les données de la sous-catégorie, ou None lorsqu'elle est absente.
        """
        ligne = self._connexion.execute(
            "SELECT id, categorie_id, nom FROM sous_categories WHERE id = ? AND categorie_id = ?",
            (identifiant_sous_categorie, identifiant_categorie),
        ).fetchone()
        return dict(ligne) if ligne is not None else None

    def recuperer_sous_categories(self, identifiant_categorie: int) -> list[dict[str, int | str]]:
        """Lire les sous-catégories d'une catégorie.

        Args:
            identifiant_categorie: Identifiant de la catégorie parente.

        Returns:
            Les sous-catégories rattachées à cette catégorie.
        """
        lignes = self._connexion.execute(
            "SELECT id, categorie_id, nom FROM sous_categories WHERE categorie_id = ? ORDER BY id",
            (identifiant_categorie,),
        ).fetchall()
        return [dict(ligne) for ligne in lignes]

    def modifier_sous_categorie(self, identifiant_categorie: int, identifiant_sous_categorie: int, nom: str) -> dict[str, int | str] | None:
        """Mettre à jour le nom d'une sous-catégorie.

        Args:
            identifiant_categorie: Identifiant de la catégorie parente attendue.
            identifiant_sous_categorie: Identifiant de la sous-catégorie.
            nom: Nouveau nom de la sous-catégorie.

        Returns:
            La sous-catégorie modifiée, ou None lorsqu'elle est absente.
        """
        curseur = self._connexion.execute(
            "UPDATE sous_categories SET nom = ? WHERE id = ? AND categorie_id = ?",
            (nom, identifiant_sous_categorie, identifiant_categorie),
        )
        self._connexion.commit()
        if curseur.rowcount == 0:
            return None
        return self.recuperer_sous_categorie(identifiant_categorie, identifiant_sous_categorie)

    def supprimer_sous_categorie(self, identifiant_categorie: int, identifiant_sous_categorie: int) -> bool:
        """Supprimer une sous-catégorie appartenant à une catégorie.

        Args:
            identifiant_categorie: Identifiant de la catégorie parente attendue.
            identifiant_sous_categorie: Identifiant de la sous-catégorie à supprimer.

        Returns:
            True si une sous-catégorie a été supprimée, sinon False.
        """
        curseur = self._connexion.execute(
            "DELETE FROM sous_categories WHERE id = ? AND categorie_id = ?",
            (identifiant_sous_categorie, identifiant_categorie),
        )
        self._connexion.commit()
        return curseur.rowcount > 0
