
"""Point d'entrée de la couche cliente."""

from datetime import datetime
from decimal import Decimal

import customtkinter as ctk

from interface.dashboard import TableauDeBord
from interface.transactions import VueTransactions
from interface.budgets import VueBudgets
from interface.connexion import Connexion
from interface.inscription import VueInscription
from interface.parametres import VueParametres
from interface.alertes import VueAlertes
from interface.factures import VueFactures
from interface.objectifs import VueObjectifs
from communication.api import ApiClient


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
        self.factures = []
        self.profil = {}
        self.theme = "Clair"
        self.api = ApiClient()
        self.categories = []

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
            on_register=self.afficher_inscription
        )
        vue.pack(fill="both", expand=True)

    def afficher_inscription(self):
        """Afficher l'écran d'inscription."""

        self.nettoyer_fenetre()

        vue = VueInscription(
            self,
            on_register=self.demander_inscription,
            on_login=self.afficher_connexion
        )
        vue.pack(fill="both", expand=True)

    def demander_connexion(self, email, password):
        """Ouvrir une session authentifiée auprès du serveur."""
        compte = self.api.connecter(email, password)
        self.profil = {"nom":"","prenom":"","email":compte["identifiant"]}
        self.charger_donnees()
        self.afficher_application()

    def demander_inscription(
        self,
        nom,
        prenom,
        email,
        password
    ):
        """Créer le compte puis ouvrir sa session."""
        self.api.inscrire(email,password)
        compte=self.api.connecter(email,password)
        self.profil={"nom":nom,"prenom":prenom,"email":compte["identifiant"]}
        self.charger_donnees()
        self.afficher_application()

    def charger_donnees(self):
        """Recharger depuis SQLite les données utilisées par les écrans."""
        self.categories=self.api.appeler("categories.lister")
        noms={c["id"]:c["nom"] for c in self.categories}
        budgets=self.api.appeler("budgets.lister")
        self.budgets=[{"id":b["id"],"categorie":noms.get(b["categorie_id"],"Sans catégorie"),
                       "categorie_id":b["categorie_id"],"plafond":Decimal(str(b["montant_alloue"]))}
                      for b in budgets]
        revenus=self.api.appeler("revenus.lister")
        depenses=self.api.appeler("depenses.lister")
        self.transactions=[{"id":f"revenu:{r['id']}","type":"Revenu",
            "libelle":r.get("description") or "Revenu","montant":Decimal(str(r["montant"])),
            "categorie":"Revenu","date":datetime.fromisoformat(r["date"]).strftime("%d/%m/%Y")}
            for r in revenus]
        self.transactions += [{"id":f"depense:{d['id']}","type":"Dépense",
            "libelle":d.get("description") or "Dépense","montant":Decimal(str(d["montant"])),
            "categorie":noms.get(d["categorie_id"],"Sans catégorie"),
            "date":datetime.fromisoformat(d["date"]).strftime("%d/%m/%Y")}
            for d in depenses]

    def _categorie(self, nom):
        for categorie in self.categories:
            if categorie["nom"] == nom: return categorie
        categorie=self.api.appeler("categories.creer",nom=nom)
        self.categories.append(categorie); return categorie

    # ---------------------------------------
    # STRUCTURE PRINCIPALE
    # ---------------------------------------

    def afficher_application(self):
        """Construire la fenêtre principale."""

        self.nettoyer_fenetre()

        self.configure(fg_color=self.beige)

        # Barre latérale
        self.menu = ctk.CTkFrame(
            self,
            width=190,
            corner_radius=0,
            fg_color=self.sombre
        )
        self.menu.pack(
            side="left",
            fill="y"
        )
        self.menu.pack_propagate(False)

        # Logo
        ctk.CTkLabel(
            self.menu,
            text="MonBudget",
            font=("Arial", 21, "bold"),
            text_color=self.blanc
        ).pack(
            anchor="w",
            padx=20,
            pady=(25, 35)
        )

        # Navigation
        pages = [
            ("Tableau de bord", "dashboard"),
            ("Transactions", "transactions"),
            ("Budgets", "budgets"),
            ("Épargne & projection", "objectifs"),
            ("Alertes", "alertes"),
            ("Paramètres", "parametres")
        ]

        for titre, page in pages:
            self.creer_bouton_menu(titre, page)

        # Partie inférieure du menu
        bas = ctk.CTkFrame(
            self.menu,
            fg_color="transparent"
        )
        bas.pack(
            side="bottom",
            fill="x",
            padx=15,
            pady=20
        )

        self.label_utilisateur = ctk.CTkLabel(
            bas,
            text=self.nom_utilisateur(),
            text_color=self.blanc,
            anchor="w",
            wraplength=150
        )
        self.label_utilisateur.pack(
            fill="x",
            pady=(0, 12)
        )

        ctk.CTkButton(
            bas,
            text="Déconnexion",
            fg_color="transparent",
            hover_color="#303A3D",
            anchor="w",
            command=self.deconnecter
        ).pack(fill="x")

        # Zone principale
        self.contenu = ctk.CTkFrame(
            self,
            fg_color=self.beige,
            corner_radius=0
        )
        self.contenu.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.afficher_page("dashboard")

    def creer_bouton_menu(self, titre, page):
        """Créer un bouton de navigation."""

        ctk.CTkButton(
            self.menu,
            text=titre,
            height=42,
            anchor="w",
            corner_radius=7,
            fg_color="transparent",
            hover_color="#00634F",
            text_color=self.blanc,
            command=lambda p=page: self.afficher_page(p)
        ).pack(
            fill="x",
            padx=12,
            pady=4
        )

    def nom_utilisateur(self):
        """Retourner le nom à afficher."""

        nom = (
            self.profil.get("prenom", "") + " " +
            self.profil.get("nom", "")
        ).strip()

        return nom or self.profil.get("email", "")

    # ---------------------------------------
    # NAVIGATION
    # ---------------------------------------

    def afficher_page(self, page):
        """Afficher la page sélectionnée."""

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

        elif page == "factures":
            self.afficher_factures()

        elif page == "alertes":
            self.afficher_alertes()

        elif page == "parametres":
            self.afficher_parametres()



    def afficher_dashboard(self):
        """Afficher le tableau de bord avec les données actuelles."""

        from collections import defaultdict
        from calendar import monthrange

        aujourd_hui = datetime.now()
        mois_actuel = aujourd_hui.strftime("%m/%Y")

        # Récupérer les budgets déjà calculés
        budgets = self.calculer_budgets_affichage()

        # Total des plafonds mensuels
        budget_total = sum(
            (b["plafond"] for b in budgets),
            Decimal("0")
        )

        # Dépenses du mois en cours
        depenses_mois = [
            t for t in self.transactions
            if (
                t["type"] == "Dépense"
                and str(t["date"])[3:] == mois_actuel
            )
        ]

        total_depenses = sum(
            (Decimal(str(t["montant"])) for t in depenses_mois),
            Decimal("0")
        )

        # Budget restant
        restant = budget_total - total_depenses

        # Répartition par catégorie
        repartition_categories = defaultdict(
            lambda: Decimal("0")
        )

        for transaction in depenses_mois:
            categorie = transaction.get(
                "categorie", "Sans catégorie"
            )

            repartition_categories[categorie] += Decimal(
                str(transaction["montant"])
            )

        repartition = [
            {
                "categorie": categorie,
                "montant": float(montant)
            }
            for categorie, montant
            in repartition_categories.items()
        ]

        # Budgets par catégorie
        budgets_dashboard = []

        for budget in budgets:
            budgets_dashboard.append({
                "categorie": budget["categorie"],
                "plafond": float(budget["plafond"]),
                "depense": float(budget["depense"]),
                "pourcentage": budget["progression"] * 100
            })

        # Évolution des dépenses sur 6 mois
        evolution = []

        for decalage in range(5, -1, -1):
            indice_mois = (
                aujourd_hui.year * 12
                + aujourd_hui.month - 1
                - decalage
            )

            annee = indice_mois // 12
            mois = indice_mois % 12 + 1

            total = Decimal("0")

            for transaction in self.transactions:
                if transaction["type"] != "Dépense":
                    continue

                try:
                    date_transaction = datetime.strptime(
                        transaction["date"],
                        "%d/%m/%Y"
                    )
                except ValueError:
                    continue

                if (
                    date_transaction.year == annee
                    and date_transaction.month == mois
                ):
                    total += Decimal(
                        str(transaction["montant"])
                    )

            evolution.append({
                "mois": f"{mois:02d}/{annee}",
                "montant": float(total)
            })

        # Dernières dépenses
        dernieres_depenses = sorted(
            [
                t for t in self.transactions
                if t["type"] == "Dépense"
            ],
            key=lambda t: datetime.strptime(
                t["date"], "%d/%m/%Y"
            ),
            reverse=True
        )[:5]

        # Alertes
        alertes = self.obtenir_alertes()

        # Garder uniquement les alertes urgentes
        alertes_urgentes = [
            alerte for alerte in alertes
            if alerte.get("type") in ("attention", "risque")
        ]

        # Préparer toutes les données
        donnees = {
            "prenom": self.profil.get("prenom", ""),
            "mois": aujourd_hui.strftime(
                "Résumé du mois %m/%Y"
            ),
            "budget_mois": float(budget_total),
            "depense": float(total_depenses),
            "restant": float(restant),
            "alertes_actives": len(alertes_urgentes),
            "repartition": repartition,
            "budgets": budgets_dashboard,
            "evolution": evolution,
            "dernieres_depenses": dernieres_depenses,
            "alertes": alertes_urgentes
        }

        # Créer le tableau de bord
        self.vue = TableauDeBord(
            self.contenu,
            ajouter_depense=lambda: self.afficher_page(
                "transactions"
            ),
            voir_depenses=lambda: self.afficher_page(
                "transactions"
            ),
            voir_alertes=lambda: self.afficher_page(
                "alertes"
            )
        )

        self.vue.pack(
            fill="both",
            expand=True
        )

        # Actualiser l'affichage
        self.vue.actualiser(donnees)



    def afficher_transactions(self):
        """Afficher la gestion des transactions."""

        self.vue = VueTransactions(
            self.contenu,
            on_ajouter=self.ajouter_transaction,
            on_modifier=self.modifier_transaction,
            on_supprimer=self.supprimer_transaction
        )

        self.vue.pack(fill="both", expand=True)
        self.actualiser_transactions()

    def afficher_budgets(self):
        """Afficher la gestion des budgets."""

        self.vue = VueBudgets(
            self.contenu,
            on_ajouter=self.ajouter_budget,
            on_modifier=self.modifier_budget,
            on_supprimer=self.supprimer_budget
        )

        self.vue.pack(fill="both", expand=True)
        self.actualiser_budgets()

    def afficher_objectifs(self):
        """Afficher les objectifs d'épargne et le simulateur."""
        self.vue=VueObjectifs(self.contenu,self.ajouter_objectif,self.simuler_depense)
        self.vue.pack(fill="both",expand=True)
        self.vue.actualiser(self.api.appeler("objectifs.lister"))

    def ajouter_objectif(self, donnees):
        """Créer un objectif puis rafraîchir sa liste."""
        self.api.appeler("objectifs.creer",**donnees)
        if self.page_actuelle=="objectifs":
            self.vue.actualiser(self.api.appeler("objectifs.lister"))

    def simuler_depense(self, montant):
        """Projeter l'impact d'une dépense sans la persister."""
        if montant <= 0: raise ValueError("Le montant doit être supérieur à zéro.")
        return self.api.appeler("projection.simuler",montant=montant)

    def afficher_parametres(self):
        """Afficher les paramètres."""

        self.vue = VueParametres(
            self.contenu,
            on_modifier_profil=self.modifier_profil,
            on_changer_mot_de_passe=self.changer_mot_de_passe,
            on_changer_theme=self.changer_theme,
            on_deconnexion=self.deconnecter
        )

        self.vue.pack(fill="both", expand=True)

        self.vue.actualiser(
            self.profil,
            self.theme
        )

    # ---------------------------------------
    # TRANSACTIONS TEMPORAIRES
    # ---------------------------------------

    def ajouter_transaction(self, donnees):
        """Ajouter une transaction persistée."""
        date_iso=datetime.strptime(donnees["date"],"%d/%m/%Y").date().isoformat()
        if donnees["type"] == "Revenu":
            self.api.appeler("revenus.creer",montant=float(donnees["montant"]),date=date_iso,
                             description=donnees["libelle"],statut="recu")
        else:
            categorie=self._categorie(donnees["categorie"])
            budget=next((b for b in self.budgets if b["categorie_id"]==categorie["id"]),None)
            if budget is None: raise ValueError("Créez d'abord un budget pour cette catégorie.")
            self.api.appeler("depenses.creer",budget_id=budget["id"],categorie_id=categorie["id"],
                montant=float(donnees["montant"]),date=date_iso,description=donnees["libelle"],statut="realisee")
        self.charger_donnees()
        self.actualiser_transactions()

    def modifier_transaction(self, identifiant, donnees):
        """Modifier une transaction existante."""

        type_objet,numero=identifiant.split(":",1); date_iso=datetime.strptime(donnees["date"],"%d/%m/%Y").date().isoformat()
        if type_objet=="revenu":
            self.api.appeler("revenus.modifier",id=int(numero),montant=float(donnees["montant"]),
                             date=date_iso,description=donnees["libelle"],statut="recu")
        else:
            categorie=self._categorie(donnees["categorie"]); budget=next(b for b in self.budgets if b["categorie_id"]==categorie["id"])
            self.api.appeler("depenses.modifier",id=int(numero),budget_id=budget["id"],categorie_id=categorie["id"],
                             montant=float(donnees["montant"]),date=date_iso,description=donnees["libelle"],statut="realisee")
        self.charger_donnees()
        self.actualiser_transactions()

    def supprimer_transaction(self, identifiant):
        """Supprimer une transaction en mémoire."""

        type_objet,numero=identifiant.split(":",1)
        self.api.appeler(f"{'revenus' if type_objet=='revenu' else 'depenses'}.supprimer",id=int(numero))
        self.charger_donnees()
        self.actualiser_transactions()

    def actualiser_transactions(self):
        """Transmettre les données à VueTransactions."""

        if self.page_actuelle != "transactions":
            return

        revenus = sum(
            (
                Decimal(str(t["montant"]))
                for t in self.transactions
                if t["type"] == "Revenu"
            ),
            Decimal("0")
        )

        depenses = sum(
            (
                Decimal(str(t["montant"]))
                for t in self.transactions
                if t["type"] == "Dépense"
            ),
            Decimal("0")
        )

        resume = {
            "revenus": revenus,
            "depenses": depenses,
            "solde": revenus - depenses
        }

        self.vue.definir_categories(
            [b["categorie"] for b in self.budgets]
        )

        self.vue.actualiser(
            self.transactions,
            resume
        )


    # ---------------------------------------
    # ALERTES
    # ---------------------------------------

    def obtenir_alertes(self):
        """Préparer les états des budgets du mois."""

        alertes = []

        for budget in self.calculer_budgets_affichage():
            categorie = budget["categorie"]

            pourcentage = max(
                0,
                float(budget["progression"]) * 100
            )

            # ROUGE : risques et dépassements
            if pourcentage >= 90:
                niveau = "risque"

                if pourcentage > 100:
                    message = (
                        f"Le budget {categorie} est dépassé ! "
                        f"Vous avez utilisé {pourcentage:.1f} % "
                        "de votre budget mensuel."
                    )

                elif pourcentage >= 100:
                    message = (
                        f"Le budget {categorie} a atteint "
                        "100 % de sa limite mensuelle."
                    )

                else:
                    message = (
                        f"Le budget {categorie} est utilisé à "
                        f"{pourcentage:.1f} %. "
                        "Il reste peu de marge avant le dépassement."
                    )

            # ORANGE : attention
            elif pourcentage >= 80:
                niveau = "attention"

                message = (
                    f"Le budget {categorie} est utilisé à "
                    f"{pourcentage:.1f} %. "
                    "Il approche de sa limite mensuelle."
                )

            # VERT : informations
            elif pourcentage >= 50:
                niveau = "information"

                message = (
                    f"Le budget {categorie} est utilisé à "
                    f"{pourcentage:.1f} %. "
                    "Plus de la moitié du budget est consommée."
                )

            # GRIS : normal
            else:
                niveau = "normal"

                message = (
                    f"Le budget {categorie} est utilisé à "
                    f"{pourcentage:.1f} %. "
                    "La consommation est normale."
                )

            alertes.append({
                "id": budget["id"],
                "titre": f"Budget {categorie}",
                "categorie": categorie,
                "type": niveau,
                "message": message,
                "pourcentage": pourcentage,
                "statut": "active"
            })

        return alertes



    def afficher_alertes(self):
        """Afficher la page des alertes."""

        self.vue = VueAlertes(
            self.contenu,
            on_retour=lambda: self.afficher_page("dashboard")
        )
        self.vue.pack(fill="both", expand=True)
        self.vue.actualiser(self.obtenir_alertes())



    # ---------------------------------------
    # BUDGETS TEMPORAIRES
    # ---------------------------------------

    def ajouter_budget(self, categorie, plafond):
        """Ajouter un budget mensuel persistant."""
        classement=self._categorie(categorie); maintenant=datetime.now()
        self.api.appeler("budgets.creer",annee=maintenant.year,mois=maintenant.month,
                         categorie_id=classement["id"],montant_alloue=float(plafond),obligatoire=False)
        self.charger_donnees()
        self.actualiser_budgets()

    def modifier_budget(
        self,
        identifiant,
        categorie,
        plafond
    ):
        """Modifier un budget existant."""

        classement=self._categorie(categorie); maintenant=datetime.now()
        self.api.appeler("budgets.modifier",id=int(identifiant),annee=maintenant.year,mois=maintenant.month,
                         categorie_id=classement["id"],montant_alloue=float(plafond),obligatoire=False)
        self.charger_donnees()
        self.actualiser_budgets()

    def supprimer_budget(self, identifiant):
        """Supprimer un budget en mémoire."""

        self.api.appeler("budgets.supprimer",id=int(identifiant)); self.charger_donnees()
        self.actualiser_budgets()

    def calculer_budgets_affichage(self):
        """Préparer les données de présentation des budgets."""

        resultat = []

        mois_actuel = datetime.now().strftime("%m/%Y")

        for budget in self.budgets:
            plafond = budget["plafond"]

            depense = sum(
                (
                    Decimal(str(t["montant"]))
                    for t in self.transactions
                    if (
                        t["type"] == "Dépense"
                        and t["categorie"] == budget["categorie"]
                        and str(t["date"])[3:] == mois_actuel
                    )
                ),
                Decimal("0")
            )

            restant = plafond - depense

            progression = (
                float(depense / plafond)
                if plafond > 0 else 0
            )

            alerte = None

            if progression >= 0.90:
                alerte = "risque"
            elif progression >= 0.80:
                alerte = "attention"
            elif progression >= 0.50:
                alerte = "information"
            else:
                alerte = "normal"

            resultat.append({
                "id": budget["id"],
                "categorie": budget["categorie"],
                "plafond": plafond,
                "depense": depense,
                "restant": restant,
                "progression": progression,
                "alerte": alerte
            })

        return resultat

    def actualiser_budgets(self):
        """Transmettre les données à VueBudgets."""

        if self.page_actuelle != "budgets":
            return

        budgets = self.calculer_budgets_affichage()

        total = sum(
            (b["plafond"] for b in budgets),
            Decimal("0")
        )

        depense = sum(
            (b["depense"] for b in budgets),
            Decimal("0")
        )

        resume = {
            "total": total,
            "depense": depense,
            "restant": total - depense
        }

        self.vue.actualiser(budgets, resume)



    # ---------------------------------------
    # FACTURES TEMPORAIRES
    # ---------------------------------------

    def afficher_factures(self):
        """Afficher la page des factures."""

        self.vue = VueFactures(
            self.contenu,
            on_ajouter=self.ajouter_facture,
            on_supprimer=self.supprimer_facture
        )

        self.vue.pack(fill="both", expand=True)
        self.actualiser_factures()

    def ajouter_facture(self, donnees):
        """Ajouter une facture en mémoire."""

        facture = dict(donnees)
        facture["id"] = str(uuid4())

        self.factures.append(facture)
        self.actualiser_factures()

    def supprimer_facture(self, identifiant):
        """Retirer une facture de la liste."""

        self.factures = [
            facture for facture in self.factures
            if facture["id"] != identifiant
        ]

        self.actualiser_factures()

    def actualiser_factures(self):
        """Transmettre les factures à leur interface."""

        if self.page_actuelle != "factures":
            return

        self.vue.actualiser(self.factures)



    # ---------------------------------------
    # PARAMÈTRES
    # ---------------------------------------

    def modifier_profil(self, donnees):
        """Modifier temporairement le profil."""

        self.profil.update(donnees)

        if self.label_utilisateur is not None:
            self.label_utilisateur.configure(
                text=self.nom_utilisateur()
            )

    def changer_mot_de_passe(self, ancien, nouveau):
        """Signaler que la fonction n'est pas disponible."""

        if self.page_actuelle == "parametres":
            self.vue.afficher_erreur(
                "securite",
                "Le changement de mot de passe nécessite "
                "un serveur d'authentification."
            )

    def changer_theme(self, valeur):
        """Enregistrer temporairement la préférence."""

        self.theme = valeur

        modes = {
            "Clair": "light",
            "Sombre": "dark",
            "Système": "system"
        }

        ctk.set_appearance_mode(modes[valeur])

    # ---------------------------------------
    # DÉCONNEXION
    # ---------------------------------------

    def deconnecter(self):
        """Terminer la session serveur et vider l'affichage local."""

        self.api.deconnecter()

        self.transactions.clear()
        self.budgets.clear()
        self.factures.clear()
        self.profil.clear()

        self.theme = "Clair"
        ctk.set_appearance_mode("light")

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
