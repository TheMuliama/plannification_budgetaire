"""Assemblage des services et routage sécurisé des requêtes du MVP."""

import secrets
import sqlite3
from datetime import date
from typing import Any

from persistance.repositories.budgets import RepositoryBudgets
from persistance.repositories.categories import RepositoryCategories
from persistance.repositories.depenses import RepositoryDepenses
from persistance.repositories.objectifs_epargne import RepositoryObjectifsEpargne
from persistance.repositories.revenus import RepositoryRevenus
from persistance.repositories.utilisateurs import RepositoryUtilisateurs
from serveur.communication.serveur_socket import ServeurSocket
from serveur.services.budget import GestionnaireBudget
from serveur.services.categories import GestionnaireCategories
from serveur.services.depenses import GestionnaireDepenses
from serveur.services.objectifs_epargne import GestionnaireObjectifsEpargne
from serveur.services.revenus import GestionnaireRevenus
from serveur.services.utilisateurs import GestionnaireUtilisateurs


class ApplicationServeur:
    """Exposer les services sans accepter d'identifiant utilisateur du client."""

    def __init__(self, connexion: sqlite3.Connection) -> None:
        self.utilisateurs=GestionnaireUtilisateurs(RepositoryUtilisateurs(connexion))
        self.categories=GestionnaireCategories(RepositoryCategories(connexion))
        self.revenus=GestionnaireRevenus(RepositoryRevenus(connexion))
        self.budgets=GestionnaireBudget(RepositoryBudgets(connexion))
        self.depenses=GestionnaireDepenses(RepositoryDepenses(connexion))
        self.objectifs=GestionnaireObjectifsEpargne(RepositoryObjectifsEpargne(connexion))
        self._sessions: dict[str,int]={}

    def traitements(self) -> dict[str, Any]:
        return {"utilisateurs.creer":self.creer_compte,"utilisateurs.connecter":self.connecter,
            "utilisateurs.deconnecter":self.deconnecter,
            "utilisateurs.changer_mot_de_passe":self.changer_mot_de_passe,
            "utilisateurs.supprimer":self.supprimer_compte,
            "categories.creer":self.creer_categorie,
            "categories.lister":self.lister_categories,
            "sous_categories.creer":self.creer_sous_categorie,
            "sous_categories.lister":self.lister_sous_categories,
            "revenus.creer":self.creer_revenu,
            "revenus.modifier":self.modifier_revenu,"revenus.supprimer":self.supprimer_revenu,
            "revenus.lister":self.lister_revenus,"budgets.creer":self.creer_budget,
            "budgets.modifier":self.modifier_budget,"budgets.supprimer":self.supprimer_budget,
            "budgets.lister":self.lister_budgets,"depenses.creer":self.creer_depense,
            "depenses.modifier":self.modifier_depense,"depenses.supprimer":self.supprimer_depense,
            "depenses.lister":self.lister_depenses,"objectifs.creer":self.creer_objectif,
            "objectifs.lister":self.lister_objectifs,
            "objectifs.analyser":self.analyser_objectifs,
            "objectifs.alimenter":self.alimenter_objectif,
            "objectifs.versements":self.lister_versements,
            "solde.obtenir":self.obtenir_solde}

    def creer_compte(self, d: dict[str,Any]) -> dict[str,Any]:
        return self.utilisateurs.creer_compte(d["identifiant"],d["mot_de_passe"])

    def connecter(self, d: dict[str,Any]) -> dict[str,Any]:
        if not self.utilisateurs.authentifier_utilisateur(d["identifiant"],d["mot_de_passe"]):
            raise ValueError("Identifiants invalides.")
        compte=self.utilisateurs.recuperer_compte(d["identifiant"])
        jeton=secrets.token_urlsafe(32); self._sessions[jeton]=compte["id"]
        return {"session":jeton,"utilisateur":compte}

    def deconnecter(self,d): self._sessions.pop(d.get("session",""),None); return None
    def changer_mot_de_passe(self,d):
        self.utilisateurs.changer_mot_de_passe(self._id(d),d["ancien"],d["nouveau"])
        return None
    def supprimer_compte(self,d):
        jeton=d.get("session",""); utilisateur_id=self._id(d)
        self.utilisateurs.supprimer_compte_authentifie(utilisateur_id,d["mot_de_passe"])
        self._sessions.pop(jeton,None); return None
    def _id(self,d):
        try: return self._sessions[d["session"]]
        except KeyError as erreur: raise ValueError("Session invalide ou expirée.") from erreur
    def creer_categorie(self,d): return self.categories.creer_categorie(self._id(d),d["nom"])
    def lister_categories(self,d): return self.categories.recuperer_categories(self._id(d))
    def creer_sous_categorie(self,d):
        return self.categories.creer_sous_categorie(self._id(d),d["categorie_id"],d["nom"])
    def lister_sous_categories(self,d):
        return self.categories.recuperer_sous_categories(self._id(d),d["categorie_id"])
    def creer_revenu(self,d): return self.revenus.ajouter_revenu({**d,"utilisateur_id":self._id(d)})
    def modifier_revenu(self,d): return self.revenus.modifier_revenu(self._id(d),d["id"],d)
    def supprimer_revenu(self,d): self.revenus.supprimer_revenu(self._id(d),d["id"]); return None
    def lister_revenus(self,d): return self.revenus.consulter_revenus(self._id(d),d.get("debut"),d.get("fin"),d.get("statut"))
    def creer_budget(self,d): return self.budgets.creer_budget({**d,"utilisateur_id":self._id(d)})
    def modifier_budget(self,d): return self.budgets.modifier_budget(self._id(d),d["id"],d)
    def supprimer_budget(self,d): self.budgets.supprimer_budget(self._id(d),d["id"]); return None
    def lister_budgets(self,d): return self.budgets.consulter_budget(self._id(d),d.get("annee"),d.get("mois"))
    def _verifier_solde(self,utilisateur_id: int,donnees: dict[str,Any],
                        depense_ignoree: int | None=None) -> None:
        """Refuser une dépense réalisée qui rendrait le solde négatif."""
        if donnees.get("statut") != "realisee": return
        try: montant=float(donnees["montant"])
        except (KeyError,TypeError,ValueError) as erreur:
            raise ValueError("Le montant de la dépense est invalide.") from erreur
        depenses=sum(float(x["montant"]) for x in
                     self.depenses.consulter_depenses(utilisateur_id,"realisee")
                     if x["id"] != depense_ignoree)
        revenus=sum(float(x["montant"]) for x in
                    self.revenus.consulter_revenus(utilisateur_id,statut="recu"))
        epargne=self.objectifs.total_versements(utilisateur_id)
        disponible=round(revenus-depenses-epargne,2)
        if montant > disponible + 1e-9:
            raise ValueError(
                f"Solde insuffisant : {disponible:.2f} € disponible(s). "
                "Une dépense ne peut pas rendre le solde négatif."
            )
    def creer_depense(self,d):
        utilisateur_id=self._id(d); self._verifier_solde(utilisateur_id,d)
        return self.depenses.ajouter_depense({**d,"utilisateur_id":utilisateur_id})
    def modifier_depense(self,d):
        utilisateur_id=self._id(d)
        existante=next((x for x in self.depenses.consulter_depenses(utilisateur_id)
                        if x["id"]==d["id"]),None)
        if existante is None: raise ValueError("Dépense introuvable pour cet utilisateur.")
        self._verifier_solde(utilisateur_id,d,d["id"])
        return self.depenses.modifier_depense(utilisateur_id,d["id"],d)
    def supprimer_depense(self,d): self.depenses.supprimer_depense(self._id(d),d["id"]); return None
    def lister_depenses(self,d): return self.depenses.consulter_depenses(self._id(d),d.get("statut"))
    def creer_objectif(self,d): return self.objectifs.creer_objectif({**d,"utilisateur_id":self._id(d)})
    def lister_objectifs(self,d): return self.objectifs.consulter_objectifs(self._id(d))
    def lister_versements(self,d):
        return self.objectifs.consulter_versements(self._id(d),d.get("objectif_id"))
    def obtenir_solde(self,d):
        utilisateur_id=self._id(d)
        revenus=sum(float(x["montant"]) for x in
                    self.revenus.consulter_revenus(utilisateur_id,statut="recu"))
        depenses=sum(float(x["montant"]) for x in
                     self.depenses.consulter_depenses(utilisateur_id,"realisee"))
        epargne=self.objectifs.total_versements(utilisateur_id)
        return {"revenus":round(revenus,2),"depenses":round(depenses,2),
                "epargne":round(epargne,2),"disponible":round(revenus-depenses-epargne,2)}
    def alimenter_objectif(self,d):
        utilisateur_id=self._id(d); montant=float(d["montant"])
        disponible=self.obtenir_solde(d)["disponible"]
        if montant > disponible + 1e-9:
            raise ValueError(f"Solde insuffisant : {disponible:.2f} € disponible(s).")
        return self.objectifs.alimenter_objectif(
            utilisateur_id,d["objectif_id"],montant,d["date"]
        )
    def analyser_objectifs(self,d):
        utilisateur_id=self._id(d); aujourd_hui=date.today()
        debut=aujourd_hui.replace(day=1).isoformat()
        revenus=self.revenus.consulter_revenus(utilisateur_id,debut,aujourd_hui.isoformat(),"recu")
        depenses=self.depenses.consulter_depenses(utilisateur_id,"realisee")
        depenses=[x for x in depenses if debut <= x["date"] <= aujourd_hui.isoformat()]
        revenu_mois=sum(float(x["montant"]) for x in revenus)
        depense_mois=sum(float(x["montant"]) for x in depenses)
        versements_mois=self.objectifs.total_versements(
            utilisateur_id,debut,aujourd_hui.isoformat()
        )
        epargne_maximale=max(0.0,revenu_mois-depense_mois-versements_mois)
        analyses=[]
        for objectif in self.objectifs.consulter_objectifs(utilisateur_id):
            plan=self.objectifs.determiner_plan_epargne({**objectif,"utilisateur_id":utilisateur_id})
            requise=float(plan["montant_periodique_recommande"])
            analyses.append({**objectif,**plan,"revenus_mois":round(revenu_mois,2),
                "depenses_mois":round(depense_mois,2),"versements_mois":round(versements_mois,2),
                "epargne_maximale":round(epargne_maximale,2),
                "revenu_utilisable":round(max(0.0,revenu_mois-requise),2),
                "objectif_atteignable":requise <= epargne_maximale})
        return analyses


def construire_serveur(connexion: sqlite3.Connection) -> ServeurSocket:
    return ServeurSocket(ApplicationServeur(connexion).traitements())
