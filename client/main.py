"""Point d'entrée de la couche cliente."""

from datetime import datetime
from decimal import Decimal

import customtkinter as ctk
from tkinter import messagebox
from communication.api import ApiClient, ErreurServeur
from interface.alertes import VueAlertes
from interface.budgets import VueBudgets
from interface.connexion import Connexion
from interface.dashboard import TableauDeBord
from interface.inscription import VueInscription
from interface.objectifs import VueObjectifs
from interface.parametres import VueParametres
from interface.transactions import VueTransactions


class ApplicationMonBudget(ctk.CTk):
    """Coordonner les interfaces de MonBudget.

    Les données du MVP sont chargées et modifiées par le serveur JSON/TCP.
    """

    def __init__(self):
        super().__init__()

        self.title("MonBudget")
        self.geometry("1250x780")
        self.minsize(1050, 650)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        # Couleurs
        self.vert = "#00634F"
        self.beige = "#F5F3EF"
        self.sombre = "#1B2225"
        self.blanc = "#FFFFFF"

        # Données temporaires
        self.transactions = []
        self.budgets = []
        self.profil = {}
        self.api = ApiClient()
        self.categories = []
        self.sous_categories = []
        self.solde = {"revenus": 0, "depenses": 0, "epargne": 0, "disponible": 0}
        self.etat_budget = {"categories": [], "total_alloue": 0, "total_depense": 0}

        # État de l'interface
        self.page_actuelle = None
        self.menu = None
        self.contenu = None

        # Commencer par la connexion
        self.afficher_connexion()

    def nettoyer_fenetre(self):
        """Supprimer les éléments de la fenêtre."""

        for widget in self.winfo_children():
            widget.destroy()

        self.menu = None
        self.contenu = None
        self.page_actuelle = None

    # ---------------------------------------
    # CONNEXION ET INSCRIPTION
    # ---------------------------------------

    def afficher_connexion(self):
        """Afficher l'écran de connexion."""

        self.nettoyer_fenetre()

        vue = Connexion(
            self,
            on_login=self.demander_connexion,
            on_register=self.afficher_inscription,
        )
        vue.pack(fill="both", expand=True)

    def afficher_inscription(self):
        """Afficher l'écran d'inscription."""

        self.nettoyer_fenetre()

        vue = VueInscription(
            self,
            on_register=self.demander_inscription,
            on_login=self.afficher_connexion,
        )
        vue.pack(fill="both", expand=True)

    def demander_connexion(self, email, password):
        """Ouvrir une session authentifiée auprès du serveur.

        Args:
            email: Identifiant saisi dans le formulaire.
            password: Mot de passe saisi dans le formulaire.
        """
        compte = self.api.connecter(email, password)
        self.profil = {"nom": "", "prenom": "", "email": compte["identifiant"]}
        self.charger_donnees()
        self.afficher_application()

    def demander_inscription(self, nom, prenom, email, password):
        """Créer un compte puis ouvrir sa session.

        Args:
            nom: Nom renseigné dans le profil local.
            prenom: Prénom renseigné dans le profil local.
            email: Identifiant utilisé pour créer le compte.
            password: Mot de passe du nouveau compte.
        """
        self.api.inscrire(email, password)
        compte = self.api.connecter(email, password)
        self.profil = {"nom": nom, "prenom": prenom, "email": compte["identifiant"]}
        self.charger_donnees()
        self.afficher_application()

    def charger_donnees(self):
        """Recharger depuis SQLite les données utilisées par les écrans."""
        self.categories = self.api.appeler("categories.lister")
        noms = {c["id"]: c["nom"] for c in self.categories}
        self.sous_categories = []
        for categorie in self.categories:
            self.sous_categories.extend(
                self.api.appeler("sous_categories.lister", categorie_id=categorie["id"])
            )
        noms_sous_categories = {s["id"]: s["nom"] for s in self.sous_categories}
        budgets = self.api.appeler("budgets.lister")
        self.budgets = [
            {
                "id": b["id"],
                "categorie": noms.get(b["categorie_id"], "Sans catégorie"),
                "categorie_id": b["categorie_id"],
                "annee": b["annee"],
                "mois": b["mois"],
                "sous_categorie_id": b.get("sous_categorie_id"),
                "sous_categorie": noms_sous_categories.get(b.get("sous_categorie_id")),
                "plafond": Decimal(str(b["montant_alloue"])),
            }
            for b in budgets
        ]
        for budget in self.budgets:
            budget["libelle"] = budget["categorie"] + (
                f" · {budget['sous_categorie']}" if budget["sous_categorie"] else ""
            )
        revenus = self.api.appeler("revenus.lister")
        depenses = self.api.appeler("depenses.lister")
        self.solde = self.api.appeler("solde.obtenir")
        self.etat_budget = self.api.appeler("budgets.etat")
        self.transactions = [
            {
                "id": f"revenu:{r['id']}",
                "type": "Revenu",
                "libelle": r.get("description") or "Revenu",
                "montant": Decimal(str(r["montant"])),
                "categorie": r.get("categorie", "Salaire"),
                "statut": r["statut"],
                "date": datetime.fromisoformat(r["date"]).strftime("%d/%m/%Y"),
            }
            for r in revenus
        ]
        self.transactions += [
            {
                "id": f"depense:{d['id']}",
                "type": "Dépense",
                "libelle": d.get("description") or "Dépense",
                "montant": Decimal(str(d["montant"])),
                "budget_id": d["budget_id"],
                "statut": d["statut"],
                "categorie": noms.get(d["categorie_id"], "Sans catégorie")
                + (
                    f" · {noms_sous_categories[d['sous_categorie_id']]}"
                    if d.get("sous_categorie_id") in noms_sous_categories
                    else ""
                ),
                "date": datetime.fromisoformat(d["date"]).strftime("%d/%m/%Y"),
            }
            for d in depenses
        ]
        self.transactions.sort(
            key=lambda transaction: datetime.strptime(transaction["date"], "%d/%m/%Y"),
            reverse=True,
        )

    def _categorie(self, nom):
        for categorie in self.categories:
            if categorie["nom"] == nom:
                return categorie
        categorie = self.api.appeler("categories.creer", nom=nom)
        self.categories.append(categorie)
        return categorie

    def _sous_categorie(self, categorie_id, nom):
        if not nom:
            return None
        for sous_categorie in self.sous_categories:
            if (
                sous_categorie["categorie_id"] == categorie_id
                and sous_categorie["nom"] == nom
            ):
                return sous_categorie
        sous_categorie = self.api.appeler(
            "sous_categories.creer", categorie_id=categorie_id, nom=nom
        )
        self.sous_categories.append(sous_categorie)
        return sous_categorie

    # ---------------------------------------
    # STRUCTURE PRINCIPALE
    # ---------------------------------------

    def afficher_application(self):
        """Construire la fenêtre principale."""

        self.nettoyer_fenetre()

        self.configure(fg_color=self.beige)

        # Barre latérale
        self.menu = ctk.CTkFrame(self, width=190, corner_radius=0, fg_color=self.sombre)
        self.menu.pack(side="left", fill="y")
        self.menu.pack_propagate(False)

        # Logo
        ctk.CTkLabel(
            self.menu,
            text="MonBudget",
            font=("Arial", 21, "bold"),
            text_color=self.blanc,
        ).pack(anchor="w", padx=20, pady=(25, 35))

        # Navigation
        pages = [
            ("Tableau de bord", "dashboard"),
            ("Transactions", "transactions"),
            ("Budgets", "budgets"),
            ("Épargne", "objectifs"),
            ("Alertes", "alertes"),
            ("Paramètres", "parametres"),
        ]

        for titre, page in pages:
            self.creer_bouton_menu(titre, page)

        # Partie inférieure du menu
        bas = ctk.CTkFrame(self.menu, fg_color="transparent")
        bas.pack(side="bottom", fill="x", padx=15, pady=20)

        self.label_utilisateur = ctk.CTkLabel(
            bas,
            text=self.nom_utilisateur(),
            text_color=self.blanc,
            anchor="w",
            wraplength=150,
        )
        self.label_utilisateur.pack(fill="x", pady=(0, 12))

        ctk.CTkButton(
            bas,
            text="Déconnexion",
            fg_color="transparent",
            hover_color="#303A3D",
            anchor="w",
            command=self.deconnecter,
        ).pack(fill="x")

        # Zone principale
        self.contenu = ctk.CTkFrame(self, fg_color=self.beige, corner_radius=0)
        self.contenu.pack(side="right", fill="both", expand=True)

        self.afficher_page("dashboard")

    def creer_bouton_menu(self, titre, page):
        """Créer un bouton de navigation.

        Args:
            titre: Texte affiché dans le menu.
            page: Identifiant de la page à ouvrir.
        """

        ctk.CTkButton(
            self.menu,
            text=titre,
            height=42,
            anchor="w",
            corner_radius=7,
            fg_color="transparent",
            hover_color="#00634F",
            text_color=self.blanc,
            command=lambda p=page: self.afficher_page(p),
        ).pack(fill="x", padx=12, pady=4)

    def nom_utilisateur(self):
        """Retourner le nom à afficher."""

        nom = (self.profil.get("prenom", "") + " " + self.profil.get("nom", "")).strip()

        return nom or self.profil.get("email", "")

    # ---------------------------------------
    # NAVIGATION
    # ---------------------------------------

    def afficher_page(self, page):
        """Afficher une page de l'application.

        Args:
            page: Identifiant de la page à afficher.
        """

        if self.contenu is None:
            return

        for widget in self.contenu.winfo_children():
            widget.destroy()

        self.page_actuelle = page

        if page == "dashboard":
            self.afficher_dashboard()

        elif page == "transactions":
            self.afficher_transactions()

        elif page == "budgets":
            self.afficher_budgets()

        elif page == "objectifs":
            self.afficher_objectifs()

        elif page == "alertes":
            self.afficher_alertes()

        elif page == "parametres":
            self.afficher_parametres()

    def afficher_dashboard(self):
        """Afficher les indicateurs déjà calculés par le serveur."""
        donnees = self.api.appeler("dashboard.obtenir")
        donnees["prenom"] = self.profil.get("prenom", "")
        self.vue = TableauDeBord(
            self.contenu,
            ajouter_depense=lambda: self.afficher_page("transactions"),
            voir_depenses=lambda: self.afficher_page("transactions"),
            voir_alertes=lambda: self.afficher_page("alertes"),
        )

        self.vue.pack(fill="both", expand=True)

        self.vue.actualiser(donnees)

    def afficher_transactions(self):
        """Afficher la gestion des transactions."""

        self.vue = VueTransactions(
            self.contenu,
            on_ajouter=self.ajouter_transaction,
            on_modifier=self.modifier_transaction,
            on_supprimer=self.supprimer_transaction,
        )

        self.vue.pack(fill="both", expand=True)
        self.actualiser_transactions()

    def afficher_budgets(self):
        """Afficher la gestion des budgets."""

        self.vue = VueBudgets(
            self.contenu,
            on_ajouter=self.ajouter_budget,
            on_modifier=self.modifier_budget,
            on_supprimer=self.supprimer_budget,
            on_modifier_categorie=self.modifier_categorie,
            on_supprimer_categorie=self.supprimer_categorie,
            on_modifier_sous_categorie=self.modifier_sous_categorie,
            on_supprimer_sous_categorie=self.supprimer_sous_categorie,
        )

        self.vue.pack(fill="both", expand=True)
        self.vue.definir_categories(self.categories, self.sous_categories)
        self.actualiser_budgets()

    def afficher_objectifs(self):
        """Afficher les objectifs et leurs versements d'épargne."""
        self.vue = VueObjectifs(
            self.contenu,
            self.ajouter_objectif,
            self.alimenter_objectif,
            self.modifier_objectif,
            self.supprimer_objectif,
        )
        self.vue.pack(fill="both", expand=True)
        self.vue.actualiser(self.api.appeler("objectifs.analyser"))

    def ajouter_objectif(self, donnees):
        """Créer un objectif puis rafraîchir sa liste.

        Args:
            donnees: Informations validées par le formulaire d'objectif.
        """
        self.api.appeler("objectifs.creer", **donnees)
        if self.page_actuelle == "objectifs":
            self.vue.actualiser(self.api.appeler("objectifs.analyser"))

    def alimenter_objectif(self, objectif_id, montant, date_versement):
        """Verser une partie du solde sur un objectif.

        Args:
            objectif_id: Identifiant de l'objectif à alimenter.
            montant: Montant du versement.
            date_versement: Date du versement au format ISO.
        """
        self.api.appeler(
            "objectifs.alimenter",
            objectif_id=objectif_id,
            montant=montant,
            date=date_versement,
        )
        self.charger_donnees()
        if self.page_actuelle == "objectifs":
            self.vue.actualiser(self.api.appeler("objectifs.analyser"))

    def modifier_objectif(self, objectif_id, donnees):
        """Modifier un objectif puis rafraîchir son analyse.

        Args:
            objectif_id: Identifiant de l'objectif à modifier.
            donnees: Nouvelles informations saisies dans l'interface.
        """
        self.api.appeler("objectifs.modifier", id=objectif_id, **donnees)
        self.charger_donnees()
        if self.page_actuelle == "objectifs":
            self.vue.actualiser(self.api.appeler("objectifs.analyser"))

    def supprimer_objectif(self, objectif_id):
        """Supprimer un objectif et rafraîchir la page d'épargne."""
        self.api.appeler("objectifs.supprimer", id=objectif_id)
        self.charger_donnees()
        if self.page_actuelle == "objectifs":
            self.vue.actualiser(self.api.appeler("objectifs.analyser"))

    def afficher_parametres(self):
        """Afficher les paramètres."""

        self.vue = VueParametres(
            self.contenu,
            on_modifier_profil=self.modifier_profil,
            on_changer_mot_de_passe=self.changer_mot_de_passe,
            on_deconnexion=self.deconnecter,
            on_supprimer_compte=self.supprimer_compte,
        )

        self.vue.pack(fill="both", expand=True)

        self.vue.actualiser(self.profil)

    # ---------------------------------------
    # TRANSACTIONS
    # ---------------------------------------

    def ajouter_transaction(self, donnees):
        """Ajouter une ou plusieurs transactions persistées.

        Args:
            donnees: Informations et récurrence choisies dans le formulaire.
        """
        date_transaction = datetime.strptime(donnees["date"], "%d/%m/%Y")
        date_fin = (
            datetime.strptime(donnees["date_fin"], "%d/%m/%Y").date().isoformat()
            if donnees.get("date_fin")
            else None
        )
        recurrence = {
            "date": date_transaction.date().isoformat(),
            "date_fin": date_fin,
            "frequence": donnees.get("frequence", "Aucune"),
            "montant": float(donnees["montant"]),
            "description": donnees["libelle"],
        }
        if donnees["type"] == "Revenu":
            self.api.appeler(
                "revenus.creer_recurrents",
                **recurrence,
                categorie=donnees["categorie"],
            )
        else:
            budget = next(
                (
                    b
                    for b in self.budgets
                    if b["libelle"] == donnees["categorie"]
                    and b["annee"] == date_transaction.year
                    and b["mois"] == date_transaction.month
                ),
                None,
            )
            if budget is None:
                raise ValueError(
                    "Aucun budget pour cette catégorie au mois de la transaction."
                )
            parametres = {
                **recurrence,
                "budget_id": budget["id"],
                "categorie_id": budget["categorie_id"],
                "sous_categorie_id": budget["sous_categorie_id"],
            }

            try:
                self.api.appeler(
                    "depenses.creer_recurrentes",
                    **parametres,
                    creer_budgets_manquants=False,
                )

            except ErreurServeur as erreur:
                if not str(erreur).startswith("Aucun budget compatible pour le mois "):
                    raise

                confirmation = messagebox.askyesno(
                    "Budgets mensuels manquants",
                    (
                        f"{erreur}\n\n"
                        "Le budget du premier mois sera reconduit pour les "
                        "mois manquants jusqu'à la fin de la récurrence.\n\n"
                        "Les budgets existants ne seront pas modifiés.\n\n"
                        "Créer ces budgets et enregistrer les dépenses ?"
                    ),
                    parent=self,
                )

                if not confirmation:
                    raise ValueError(
                        "Enregistrement annulé ; aucune donnée créée."
                    ) from erreur

                self.api.appeler(
                    "depenses.creer_recurrentes",
                    **parametres,
                    creer_budgets_manquants=True,
                )
        self.charger_donnees()
        self.actualiser_transactions()

    def modifier_transaction(self, identifiant, donnees):
        """Modifier une transaction existante.

        Args:
            identifiant: Identifiant local préfixé par le type de transaction.
            donnees: Nouvelles valeurs validées par le formulaire.
        """

        type_objet, numero = identifiant.split(":", 1)
        date_transaction = datetime.strptime(donnees["date"], "%d/%m/%Y")
        date_iso = date_transaction.date().isoformat()
        if type_objet == "revenu":
            self.api.appeler(
                "revenus.modifier",
                id=int(numero),
                montant=float(donnees["montant"]),
                date=date_iso,
                description=donnees["libelle"],
                categorie=donnees["categorie"],
            )
        else:
            budget = next(
                (
                    b
                    for b in self.budgets
                    if b["libelle"] == donnees["categorie"]
                    and b["annee"] == date_transaction.year
                    and b["mois"] == date_transaction.month
                ),
                None,
            )
            if budget is None:
                transaction_existante = next(
                    (t for t in self.transactions if t["id"] == identifiant), {}
                )
                budget = next(
                    (
                        b
                        for b in self.budgets
                        if b["id"] == transaction_existante.get("budget_id")
                    ),
                    None,
                )
            if budget is None:
                raise ValueError(
                    "Aucun budget pour cette catégorie au mois de la transaction."
                )
            self.api.appeler(
                "depenses.modifier",
                id=int(numero),
                budget_id=budget["id"],
                categorie_id=budget["categorie_id"],
                sous_categorie_id=budget["sous_categorie_id"],
                montant=float(donnees["montant"]),
                date=date_iso,
                description=donnees["libelle"],
            )
        self.charger_donnees()
        self.actualiser_transactions()

    def supprimer_transaction(self, identifiant):
        """Supprimer une transaction persistée.

        Args:
            identifiant: Identifiant local préfixé par le type de transaction.
        """

        type_objet, numero = identifiant.split(":", 1)
        self.api.appeler(
            f"{'revenus' if type_objet == 'revenu' else 'depenses'}.supprimer",
            id=int(numero),
        )
        self.charger_donnees()
        self.actualiser_transactions()

    def actualiser_transactions(self):
        """Transmettre les données à VueTransactions."""

        if self.page_actuelle != "transactions":
            return

        resume = {
            "revenus": Decimal(str(self.solde["revenus"])),
            "depenses": Decimal(str(self.solde["depenses"])),
            "solde": Decimal(str(self.solde["disponible"])),
        }

        maintenant = datetime.now()
        self.vue.definir_categories(
            sorted(
                {
                    b["libelle"]
                    for b in self.budgets
                    if b["annee"] == maintenant.year and b["mois"] == maintenant.month
                }
            )
        )

        self.vue.actualiser(self.transactions, resume)

    # ---------------------------------------
    # ALERTES
    # ---------------------------------------

    def obtenir_alertes(self):
        """Demander au gestionnaire serveur les alertes actives."""
        return self.api.appeler("alertes.lister")

    def afficher_alertes(self):
        """Afficher la page des alertes."""

        self.vue = VueAlertes(
            self.contenu, on_retour=lambda: self.afficher_page("dashboard")
        )
        self.vue.pack(fill="both", expand=True)
        self.vue.actualiser(self.obtenir_alertes())

    # ---------------------------------------
    # BUDGETS
    # ---------------------------------------

    def ajouter_budget(self, categorie, sous_categorie, plafond):
        """Ajouter un budget mensuel persistant.

        Args:
            categorie: Nom de la catégorie financée.
            sous_categorie: Nom facultatif de la sous-catégorie.
            plafond: Montant alloué au budget.
        """
        classement = self._categorie(categorie)
        maintenant = datetime.now()
        sous_classement = self._sous_categorie(classement["id"], sous_categorie)
        self.api.appeler(
            "budgets.creer",
            annee=maintenant.year,
            mois=maintenant.month,
            categorie_id=classement["id"],
            sous_categorie_id=sous_classement["id"] if sous_classement else None,
            montant_alloue=float(plafond),
            obligatoire=False,
        )
        self.charger_donnees()
        self.actualiser_budgets()

    def modifier_budget(self, identifiant, categorie, sous_categorie, plafond):
        """Modifier un budget existant.

        Args:
            identifiant: Identifiant du budget à modifier.
            categorie: Nouveau nom de catégorie.
            sous_categorie: Nouveau nom facultatif de sous-catégorie.
            plafond: Nouveau montant alloué.
        """

        classement = self._categorie(categorie)
        maintenant = datetime.now()
        sous_classement = self._sous_categorie(classement["id"], sous_categorie)
        self.api.appeler(
            "budgets.modifier",
            id=int(identifiant),
            annee=maintenant.year,
            mois=maintenant.month,
            categorie_id=classement["id"],
            sous_categorie_id=sous_classement["id"] if sous_classement else None,
            montant_alloue=float(plafond),
            obligatoire=False,
        )
        self.charger_donnees()
        self.actualiser_budgets()

    def supprimer_budget(self, identifiant):
        """Supprimer un budget persistant.

        Args:
            identifiant: Identifiant du budget à supprimer.
        """

        self.api.appeler("budgets.supprimer", id=int(identifiant))
        self.charger_donnees()
        self.actualiser_budgets()

    def modifier_categorie(self, identifiant, nom):
        """Renommer une catégorie depuis l'écran des budgets.

        Args:
            identifiant: Identifiant de la catégorie.
            nom: Nouveau nom validé par l'interface.
        """
        self.api.appeler("categories.modifier", id=int(identifiant), nom=nom)
        self.charger_donnees()
        self.actualiser_budgets()

    def supprimer_categorie(self, identifiant):
        """Supprimer une catégorie après confirmation dans l'interface."""
        self.api.appeler("categories.supprimer", id=int(identifiant))
        self.charger_donnees()
        self.actualiser_budgets()

    def modifier_sous_categorie(self, categorie_id, identifiant, nom):
        """Renommer une sous-catégorie depuis l'écran des budgets."""
        self.api.appeler(
            "sous_categories.modifier",
            categorie_id=int(categorie_id),
            id=int(identifiant),
            nom=nom,
        )
        self.charger_donnees()
        self.actualiser_budgets()

    def supprimer_sous_categorie(self, categorie_id, identifiant):
        """Supprimer une sous-catégorie après confirmation."""
        self.api.appeler(
            "sous_categories.supprimer",
            categorie_id=int(categorie_id),
            id=int(identifiant),
        )
        self.charger_donnees()
        self.actualiser_budgets()

    def obtenir_budgets_affichage(self):
        """Retourner les états déjà calculés par le serveur."""
        return self.etat_budget.get("categories", [])

    def actualiser_budgets(self):
        """Transmettre les données à VueBudgets."""

        if self.page_actuelle != "budgets":
            return

        budgets = self.obtenir_budgets_affichage()
        self.vue.definir_categories(self.categories, self.sous_categories)

        resume = {
            "total": self.etat_budget.get("total_alloue", 0),
            "depense": self.etat_budget.get("total_depense", 0),
            "restant": self.etat_budget.get("total_restant", 0),
        }

        self.vue.actualiser(budgets, resume)

    # ---------------------------------------
    # PARAMÈTRES
    # ---------------------------------------

    def modifier_profil(self, donnees):
        """Modifier les informations locales du profil.

        Args:
            donnees: Nom, prénom et adresse saisis dans les paramètres.
        """

        self.profil.update(donnees)

        if self.label_utilisateur is not None:
            self.label_utilisateur.configure(text=self.nom_utilisateur())

    def changer_mot_de_passe(self, ancien, nouveau):
        """Changer le mot de passe du compte authentifié.

        Args:
            ancien: Mot de passe actuel.
            nouveau: Nouveau mot de passe à enregistrer.
        """
        self.api.appeler(
            "utilisateurs.changer_mot_de_passe", ancien=ancien, nouveau=nouveau
        )

    # ---------------------------------------
    # DÉCONNEXION
    # ---------------------------------------

    def deconnecter(self):
        """Terminer la session serveur et vider l'affichage local."""

        self.api.deconnecter()

        self.transactions.clear()
        self.budgets.clear()
        self.profil.clear()

        ctk.set_appearance_mode("light")

        self.afficher_connexion()

    def supprimer_compte(self, mot_de_passe):
        """Supprimer le compte courant et revenir à la connexion.

        Args:
            mot_de_passe: Mot de passe utilisé pour confirmer la suppression.
        """
        self.api.appeler("utilisateurs.supprimer", mot_de_passe=mot_de_passe)
        self.api.session = None
        self.transactions.clear()
        self.budgets.clear()
        self.profil.clear()
        self.afficher_connexion()


def main() -> None:
    """Démarrer l'application cliente.

    Returns:
        None.
    """

    application = ApplicationMonBudget()
    application.mainloop()


if __name__ == "__main__":
    main()
