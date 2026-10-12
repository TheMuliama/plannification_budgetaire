"""Service de gestion des dépenses."""

from typing import Any


class GestionnaireDepenses:
    """Gérer les dépenses prévues et réalisées.

    Cette classe associe les dépenses à des catégories, sans décider de leur
    acceptabilité financière.
    """

    def ajouter_depense(self, depense: dict[str, Any]) -> dict[str, Any]:
        """Ajouter une dépense prévue ou réalisée.

        Args:
            depense: Informations de la dépense, dont sa catégorie éventuelle.

        Returns:
            La dépense enregistrée.
        """
        pass

    def modifier_depense(self, identifiant_depense: int, depense: dict[str, Any]) -> dict[str, Any]:
        """Modifier une dépense existante.

        Args:
            identifiant_depense: Identifiant de la dépense à modifier.
            depense: Nouvelles informations de la dépense.

        Returns:
            La dépense modifiée.
        """
        pass

    def supprimer_depense(self, identifiant_depense: int) -> None:
        """Supprimer une dépense.

        Args:
            identifiant_depense: Identifiant de la dépense à supprimer.

        Returns:
            None.
        """
        pass

    def consulter_depenses(self, identifiant_utilisateur: int) -> list[dict[str, Any]]:
        """Consulter l'historique des dépenses d'un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant de l'utilisateur concerné.

        Returns:
            La liste de ses dépenses.
        """
        pass
