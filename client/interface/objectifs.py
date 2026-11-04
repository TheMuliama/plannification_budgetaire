"""Écran des objectifs d'épargne et de la projection budgétaire."""

from datetime import datetime
from decimal import Decimal, InvalidOperation

import customtkinter as ctk
from tkcalendar import Calendar

from interface.transactions import centrer_fenetre


class VueObjectifs(ctk.CTkFrame):
    """Présenter les objectifs d'épargne avec le style commun de l'application."""

    FOND = "#F5F3EF"
    BLANC = "#FFFFFF"
    TEXTE = "#172326"
    SECONDAIRE = "#777777"
    VERT = "#00634F"
    VERT_FONCE = "#004D3E"
    BORDURE = "#E5E5E5"
    ROUGE = "#C94C4C"

    def __init__(self, master, on_ajouter, on_simuler):
        super().__init__(master, fg_color=self.FOND)
        self.on_ajouter = on_ajouter
        self.on_simuler = on_simuler
        self.champs = {}
        self._construire_interface()

    def _construire_interface(self):
        zone = ctk.CTkScrollableFrame(self, fg_color="transparent")
        zone.pack(fill="both", expand=True, padx=25, pady=20)

        ctk.CTkLabel(
            zone, text="Épargne et projection", font=("Arial", 26, "bold"),
            text_color=self.TEXTE,
        ).pack(anchor="w")
        ctk.CTkLabel(
            zone,
            text="Planifiez vos objectifs et mesurez l'impact d'une dépense avant de la réaliser.",
            text_color=self.SECONDAIRE,
        ).pack(anchor="w", pady=(3, 16))

        formulaire = self._carte(zone)
        formulaire.pack(fill="x", pady=(0, 15))
        formulaire.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(
            formulaire, text="Nouvel objectif", font=("Arial", 17, "bold"),
            text_color=self.TEXTE,
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(16, 10))

        self._ajouter_champ(formulaire, "nom", "Nom de l'objectif", 1, 0)
        self._ajouter_champ(formulaire, "montant_cible", "Montant cible (€)", 1, 1)
        self._ajouter_champ(formulaire, "montant_actuel", "Montant déjà épargné (€)", 2, 0)
        self._ajouter_champ(formulaire, "montant_periodique", "Épargne mensuelle prévue (€)", 2, 1)

        zone_date = ctk.CTkFrame(formulaire, fg_color="transparent")
        zone_date.grid(row=3, column=0, sticky="ew", padx=(18, 9), pady=7)
        zone_date.grid_columnconfigure(0, weight=1)
        self.champs["date_cible"] = ctk.CTkEntry(
            zone_date, height=40, placeholder_text="Date cible (JJ/MM/AAAA)"
        )
        self.champs["date_cible"].grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(
            zone_date, text="📅", width=40, height=40, fg_color="#E8F2EE",
            text_color=self.VERT, hover_color="#D6E9E1", command=self._ouvrir_calendrier,
        ).grid(row=0, column=1, padx=(8, 0))

        ctk.CTkButton(
            formulaire, text="+ Ajouter l'objectif", height=40, fg_color=self.VERT,
            hover_color=self.VERT_FONCE, command=self._ajouter,
        ).grid(row=3, column=1, sticky="e", padx=(9, 18), pady=7)

        self.message = ctk.CTkLabel(formulaire, text="", text_color=self.ROUGE)
        self.message.grid(row=4, column=0, columnspan=2, sticky="w", padx=18, pady=(0, 12))

        projection = self._carte(zone)
        projection.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(
            projection, text="Simuler une dépense", font=("Arial", 17, "bold"),
            text_color=self.TEXTE,
        ).pack(anchor="w", padx=18, pady=(16, 2))
        ctk.CTkLabel(
            projection,
            text="Cette simulation ne crée aucune transaction et utilise les budgets du mois courant.",
            text_color=self.SECONDAIRE,
        ).pack(anchor="w", padx=18, pady=(0, 10))
        ligne_projection = ctk.CTkFrame(projection, fg_color="transparent")
        ligne_projection.pack(fill="x", padx=18, pady=(0, 16))
        self.montant_projection = ctk.CTkEntry(
            ligne_projection, placeholder_text="Montant de la dépense (€)", width=250, height=40
        )
        self.montant_projection.pack(side="left")
        ctk.CTkButton(
            ligne_projection, text="Simuler l'impact", height=40, fg_color=self.VERT,
            hover_color=self.VERT_FONCE, command=self._simuler,
        ).pack(side="left", padx=10)
        self.resultat = ctk.CTkLabel(
            ligne_projection, text="", text_color=self.TEXTE, font=("Arial", 13, "bold")
        )
        self.resultat.pack(side="left", padx=10)

        ctk.CTkLabel(
            zone, text="Mes objectifs", font=("Arial", 18, "bold"), text_color=self.TEXTE
        ).pack(anchor="w", pady=(2, 8))
        self.liste = ctk.CTkFrame(zone, fg_color="transparent")
        self.liste.pack(fill="x")

    def _carte(self, parent):
        return ctk.CTkFrame(
            parent, fg_color=self.BLANC, corner_radius=10,
            border_width=1, border_color=self.BORDURE,
        )

    def _ajouter_champ(self, parent, cle, indication, ligne, colonne):
        champ = ctk.CTkEntry(parent, placeholder_text=indication, height=40)
        champ.grid(
            row=ligne, column=colonne, sticky="ew",
            padx=(18, 9) if colonne == 0 else (9, 18), pady=7,
        )
        self.champs[cle] = champ

    def _ouvrir_calendrier(self):
        fenetre = ctk.CTkToplevel(self)
        fenetre.title("Choisir une date cible")
        fenetre.resizable(False, False)
        fenetre.transient(self.winfo_toplevel())
        centrer_fenetre(fenetre, self.winfo_toplevel(), 240, 210)
        try:
            initiale = datetime.strptime(self.champs["date_cible"].get().strip(), "%d/%m/%Y")
        except ValueError:
            initiale = datetime.now()
        calendrier = Calendar(
            fenetre, selectmode="day", year=initiale.year, month=initiale.month,
            day=initiale.day, date_pattern="dd/mm/yyyy", locale="fr_FR",
            background=self.VERT, foreground="white", selectbackground=self.VERT,
            selectforeground="white", headersbackground="#E8F2EE", headersforeground=self.TEXTE,
        )
        calendrier.pack(padx=16, pady=(16, 10))

        def choisir():
            self.champs["date_cible"].delete(0, "end")
            self.champs["date_cible"].insert(0, calendrier.get_date())
            fenetre.destroy()

        ctk.CTkButton(
            fenetre, text="Choisir cette date", fg_color=self.VERT,
            hover_color=self.VERT_FONCE, command=choisir,
        ).pack(fill="x", padx=16, pady=(0, 16))
        fenetre.after(100, fenetre.lift)

    @staticmethod
    def _montant(champ, obligatoire=False):
        texte = champ.get().strip().replace(",", ".")
        if not texte and not obligatoire:
            return 0.0
        try:
            montant = Decimal(texte)
        except InvalidOperation as erreur:
            raise ValueError("Saisissez des montants valides.") from erreur
        if not montant.is_finite() or montant < 0 or (obligatoire and montant == 0):
            raise ValueError("Les montants doivent être positifs.")
        return float(montant)

    def _ajouter(self):
        try:
            date_cible = datetime.strptime(
                self.champs["date_cible"].get().strip(), "%d/%m/%Y"
            ).date()
            if date_cible <= datetime.now().date():
                raise ValueError("La date cible doit être postérieure à aujourd'hui.")
            self.on_ajouter({
                "nom": self.champs["nom"].get().strip(),
                "montant_cible": self._montant(self.champs["montant_cible"], obligatoire=True),
                "montant_actuel": self._montant(self.champs["montant_actuel"]),
                "montant_periodique": self._montant(self.champs["montant_periodique"]),
                "date_cible": date_cible.isoformat(),
            })
            for champ in self.champs.values():
                champ.delete(0, "end")
            self.message.configure(text="")
        except (ValueError, ConnectionError, OSError) as erreur:
            self.message.configure(text=str(erreur))

    def _simuler(self):
        try:
            montant = self._montant(self.montant_projection, obligatoire=True)
            resultat = self.on_simuler(montant)
            restant = resultat["budget_restant_projete"]
            texte = f"Budget restant projeté : {restant:,.2f} €"
            self.resultat.configure(
                text=texte.replace(",", " ").replace(".", ","),
                text_color=self.ROUGE if restant < 0 else self.VERT,
            )
            self.message.configure(text="")
        except (ValueError, ConnectionError, OSError) as erreur:
            self.message.configure(text=str(erreur))

    def actualiser(self, objectifs):
        for widget in self.liste.winfo_children():
            widget.destroy()
        if not objectifs:
            ctk.CTkLabel(
                self.liste, text="Aucun objectif enregistré.", text_color=self.SECONDAIRE
            ).pack(pady=25)
            return
        for objectif in objectifs:
            carte = self._carte(self.liste)
            carte.pack(fill="x", pady=5)
            actuel = float(objectif["montant_actuel"])
            cible = float(objectif["montant_cible"])
            progression = min(1.0, actuel / cible if cible else 0.0)
            ctk.CTkLabel(
                carte, text=objectif["nom"], font=("Arial", 14, "bold"), text_color=self.TEXTE
            ).pack(anchor="w", padx=16, pady=(13, 2))
            date_affichee = datetime.fromisoformat(objectif["date_cible"]).strftime("%d/%m/%Y")
            texte = f"{actuel:,.2f} € sur {cible:,.2f} € · cible le {date_affichee}"
            ctk.CTkLabel(
                carte, text=texte.replace(",", " ").replace(".", ","),
                text_color=self.SECONDAIRE,
            ).pack(anchor="w", padx=16)
            barre = ctk.CTkProgressBar(carte, progress_color=self.VERT, height=10)
            barre.pack(fill="x", padx=16, pady=(8, 14))
            barre.set(progression)
