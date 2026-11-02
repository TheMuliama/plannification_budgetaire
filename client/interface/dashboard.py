"""Tableau de bord de présentation côté client.

Ce module ne contient ni accès réseau, ni accès à la base de données,
ni calcul métier. Les indicateurs sont fournis par le reste de l'application.
"""

from datetime import date
from typing import Callable, Optional

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class TableauDeBord(ctk.CTkFrame):
    """Présenter les informations budgétaires au client."""

    FOND = "#F5F3EF"
    BLANC = "#FFFFFF"
    TEXTE = "#19252B"
    SECONDAIRE = "#79808A"
    VERT = "#09644F"
    BORDURE = "#E9E7E3"
    COULEURS = ["#DA7950", "#6C5CC7", "#2D9B78", "#D9A441", "#4A91BC"]

    def __init__(
        self,
        parent,
        *,
        ajouter_depense: Optional[Callable] = None,
        voir_depenses: Optional[Callable] = None,
        voir_alertes: Optional[Callable] = None,
        **kwargs,
    ):
        super().__init__(parent, fg_color=self.FOND, **kwargs)
        self.ajouter_depense = ajouter_depense
        self.voir_depenses = voir_depenses
        self.voir_alertes = voir_alertes
        self.donnees = {}
        self._construire_interface()
        self.actualiser({})

    @staticmethod
    def _euros(valeur):
        """Formater un montant déjà calculé, sans le recalculer."""
        try:
            return f"{float(valeur):,.2f} €".replace(",", " ").replace(".", ",")
        except (ValueError, TypeError):
            return "0,00 €"

    def _texte(self, parent, contenu, taille=12, couleur=None, gras=False, **kwargs):
        return ctk.CTkLabel(
            parent, text=contenu, font=ctk.CTkFont(size=taille, weight="bold" if gras else "normal"),
            text_color=couleur or self.TEXTE, anchor="w", **kwargs
        )

    def _carte(self, parent):
        return ctk.CTkFrame(parent, fg_color=self.BLANC, corner_radius=10,
                            border_width=1, border_color=self.BORDURE)

    def _construire_interface(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.zone = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.zone.grid(row=0, column=0, sticky="nsew")
        self.zone.grid_columnconfigure(0, weight=1)

        entete = ctk.CTkFrame(self.zone, fg_color="transparent")
        entete.grid(row=0, column=0, sticky="ew", pady=(8, 16))
        entete.grid_columnconfigure(0, weight=1)
        self.titre = self._texte(entete, "Bonjour !", 23, gras=True)
        self.titre.grid(row=0, column=0, sticky="w")
        self.sous_titre = self._texte(entete, "", 11, self.SECONDAIRE)
        self.sous_titre.grid(row=1, column=0, sticky="w", pady=(3, 0))
        ctk.CTkButton(entete, text="+ Ajouter une dépense", fg_color=self.VERT,
                      hover_color="#074C3D", height=35, width=165,
                      command=self._ouvrir_ajout).grid(row=0, column=1, rowspan=2, padx=(12, 0))

        indicateurs = ctk.CTkFrame(self.zone, fg_color="transparent")
        indicateurs.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        self.valeurs = {}
        for col, (cle, titre) in enumerate([
            ("budget_mois", "Budget du mois"), ("depense", "Dépensé"),
            ("restant", "Restant"), ("alertes_actives", "Alertes actives")
        ]):
            indicateurs.grid_columnconfigure(col, weight=1, uniform="indicateurs")
            carte = self._carte(indicateurs)
            carte.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 5, 0))
            self._texte(carte, titre, 11, self.SECONDAIRE).pack(anchor="w", padx=16, pady=(13, 4))
            label = self._texte(carte, "0" if cle == "alertes_actives" else "0,00 €",
                                20, self.VERT if cle == "restant" else self.TEXTE, gras=True)
            label.pack(anchor="w", padx=16, pady=(0, 18))
            self.valeurs[cle] = label

        graphiques = ctk.CTkFrame(self.zone, fg_color="transparent")
        graphiques.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        for col in range(3):
            graphiques.grid_columnconfigure(col, weight=1, uniform="graphes")
        self.carte_repartition = self._carte(graphiques)
        self.carte_repartition.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.carte_budgets = self._carte(graphiques)
        self.carte_budgets.grid(row=0, column=1, sticky="nsew", padx=5)
        self.carte_evolution = self._carte(graphiques)
        self.carte_evolution.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        self._texte(self.carte_repartition, "Répartition par catégorie", 13, gras=True).pack(anchor="w", padx=14, pady=(14, 5))
        self._texte(self.carte_budgets, "Budgets par catégorie", 13, gras=True).pack(anchor="w", padx=14, pady=(14, 5))
        self._texte(self.carte_evolution, "Évolution sur 6 mois", 13, gras=True).pack(anchor="w", padx=14, pady=(14, 5))
        self.zone_repartition = ctk.CTkFrame(self.carte_repartition, fg_color="transparent", height=190)
        self.zone_budgets = ctk.CTkScrollableFrame(self.carte_budgets, fg_color="transparent", height=175)
        self.zone_evolution = ctk.CTkFrame(self.carte_evolution, fg_color="transparent", height=190)
        self.zone_repartition.pack(fill="both", expand=True, padx=10, pady=(0, 12))
        self.zone_budgets.pack(fill="both", expand=True, padx=10, pady=(0, 12))
        self.zone_evolution.pack(fill="both", expand=True, padx=10, pady=(0, 12))
        self.canvas_repartition = None
        self.canvas_evolution = None

        bas = ctk.CTkFrame(self.zone, fg_color="transparent")
        bas.grid(row=3, column=0, sticky="nsew")
        bas.grid_columnconfigure(0, weight=3)
        bas.grid_columnconfigure(1, weight=1)
        depenses = self._carte(bas)
        depenses.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        alertes = self._carte(bas)
        alertes.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        haut_depenses = ctk.CTkFrame(depenses, fg_color="transparent")
        haut_depenses.pack(fill="x", padx=14, pady=(12, 5))
        self._texte(haut_depenses, "Dernières dépenses", 13, gras=True).pack(side="left")
        ctk.CTkButton(haut_depenses, text="Voir tout", fg_color="transparent",
                      text_color=self.VERT, hover_color="#EDF5F1", width=65,
                      command=self._ouvrir_depenses).pack(side="right")
        self.zone_depenses = ctk.CTkFrame(depenses, fg_color="transparent")
        self.zone_depenses.pack(fill="both", expand=True, padx=14, pady=(3, 14))
        haut_alertes = ctk.CTkFrame(alertes, fg_color="transparent")
        haut_alertes.pack(fill="x", padx=14, pady=(12, 5))
        self._texte(haut_alertes, "Alertes", 13, gras=True).pack(side="left")
        ctk.CTkButton(haut_alertes, text="Voir", fg_color="transparent", width=45,
                      text_color=self.VERT, hover_color="#EDF5F1",
                      command=self._ouvrir_alertes).pack(side="right")
        self.zone_alertes = ctk.CTkFrame(alertes, fg_color="transparent")
        self.zone_alertes.pack(fill="both", expand=True, padx=14, pady=(3, 14))

    def _vider(self, conteneur):
        for enfant in conteneur.winfo_children():
            enfant.destroy()

    def _etat_vide(self, conteneur, message):
        self._texte(conteneur, message, 11, self.SECONDAIRE, wraplength=180).pack(
            anchor="center", expand=True, pady=35, padx=8)

    def _dessiner_graphique(self, conteneur, valeurs, etiquettes, type_graphique):
        fig = Figure(figsize=(3.1, 2.1), dpi=90, facecolor=self.BLANC)
        axe = fig.add_subplot(111)
        if type_graphique == "camembert":
            axe.pie(valeurs, colors=self.COULEURS[:len(valeurs)], startangle=90,
                    wedgeprops={"width": 0.45})
            axe.legend(etiquettes, loc="center left", bbox_to_anchor=(0.85, 0.5),
                       fontsize=7, frameon=False)
        else:
            axe.bar(range(len(valeurs)), valeurs, color="#B9D1C9", width=0.7)
            axe.set_xticks(range(len(etiquettes)), etiquettes, fontsize=8)
            axe.spines[["top", "right", "left"]].set_visible(False)
            axe.tick_params(axis="y", left=False, labelleft=False)
            axe.tick_params(axis="x", bottom=False)
            for i, v in enumerate(valeurs):
                axe.text(i, v, self._euros(v).replace(" €", ""), ha="center", va="bottom", fontsize=7)
            axe.set_ylim(0, max(valeurs) * 1.25 if max(valeurs) else 1)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=conteneur)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        return canvas

    def actualiser(self, donnees: dict):
        """Actualiser l'interface avec des valeurs déjà préparées.

        Format attendu :
        {
            "prenom": "", "mois": "", "budget_mois": 0, "depense": 0,
            "restant": 0, "alertes_actives": 0,
            "repartition": [{"categorie": "...", "montant": 0}],
            "budgets": [{"categorie": "...", "depense": 0, "plafond": 0, "pourcentage": 0}],
            "evolution": [{"mois": "...", "montant": 0}],
            "dernieres_depenses": [{"date": "...", "libelle": "...", "categorie": "...", "montant": 0}],
            "alertes": [{"message": "..."}]
        }
        """
        self.donnees = donnees or {}
        prenom = self.donnees.get("prenom", "")
        self.titre.configure(text=f"Bonjour {prenom} !" if prenom else "Bonjour !")
        self.sous_titre.configure(text=self.donnees.get("mois") or f"Résumé du {date.today():%m/%Y}")
        for cle, label in self.valeurs.items():
            valeur = self.donnees.get(cle, 0)
            label.configure(text=str(valeur) if cle == "alertes_actives" else self._euros(valeur))

        self._vider(self.zone_repartition)
        repartition = [x for x in self.donnees.get("repartition", []) if x.get("montant", 0) > 0]
        if repartition:
            self.canvas_repartition = self._dessiner_graphique(
                self.zone_repartition, [x["montant"] for x in repartition],
                [x["categorie"] for x in repartition], "camembert")
        else:
            self._etat_vide(self.zone_repartition, "Aucune dépense enregistrée")

        self._vider(self.zone_budgets)
        budgets = self.donnees.get("budgets", [])
        if not budgets:
            self._etat_vide(self.zone_budgets, "Aucun budget défini")
        for element in budgets:
            ligne = ctk.CTkFrame(self.zone_budgets, fg_color="transparent")
            ligne.pack(fill="x", pady=7)
            self._texte(ligne, element.get("categorie", "Sans catégorie"), 11, gras=True).pack(anchor="w")
            self._texte(ligne, f"{self._euros(element.get('depense', 0))} / {self._euros(element.get('plafond', 0))}",
                        10, self.SECONDAIRE).pack(anchor="w")
            pourcentage = max(0, min(100, float(element.get("pourcentage", 0))))
            barre = ctk.CTkProgressBar(ligne, height=6, progress_color=self.VERT)
            barre.pack(fill="x", pady=(5, 0))
            barre.set(pourcentage / 100)

        self._vider(self.zone_evolution)
        evolution = self.donnees.get("evolution", [])
        if evolution:
            self.canvas_evolution = self._dessiner_graphique(
                self.zone_evolution, [x.get("montant", 0) for x in evolution],
                [x.get("mois", "") for x in evolution], "barres")
        else:
            self._etat_vide(self.zone_evolution, "Aucun historique disponible")

        self._vider(self.zone_depenses)
        depenses = self.donnees.get("dernieres_depenses", [])
        if not depenses:
            self._etat_vide(self.zone_depenses, "Aucune dépense pour le moment")
        for depense in depenses[:5]:
            ligne = ctk.CTkFrame(self.zone_depenses, fg_color="transparent")
            ligne.pack(fill="x", pady=5)
            self._texte(ligne, str(depense.get("date", "")), 10, self.SECONDAIRE, width=90).pack(side="left")
            self._texte(ligne, depense.get("libelle", ""), 11).pack(side="left", fill="x", expand=True)
            self._texte(ligne, depense.get("categorie", ""), 10, self.SECONDAIRE).pack(side="left", padx=8)
            self._texte(ligne, self._euros(depense.get("montant", 0)), 11, gras=True).pack(side="right")

        self._vider(self.zone_alertes)
        alertes = self.donnees.get("alertes", [])
        if not alertes:
            self._etat_vide(self.zone_alertes, "Aucune alerte active")
        for alerte in alertes[:4]:
            self._texte(self.zone_alertes, "⚠ " + alerte.get("message", ""),
                        11, "#9A650B", wraplength=210).pack(fill="x", pady=6)

    def _ouvrir_ajout(self):
        if callable(self.ajouter_depense):
            self.ajouter_depense()

    def _ouvrir_depenses(self):
        if callable(self.voir_depenses):
            self.voir_depenses()

    def _ouvrir_alertes(self):
        if callable(self.voir_alertes):
            self.voir_alertes()
