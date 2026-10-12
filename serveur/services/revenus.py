"""Service de gestion des revenus."""

from typing import Any


class GestionnaireRevenus:
    """Gérer les revenus prévisionnels et réellement reçus.

    Cette classe enregistre et consulte les revenus sans implémenter leurs
    calculs.
    """

    def ajouter_revenu(self, revenu: dict[str, Any]) -> dict[str, Any]:
        """Ajouter un revenu prévisionnel ou réel.

        Args:
            revenu: Informations du revenu à enregistrer.

        Returns:
            Le revenu enregistré.
        """
        pass

    def modifier_revenu(self, identifiant_revenu: int, revenu: dict[str, Any]) -> dict[str, Any]:
        """Modifier un revenu existant.

        Args:
            identifiant_revenu: Identifiant du revenu à modifier.
            revenu: Nouvelles informations du revenu.

        Returns:
            Le revenu modifié.
        """
        pass

    def supprimer_revenu(self, identifiant_revenu: int) -> None:
        """Supprimer un revenu.

        Args:
            identifiant_revenu: Identifiant du revenu à supprimer.

        Returns:
            None.
        """
        pass

    def consulter_revenus(self, identifiant_utilisateur: int) -> list[dict[str, Any]]:
        """Consulter les revenus d'un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant de l'utilisateur concerné.

        Returns:
            La liste de ses revenus.
        """
        pass
