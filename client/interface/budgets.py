
"""Écran de gestion des budgets côté client."""

import customtkinter as ctk
from tkinter import messagebox


def centrer_fenetre(fenetre, parent, largeur, hauteur):
    """Centrer une fenêtre par rapport à son parent."""

    parent.update_idletasks()

    x = parent.winfo_rootx() + (parent.winfo_width() - largeur) // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - hauteur) // 2

    fenetre.geometry(f"{largeur}x{hauteur}+{max(0, x)}+{max(0, y)}")


class VueBudgets(ctk.CTkFrame):
    """Présenter la gestion des budgets.

    Cette classe ne calcule ni ne modifie elle-même
    les règles budgétaires.
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

        # Données reçues de l'extérieur
        self.budgets = []

        # Couleurs
        self.vert = "#00634F"
        self.vert_fonce = "#004D3E"
        self.beige = "#F5F3EF"
        self.blanc = "#FFFFFF"
        self.texte = "#172326"
        self.gris = "#777777"
        self.orange = "#D99520"
        self.rouge = "#C94C4C"

        self._construire_interface()

    def _construire_interface(self):
        """Construire l'interface des budgets."""

        # En-tête
        self.entete = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.entete.pack(
            fill="x",
            padx=25,
            pady=(25, 15)
        )

        ctk.CTkLabel(
            self.entete,
            text="Gestion des budgets",
            font=("Arial", 26, "bold"),
            text_color=self.texte
        ).pack(side="left")

        ctk.CTkButton(
            self.entete,
            text="+ Ajouter un budget",
            width=170,
            height=40,
            corner_radius=8,
            fg_color=self.vert,
            hover_color=self.vert_fonce,
            command=self.ouvrir_ajout
        ).pack(side="right")

        # Zone de résumé
        self.resume = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.resume.pack(
            fill="x",
            padx=25,
            pady=(0, 15)
        )

        self.carte_total = self._creer_carte(
            self.resume,
            "Budget total",
            "0,00 €"
        )

        self.carte_depense = self._creer_carte(
            self.resume,
            "Total dépensé",
            "0,00 €"
        )

        self.carte_restant = self._creer_carte(
            self.resume,
            "Budget restant",
            "0,00 €"
        )

        # Titre de la liste
        ctk.CTkLabel(
            self,
            text="Budgets par catégorie",
            font=("Arial", 18, "bold"),
            text_color=self.texte
        ).pack(
            anchor="w",
            padx=25,
            pady=(10, 10)
        )

        # Liste défilante
        self.liste_budgets = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.liste_budgets.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 20)
        )

        self._afficher_budgets()

    def _creer_carte(self, parent, titre, valeur):
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
            text=valeur,
            font=("Arial", 22, "bold"),
            text_color=self.texte
        )
        montant.pack(
            anchor="w",
            padx=15,
            pady=(0, 15)
        )

        return montant

    def actualiser(self, budgets, resume=None):
        """Actualiser les informations affichées.

        budgets : liste de dictionnaires contenant :
            id, categorie, plafond, depense,
            progression, restant, alerte.

        resume : dictionnaire contenant :
            total, depense, restant.

        Les calculs sont effectués à l'extérieur.
        """

        self.budgets = list(budgets)

        if resume is not None:
            self.carte_total.configure(
                text=self._formater_montant(
                    resume.get("total", 0)
                )
            )

            self.carte_depense.configure(
                text=self._formater_montant(
                    resume.get("depense", 0)
                )
            )

            self.carte_restant.configure(
                text=self._formater_montant(
                    resume.get("restant", 0)
                )
            )
        else:
            self.carte_total.configure(text="—")
            self.carte_depense.configure(text="—")
            self.carte_restant.configure(text="—")

        self._afficher_budgets()

    def _formater_montant(self, montant):
        """Formater un montant pour l'affichage."""

        return (
            f"{float(montant):,.2f} €"
            .replace(",", " ")
            .replace(".", ",")
        )

    def _afficher_budgets(self):
        """Afficher les budgets reçus."""

        # Nettoyer la liste
        for widget in self.liste_budgets.winfo_children():
            widget.destroy()

        if not self.budgets:
            ctk.CTkLabel(
                self.liste_budgets,
                text="Aucun budget défini pour le moment.",
                font=("Arial", 14),
                text_color=self.gris
            ).pack(pady=50)

            return

        for budget in self.budgets:
            self._creer_ligne_budget(budget)

    def _creer_ligne_budget(self, budget):
        """Créer la carte d'un budget."""

        carte = ctk.CTkFrame(
            self.liste_budgets,
            fg_color=self.blanc,
            corner_radius=10,
            border_width=1,
            border_color="#E5E5E5"
        )
        carte.pack(
            fill="x",
            pady=7
        )

        # Partie supérieure
        haut = ctk.CTkFrame(
            carte,
            fg_color="transparent"
        )
        haut.pack(
            fill="x",
            padx=20,
            pady=(15, 5)
        )

        categorie = budget.get(
            "categorie",
            "Sans catégorie"
        )

        ctk.CTkLabel(
            haut,
            text=categorie,
            font=("Arial", 16, "bold"),
            text_color=self.texte
        ).pack(side="left")

        # Bouton supprimer
        ctk.CTkButton(
            haut,
            text="Supprimer",
            width=85,
            height=30,
            fg_color="#FCE8E8",
            hover_color="#F5D0D0",
            text_color=self.rouge,
            command=lambda b=budget: self.supprimer_budget(b)
        ).pack(side="right", padx=5)

        # Bouton modifier
        ctk.CTkButton(
            haut,
            text="Modifier",
            width=85,
            height=30,
            fg_color="#E8F3EF",
            hover_color="#D3E8DF",
            text_color=self.vert,
            command=lambda b=budget: self.ouvrir_modification(b)
        ).pack(side="right", padx=5)

        # Montants
        depense = budget.get("depense", 0)
        plafond = budget.get("plafond", 0)
        restant = budget.get("restant", 0)

        texte_montant = (
            f"{self._formater_montant(depense)} / "
            f"{self._formater_montant(plafond)}"
        )

        ctk.CTkLabel(
            carte,
            text=texte_montant,
            font=("Arial", 13),
            text_color=self.gris
        ).pack(
            anchor="w",
            padx=20,
            pady=(5, 5)
        )

        # Progression fournie par la logique externe
        progression = budget.get("progression", 0)

        # Limiter uniquement l'affichage de la barre
        progression_visuelle = max(
            0,
            min(1, float(progression))
        )

        couleur = self.vert

        if budget.get("alerte") == "attention":
            couleur = self.orange

        elif budget.get("alerte") == "depasse":
            couleur = self.rouge

        barre = ctk.CTkProgressBar(
            carte,
            height=10,
            progress_color=couleur,
            fg_color="#EAEAEA"
        )
        barre.pack(
            fill="x",
            padx=20,
            pady=5
        )
        barre.set(progression_visuelle)

        # Budget restant
        ctk.CTkLabel(
            carte,
            text=(
                "Restant : "
                f"{self._formater_montant(restant)}"
            ),
            font=("Arial", 12),
            text_color=self.gris
        ).pack(
            anchor="w",
            padx=20,
            pady=(5, 15)
        )

    def ouvrir_ajout(self):
        """Ouvrir le formulaire d'ajout."""

        self._ouvrir_formulaire()

    def ouvrir_modification(self, budget):
        """Ouvrir le formulaire de modification."""

        self._ouvrir_formulaire(budget)

    def _ouvrir_formulaire(self, budget=None):
        """Afficher le formulaire d'ajout ou modification."""

        modification = budget is not None

        fenetre = ctk.CTkToplevel(self)
        fenetre.title(
            "Modifier un budget"
            if modification
            else "Ajouter un budget"
        )

        centrer_fenetre(fenetre, self.winfo_toplevel(), 430, 400)
        fenetre.resizable(False, False)
        fenetre.configure(fg_color=self.beige)
        fenetre.transient(self.winfo_toplevel())
        fenetre.grab_set()

        titre = (
            "Modifier un budget"
            if modification
            else "Nouveau budget"
        )

        ctk.CTkLabel(
            fenetre,
            text=titre,
            font=("Arial", 22, "bold"),
            text_color=self.texte
        ).pack(pady=(25, 20))

        # Champ catégorie
        ctk.CTkLabel(
            fenetre,
            text="Catégorie",
            text_color=self.texte
        ).pack(anchor="w", padx=45)

        champ_categorie = ctk.CTkEntry(
            fenetre,
            width=340,
            height=40,
            placeholder_text="Nom de la catégorie"
        )
        champ_categorie.pack(pady=(5, 15))

        # Champ plafond
        ctk.CTkLabel(
            fenetre,
            text="Plafond mensuel (€)",
            text_color=self.texte
        ).pack(anchor="w", padx=45)

        champ_plafond = ctk.CTkEntry(
            fenetre,
            width=340,
            height=40,
            placeholder_text="Exemple : 200"
        )
        champ_plafond.pack(pady=(5, 15))

        if modification:
            champ_categorie.insert(
                0,
                str(budget.get("categorie", ""))
            )

            champ_plafond.insert(
                0,
                str(budget.get("plafond", ""))
            )

        message = ctk.CTkLabel(
            fenetre,
            text="",
            text_color=self.rouge,
            wraplength=340
        )
        message.pack(pady=5)

        def valider():
            categorie = champ_categorie.get().strip()
            texte_plafond = (
                champ_plafond.get()
                .strip()
                .replace(",", ".")
            )

            if not categorie or not texte_plafond:
                message.configure(
                    text="Veuillez remplir tous les champs."
                )
                return

            try:
                plafond = float(texte_plafond)
            except ValueError:
                message.configure(
                    text="Veuillez saisir un montant valide."
                )
                return

            if plafond <= 0:
                message.configure(
                    text="Le plafond doit être supérieur à zéro."
                )
                return

            # Transmettre les informations
            if modification:
                if self.on_modifier is None:
                    message.configure(
                        text="Modification non configurée."
                    )
                    return

                try:
                    self.on_modifier(budget.get("id"), categorie, plafond)
                except (ConnectionError, OSError, ValueError) as erreur:
                    message.configure(text=str(erreur))
                    return

            else:
                if self.on_ajouter is None:
                    message.configure(
                        text="Ajout non configuré."
                    )
                    return

                try:
                    self.on_ajouter(categorie, plafond)
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

    def supprimer_budget(self, budget):
        """Demander la suppression d'un budget."""

        confirmation = messagebox.askyesno(
            "Confirmation",
            "Voulez-vous vraiment supprimer le budget "
            f"« {budget.get('categorie', '')} » ?",
            parent=self.winfo_toplevel()
        )

        if not confirmation:
            return

        if self.on_supprimer:
            self.on_supprimer(
                budget.get("id")
            )
        else:
            messagebox.showwarning(
                "Action indisponible",
                "La suppression n'est pas configurée.",
                parent=self.winfo_toplevel()
            )

    def vider(self):
        """Réinitialiser les données affichées."""

        self.actualiser(
            budgets=[],
            resume={
                "total": 0,
                "depense": 0,
                "restant": 0
            }
        )

