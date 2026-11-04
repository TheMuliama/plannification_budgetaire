"""Analyse de la capacité mensuelle d'épargne."""

from datetime import date
from typing import Any

from serveur.services.depenses import GestionnaireDepenses
from serveur.services.objectifs_epargne import GestionnaireObjectifsEpargne
from serveur.services.revenus import GestionnaireRevenus


class AnalyseurEpargne:
    """Assembler les données financières nécessaires au suivi des objectifs."""

    def __init__(
        self,
        revenus: GestionnaireRevenus,
        depenses: GestionnaireDepenses,
        objectifs: GestionnaireObjectifsEpargne,
    ) -> None:
        self._revenus = revenus
        self._depenses = depenses
        self._objectifs = objectifs

    def analyser(self, identifiant_utilisateur: int) -> list[dict[str, Any]]:
        """Évaluer chaque objectif avec la situation du mois courant.

        Args:
            identifiant_utilisateur: Identifiant du propriétaire des objectifs.

        Returns:
            Les objectifs enrichis du plan et de la capacité mensuelle d'épargne.
        """
        aujourd_hui = date.today()
        debut_mois = aujourd_hui.replace(day=1).isoformat()
        fin_periode = aujourd_hui.isoformat()

        revenus = self._revenus.consulter_revenus(
            identifiant_utilisateur,
            debut_mois,
            fin_periode,
            "recu",
        )
        depenses = self._depenses.consulter_depenses(
            identifiant_utilisateur,
            "realisee",
        )
        depenses_du_mois = [
            depense
            for depense in depenses
            if debut_mois <= depense["date"] <= fin_periode
        ]

        total_revenus = sum(float(revenu["montant"]) for revenu in revenus)
        total_depenses = sum(float(depense["montant"]) for depense in depenses_du_mois)
        total_versements = self._objectifs.total_versements(
            identifiant_utilisateur,
            debut_mois,
            fin_periode,
        )
        epargne_maximale = max(
            0.0,
            total_revenus - total_depenses - total_versements,
        )

        return [
            self._analyser_objectif(
                identifiant_utilisateur,
                objectif,
                total_revenus,
                total_depenses,
                total_versements,
                epargne_maximale,
            )
            for objectif in self._objectifs.consulter_objectifs(identifiant_utilisateur)
        ]

    def _analyser_objectif(
        self,
        identifiant_utilisateur: int,
        objectif: dict[str, Any],
        total_revenus: float,
        total_depenses: float,
        total_versements: float,
        epargne_maximale: float,
    ) -> dict[str, Any]:
        """Ajouter les indicateurs mensuels à un objectif."""
        plan = self._objectifs.determiner_plan_epargne(
            {**objectif, "utilisateur_id": identifiant_utilisateur}
        )
        montant_requis = float(plan["montant_periodique_recommande"])

        return {
            **objectif,
            **plan,
            "revenus_mois": round(total_revenus, 2),
            "depenses_mois": round(total_depenses, 2),
            "versements_mois": round(total_versements, 2),
            "epargne_maximale": round(epargne_maximale, 2),
            "revenu_utilisable": round(max(0.0, total_revenus - montant_requis), 2),
            "objectif_atteignable": montant_requis <= epargne_maximale,
        }
