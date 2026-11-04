"""Service de gestion des revenus."""

from datetime import date
from math import isfinite
from typing import Any

from persistance.repositories.revenus import RepositoryRevenus


class GestionnaireRevenus:
    """Gérer les revenus prévisionnels et réellement reçus.

    Cette classe enregistre et consulte les revenus sans implémenter leurs
    calculs.
    """

    CATEGORIES = frozenset({"Salaire", "Remboursement", "Cadeau", "Prime", "Autre"})

    def __init__(self, repository: RepositoryRevenus) -> None:
        self._repository = repository

    def ajouter_revenu(self, revenu: dict[str, Any]) -> dict[str, Any]:
        """Ajouter un revenu prévisionnel ou réel.

        Args:
            revenu: Informations du revenu à enregistrer.

        Returns:
            Le revenu enregistré.
        """
        donnees = self._valider_revenu(revenu)
        identifiant = self._repository.ajouter_revenu(**donnees)
        revenu_enregistre = self._repository.obtenir_revenu(
            donnees["utilisateur_id"],
            identifiant,
        )
        assert revenu_enregistre is not None
        return revenu_enregistre

    def modifier_revenu(
        self,
        identifiant_utilisateur: int,
        identifiant_revenu: int,
        revenu: dict[str, Any],
    ) -> dict[str, Any]:
        """Modifier un revenu existant.

        Args:
            identifiant_revenu: Identifiant du revenu à modifier.
            revenu: Nouvelles informations du revenu.

        Returns:
            Le revenu modifié.
        """
        donnees = self._valider_revenu(
            {**revenu, "utilisateur_id": identifiant_utilisateur}
        )
        modifie = self._repository.modifier_revenu(
            identifiant_utilisateur,
            identifiant_revenu,
            donnees["montant"],
            donnees["date"],
            donnees["description"],
            donnees["statut"],
            donnees["categorie"],
        )
        if not modifie:
            raise ValueError("Revenu introuvable pour cet utilisateur.")
        resultat = self._repository.obtenir_revenu(
            identifiant_utilisateur,
            identifiant_revenu,
        )
        assert resultat is not None
        return resultat

    def supprimer_revenu(
        self,
        identifiant_utilisateur: int,
        identifiant_revenu: int,
    ) -> None:
        """Supprimer un revenu.

        Args:
            identifiant_revenu: Identifiant du revenu à supprimer.

        Returns:
            None.
        """
        if not self._repository.supprimer_revenu(
            identifiant_utilisateur,
            identifiant_revenu,
        ):
            raise ValueError("Revenu introuvable pour cet utilisateur.")

    def consulter_revenus(
        self,
        identifiant_utilisateur: int,
        debut: str | None = None,
        fin: str | None = None,
        statut: str | None = None,
    ) -> list[dict[str, Any]]:
        """Consulter les revenus d'un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant de l'utilisateur concerné.

        Returns:
            La liste de ses revenus.
        """
        if debut is not None:
            self._valider_date(debut)
        if fin is not None:
            self._valider_date(fin)
        if debut is not None and fin is not None and debut > fin:
            raise ValueError("La date de début doit précéder la date de fin.")
        if statut is not None and statut not in {"prevu", "recu"}:
            raise ValueError("Le statut du revenu est invalide.")
        return self._repository.consulter_revenus(
            identifiant_utilisateur,
            debut,
            fin,
            statut,
        )

    @classmethod
    def _valider_revenu(cls, revenu: dict[str, Any]) -> dict[str, Any]:
        try:
            utilisateur_id = int(revenu["utilisateur_id"])
            montant = float(revenu["montant"])
            date_revenu = revenu["date"]
            statut = revenu["statut"]
        except (KeyError, TypeError, ValueError) as erreur:
            raise ValueError("Les informations du revenu sont incomplètes.") from erreur
        if utilisateur_id <= 0:
            raise ValueError("L'utilisateur du revenu est invalide.")
        if not isfinite(montant) or montant <= 0:
            raise ValueError("Le montant du revenu doit être strictement positif.")
        cls._valider_date(date_revenu)
        if statut not in {"prevu", "recu"}:
            raise ValueError("Le statut du revenu est invalide.")
        description = revenu.get("description")
        if description is not None:
            if not isinstance(description, str):
                raise ValueError("La description du revenu est invalide.")
            description = description.strip() or None
        categorie = revenu.get("categorie", "Salaire")
        if not isinstance(categorie, str) or categorie.strip() not in cls.CATEGORIES:
            raise ValueError("La catégorie du revenu est invalide.")
        categorie = categorie.strip()
        return {
            "utilisateur_id": utilisateur_id,
            "montant": montant,
            "date": date_revenu,
            "description": description,
            "statut": statut,
            "categorie": categorie,
        }

    @staticmethod
    def _valider_date(valeur: str) -> None:
        try:
            date.fromisoformat(valeur)
        except (TypeError, ValueError) as erreur:
            raise ValueError(
                "La date du revenu doit être au format AAAA-MM-JJ."
            ) from erreur
