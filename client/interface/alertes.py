
"""Écran des alertes côté client."""

import customtkinter as ctk


class VueAlertes(ctk.CTkFrame):
    """Présenter les états et alertes budgétaires.

    Cette classe ne calcule pas les seuils budgétaires
    et ne modifie pas les données financières.
    """

    NIVEAUX = {
        "normal": {
            "nom": "Normal",
            "couleur": "#89949C",
            "fond": "#F0F2F4",
            "symbole": "✓"
        },
        "information": {
            "nom": "Informations",
            "couleur": "#16A34A",
            "fond": "#E5F5EA",
            "symbole": "i"
        },
        "attention": {
            "nom": "Attention",
            "couleur": "#D99520",
            "fond": "#FFF2DA",
            "symbole": "!"
        },
        "risque": {
            "nom": "Risques et dépassement",
            "couleur": "#C94C4C",
            "fond": "#FCE8E8",
            "symbole": "!"
        }
    }

    def __init__(self, master, on_retour=None):
        super().__init__(master, fg_color="#F5F3EF")

        self.on_retour = on_retour
        self.alertes = []

        self.vert = "#00634F"
        self.blanc = "#FFFFFF"
        self.texte = "#172326"
        self.gris = "#777777"

        self._construire_interface()

    def _construire_interface(self):
        """Construire l'interface des alertes."""

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
            text="Alertes budgétaires",
            font=("Arial", 26, "bold"),
            text_color=self.texte
        ).pack(side="left")

        ctk.CTkButton(
            entete,
            text="Retour au tableau de bord",
            fg_color=self.vert,
            hover_color="#004D3E",
            command=self.retour_dashboard
        ).pack(side="right")

        # Cartes de résumé
        resume = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        resume.pack(
            fill="x",
            padx=20,
            pady=(0, 15)
        )

        self.total_actives = self._creer_carte(
            resume,
            "Alertes actives"
        )

        self.total_attention = self._creer_carte(
            resume,
            "Budgets à surveiller"
        )

        self.total_risques = self._creer_carte(
            resume,
            "Risques et dépassements"
        )

        # Zone des filtres
        zone_filtres = ctk.CTkFrame(
            self,
            fg_color=self.blanc,
            corner_radius=10
        )
        zone_filtres.pack(
            fill="x",
            padx=25,
            pady=(0, 15)
        )

        ctk.CTkLabel(
            zone_filtres,
            text="Afficher :",
            text_color=self.texte
        ).pack(
            side="left",
            padx=(15, 10),
            pady=15
        )

        self.filtre = ctk.CTkOptionMenu(
            zone_filtres,
            values=[
                "Toutes",
                "Normal",
                "Informations",
                "Attention",
                "Risques et dépassement"
            ],
            width=220,
            fg_color=self.vert,
            button_color="#004D3E",
            command=self._changer_filtre
        )
        self.filtre.pack(side="left", pady=12)
        self.filtre.set("Toutes")

        # Compteur des résultats filtrés
        self.label_resultats = ctk.CTkLabel(
            zone_filtres,
            text="0 budget",
            text_color=self.gris
        )
        self.label_resultats.pack(
            side="right",
            padx=20
        )

        # Liste défilante
        self.liste_alertes = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.liste_alertes.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 20)
        )

        self._afficher_alertes()

    def _creer_carte(self, parent, titre):
        """Créer une carte de statistiques."""

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
            text_color=self.gris,
            font=("Arial", 12)
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 5)
        )

        valeur = ctk.CTkLabel(
            carte,
            text="0",
            font=("Arial", 24, "bold"),
            text_color=self.texte
        )
        valeur.pack(
            anchor="w",
            padx=15,
            pady=(0, 15)
        )

        return valeur

    def actualiser(self, alertes):
        """Recevoir les états budgétaires à afficher.

        Chaque élément contient notamment :
            id, titre, message, categorie,
            type, pourcentage, statut.
        """

        self.alertes = list(alertes)

        attention = sum(
            1 for a in self.alertes
            if a.get("type") == "attention"
        )

        risques = sum(
            1 for a in self.alertes
            if a.get("type") == "risque"
        )

        self.total_actives.configure(
            text=str(attention + risques)
        )

        self.total_attention.configure(
            text=str(attention)
        )

        self.total_risques.configure(
            text=str(risques)
        )

        self._afficher_alertes()

    def _changer_filtre(self, valeur):
        """Réafficher la liste après sélection."""

        self._afficher_alertes()

    def _afficher_alertes(self):
        """Filtrer et afficher les budgets."""

        for widget in self.liste_alertes.winfo_children():
            widget.destroy()

        filtre = self.filtre.get()

        filtres = {
            "Toutes": None,
            "Normal": "normal",
            "Informations": "information",
            "Attention": "attention",
            "Risques et dépassement": "risque"
        }

        niveau_selectionne = filtres.get(filtre)

        resultat = [
            alerte
            for alerte in self.alertes
            if (
                niveau_selectionne is None
                or alerte.get("type") == niveau_selectionne
            )
        ]

        nombre = len(resultat)

        self.label_resultats.configure(
            text=(
                f"{nombre} budget"
                if nombre == 1
                else f"{nombre} budgets"
            )
        )

        if not resultat:
            ctk.CTkLabel(
                self.liste_alertes,
                text="Aucun budget à afficher.",
                font=("Arial", 14),
                text_color=self.gris
            ).pack(pady=60)
            return

        ordre = {
            "risque": 0,
            "attention": 1,
            "information": 2,
            "normal": 3
        }

        resultat.sort(
            key=lambda a: (
                ordre.get(a.get("type"), 4),
                -float(a.get("pourcentage", 0))
            )
        )

        for alerte in resultat:
            self._creer_alerte(alerte)

    def _creer_alerte(self, alerte):
        """Créer une carte pour un état budgétaire."""

        niveau = alerte.get("type", "normal")
        style = self.NIVEAUX.get(
            niveau,
            self.NIVEAUX["normal"]
        )

        couleur = style["couleur"]

        carte = ctk.CTkFrame(
            self.liste_alertes,
            fg_color=self.blanc,
            corner_radius=10,
            border_width=1,
            border_color="#E5E5E5"
        )
        carte.pack(fill="x", pady=6)

        contenu = ctk.CTkFrame(
            carte,
            fg_color="transparent"
        )
        contenu.pack(
            fill="x",
            padx=18,
            pady=15
        )

        # Icône colorée
        ctk.CTkLabel(
            contenu,
            text=style["symbole"],
            width=42,
            height=42,
            corner_radius=8,
            fg_color=style["fond"],
            text_color=couleur,
            font=("Arial", 20, "bold")
        ).pack(
            side="left",
            padx=(0, 15)
        )

        informations = ctk.CTkFrame(
            contenu,
            fg_color="transparent"
        )
        informations.pack(
            side="left",
            fill="both",
            expand=True
        )

        ctk.CTkLabel(
            informations,
            text=alerte.get("titre", "Budget"),
            font=("Arial", 15, "bold"),
            text_color=self.texte,
            anchor="w"
        ).pack(fill="x")

        ctk.CTkLabel(
            informations,
            text=alerte.get("message", ""),
            font=("Arial", 12),
            text_color=self.gris,
            anchor="w",
            justify="left",
            wraplength=500
        ).pack(
            fill="x",
            pady=(5, 8)
        )

        # Pourcentage et barre de progression
        pourcentage = float(
            alerte.get("pourcentage", 0)
        )

        ligne = ctk.CTkFrame(
            informations,
            fg_color="transparent"
        )
        ligne.pack(fill="x")

        ctk.CTkLabel(
            ligne,
            text=style["nom"],
            font=("Arial", 12, "bold"),
            text_color=couleur
        ).pack(side="left")

        ctk.CTkLabel(
            ligne,
            text=f"{pourcentage:.1f} %",
            font=("Arial", 12, "bold"),
            text_color=couleur
        ).pack(side="right")

        progression = ctk.CTkProgressBar(
            informations,
            height=8,
            corner_radius=5,
            fg_color="#E5E7EB",
            progress_color=couleur
        )
        progression.pack(
            fill="x",
            pady=(6, 0)
        )

        progression.set(
            max(0, min(pourcentage / 100, 1))
        )

        ctk.CTkButton(
            contenu,
            text="Détails",
            width=85,
            fg_color=self.vert,
            hover_color="#004D3E",
            command=lambda a=alerte: self.afficher_details(a)
        ).pack(
            side="right",
            padx=(20, 0)
        )

    def afficher_details(self, alerte):
        """Afficher les informations d'un budget."""

        fenetre = ctk.CTkToplevel(self)
        fenetre.title("Détails du budget")
        fenetre.geometry("470x390")
        fenetre.configure(fg_color="#F5F3EF")
        fenetre.resizable(False, False)
        fenetre.transient(self.winfo_toplevel())
        fenetre.grab_set()

        niveau = alerte.get("type", "normal")
        style = self.NIVEAUX.get(
            niveau,
            self.NIVEAUX["normal"]
        )

        carte = ctk.CTkFrame(
            fenetre,
            fg_color=self.blanc,
            corner_radius=12
        )
        carte.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        ctk.CTkLabel(
            carte,
            text=alerte.get("titre", "Budget"),
            font=("Arial", 20, "bold"),
            text_color=self.texte,
            wraplength=390
        ).pack(pady=(25, 15))

        ctk.CTkLabel(
            carte,
            text=style["nom"],
            font=("Arial", 14, "bold"),
            text_color=style["couleur"]
        ).pack(pady=5)

        ctk.CTkLabel(
            carte,
            text=alerte.get("message", ""),
            font=("Arial", 13),
            text_color=self.texte,
            wraplength=390,
            justify="center"
        ).pack(padx=20, pady=10)

        ctk.CTkLabel(
            carte,
            text=(
                "Catégorie : "
                + str(alerte.get("categorie", ""))
            ),
            text_color=self.gris
        ).pack(pady=5)

        ctk.CTkLabel(
            carte,
            text=(
                f"Budget consommé : "
                f"{float(alerte.get('pourcentage', 0)):.1f} %"
            ),
            text_color=self.texte,
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        ctk.CTkButton(
            carte,
            text="Fermer",
            fg_color=self.vert,
            command=fenetre.destroy
        ).pack(pady=20)

    def retour_dashboard(self):
        """Demander le retour au tableau de bord."""

        if self.on_retour:
            self.on_retour()

    def vider(self):
        """Réinitialiser l'affichage."""

        self.actualiser([])
