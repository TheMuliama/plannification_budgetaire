
"""Écran des transactions côté client."""

from datetime import datetime
from decimal import Decimal, InvalidOperation
from tkinter import messagebox

import customtkinter as ctk
from tkcalendar import Calendar


def centrer_fenetre(fenetre, parent, largeur, hauteur):
    """Centrer une fenêtre par rapport à son parent."""

    parent.update_idletasks()

    x = parent.winfo_rootx() + (parent.winfo_width() - largeur) // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - hauteur) // 2

    fenetre.geometry(f"{largeur}x{hauteur}+{max(0, x)}+{max(0, y)}")


class VueTransactions(ctk.CTkFrame):
    """Présenter les revenus et dépenses.

    Cette classe ne contient pas de logique de gestion financière.
    """

    def __init__(
        self,
        master,
        on_ajouter=None,
        on_modifier=None,
        on_supprimer=None
    ):
        super().__init__(master, fg_color="#F5F3EF")

        # Fonctions de rappel
        self.on_ajouter = on_ajouter
        self.on_modifier = on_modifier
        self.on_supprimer = on_supprimer

        # Données fournies par la logique externe
        self.transactions = []
        self.categories = []

        # Couleurs
        self.vert = ("#00634F", "#087D65")
        self.vert_fonce = ("#004D3E", "#05634F")
        self.beige = ("#F5F3EF", "#121A1D")
        self.blanc = ("#FFFFFF", "#202B30")
        self.texte = ("#172326", "#F5F5F5")
        self.gris = ("#777777", "#AAB5B9")
        self.rouge = ("#C94C4C", "#FF7777")

        self._construire_interface()

    def _construire_interface(self):
        """Construire l'interface des transactions."""

        # En-tête
        entete = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        entete.pack(
            fill="x",
            padx=25,
            pady=(25, 15)
        )

        ctk.CTkLabel(
            entete,
            text="Transactions",
            font=("Arial", 26, "bold"),
            text_color=self.texte
        ).pack(side="left")

        ctk.CTkButton(
            entete,
            text="+ Ajouter une transaction",
            width=190,
            height=40,
            corner_radius=8,
            fg_color=self.vert,
            hover_color=self.vert_fonce,
            command=self.ouvrir_ajout
        ).pack(side="right")

        # Cartes récapitulatives
        resume = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        resume.pack(
            fill="x",
            padx=20,
            pady=(0, 15)
        )

        self.carte_revenus = self._creer_carte(
            resume,
            "Total des revenus"
        )

        self.carte_depenses = self._creer_carte(
            resume,
            "Total des dépenses"
        )

        self.carte_solde = self._creer_carte(
            resume,
            "Solde"
        )

        # Filtres
        filtres = ctk.CTkFrame(
            self,
            fg_color=self.blanc,
            corner_radius=10
        )
        filtres.pack(
            fill="x",
            padx=25,
            pady=(0, 15)
        )

        self.recherche = ctk.CTkEntry(
            filtres,
            width=280,
            height=38,
            placeholder_text="Rechercher une transaction..."
        )
        self.recherche.pack(
            side="left",
            padx=15,
            pady=15
        )
        self.recherche.bind(
            "<KeyRelease>",
            lambda event: self._afficher_transactions()
        )

        self.filtre_type = ctk.CTkOptionMenu(
            filtres,
            values=[
                "Toutes",
                "Dépense",
                "Revenu"
            ],
            width=150,
            fg_color=self.vert,
            button_color=self.vert_fonce,
            command=lambda valeur: self._afficher_transactions()
        )
        self.filtre_type.pack(
            side="left",
            padx=5
        )
        self.filtre_type.set("Toutes")

        # Titre de la liste
        ctk.CTkLabel(
            self,
            text="Historique des transactions",
            font=("Arial", 18, "bold"),
            text_color=self.texte
        ).pack(
            anchor="w",
            padx=25,
            pady=(5, 10)
        )

        # Liste défilante
        self.liste_transactions = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.liste_transactions.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 20)
        )

        self._afficher_transactions()

    def _creer_carte(self, parent, titre):
        """Créer une carte récapitulative."""

        carte = ctk.CTkFrame(
            parent,
            fg_color=self.blanc,
            corner_radius=10,
            border_width=1,
            border_color="#E5E5E5"
        )
        carte.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5
        )

        ctk.CTkLabel(
            carte,
            text=titre,
            font=("Arial", 12),
            text_color=self.gris
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 5)
        )

        montant = ctk.CTkLabel(
            carte,
            text="0,00 €",
            font=("Arial", 22, "bold"),
            text_color=self.texte
        )
        montant.pack(
            anchor="w",
            padx=15,
            pady=(0, 15)
        )

        return montant

    def _formater_montant(self, montant):
        """Formater un montant reçu pour l'affichage."""

        texte = f"{Decimal(str(montant)):,.2f}"

        return (
            texte.replace(",", " ")
            .replace(".", ",")
            + " €"
        )

    def actualiser(self, transactions, resume=None):
        """Actualiser les transactions affichées.

        Chaque transaction contient :
            id, date, libelle, type,
            categorie, montant.

        resume contient :
            revenus, depenses, solde.

        Les calculs sont effectués à l'extérieur.
        """

        self.transactions = list(transactions)

        if resume is not None:
            self.carte_revenus.configure(
                text=self._formater_montant(
                    resume.get("revenus", 0)
                )
            )

            self.carte_depenses.configure(
                text=self._formater_montant(
                    resume.get("depenses", 0)
                )
            )

            self.carte_solde.configure(
                text=self._formater_montant(
                    resume.get("solde", 0)
                )
            )
        else:
            # Résumé non fourni
            self.carte_revenus.configure(text="—")
            self.carte_depenses.configure(text="—")
            self.carte_solde.configure(text="—")

        self._afficher_transactions()

    def definir_categories(self, categories):
        """Recevoir les catégories disponibles."""

        self.categories = list(categories)

    def _afficher_transactions(self):
        """Afficher les transactions selon les filtres."""

        # Nettoyer la liste
        for widget in self.liste_transactions.winfo_children():
            widget.destroy()

        recherche = self.recherche.get().strip().lower()
        filtre = self.filtre_type.get()

        transactions_filtrees = []

        for transaction in self.transactions:
            libelle = str(
                transaction.get("libelle", "")
            ).lower()

            categorie = str(
                transaction.get("categorie", "")
            ).lower()

            type_transaction = transaction.get(
                "type",
                "Dépense"
            )

            # Filtre de recherche
            if (
                recherche not in libelle
                and recherche not in categorie
            ):
                continue

            # Filtre par type
            if (
                filtre != "Toutes"
                and type_transaction != filtre
            ):
                continue

            transactions_filtrees.append(transaction)

        if not transactions_filtrees:
            ctk.CTkLabel(
                self.liste_transactions,
                text="Aucune transaction à afficher.",
                font=("Arial", 14),
                text_color=self.gris
            ).pack(pady=50)

            return

        for transaction in transactions_filtrees:
            self._creer_ligne_transaction(transaction)

    def _creer_ligne_transaction(self, transaction):
        """Créer une ligne de transaction."""

        ligne = ctk.CTkFrame(
            self.liste_transactions,
            fg_color=self.blanc,
            corner_radius=10,
            border_width=1,
            border_color="#E5E5E5"
        )
        ligne.pack(
            fill="x",
            pady=5
        )

        contenu = ctk.CTkFrame(
            ligne,
            fg_color="transparent"
        )
        contenu.pack(
            fill="x",
            padx=15,
            pady=12
        )

        # Date
        ctk.CTkLabel(
            contenu,
            text=str(transaction.get("date", "")),
            width=100,
            anchor="w",
            text_color=self.gris
        ).pack(side="left", padx=5)

        # Libellé
        ctk.CTkLabel(
            contenu,
            text=str(transaction.get("libelle", "")),
            width=200,
            anchor="w",
            text_color=self.texte,
            font=("Arial", 13, "bold")
        ).pack(side="left", padx=5)

        # Catégorie
        ctk.CTkLabel(
            contenu,
            text=str(transaction.get("categorie", "")),
            width=120,
            anchor="w",
            text_color=self.gris
        ).pack(side="left", padx=5)

        # Type et montant
        type_transaction = transaction.get(
            "type",
            "Dépense"
        )

        couleur = (
            self.vert
            if type_transaction == "Revenu"
            else self.rouge
        )

        signe = (
            "+"
            if type_transaction == "Revenu"
            else "-"
        )

        montant = self._formater_montant(
            transaction.get("montant", 0)
        )

        ctk.CTkLabel(
            contenu,
            text=f"{signe}{montant}",
            width=110,
            text_color=couleur,
            font=("Arial", 13, "bold")
        ).pack(side="left", padx=5)

        # Boutons d'action
        ctk.CTkButton(
            contenu,
            text="Modifier",
            width=75,
            height=30,
            fg_color="#E8F3EF",
            hover_color="#D3E8DF",
            text_color=self.vert,
            command=lambda t=transaction: (
                self.ouvrir_modification(t)
            )
        ).pack(side="right", padx=3)

        ctk.CTkButton(
            contenu,
            text="Supprimer",
            width=80,
            height=30,
            fg_color="#FCE8E8",
            hover_color="#F5D0D0",
            text_color=self.rouge,
            command=lambda t=transaction: (
                self.supprimer_transaction(t)
            )
        ).pack(side="right", padx=3)

    def ouvrir_ajout(self):
        """Ouvrir le formulaire d'ajout."""

        self._ouvrir_formulaire()

    def ouvrir_modification(self, transaction):
        """Ouvrir le formulaire de modification."""

        self._ouvrir_formulaire(transaction)

    def _ouvrir_formulaire(self, transaction=None):
        """Afficher le formulaire de transaction."""

        modification = transaction is not None

        fenetre = ctk.CTkToplevel(self)
        fenetre.title(
            "Modifier une transaction"
            if modification
            else "Ajouter une transaction"
        )
        #fenetre.geometry("450x540")
        
        centrer_fenetre(fenetre, self.winfo_toplevel(), 450, 560)
        fenetre.resizable(False, False)
        fenetre.configure(fg_color=self.beige)
        fenetre.transient(self.winfo_toplevel())
        fenetre.grab_set()

        ctk.CTkLabel(
            fenetre,
            text=(
                "Modifier une transaction"
                if modification
                else "Nouvelle transaction"
            ),
            font=("Arial", 22, "bold"),
            text_color=self.texte
        ).pack(pady=(20, 15))

        # Type
        ctk.CTkLabel(
            fenetre,
            text="Type de transaction",
            text_color=self.texte
        ).pack(anchor="w", padx=55)

        champ_type = ctk.CTkOptionMenu(
            fenetre,
            values=["Dépense", "Revenu"],
            width=340,
            fg_color=self.vert,
            button_color=self.vert_fonce
        )
        champ_type.pack(pady=(5, 12))

        # Libellé
        champ_libelle = ctk.CTkEntry(
            fenetre,
            width=340,
            height=40,
            placeholder_text="Libellé"
        )
        champ_libelle.pack(pady=8)

        # Montant
        champ_montant = ctk.CTkEntry(
            fenetre,
            width=340,
            height=40,
            placeholder_text="Montant (€)"
        )
        champ_montant.pack(pady=8)

        # Catégorie
        ctk.CTkLabel(
            fenetre,
            text="Catégorie",
            text_color=self.texte
        ).pack(anchor="w", padx=55)

        valeurs_categories = (
            self.categories
            if self.categories
            else ["Sans catégorie"]
        )

        champ_categorie = ctk.CTkOptionMenu(
            fenetre,
            values=valeurs_categories,
            width=340,
            fg_color=self.vert,
            button_color=self.vert_fonce
        )
        champ_categorie.pack(pady=(5, 12))

        # Date : saisie manuelle ou sélection dans un calendrier
        zone_date = ctk.CTkFrame(fenetre, fg_color="transparent", width=340)
        zone_date.pack(pady=8)

        champ_date = ctk.CTkEntry(
            zone_date,
            width=290,
            height=40,
            placeholder_text="Date (JJ/MM/AAAA)"
        )
        champ_date.pack(side="left")

        def ouvrir_calendrier():
            """Afficher un calendrier pour le champ date du formulaire."""
            calendrier_fenetre = ctk.CTkToplevel(fenetre)
            calendrier_fenetre.title("Choisir une date")
            calendrier_fenetre.resizable(False, False)
            calendrier_fenetre.transient(fenetre)
            centrer_fenetre(calendrier_fenetre, fenetre, 240, 210)

            try:
                date_initiale = datetime.strptime(
                    champ_date.get().strip(), "%d/%m/%Y"
                )
            except ValueError:
                date_initiale = datetime.now()

            calendrier = Calendar(
                calendrier_fenetre,
                selectmode="day",
                year=date_initiale.year,
                month=date_initiale.month,
                day=date_initiale.day,
                date_pattern="dd/mm/yyyy",
                locale="fr_FR",
                background="#00634F",
                foreground="white",
                selectbackground="#00634F",
                selectforeground="white",
                headersbackground="#E8F2EE",
                headersforeground="#172326"
            )
            calendrier.pack(padx=16, pady=(16, 10))

            def choisir_date():
                champ_date.delete(0, "end")
                champ_date.insert(0, calendrier.get_date())
                calendrier_fenetre.destroy()

            ctk.CTkButton(
                calendrier_fenetre,
                text="Choisir cette date",
                fg_color=self.vert,
                hover_color=self.vert_fonce,
                command=choisir_date
            ).pack(fill="x", padx=16, pady=(0, 16))

            calendrier_fenetre.after(100, calendrier_fenetre.lift)

        ctk.CTkButton(
            zone_date,
            text="📅",
            width=40,
            height=40,
            fg_color="#E8F2EE",
            text_color="#00634F",
            hover_color="#D6E9E1",
            command=ouvrir_calendrier
        ).pack(side="left", padx=(10, 0))

        # Préremplissage lors d'une modification
        if modification:
            champ_type.set(
                transaction.get("type", "Dépense")
            )

            champ_libelle.insert(
                0,
                str(transaction.get("libelle", ""))
            )

            champ_montant.insert(
                0,
                str(transaction.get("montant", ""))
            )

            categorie = transaction.get(
                "categorie",
                "Sans catégorie"
            )

            if categorie not in valeurs_categories:
                champ_categorie.configure(
                    values=valeurs_categories + [categorie]
                )

            champ_categorie.set(categorie)

            champ_date.insert(
                0,
                str(transaction.get("date", ""))
            )
        else:
            champ_date.insert(
                0,
                datetime.now().strftime("%d/%m/%Y")
            )

        # Message d'erreur
        message = ctk.CTkLabel(
            fenetre,
            text="",
            text_color=self.rouge
        )
        message.pack(pady=5)

        def valider():
            """Valider la saisie et transmettre la demande."""

            type_transaction = champ_type.get()
            libelle = champ_libelle.get().strip()
            texte_montant = (
                champ_montant.get()
                .strip()
                .replace(",", ".")
            )
            categorie = champ_categorie.get()
            date = champ_date.get().strip()

            if not libelle or not texte_montant or not date:
                message.configure(
                    text="Veuillez remplir tous les champs."
                )
                return

            # Validation du montant
            try:
                montant = Decimal(texte_montant)
            except InvalidOperation:
                message.configure(
                    text="Montant invalide."
                )
                return

            if not montant.is_finite() or montant <= 0:
                message.configure(
                    text="Le montant doit être supérieur à zéro."
                )
                return

            # Validation de la date
            try:
                datetime.strptime(date, "%d/%m/%Y")
            except ValueError:
                message.configure(
                    text="Date invalide (JJ/MM/AAAA)."
                )
                return

            # Données à transmettre
            donnees = {
                "type": type_transaction,
                "libelle": libelle,
                "montant": montant,
                "categorie": categorie,
                "date": date
            }

            if modification:
                if self.on_modifier is None:
                    message.configure(
                        text="Modification non configurée."
                    )
                    return

                try:
                    self.on_modifier(transaction.get("id"), donnees)
                except (ConnectionError, OSError, ValueError, StopIteration) as erreur:
                    message.configure(text=str(erreur))
                    return

            else:
                if self.on_ajouter is None:
                    message.configure(
                        text="Ajout non configuré."
                    )
                    return

                try:
                    self.on_ajouter(donnees)
                except (ConnectionError, OSError, ValueError) as erreur:
                    message.configure(text=str(erreur))
                    return

            fenetre.destroy()

        ctk.CTkButton(
            fenetre,
            text="Enregistrer",
            width=340,
            height=42,
            fg_color=self.vert,
            hover_color=self.vert_fonce,
            command=valider
        ).pack(pady=10)

    def supprimer_transaction(self, transaction):
        """Demander la suppression d'une transaction."""

        confirmation = messagebox.askyesno(
            "Confirmation",
            "Voulez-vous supprimer cette transaction ?",
            parent=self.winfo_toplevel()
        )

        if not confirmation:
            return

        if self.on_supprimer:
            self.on_supprimer(
                transaction.get("id")
            )
        else:
            messagebox.showwarning(
                "Action indisponible",
                "La suppression n'est pas configurée.",
                parent=self.winfo_toplevel()
            )

    def vider(self):
        """Réinitialiser l'affichage."""

        self.actualiser(
            transactions=[],
            resume={
                "revenus": 0,
                "depenses": 0,
                "solde": 0
            }
        )



