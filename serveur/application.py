"""Assemblage des services et routage sécurisé des requêtes du MVP."""

import sqlite3
from collections.abc import Callable
from datetime import date
from typing import Any

from persistance.repositories.budgets import RepositoryBudgets
from persistance.repositories.categories import RepositoryCategories
from persistance.repositories.depenses import RepositoryDepenses
from persistance.repositories.objectifs_epargne import RepositoryObjectifsEpargne
from persistance.repositories.revenus import RepositoryRevenus
from persistance.repositories.utilisateurs import RepositoryUtilisateurs
from serveur.communication.serveur_socket import ServeurSocket
from serveur.securite.sessions import GestionnaireSessions
from serveur.services.alertes import GestionnaireAlertes
from serveur.services.budget import GestionnaireBudget
from serveur.services.calcul_budget import CalculateurBudget
from serveur.services.categories import GestionnaireCategories
from serveur.services.depenses import GestionnaireDepenses
from serveur.services.objectifs_epargne import GestionnaireObjectifsEpargne
from serveur.services.projection import MoteurProjection
from serveur.services.revenus import GestionnaireRevenus
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
        self.objectifs = GestionnaireObjectifsEpargne(
            RepositoryObjectifsEpargne(connexion)
        )
        self.budgets = GestionnaireBudget(
            RepositoryBudgets(connexion),
            self.revenus,
            self.objectifs,
            self.categories,
        )
        self.depenses = GestionnaireDepenses(
            RepositoryDepenses(connexion), self.categories, self.budgets
        )

        self.sessions = GestionnaireSessions()
        self.calculateur = CalculateurBudget(
            self.budgets, self.revenus, self.depenses, self.objectifs
        )
        self.projection = MoteurProjection(
            self.calculateur, self.depenses, self.objectifs
        )
        self.alertes = GestionnaireAlertes(self.calculateur, self.projection)

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
            "categories.modifier": self.modifier_categorie,
            "categories.supprimer": self.supprimer_categorie,
            "categories.lister": self.lister_categories,
            "sous_categories.creer": self.creer_sous_categorie,
            "sous_categories.modifier": self.modifier_sous_categorie,
            "sous_categories.supprimer": self.supprimer_sous_categorie,
            "sous_categories.lister": self.lister_sous_categories,
            "revenus.creer": self.creer_revenu,
            "revenus.creer_recurrents": self.creer_revenus_recurrents,
            "revenus.modifier": self.modifier_revenu,
            "revenus.supprimer": self.supprimer_revenu,
            "revenus.lister": self.lister_revenus,
            "budgets.creer": self.creer_budget,
            "budgets.modifier": self.modifier_budget,
            "budgets.supprimer": self.supprimer_budget,
            "budgets.lister": self.lister_budgets,
            "budgets.etat": self.obtenir_etat_budget,
            "depenses.creer": self.creer_depense,
            "depenses.creer_recurrentes": self.creer_depenses_recurrentes,
            "depenses.modifier": self.modifier_depense,
            "depenses.supprimer": self.supprimer_depense,
            "depenses.lister": self.lister_depenses,
            "objectifs.creer": self.creer_objectif,
            "objectifs.modifier": self.modifier_objectif,
            "objectifs.supprimer": self.supprimer_objectif,
            "objectifs.lister": self.lister_objectifs,
            "objectifs.analyser": self.analyser_objectifs,
            "objectifs.alimenter": self.alimenter_objectif,
            "objectifs.versements": self.lister_versements,
            "solde.obtenir": self.obtenir_solde,
            "projection.simuler": self.simuler_projection,
            "alertes.lister": self.lister_alertes,
            "dashboard.obtenir": self.obtenir_tableau_de_bord,
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

    def modifier_categorie(self, donnees: DonneesRequete) -> dict[str, Any]:
        """Modifier une catégorie de l'utilisateur authentifié.

        Args:
            donnees: Session, identifiant et nouveau nom de la catégorie.

        Returns:
            La catégorie modifiée.
        """
        return self.categories.modifier_categorie(
            self._identifiant_utilisateur(donnees), donnees["id"], donnees["nom"]
        )

    def supprimer_categorie(self, donnees: DonneesRequete) -> None:
        """Supprimer une catégorie de l'utilisateur authentifié.

        Args:
            donnees: Session et identifiant de la catégorie.
        """
        self.categories.supprimer_categorie(
            self._identifiant_utilisateur(donnees), donnees["id"]
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

    def modifier_sous_categorie(self, donnees: DonneesRequete) -> dict[str, Any]:
        """Modifier une sous-catégorie accessible à l'utilisateur.

        Args:
            donnees: Session, catégorie parente, identifiant et nouveau nom.

        Returns:
            La sous-catégorie modifiée.
        """
        return self.categories.modifier_sous_categorie(
            self._identifiant_utilisateur(donnees),
            donnees["categorie_id"],
            donnees["id"],
            donnees["nom"],
        )

    def supprimer_sous_categorie(self, donnees: DonneesRequete) -> None:
        """Supprimer une sous-catégorie accessible à l'utilisateur.

        Args:
            donnees: Session, catégorie parente et identifiant à supprimer.
        """
        self.categories.supprimer_sous_categorie(
            self._identifiant_utilisateur(donnees),
            donnees["categorie_id"],
            donnees["id"],
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

    def creer_revenus_recurrents(
        self, donnees: DonneesRequete
    ) -> list[dict[str, Any]]:
        """Créer côté serveur toutes les occurrences d'un revenu récurrent.

        Args:
            donnees: Session, revenu commun, fréquence et date de fin.

        Returns:
            Les revenus créés dans l'ordre chronologique.
        """
        identifiant_utilisateur = self._identifiant_utilisateur(donnees)
        return self.revenus.ajouter_revenus_recurrents(
            identifiant_utilisateur, donnees
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

    def obtenir_etat_budget(self, donnees: DonneesRequete) -> dict[str, Any]:
        """Calculer l'état mensuel des allocations de l'utilisateur.

        Args:
            donnees: Session et période mensuelle facultative.

        Returns:
            L'état budgétaire mensuel complet.
        """
        aujourd_hui = date.today()
        return self.calculateur.calculer_etat_mensuel(
            self._identifiant_utilisateur(donnees),
            int(donnees.get("annee", aujourd_hui.year)),
            int(donnees.get("mois", aujourd_hui.month)),
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
        return self.depenses.ajouter_depense(
            {**donnees, "utilisateur_id": identifiant_utilisateur},
            self.calculateur.verifier_depense,
        )

    def creer_depenses_recurrentes(
        self, donnees: DonneesRequete
    ) -> list[dict[str, Any]]:
        """Créer une série de dépenses avec les budgets de chaque mois.

        La série entière est validée avant la première écriture afin d'éviter
        une création partielle lorsqu'un budget mensuel manque.
        """
        identifiant_utilisateur = self._identifiant_utilisateur(donnees)
        depenses = self.depenses.preparer_depenses_recurrentes(
            identifiant_utilisateur,
            donnees,
            creer_budgets_manquants=donnees.get("creer_budgets_manquants") is True,
        )
        self.calculateur.verifier_depenses_recurrentes(
            identifiant_utilisateur, depenses
        )
        return self.depenses.enregistrer_depenses_preparees(depenses)

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
        return self.depenses.modifier_depense(
            identifiant_utilisateur,
            identifiant_depense,
            donnees,
            self.calculateur.verifier_depense,
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

    def modifier_objectif(self, donnees: DonneesRequete) -> dict[str, Any]:
        """Modifier un objectif d'épargne accessible.

        Args:
            donnees: Session, identifiant et nouvelles valeurs de l'objectif.

        Returns:
            L'objectif modifié.
        """
        return self.objectifs.modifier_objectif(
            self._identifiant_utilisateur(donnees), donnees["id"], donnees
        )

    def supprimer_objectif(self, donnees: DonneesRequete) -> None:
        """Supprimer un objectif d'épargne accessible.

        Args:
            donnees: Session et identifiant de l'objectif.
        """
        self.objectifs.supprimer_objectif(
            self._identifiant_utilisateur(donnees), donnees["id"]
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
        return self.calculateur.obtenir_solde(
            self._identifiant_utilisateur(donnees)
        )

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
        self.calculateur.verifier_versement(identifiant_utilisateur, montant)
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
        return self.calculateur.analyser_objectifs(
            self._identifiant_utilisateur(donnees)
        )

    def simuler_projection(self, donnees: DonneesRequete) -> dict[str, Any]:
        """Projeter le budget mensuel sans modifier les données persistantes.

        Args:
            donnees: Session, période et dépense hypothétique facultatives.

        Returns:
            La situation projetée et ses conséquences.
        """
        aujourd_hui = date.today()
        return self.projection.projeter_mois(
            self._identifiant_utilisateur(donnees),
            int(donnees.get("annee", aujourd_hui.year)),
            int(donnees.get("mois", aujourd_hui.month)),
            float(donnees.get("montant", 0)),
            donnees.get("objectif_id"),
            donnees.get("budget_id"),
        )

    def lister_alertes(self, donnees: DonneesRequete) -> list[dict[str, Any]]:
        """Lister les alertes actives à partir du seuil de 80 %.

        Args:
            donnees: Session, période et seuil facultatifs.

        Returns:
            Les alertes actives prêtes à présenter.
        """
        aujourd_hui = date.today()
        return self.alertes.lister_alertes(
            self._identifiant_utilisateur(donnees),
            int(donnees.get("annee", aujourd_hui.year)),
            int(donnees.get("mois", aujourd_hui.month)),
            float(donnees.get("seuil", 80)),
        )

    def obtenir_tableau_de_bord(self, donnees: DonneesRequete) -> dict[str, Any]:
        """Fournir au client un tableau de bord déjà calculé.

        Args:
            donnees: Session et période mensuelle facultative.

        Returns:
            Les indicateurs, graphiques et alertes du tableau de bord.
        """
        aujourd_hui = date.today()
        annee = int(donnees.get("annee", aujourd_hui.year))
        mois = int(donnees.get("mois", aujourd_hui.month))
        identifiant_utilisateur = self._identifiant_utilisateur(donnees)
        tableau = self.calculateur.construire_tableau_de_bord(
            identifiant_utilisateur, annee, mois
        )
        alertes = self.alertes.lister_alertes(
            identifiant_utilisateur, annee, mois
        )
        return {
            **tableau,
            "alertes": alertes,
            "alertes_actives": len(alertes),
        }

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
