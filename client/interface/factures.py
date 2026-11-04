"""Interface locale de gestion des factures (démonstration en mémoire)."""

from datetime import datetime
from pathlib import Path
import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Callable, Optional

import customtkinter as ctk
from tkcalendar import Calendar


def centrer_fenetre(fenetre, parent, largeur, hauteur):
    """Centrer une fenêtre par rapport à son parent."""

    parent.update_idletasks()

    x = parent.winfo_rootx() + (parent.winfo_width() - largeur) // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - hauteur) // 2

    fenetre.geometry(f"{largeur}x{hauteur}+{max(0, x)}+{max(0, y)}")


class VueFactures(ctk.CTkFrame):
    FOND = "#F5F3EF"
    BLANC = "#FFFFFF"
    TEXTE = "#19252B"
    SECONDAIRE = "#79808A"
    VERT = "#09644F"
    BORDURE = "#E9E7E3"

    def __init__(self, parent, *, on_ajouter: Optional[Callable] = None,
                 on_supprimer: Optional[Callable] = None, **kwargs):
        super().__init__(parent, fg_color=self.FOND, **kwargs)
        self.on_ajouter = on_ajouter
        self.on_supprimer = on_supprimer
        self.factures = []
        self.fichier_selectionne = ""
        self._construire()

    def _texte(self, parent, texte, taille=12, couleur=None, gras=False, **kwargs):
        return ctk.CTkLabel(parent, text=texte,
                            font=ctk.CTkFont(size=taille, weight="bold" if gras else "normal"),
                            text_color=couleur or self.TEXTE, anchor="w", **kwargs)


    def _construire(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        zone = ctk.CTkScrollableFrame(self, fg_color="transparent")
        zone.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        zone.grid_columnconfigure(0, weight=1)

        self._texte(zone, "Mes factures", 24, gras=True).grid(row=0, column=0, sticky="w")
        self._texte(zone, "Retrouvez et consultez vos justificatifs.", 12,
                    self.SECONDAIRE).grid(row=1, column=0, sticky="w", pady=(2, 16))

        formulaire = ctk.CTkFrame(zone, fg_color=self.BLANC, corner_radius=10,
                                  border_width=1, border_color=self.BORDURE)
        formulaire.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        formulaire.grid_columnconfigure((0, 1), weight=1)
        self._texte(formulaire, "Ajouter une facture", 15, gras=True).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(14, 10))

        self.champ_nom = ctk.CTkEntry(formulaire, placeholder_text="Nom de la facture")
        self.champ_nom.grid(row=1, column=0, sticky="ew", padx=(16, 8), pady=5)
        zone_date = ctk.CTkFrame(formulaire, fg_color="transparent")
        zone_date.grid(row=1, column=1, sticky="ew", padx=(8, 16), pady=5)
        zone_date.grid_columnconfigure(0, weight=1)

        self.champ_date = ctk.CTkEntry(zone_date, placeholder_text="Date (JJ/MM/AAAA)")
        self.champ_date.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.champ_date.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(
            zone_date, text="📅", width=40,
            fg_color="#E8F2EE", text_color=self.VERT,
            hover_color="#D6E9E1", command=self._ouvrir_calendrier
        ).grid(row=0, column=1, padx=(6, 0))

        fichier = ctk.CTkFrame(formulaire, fg_color="transparent")
        fichier.grid(row=2, column=0, columnspan=2, sticky="ew", padx=16, pady=(8, 4))
        ctk.CTkButton(fichier, text="Choisir un document", width=155,
                      fg_color="#E8F2EE", text_color=self.VERT,
                      hover_color="#D6E9E1", command=self._choisir_fichier).pack(side="left")
        self.label_fichier = self._texte(fichier, "Aucun fichier sélectionné", 11, self.SECONDAIRE)
        self.label_fichier.pack(side="left", padx=12, fill="x", expand=True)
        ctk.CTkButton(formulaire, text="+ Ajouter la facture", fg_color=self.VERT,
                      hover_color="#074C3D", command=self._ajouter).grid(
            row=3, column=0, columnspan=2, sticky="e", padx=16, pady=(8, 16))

        liste = ctk.CTkFrame(zone, fg_color=self.BLANC, corner_radius=10,
                             border_width=1, border_color=self.BORDURE)
        liste.grid(row=3, column=0, sticky="ew")
        liste.grid_columnconfigure(0, weight=1)
        entete = ctk.CTkFrame(liste, fg_color="transparent")
        entete.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 10))
        self._texte(entete, "Factures enregistrées", 15, gras=True).pack(side="left")
        self.recherche = ctk.CTkEntry(entete, placeholder_text="Rechercher une facture...", width=240)
        self.recherche.pack(side="right")
        self.recherche.bind("<KeyRelease>", lambda _event: self._afficher_liste())
        self.filtre = ctk.CTkOptionMenu(
            liste,
            values=["Date (récentes d'abord)", "Date (anciennes d'abord)", "Nom (A-Z)", "Nom (Z-A)"],
            fg_color=self.VERT,
            button_color=self.VERT,
            width=210,
            command=lambda _valeur: self._afficher_liste()
        )
        self.filtre.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 8))
        self.zone_liste = ctk.CTkFrame(liste, fg_color="transparent")
        self.zone_liste.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))
        self._afficher_liste()

    def _ouvrir_calendrier(self):
        """Choisir une date sans empêcher la saisie manuelle."""
        fenetre = ctk.CTkToplevel(self)
        fenetre.title("Choisir une date")
        fenetre.resizable(False, False)
        fenetre.transient(self.winfo_toplevel())
        centrer_fenetre(fenetre, self.winfo_toplevel(), 240, 210)

        try:
            date_initiale = datetime.strptime(self.champ_date.get().strip(), "%d/%m/%Y")
        except ValueError:
            date_initiale = datetime.now()

        calendrier = Calendar(
            fenetre,
            selectmode="day",
            year=date_initiale.year,
            month=date_initiale.month,
            day=date_initiale.day,
            date_pattern="dd/mm/yyyy",
            locale="fr_FR",
            background=self.VERT,
            foreground="white",
            selectbackground=self.VERT,
            selectforeground="white",
            headersbackground="#E8F2EE",
            headersforeground=self.TEXTE,
        )
        calendrier.pack(padx=16, pady=(16, 10))

        def valider():
            self.champ_date.delete(0, "end")
            self.champ_date.insert(0, calendrier.get_date())
            fenetre.destroy()

        ctk.CTkButton(
            fenetre, text="Choisir cette date", fg_color=self.VERT,
            hover_color="#074C3D", command=valider
        ).pack(padx=16, pady=(0, 16), fill="x")

        fenetre.after(100, fenetre.lift)

    def _choisir_fichier(self):
        chemin = filedialog.askopenfilename(
            parent=self.winfo_toplevel(), title="Choisir une facture",
            filetypes=[("Documents PDF et images", "*.pdf *.png *.jpg *.jpeg *.webp"),
                       ("Tous les fichiers", "*.*")])
        if chemin:
            self.fichier_selectionne = chemin
            self.label_fichier.configure(text=Path(chemin).name)

    def _ajouter(self):
        nom = self.champ_nom.get().strip()
        date_texte = self.champ_date.get().strip()
        if not nom or not self.fichier_selectionne:
            messagebox.showwarning(
                "Champs manquants", "Renseignez le nom et choisissez un document.", parent=self
            )
            return
        try:
            datetime.strptime(date_texte, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror(
                "Date invalide", "Saisissez une date valide au format JJ/MM/AAAA.", parent=self
            )
            return
        if not Path(self.fichier_selectionne).is_file():
            messagebox.showerror(
                "Fichier introuvable", "Le document sélectionné n'existe plus.", parent=self
            )
            return
        if callable(self.on_ajouter):
            self.on_ajouter({
                "nom": nom,
                "date": date_texte,
                "fichier": self.fichier_selectionne
            })
            self.champ_nom.delete(0, "end")
            self.fichier_selectionne = ""
            self.label_fichier.configure(text="Aucun fichier sélectionné")

    def actualiser(self, factures):
        self.factures = list(factures)
        self._afficher_liste()

    def _afficher_liste(self):
        for enfant in self.zone_liste.winfo_children():
            enfant.destroy()

        terme = self.recherche.get().strip().casefold()
        visibles = [
            f for f in self.factures
            if terme in f.get("nom", "").casefold()
        ]

        tri = self.filtre.get()
        if tri == "Nom (A-Z)":
            visibles.sort(key=lambda f: f.get("nom", "").casefold())
        elif tri == "Nom (Z-A)":
            visibles.sort(key=lambda f: f.get("nom", "").casefold(), reverse=True)
        else:
            def cle_date(facture):
                try:
                    return datetime.strptime(facture.get("date", ""), "%d/%m/%Y")
                except (ValueError, TypeError):
                    return datetime.min

            visibles.sort(
                key=cle_date,
                reverse=(tri != "Date (anciennes d'abord)")
            )

        if not visibles:
            self._texte(
                self.zone_liste, "Aucune facture trouvée.", 12, self.SECONDAIRE
            ).pack(pady=25)
            return

        for facture in visibles:
            ligne = ctk.CTkFrame(self.zone_liste, fg_color="#F8F9F8", corner_radius=8)
            ligne.pack(fill="x", pady=4)
            info = ctk.CTkFrame(ligne, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=12, pady=10)
            self._texte(info, facture.get("nom", ""), 12, gras=True).pack(anchor="w")
            self._texte(
                info, facture.get("date", ""), 11, self.SECONDAIRE
            ).pack(anchor="w", pady=(3, 0))
            ctk.CTkButton(
                ligne, text="Ouvrir", width=65, fg_color=self.VERT,
                command=lambda f=facture: self._ouvrir(f)
            ).pack(side="right", padx=(3, 12))
            ctk.CTkButton(
                ligne, text="Supprimer", width=85, fg_color="#B93838",
                hover_color="#922D2D",
                command=lambda f=facture: self._supprimer(f)
            ).pack(side="right", padx=3)

    def _ouvrir(self, facture):
        chemin = Path(facture.get("fichier", ""))
        if not chemin.is_file():
            messagebox.showerror("Fichier introuvable", "Le fichier original a été déplacé ou supprimé.", parent=self)
            return
        try:
            if sys.platform == "win32":
                os.startfile(str(chemin))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(chemin)])
            else:
                subprocess.Popen(["xdg-open", str(chemin)])
        except (OSError, subprocess.SubprocessError) as erreur:
            messagebox.showerror("Ouverture impossible", str(erreur), parent=self)

    def _supprimer(self, facture):
        if not messagebox.askyesno("Supprimer la facture",
                                   f"Supprimer « {facture.get('nom', '')} » de la liste ?\nLe fichier original sera conservé.",
                                   parent=self):
            return
        if callable(self.on_supprimer):
            self.on_supprimer(facture["id"])

