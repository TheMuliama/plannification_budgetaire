"""Écran des objectifs et versements d'épargne."""

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

    def __init__(self, master, on_ajouter, on_alimenter):
        super().__init__(master, fg_color=self.FOND)
        self.on_ajouter = on_ajouter
        self.on_alimenter = on_alimenter
        self.champs = {}
        self._construire_interface()

    def _construire_interface(self):
        zone = ctk.CTkScrollableFrame(self, fg_color="transparent")
        zone.pack(fill="both", expand=True, padx=25, pady=20)

        ctk.CTkLabel(
            zone, text="Épargne", font=("Arial", 26, "bold"),
            text_color=self.TEXTE,
        ).pack(anchor="w")
        ctk.CTkLabel(
            zone,
            text="Planifiez vos objectifs et alimentez-les avec votre solde disponible.",
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
        self._ouvrir_calendrier_pour(self.champs["date_cible"], "Choisir une date cible")

    def _ouvrir_calendrier_pour(self, champ, titre):
        fenetre = ctk.CTkToplevel(self)
        fenetre.title(titre)
        fenetre.resizable(False, False)
        fenetre.transient(self.winfo_toplevel())
        centrer_fenetre(fenetre, self.winfo_toplevel(), 300, 300)
        fenetre.grab_set()
        try:
            initiale = datetime.strptime(champ.get().strip(), "%d/%m/%Y")
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
            champ.delete(0, "end")
            champ.insert(0, calendrier.get_date())
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

    def _ouvrir_versement(self, objectif):
        fenetre=ctk.CTkToplevel(self)
        fenetre.title("Ajouter de l'argent")
        fenetre.resizable(False,False)
        fenetre.transient(self.winfo_toplevel())
        centrer_fenetre(fenetre,self.winfo_toplevel(),420,330)
        fenetre.grab_set()
        ctk.CTkLabel(
            fenetre,text=f"Alimenter « {objectif['nom']} »",font=("Arial",20,"bold"),
            text_color=self.TEXTE,
        ).pack(pady=(25,18))
        montant=ctk.CTkEntry(fenetre,width=320,height=40,placeholder_text="Montant du versement (€)")
        montant.pack(pady=7)
        zone_date=ctk.CTkFrame(fenetre,fg_color="transparent")
        zone_date.pack(pady=7)
        champ_date=ctk.CTkEntry(zone_date,width=270,height=40,placeholder_text="Date (JJ/MM/AAAA)")
        champ_date.insert(0,datetime.now().strftime("%d/%m/%Y")); champ_date.pack(side="left")
        ctk.CTkButton(
            zone_date,text="📅",width=40,height=40,fg_color="#E8F2EE",text_color=self.VERT,
            hover_color="#D6E9E1",
            command=lambda:self._ouvrir_calendrier_pour(champ_date,"Date du versement"),
        ).pack(side="left",padx=(8,0))
        message=ctk.CTkLabel(fenetre,text="",text_color=self.ROUGE,wraplength=340)
        message.pack(pady=4)

        def valider():
            try:
                valeur=self._montant(montant,obligatoire=True)
                date_versement=datetime.strptime(champ_date.get().strip(),"%d/%m/%Y").date()
                if date_versement > datetime.now().date():
                    raise ValueError("Un versement ne peut pas être daté dans le futur.")
                self.on_alimenter(objectif["id"],valeur,date_versement.isoformat())
            except (ValueError,ConnectionError,OSError) as erreur:
                message.configure(text=str(erreur)); return
            fenetre.destroy()

        ctk.CTkButton(
            fenetre,text="Ajouter à l'épargne",width=320,height=42,fg_color=self.VERT,
            hover_color=self.VERT_FONCE,command=valider,
        ).pack(pady=8)

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
            entete=ctk.CTkFrame(carte,fg_color="transparent")
            entete.pack(fill="x",padx=16,pady=(12,2))
            ctk.CTkLabel(
                entete, text=objectif["nom"], font=("Arial", 14, "bold"), text_color=self.TEXTE
            ).pack(side="left")
            if actuel < cible:
                ctk.CTkButton(
                    entete,text="+ Ajouter de l'argent",height=30,fg_color=self.VERT,
                    hover_color=self.VERT_FONCE,
                    command=lambda o=objectif:self._ouvrir_versement(o),
                ).pack(side="right")
            date_affichee = datetime.fromisoformat(objectif["date_cible"]).strftime("%d/%m/%Y")
            texte = f"{actuel:,.2f} € sur {cible:,.2f} € · cible le {date_affichee}"
            ctk.CTkLabel(
                carte, text=texte.replace(",", " ").replace(".", ","),
                text_color=self.SECONDAIRE,
            ).pack(anchor="w", padx=16)
            def euros(valeur):
                return f"{float(valeur):,.2f} €".replace(",", " ").replace(".", ",")

            indicateurs = ctk.CTkFrame(carte, fg_color="transparent")
            indicateurs.pack(fill="x", padx=16, pady=(9, 2))
            elements = (
                ("Reste à épargner", euros(objectif.get("montant_restant", cible-actuel))),
                ("Épargne minimale / mois", euros(objectif.get("montant_periodique_recommande", 0))),
                ("Revenu utilisable / mois", euros(objectif.get("revenu_utilisable", 0))),
                ("Épargne maximale ce mois", euros(objectif.get("epargne_maximale", 0))),
            )
            for titre, valeur in elements:
                bloc = ctk.CTkFrame(indicateurs, fg_color="#F7F8F7", corner_radius=7)
                bloc.pack(side="left", fill="x", expand=True, padx=(0, 6))
                ctk.CTkLabel(
                    bloc, text=titre, text_color=self.SECONDAIRE, font=("Arial", 10)
                ).pack(anchor="w", padx=9, pady=(7, 1))
                ctk.CTkLabel(
                    bloc, text=valeur, text_color=self.TEXTE, font=("Arial", 12, "bold")
                ).pack(anchor="w", padx=9, pady=(0, 7))
            if not objectif.get("objectif_atteignable", True):
                ctk.CTkLabel(
                    carte,
                    text="⚠ L'épargne disponible ce mois est inférieure au minimum nécessaire.",
                    text_color=self.ROUGE,
                ).pack(anchor="w", padx=16, pady=(5, 0))
            barre = ctk.CTkProgressBar(carte, progress_color=self.VERT, height=10)
            barre.pack(fill="x", padx=16, pady=(8, 14))
            barre.set(progression)
