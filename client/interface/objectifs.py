"""Écran MVP des objectifs d'épargne et de projection."""
import customtkinter as ctk

class VueObjectifs(ctk.CTkFrame):
    def __init__(self, master, on_ajouter, on_simuler):
        super().__init__(master,fg_color="#F5F3EF")
        self.on_ajouter=on_ajouter; self.on_simuler=on_simuler
        ctk.CTkLabel(self,text="Objectifs d'épargne",font=("Arial",26,"bold")).pack(anchor="w",padx=30,pady=(25,15))
        formulaire=ctk.CTkFrame(self,fg_color="white"); formulaire.pack(fill="x",padx=30,pady=10)
        self.champs={}
        for cle,texte in (("nom","Nom de l'objectif"),("montant_cible","Montant cible"),
                          ("montant_actuel","Montant actuel"),("montant_periodique","Épargne mensuelle"),
                          ("date_cible","Date cible AAAA-MM-JJ")):
            champ=ctk.CTkEntry(formulaire,placeholder_text=texte,width=220); champ.pack(side="left",padx=6,pady=18)
            self.champs[cle]=champ
        ctk.CTkButton(formulaire,text="Ajouter",command=self._ajouter).pack(side="left",padx=8)
        self.message=ctk.CTkLabel(self,text="",text_color="#B3261E"); self.message.pack()
        projection=ctk.CTkFrame(self,fg_color="white"); projection.pack(fill="x",padx=30,pady=10)
        self.montant_projection=ctk.CTkEntry(projection,placeholder_text="Dépense à simuler",width=220)
        self.montant_projection.pack(side="left",padx=12,pady=15)
        ctk.CTkButton(projection,text="Simuler l'impact",command=self._simuler).pack(side="left")
        self.resultat=ctk.CTkLabel(projection,text=""); self.resultat.pack(side="left",padx=20)
        self.liste=ctk.CTkScrollableFrame(self,fg_color="white"); self.liste.pack(fill="both",expand=True,padx=30,pady=10)

    def _ajouter(self):
        try:
            self.on_ajouter({"nom":self.champs["nom"].get(),
                "montant_cible":float(self.champs["montant_cible"].get()),
                "montant_actuel":float(self.champs["montant_actuel"].get() or 0),
                "montant_periodique":float(self.champs["montant_periodique"].get() or 0),
                "date_cible":self.champs["date_cible"].get()})
            self.message.configure(text="")
        except (ValueError,ConnectionError,OSError) as erreur: self.message.configure(text=str(erreur))

    def _simuler(self):
        try:
            resultat=self.on_simuler(float(self.montant_projection.get()))
            self.resultat.configure(text=f"Budget restant projeté : {resultat['budget_restant_projete']:.2f} €")
        except (ValueError,ConnectionError,OSError) as erreur: self.message.configure(text=str(erreur))

    def actualiser(self, objectifs):
        for widget in self.liste.winfo_children(): widget.destroy()
        if not objectifs: ctk.CTkLabel(self.liste,text="Aucun objectif enregistré.").pack(pady=20); return
        for objectif in objectifs:
            texte=(f"{objectif['nom']} — {objectif['montant_actuel']:.2f} € / "
                   f"{objectif['montant_cible']:.2f} € — cible {objectif['date_cible']}")
            ctk.CTkLabel(self.liste,text=texte,anchor="w").pack(fill="x",padx=12,pady=8)
