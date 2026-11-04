"""Calcul et validation du solde disponible d'un utilisateur."""

from typing import Any

from serveur.services.depenses import GestionnaireDepenses
from serveur.services.objectifs_epargne import GestionnaireObjectifsEpargne
from serveur.services.revenus import GestionnaireRevenus


class GestionnaireSolde:
    """Centraliser les règles qui protègent le solde disponible."""

    def __init__(
        self,
        revenus: GestionnaireRevenus,
        depenses: GestionnaireDepenses,
        objectifs: GestionnaireObjectifsEpargne,
    ) -> None:
        self._revenus = revenus
        self._depenses = depenses
        self._objectifs = objectifs

    def obtenir(self, identifiant_utilisateur: int) -> dict[str, float]:
        """Calculer le solde à partir des opérations effectivement réalisées.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire des opérations.

        Returns:
            Les totaux des revenus, dépenses, versements et du solde disponible.
        """
        total_revenus = sum(
            float(revenu["montant"])
            for revenu in self._revenus.consulter_revenus(
                identifiant_utilisateur,
                statut="recu",
            )
        )
        total_depenses = sum(
            float(depense["montant"])
            for depense in self._depenses.consulter_depenses(
                identifiant_utilisateur,
                "realisee",
            )
        )
        total_epargne = self._objectifs.total_versements(identifiant_utilisateur)

        return {
            "revenus": round(total_revenus, 2),
            "depenses": round(total_depenses, 2),
            "epargne": round(total_epargne, 2),
            "disponible": round(total_revenus - total_depenses - total_epargne, 2),
        }

    def verifier_depense(
        self,
        identifiant_utilisateur: int,
        donnees: dict[str, Any],
        depense_ignoree: int | None = None,
    ) -> None:
        """Refuser une dépense réalisée qui rendrait le solde négatif.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire de la dépense.
            donnees: Informations de la dépense à créer ou modifier.
            depense_ignoree: Dépense remplacée lors d'une modification.

        Raises:
            ValueError: Si le montant est invalide ou dépasse le solde disponible.
        """
        if donnees.get("statut") != "realisee":
            return

        try:
            montant = float(donnees["montant"])
        except (KeyError, TypeError, ValueError) as erreur:
            raise ValueError("Le montant de la dépense est invalide.") from erreur

        depenses_existantes = sum(
            float(depense["montant"])
            for depense in self._depenses.consulter_depenses(
                identifiant_utilisateur,
                "realisee",
            )
            if depense["id"] != depense_ignoree
        )
        solde = self.obtenir(identifiant_utilisateur)
        disponible = round(solde["revenus"] - depenses_existantes - solde["epargne"], 2)
        self._verifier_montant_disponible(montant, disponible)

    def verifier_versement(
        self,
        identifiant_utilisateur: int,
        montant: float,
    ) -> None:
        """Refuser un versement d'épargne supérieur au solde disponible.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire du versement.
            montant: Montant à verser sur l'objectif.

        Raises:
            ValueError: Si le montant dépasse le solde disponible.
        """
        disponible = self.obtenir(identifiant_utilisateur)["disponible"]
        self._verifier_montant_disponible(montant, disponible)

    @staticmethod
    def _verifier_montant_disponible(montant: float, disponible: float) -> None:
        """Comparer un montant au solde en tolérant les erreurs d'arrondi."""
        if montant > disponible + 1e-9:
            raise ValueError(f"Solde insuffisant : {disponible:.2f} € disponible(s).")
