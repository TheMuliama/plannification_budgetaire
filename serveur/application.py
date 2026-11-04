"""Assemblage des services et routage sécurisé des requêtes du MVP."""

import sqlite3
from collections.abc import Callable
from typing import Any

from persistance.repositories.budgets import RepositoryBudgets
from persistance.repositories.categories import RepositoryCategories
from persistance.repositories.depenses import RepositoryDepenses
from persistance.repositories.objectifs_epargne import RepositoryObjectifsEpargne
from persistance.repositories.revenus import RepositoryRevenus
from persistance.repositories.utilisateurs import RepositoryUtilisateurs
from serveur.communication.serveur_socket import ServeurSocket
from serveur.securite.sessions import GestionnaireSessions
from serveur.services.analyse_epargne import AnalyseurEpargne
from serveur.services.budget import GestionnaireBudget
from serveur.services.categories import GestionnaireCategories
from serveur.services.depenses import GestionnaireDepenses
from serveur.services.objectifs_epargne import GestionnaireObjectifsEpargne
from serveur.services.revenus import GestionnaireRevenus
from serveur.services.solde import GestionnaireSolde
from serveur.services.utilisateurs import GestionnaireUtilisateurs

DonneesRequete = dict[str, Any]
Traitement = Callable[[DonneesRequete], Any]


