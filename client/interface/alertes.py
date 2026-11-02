
"""Écran des alertes côté client."""

import customtkinter as ctk


class VueAlertes(ctk.CTkFrame):
    """Présenter les alertes budgétaires.

    Cette classe ne calcule pas les seuils budgétaires
    et ne modifie pas les données financières.
    """

    def __init__(self, master, on_retour=None):
        super().__init__(master, fg_color="#F5F3EF")

        self.on_retour = on_retour
        self.alertes = []

        self.vert = "#00634F"
        self.blanc = "#FFFFFF"
        self.texte = "#172326"
        self.gris = "#777777"
        self.orange = "#D99520"
        self.rouge = "#C94C4C"

        self._construire_interface()

    def _construire_interface(self):
        """Construire l'écran des alertes."""

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

        # Résumé des alertes
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
            resume, "Alertes actives"
        )

        self.total_attention = self._creer_carte(
            resume, "Budgets à surveiller"
        )

        self.total_depassees = self._creer_carte(
            resume, "Budgets dépassés"
        )

        # Filtres
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
                "Actives",
                "Résolues",
                "Attention",
                "Dépassement"
            ],
            fg_color=self.vert,
            button_color="#004D3E",
            command=lambda valeur: self._afficher_alertes()
        )
        self.filtre.pack(side="left")
        self.filtre.set("Actives")

        # Liste des alertes
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
        """Recevoir et afficher les alertes."""

        self.alertes = list(alertes)

        actives = [
            a for a in self.alertes
            if a.get("statut", "active") == "active"
        ]

        attention = [
            a for a in actives
            if a.get("type") == "attention"
        ]

        depassees = [
            a for a in actives
            if a.get("type") == "depasse"
        ]

        self.total_actives.configure(
            text=str(len(actives))
        )

        self.total_attention.configure(
            text=str(len(attention))
        )

        self.total_depassees.configure(
            text=str(len(depassees))
        )

        self._afficher_alertes()

    def _afficher_alertes(self):
        """Afficher les alertes selon le filtre."""

        for widget in self.liste_alertes.winfo_children():
            widget.destroy()

        filtre = self.filtre.get()
        resultat = []

        for alerte in self.alertes:
            statut = alerte.get("statut", "active")
            type_alerte = alerte.get("type", "")

            if filtre == "Actives" and statut != "active":
                continue

            if filtre == "Résolues" and statut != "resolue":
                continue

            if filtre == "Attention" and (
                statut != "active"
                or type_alerte != "attention"
            ):
                continue

            if filtre == "Dépassement" and (
                statut != "active"
                or type_alerte != "depasse"
            ):
                continue

            resultat.append(alerte)

        if not resultat:
            ctk.CTkLabel(
                self.liste_alertes,
                text="Aucune alerte à afficher.",
                font=("Arial", 14),
                text_color=self.gris
            ).pack(pady=60)
            return

        for alerte in resultat:
            self._creer_alerte(alerte)

    def _creer_alerte(self, alerte):
        """Créer une carte pour une alerte."""

        type_alerte = alerte.get("type", "attention")
        statut = alerte.get("statut", "active")

        if statut == "resolue":
            couleur = self.gris
            fond = "#F2F2F2"
        elif type_alerte == "depasse":
            couleur = self.rouge
            fond = "#FCE8E8"
        else:
            couleur = self.orange
            fond = "#FFF2DA"

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

        symbole = "!" if statut == "active" else "✓"

        ctk.CTkLabel(
            contenu,
            text=symbole,
            width=40,
            height=40,
            corner_radius=8,
            fg_color=fond,
            text_color=couleur,
            font=("Arial", 20, "bold")
        ).pack(side="left", padx=(0, 15))

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
            text=alerte.get("titre", "Alerte"),
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
            wraplength=450
        ).pack(fill="x", pady=(5, 0))

        ctk.CTkButton(
            contenu,
            text="Détails",
            width=80,
            fg_color=self.vert,
            hover_color="#004D3E",
            command=lambda a=alerte: self.afficher_details(a)
        ).pack(side="right", padx=5)

    def afficher_details(self, alerte):
        """Afficher les détails d'une alerte."""

        fenetre = ctk.CTkToplevel(self)
        fenetre.title("Détails de l'alerte")
        fenetre.geometry("450x360")
        fenetre.configure(fg_color="#F5F3EF")
        fenetre.resizable(False, False)
        fenetre.transient(self.winfo_toplevel())
        fenetre.grab_set()

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
            text=alerte.get("titre", "Alerte"),
            font=("Arial", 20, "bold"),
            text_color=self.texte,
            wraplength=360
        ).pack(pady=(25, 15))

        ctk.CTkLabel(
            carte,
            text=alerte.get("message", ""),
            font=("Arial", 13),
            text_color=self.texte,
            wraplength=360,
            justify="center"
        ).pack(padx=20, pady=10)

        categorie = alerte.get("categorie", "")
        if categorie:
            ctk.CTkLabel(
                carte,
                text=f"Catégorie : {categorie}",
                text_color=self.gris
            ).pack(pady=5)

        statut = alerte.get("statut", "active")

        ctk.CTkLabel(
            carte,
            text=(
                "Statut : Résolue"
                if statut == "resolue"
                else "Statut : Active"
            ),
            text_color=self.gris
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

        self.alertes = []
        self.actualiser([])
