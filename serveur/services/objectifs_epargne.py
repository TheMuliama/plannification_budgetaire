"""Service de gestion des objectifs d'épargne."""

from typing import Any
from datetime import date
from math import ceil, isfinite
from persistance.repositories.objectifs_epargne import RepositoryObjectifsEpargne


class GestionnaireObjectifsEpargne:
    """Gérer les objectifs d'épargne et leurs plans associés.

    Cette classe prépare le suivi et les scénarios de réajustement sans
    prendre de décision automatique à la place de l'utilisateur.
    """

    def __init__(self, repository: RepositoryObjectifsEpargne) -> None:
        self._repository = repository

    def creer_objectif(self, objectif: dict[str, Any]) -> dict[str, Any]:
        """Créer un objectif d'épargne.

        Args:
            objectif: Paramètres de l'objectif à créer.

        Returns:
            L'objectif créé.
        """
        return self._repository.creer_objectif(**self._valider(objectif))

    def modifier_objectif(self, identifiant_utilisateur: int, identifiant_objectif: int,
                          objectif: dict[str, Any]) -> dict[str, Any]:
        """Modifier un objectif d'épargne.

        Args:
            identifiant_objectif: Identifiant de l'objectif à modifier.
            objectif: Nouvelles informations de l'objectif.

        Returns:
            L'objectif modifié.
        """
        donnees = self._valider({**objectif,"utilisateur_id":identifiant_utilisateur})
        resultat = self._repository.modifier_objectif(identifiant_utilisateur,identifiant_objectif,
            **{c:v for c,v in donnees.items() if c != "utilisateur_id"})
        if resultat is None: raise ValueError("Objectif introuvable pour cet utilisateur.")
        return resultat

    def supprimer_objectif(self, identifiant_utilisateur: int, identifiant_objectif: int) -> None:
        """Supprimer un objectif d'épargne.

        Args:
            identifiant_objectif: Identifiant de l'objectif à supprimer.

        Returns:
            None.
        """
        if not self._repository.supprimer_objectif(identifiant_utilisateur,identifiant_objectif):
            raise ValueError("Objectif introuvable pour cet utilisateur.")

    def consulter_objectif(self, identifiant_utilisateur: int,
                           identifiant_objectif: int) -> dict[str, Any]:
        """Consulter un objectif d'épargne.

        Args:
            identifiant_objectif: Identifiant de l'objectif recherché.

        Returns:
            Les informations de l'objectif.
        """
        resultat = self._repository.obtenir_objectif(identifiant_utilisateur,identifiant_objectif)
        if resultat is None: raise ValueError("Objectif introuvable pour cet utilisateur.")
        return resultat

    def consulter_objectifs(self, identifiant_utilisateur: int) -> list[dict[str, Any]]:
        return self._repository.consulter_objectifs(identifiant_utilisateur)

    def determiner_plan_epargne(self, objectif: dict[str, Any]) -> dict[str, Any]:
        """Déterminer le plan d'épargne associé à un objectif.

        Args:
            objectif: Paramètres de l'objectif d'épargne.

        Returns:
            Le plan d'épargne proposé.
        """
        donnees = self._valider(objectif)
        restant = max(0.0, donnees["montant_cible"] - donnees["montant_actuel"])
        cible = date.fromisoformat(donnees["date_cible"])
        mois = max(1, ceil(max(0, (cible - date.today()).days) / 30))
        recommande = round(restant / mois, 2)
        return {"montant_restant": round(restant,2), "mois_restants": mois,
                "montant_periodique_recommande": recommande,
                "montant_periodique_prevu": donnees["montant_periodique"]}

    def constater_ecart(self, plan: dict[str, Any], epargne_realisee: float) -> dict[str, Any]:
        """Constater l'écart entre un plan et l'épargne réalisée.

        Args:
            plan: Plan d'épargne prévu.
            epargne_realisee: Montant d'épargne effectivement réalisé.

        Returns:
            Les informations relatives à l'écart constaté.
        """
        attendu = float(plan.get("montant_periodique_prevu",
                                  plan.get("montant_periodique_recommande", 0)))
        ecart = round(float(epargne_realisee) - attendu, 2)
        return {"attendu": attendu, "realise": float(epargne_realisee), "ecart": ecart,
                "en_retard": ecart < 0}

    def preparer_scenarios_reajustement(self, objectif: dict[str, Any], ecart: dict[str, Any]) -> list[dict[str, Any]]:
        """Préparer des scénarios de réajustement à soumettre à l'utilisateur.

        Args:
            objectif: Objectif d'épargne concerné.
            ecart: Écart constaté entre le plan et la réalisation.

        Returns:
            Les scénarios possibles, sans décision automatique.
        """
        if not ecart.get("en_retard"): return []
        manque = abs(float(ecart["ecart"])); cible = float(objectif["montant_cible"])
        return [{"type":"augmenter_prochaine_echeance","montant":round(manque,2)},
                {"type":"reduire_objectif","nouveau_montant_cible":round(max(0,cible-manque),2)}]

    @staticmethod
    def _valider(objectif: dict[str, Any]) -> dict[str, Any]:
        try:
            resultat={"utilisateur_id":int(objectif["utilisateur_id"]),"nom":objectif["nom"].strip(),
                "montant_cible":float(objectif["montant_cible"]),
                "montant_actuel":float(objectif.get("montant_actuel",0)),
                "montant_periodique":float(objectif.get("montant_periodique",0)),
                "date_cible":objectif["date_cible"]}
            date.fromisoformat(resultat["date_cible"])
        except (KeyError,AttributeError,TypeError,ValueError) as erreur:
            raise ValueError("Informations de l'objectif invalides.") from erreur
        if not resultat["nom"]: raise ValueError("Le nom de l'objectif est obligatoire.")
        if (resultat["utilisateur_id"]<=0 or resultat["montant_cible"]<=0 or
                not isfinite(resultat["montant_cible"])):
            raise ValueError("Le propriétaire ou la cible est invalide.")
        if any(not isfinite(resultat[c]) or resultat[c]<0 for c in ("montant_actuel","montant_periodique")):
            raise ValueError("Les montants de l'objectif sont invalides.")
        return resultat