class ApplicationServeur:
    """Relier le protocole réseau aux services de l'application.

    Le client transmet uniquement un jeton de session. L'identifiant du
    propriétaire est toujours résolu côté serveur avant d'appeler un service.
    """

    def __init__(self, connexion: sqlite3.Connection) -> None:
        self.utilisateurs = GestionnaireUtilisateurs(RepositoryUtilisateurs(connexion))
        self.categories = GestionnaireCategories(RepositoryCategories(connexion))
        self.revenus = GestionnaireRevenus(RepositoryRevenus(connexion))
        self.budgets = GestionnaireBudget(RepositoryBudgets(connexion))
        self.depenses = GestionnaireDepenses(RepositoryDepenses(connexion))
        self.objectifs = GestionnaireObjectifsEpargne(
            RepositoryObjectifsEpargne(connexion)
        )

        self.sessions = GestionnaireSessions()
        self.solde = GestionnaireSolde(
            self.revenus,
            self.depenses,
            self.objectifs,
        )
        self.analyseur_epargne = AnalyseurEpargne(
            self.revenus,
            self.depenses,
            self.objectifs,
        )

    def traitements(self) -> dict[str, Traitement]:
        """Associer chaque action du protocole à son traitement.

        Returns:
            Les traitements indexés par le nom de leur action JSON.
        """
        return {
            "utilisateurs.creer": self.creer_compte,
            "utilisateurs.connecter": self.connecter,
            "utilisateurs.deconnecter": self.deconnecter,
            "utilisateurs.changer_mot_de_passe": self.changer_mot_de_passe,
            "utilisateurs.supprimer": self.supprimer_compte,
            "categories.creer": self.creer_categorie,
            "categories.lister": self.lister_categories,
            "sous_categories.creer": self.creer_sous_categorie,
            "sous_categories.lister": self.lister_sous_categories,
            "revenus.creer": self.creer_revenu,
            "revenus.modifier": self.modifier_revenu,
            "revenus.supprimer": self.supprimer_revenu,
            "revenus.lister": self.lister_revenus,
            "budgets.creer": self.creer_budget,
            "budgets.modifier": self.modifier_budget,
            "budgets.supprimer": self.supprimer_budget,
            "budgets.lister": self.lister_budgets,
            "depenses.creer": self.creer_depense,
            "depenses.modifier": self.modifier_depense,
            "depenses.supprimer": self.supprimer_depense,
            "depenses.lister": self.lister_depenses,
            "objectifs.creer": self.creer_objectif,
            "objectifs.lister": self.lister_objectifs,
            "objectifs.analyser": self.analyser_objectifs,
            "objectifs.alimenter": self.alimenter_objectif,
            "objectifs.versements": self.lister_versements,
            "solde.obtenir": self.obtenir_solde,
        }

    def creer_compte(self, donnees: DonneesRequete) -> dict[str, Any]:
        """Créer un compte sans ouvrir automatiquement de session.

        Args:
            donnees: Identifiant et mot de passe du nouveau compte.

        Returns:
            Le compte créé, sans son mot de passe haché.
        """
        return self.utilisateurs.creer_compte(
            donnees["identifiant"],
            donnees["mot_de_passe"],
        )

    def connecter(self, donnees: DonneesRequete) -> dict[str, Any]:
        """Authentifier un utilisateur et ouvrir une session opaque.

        Args:
            donnees: Identifiant et mot de passe du compte.

        Returns:
            Le jeton de session et les informations publiques du compte.

        Raises:
            ValueError: Si les identifiants sont invalides.
        """
        identifiant = donnees["identifiant"]
        mot_de_passe = donnees["mot_de_passe"]
        if not self.utilisateurs.authentifier_utilisateur(
            identifiant,
            mot_de_passe,
        ):
            raise ValueError("Identifiants invalides.")

        compte = self.utilisateurs.recuperer_compte(identifiant)
        jeton = self.sessions.ouvrir(compte["id"])
        return {"session": jeton, "utilisateur": compte}

    def deconnecter(self, donnees: DonneesRequete) -> None:
        """Fermer la session transmise par le client.

        Args:
            donnees: Données contenant éventuellement le jeton de session.
        """
        self.sessions.fermer(donnees.get("session"))

    def changer_mot_de_passe(self, donnees: DonneesRequete) -> None:
        """Changer le mot de passe de l'utilisateur authentifié.

        Args:
            donnees: Session, ancien mot de passe et nouveau mot de passe.

        Raises:
            ValueError: Si la session ou les mots de passe sont invalides.
        """
        self.utilisateurs.changer_mot_de_passe(
            self._identifiant_utilisateur(donnees),
            donnees["ancien"],
            donnees["nouveau"],
        )

    def supprimer_compte(self, donnees: DonneesRequete) -> None:
        """Supprimer un compte après vérification du mot de passe.

        Args:
            donnees: Session et mot de passe de confirmation.

        Raises:
            ValueError: Si la session ou le mot de passe est invalide.
        """
        jeton = donnees.get("session")
        identifiant_utilisateur = self._identifiant_utilisateur(donnees)
        self.utilisateurs.supprimer_compte_authentifie(
            identifiant_utilisateur,
            donnees["mot_de_passe"],
        )
        self.sessions.fermer(jeton)

    def creer_categorie(self, donnees: DonneesRequete) -> dict[str, Any]:
        """Créer une catégorie pour l'utilisateur authentifié.

        Args:
            donnees: Session et nom de la catégorie.

        Returns:
            La catégorie créée.
        """
        return self.categories.creer_categorie(
            self._identifiant_utilisateur(donnees),
            donnees["nom"],
        )

    def lister_categories(self, donnees: DonneesRequete) -> list[dict[str, Any]]:
        """Lister les catégories de l'utilisateur authentifié.

        Args:
            donnees: Données contenant le jeton de session.

        Returns:
            Les catégories appartenant à l'utilisateur.
        """
        return self.categories.recuperer_categories(
            self._identifiant_utilisateur(donnees)
        )

    def creer_sous_categorie(self, donnees: DonneesRequete) -> dict[str, Any]:
        """Créer une sous-catégorie dans une catégorie accessible.

        Args:
            donnees: Session, catégorie parente et nom de la sous-catégorie.

        Returns:
            La sous-catégorie créée.
        """
        return self.categories.creer_sous_categorie(
            self._identifiant_utilisateur(donnees),
            donnees["categorie_id"],
            donnees["nom"],
        )

    def lister_sous_categories(
        self,
        donnees: DonneesRequete,
    ) -> list[dict[str, Any]]:
        """Lister les sous-catégories d'une catégorie accessible.

        Args:
            donnees: Session et identifiant de la catégorie parente.

        Returns:
            Les sous-catégories de la catégorie.
        """
        return self.categories.recuperer_sous_categories(
            self._identifiant_utilisateur(donnees),
            donnees["categorie_id"],
        )

    def creer_revenu(self, donnees: DonneesRequete) -> dict[str, Any]:
        """Créer un revenu pour l'utilisateur authentifié.

        Args:
            donnees: Session et informations du revenu.

        Returns:
            Le revenu créé.
        """
        return self.revenus.ajouter_revenu(
            {
                **donnees,
                "utilisateur_id": self._identifiant_utilisateur(donnees),
            }
        )

    def modifier_revenu(self, donnees: DonneesRequete) -> dict[str, Any]:
        """Modifier un revenu accessible à l'utilisateur authentifié.

        Args:
            donnees: Session, identifiant et nouvelles valeurs du revenu.

        Returns:
            Le revenu modifié.
        """
        return self.revenus.modifier_revenu(
            self._identifiant_utilisateur(donnees),
            donnees["id"],
            donnees,
        )

    def supprimer_revenu(self, donnees: DonneesRequete) -> None:
        """Supprimer un revenu accessible à l'utilisateur authentifié.

        Args:
            donnees: Session et identifiant du revenu.
        """
        self.revenus.supprimer_revenu(
            self._identifiant_utilisateur(donnees),
            donnees["id"],
        )

    def lister_revenus(self, donnees: DonneesRequete) -> list[dict[str, Any]]:
        """Lister les revenus selon les filtres transmis.

        Args:
            donnees: Session et filtres facultatifs de période et de statut.

        Returns:
            Les revenus correspondant aux filtres.
        """
        return self.revenus.consulter_revenus(
            self._identifiant_utilisateur(donnees),
            donnees.get("debut"),
            donnees.get("fin"),
            donnees.get("statut"),
        )

    def creer_budget(self, donnees: DonneesRequete) -> dict[str, Any]:
        """Créer une allocation budgétaire mensuelle.

        Args:
            donnees: Session et informations de l'allocation.

        Returns:
            Le budget créé.
        """
        return self.budgets.creer_budget(
            {
                **donnees,
                "utilisateur_id": self._identifiant_utilisateur(donnees),
            }
        )

    def modifier_budget(self, donnees: DonneesRequete) -> dict[str, Any]:
        """Modifier une allocation budgétaire accessible.

        Args:
            donnees: Session, identifiant et nouvelles valeurs du budget.

        Returns:
            Le budget modifié.
        """
        return self.budgets.modifier_budget(
            self._identifiant_utilisateur(donnees),
            donnees["id"],
            donnees,
        )

    def supprimer_budget(self, donnees: DonneesRequete) -> None:
        """Supprimer une allocation budgétaire accessible.

        Args:
            donnees: Session et identifiant du budget.
        """
        self.budgets.supprimer_budget(
            self._identifiant_utilisateur(donnees),
            donnees["id"],
        )

    def lister_budgets(self, donnees: DonneesRequete) -> list[dict[str, Any]]:
        """Lister les budgets selon la période transmise.

        Args:
            donnees: Session, année et mois facultatifs.

        Returns:
            Les budgets correspondant à la période.
        """
        return self.budgets.consulter_budget(
            self._identifiant_utilisateur(donnees),
            donnees.get("annee"),
            donnees.get("mois"),
        )

    def creer_depense(self, donnees: DonneesRequete) -> dict[str, Any]:
        """Valider le solde puis créer une dépense.

        Args:
            donnees: Session et informations de la dépense.

        Returns:
            La dépense créée.

        Raises:
            ValueError: Si la dépense dépasse le solde disponible.
        """
        identifiant_utilisateur = self._identifiant_utilisateur(donnees)
        self.solde.verifier_depense(identifiant_utilisateur, donnees)
        return self.depenses.ajouter_depense(
            {**donnees, "utilisateur_id": identifiant_utilisateur}
        )

    def modifier_depense(self, donnees: DonneesRequete) -> dict[str, Any]:
        """Valider le solde puis modifier une dépense accessible.

        Args:
            donnees: Session, identifiant et nouvelles valeurs de la dépense.

        Returns:
            La dépense modifiée.

        Raises:
            ValueError: Si la dépense est inaccessible ou dépasse le solde.
        """
        identifiant_utilisateur = self._identifiant_utilisateur(donnees)
        identifiant_depense = donnees["id"]
        depenses = self.depenses.consulter_depenses(identifiant_utilisateur)
        if not any(depense["id"] == identifiant_depense for depense in depenses):
            raise ValueError("Dépense introuvable pour cet utilisateur.")

        self.solde.verifier_depense(
            identifiant_utilisateur,
            donnees,
            identifiant_depense,
        )
        return self.depenses.modifier_depense(
            identifiant_utilisateur,
            identifiant_depense,
            donnees,
        )

    def supprimer_depense(self, donnees: DonneesRequete) -> None:
        """Supprimer une dépense accessible.

        Args:
            donnees: Session et identifiant de la dépense.
        """
        self.depenses.supprimer_depense(
            self._identifiant_utilisateur(donnees),
            donnees["id"],
        )

    def lister_depenses(self, donnees: DonneesRequete) -> list[dict[str, Any]]:
        """Lister les dépenses selon leur statut.

        Args:
            donnees: Session et statut facultatif des dépenses.

        Returns:
            Les dépenses correspondant au filtre.
        """
        return self.depenses.consulter_depenses(
            self._identifiant_utilisateur(donnees),
            donnees.get("statut"),
        )

    def creer_objectif(self, donnees: DonneesRequete) -> dict[str, Any]:
        """Créer un objectif d'épargne.

        Args:
            donnees: Session et informations de l'objectif.

        Returns:
            L'objectif créé.
        """
        return self.objectifs.creer_objectif(
            {
                **donnees,
                "utilisateur_id": self._identifiant_utilisateur(donnees),
            }
        )

    def lister_objectifs(self, donnees: DonneesRequete) -> list[dict[str, Any]]:
        """Lister les objectifs d'épargne accessibles.

        Args:
            donnees: Données contenant le jeton de session.

        Returns:
            Les objectifs de l'utilisateur.
        """
        return self.objectifs.consulter_objectifs(
            self._identifiant_utilisateur(donnees)
        )

    def lister_versements(self, donnees: DonneesRequete) -> list[dict[str, Any]]:
        """Lister les versements d'épargne accessibles.

        Args:
            donnees: Session et objectif facultatif à filtrer.

        Returns:
            Les versements correspondant au filtre.
        """
        return self.objectifs.consulter_versements(
            self._identifiant_utilisateur(donnees),
            donnees.get("objectif_id"),
        )

    def obtenir_solde(self, donnees: DonneesRequete) -> dict[str, float]:
        """Retourner le solde de l'utilisateur authentifié.

        Args:
            donnees: Données contenant le jeton de session.

        Returns:
            Les totaux des revenus, dépenses, épargne et solde disponible.
        """
        return self.solde.obtenir(self._identifiant_utilisateur(donnees))

    def alimenter_objectif(self, donnees: DonneesRequete) -> dict[str, Any]:
        """Valider le solde puis enregistrer un versement d'épargne.

        Args:
            donnees: Session, objectif, montant et date du versement.

        Returns:
            Le versement créé.

        Raises:
            ValueError: Si le versement dépasse le solde disponible.
        """
        identifiant_utilisateur = self._identifiant_utilisateur(donnees)
        montant = float(donnees["montant"])
        self.solde.verifier_versement(identifiant_utilisateur, montant)
        return self.objectifs.alimenter_objectif(
            identifiant_utilisateur,
            donnees["objectif_id"],
            montant,
            donnees["date"],
        )

    def analyser_objectifs(self, donnees: DonneesRequete) -> list[dict[str, Any]]:
        """Retourner l'analyse mensuelle des objectifs d'épargne.

        Args:
            donnees: Données contenant le jeton de session.

        Returns:
            Les objectifs enrichis de leurs indicateurs mensuels.
        """
        return self.analyseur_epargne.analyser(self._identifiant_utilisateur(donnees))

    def _identifiant_utilisateur(self, donnees: DonneesRequete) -> int:
        """Résoudre le propriétaire à partir du jeton de session."""
        return self.sessions.identifier(donnees.get("session"))


def construire_serveur(connexion: sqlite3.Connection) -> ServeurSocket:
    """Construire le serveur réseau avec tous les traitements du MVP.

    Args:
        connexion: Connexion SQLite partagée par les repositories.

    Returns:
        Le serveur configuré avec les actions de l'application.
    """
    return ServeurSocket(ApplicationServeur(connexion).traitements())
