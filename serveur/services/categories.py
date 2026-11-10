"""Service de gestion des catégories."""

import sqlite3

from persistance.repositories.categories import RepositoryCategories


class GestionnaireCategories:
    """Gérer les catégories et sous-catégories des utilisateurs.

    Cette classe crée, modifie, supprime et récupère les éléments utilisés pour
    classer les dépenses. Elle ne gère ni les dépenses, ni les budgets, ni les
    calculs financiers.
    """

    def __init__(self, repository: RepositoryCategories) -> None:
        """Initialiser le gestionnaire avec son accès aux données.

        Args:
            repository: Repository chargé de persister les catégories.
        """
        self._repository = repository

    def creer_categorie(
        self, identifiant_utilisateur: int, nom: str
    ) -> dict[str, int | str]:
        """Créer une catégorie pour un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire.
            nom: Nom de la catégorie.

        Returns:
            La catégorie créée.
        """
        try:
            return self._repository.creer_categorie(
                identifiant_utilisateur,
                self._valider_nom(nom),
            )
        except sqlite3.IntegrityError as erreur:
            raise ValueError("Cette catégorie existe déjà.") from erreur

    def recuperer_categorie(
        self, identifiant_utilisateur: int, identifiant_categorie: int
    ) -> dict[str, int | str]:
        """Récupérer une catégorie appartenant à un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire attendu.
            identifiant_categorie: Identifiant de la catégorie recherchée.

        Returns:
            La catégorie demandée.

        Raises:
            ValueError: Si la catégorie n'existe pas pour cet utilisateur.
        """
        categorie = self._repository.recuperer_categorie(
            identifiant_utilisateur, identifiant_categorie
        )
        if categorie is None:
            raise ValueError("Catégorie introuvable pour cet utilisateur.")
        return categorie

    def recuperer_categories(
        self, identifiant_utilisateur: int
    ) -> list[dict[str, int | str]]:
        """Récupérer les catégories d'un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire des catégories.

        Returns:
            La liste de ses catégories.
        """
        return self._repository.recuperer_categories(identifiant_utilisateur)

    def modifier_categorie(
        self, identifiant_utilisateur: int, identifiant_categorie: int, nom: str
    ) -> dict[str, int | str]:
        """Modifier le nom d'une catégorie appartenant à un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire attendu.
            identifiant_categorie: Identifiant de la catégorie à modifier.
            nom: Nouveau nom de la catégorie.

        Returns:
            La catégorie modifiée.

        Raises:
            ValueError: Si la catégorie n'existe pas pour cet utilisateur.
        """
        try:
            categorie = self._repository.modifier_categorie(
                identifiant_utilisateur,
                identifiant_categorie,
                self._valider_nom(nom),
            )
        except sqlite3.IntegrityError as erreur:
            raise ValueError("Cette catégorie existe déjà.") from erreur
        if categorie is None:
            raise ValueError("Catégorie introuvable pour cet utilisateur.")
        return categorie

    def supprimer_categorie(
        self, identifiant_utilisateur: int, identifiant_categorie: int
    ) -> None:
        """Supprimer une catégorie appartenant à un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire attendu.
            identifiant_categorie: Identifiant de la catégorie à supprimer.

        Returns:
            None.

        Raises:
            ValueError: Si la catégorie n'existe pas pour cet utilisateur.
        """
        supprimee = self._repository.supprimer_categorie(
            identifiant_utilisateur, identifiant_categorie
        )
        if not supprimee:
            raise ValueError("Catégorie introuvable pour cet utilisateur.")

    def creer_sous_categorie(
        self, identifiant_utilisateur: int, identifiant_categorie: int, nom: str
    ) -> dict[str, int | str]:
        """Créer une sous-catégorie dans une catégorie de l'utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire de la catégorie.
            identifiant_categorie: Identifiant de la catégorie parente.
            nom: Nom de la sous-catégorie.

        Returns:
            La sous-catégorie créée.

        Raises:
            ValueError: Si la catégorie n'existe pas pour cet utilisateur.
        """
        self.recuperer_categorie(identifiant_utilisateur, identifiant_categorie)
        try:
            return self._repository.creer_sous_categorie(
                identifiant_categorie,
                self._valider_nom(nom),
            )
        except sqlite3.IntegrityError as erreur:
            raise ValueError("Cette sous-catégorie existe déjà.") from erreur

    def recuperer_sous_categories(
        self, identifiant_utilisateur: int, identifiant_categorie: int
    ) -> list[dict[str, int | str]]:
        """Récupérer les sous-catégories d'une catégorie de l'utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire de la catégorie.
            identifiant_categorie: Identifiant de la catégorie parente.

        Returns:
            La liste de ses sous-catégories.

        Raises:
            ValueError: Si la catégorie n'existe pas pour cet utilisateur.
        """
        self.recuperer_categorie(identifiant_utilisateur, identifiant_categorie)
        return self._repository.recuperer_sous_categories(identifiant_categorie)

    def recuperer_sous_categorie(
        self,
        identifiant_utilisateur: int,
        identifiant_categorie: int,
        identifiant_sous_categorie: int,
    ) -> dict[str, int | str]:
        """Récupérer une sous-catégorie accessible à l'utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire attendu.
            identifiant_categorie: Identifiant de la catégorie parente.
            identifiant_sous_categorie: Identifiant de la sous-catégorie.

        Returns:
            La sous-catégorie demandée.

        Raises:
            ValueError: Si le classement n'appartient pas à l'utilisateur.
        """
        self.recuperer_categorie(identifiant_utilisateur, identifiant_categorie)
        resultat = self._repository.recuperer_sous_categorie(
            identifiant_categorie, identifiant_sous_categorie
        )
        if resultat is None:
            raise ValueError("Sous-catégorie incompatible avec la catégorie.")
        return resultat

    def verifier_classement(
        self,
        identifiant_utilisateur: int,
        identifiant_categorie: int,
        identifiant_sous_categorie: int | None = None,
    ) -> None:
        """Vérifier qu'une catégorie et sa sous-catégorie sont compatibles.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire attendu.
            identifiant_categorie: Identifiant de la catégorie.
            identifiant_sous_categorie: Sous-catégorie facultative.
        """
        self.recuperer_categorie(identifiant_utilisateur, identifiant_categorie)
        if identifiant_sous_categorie is not None:
            self.recuperer_sous_categorie(
                identifiant_utilisateur,
                identifiant_categorie,
                identifiant_sous_categorie,
            )

    def modifier_sous_categorie(
        self,
        identifiant_utilisateur: int,
        identifiant_categorie: int,
        identifiant_sous_categorie: int,
        nom: str,
    ) -> dict[str, int | str]:
        """Modifier une sous-catégorie d'une catégorie de l'utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire de la catégorie.
            identifiant_categorie: Identifiant de la catégorie parente.
            identifiant_sous_categorie: Identifiant de la sous-catégorie.
            nom: Nouveau nom de la sous-catégorie.

        Returns:
            La sous-catégorie modifiée.

        Raises:
            ValueError: Si la catégorie ou la sous-catégorie est introuvable.
        """
        self.recuperer_categorie(identifiant_utilisateur, identifiant_categorie)
        try:
            sous_categorie = self._repository.modifier_sous_categorie(
                identifiant_categorie,
                identifiant_sous_categorie,
                self._valider_nom(nom),
            )
        except sqlite3.IntegrityError as erreur:
            raise ValueError("Cette sous-catégorie existe déjà.") from erreur
        if sous_categorie is None:
            raise ValueError("Sous-catégorie introuvable pour cette catégorie.")
        return sous_categorie

    def supprimer_sous_categorie(
        self,
        identifiant_utilisateur: int,
        identifiant_categorie: int,
        identifiant_sous_categorie: int,
    ) -> None:
        """Supprimer une sous-catégorie d'une catégorie de l'utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire de la catégorie.
            identifiant_categorie: Identifiant de la catégorie parente.
            identifiant_sous_categorie: Identifiant de la sous-catégorie.

        Returns:
            None.

        Raises:
            ValueError: Si la catégorie ou la sous-catégorie est introuvable.
        """
        self.recuperer_categorie(identifiant_utilisateur, identifiant_categorie)
        supprimee = self._repository.supprimer_sous_categorie(
            identifiant_categorie, identifiant_sous_categorie
        )
        if not supprimee:
            raise ValueError("Sous-catégorie introuvable pour cette catégorie.")

    @staticmethod
    def _valider_nom(nom: str) -> str:
        """Nettoyer un nom de catégorie et refuser les valeurs vides."""
        if not isinstance(nom, str) or not nom.strip():
            raise ValueError("Le nom de la catégorie est obligatoire.")
        return nom.strip()
