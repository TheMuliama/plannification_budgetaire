
"""Écran des paramètres côté client."""

import customtkinter as ctk
from tkinter import messagebox


class VueParametres(ctk.CTkFrame):
    """Présenter les paramètres de l'application.

    Cette classe ne porte aucune décision métier.
    """

    def __init__(
        self,
        master,
        on_modifier_profil=None,
        on_changer_mot_de_passe=None,
        on_changer_theme=None,
        on_deconnexion=None
    ):
        super().__init__(master, fg_color="#F5F3EF")

        # Fonctions de rappel
        self.on_modifier_profil = on_modifier_profil
        self.on_changer_mot_de_passe = on_changer_mot_de_passe
        self.on_changer_theme = on_changer_theme
        self.on_deconnexion = on_deconnexion

        # Couleurs
        self.vert = "#00634F"
        self.vert_fonce = "#004D3E"
        self.beige = "#F5F3EF"
        self.blanc = "#FFFFFF"
        self.texte = "#172326"
        self.gris = "#777777"
        self.rouge = "#C94C4C"

        # Informations affichées
        self.profil = {}
        self.theme = "Clair"

        self._construire_interface()

    def _construire_interface(self):
        """Construire l'interface des paramètres."""

        # Conteneur défilant
        self.conteneur = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.conteneur.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=20
        )

        # Titre
        ctk.CTkLabel(
            self.conteneur,
            text="Paramètres",
            font=("Arial", 26, "bold"),
            text_color=self.texte
        ).pack(
            anchor="w",
            pady=(0, 5)
        )

        ctk.CTkLabel(
            self.conteneur,
            text="Gérez votre profil et vos préférences.",
            font=("Arial", 13),
            text_color=self.gris
        ).pack(
            anchor="w",
            pady=(0, 20)
        )

        self._creer_section_profil()
        self._creer_section_apparence()
        self._creer_section_securite()
        self._creer_section_compte()

    def _creer_carte(self, titre):
        """Créer une section des paramètres."""

        carte = ctk.CTkFrame(
            self.conteneur,
            fg_color=self.blanc,
            corner_radius=12,
            border_width=1,
            border_color="#E5E5E5"
        )
        carte.pack(
            fill="x",
            pady=(0, 15)
        )

        ctk.CTkLabel(
            carte,
            text=titre,
            font=("Arial", 17, "bold"),
            text_color=self.texte
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 12)
        )

        return carte

    def _creer_champ(self, parent, titre, secret=False):
        """Créer un champ de saisie avec son libellé."""

        ctk.CTkLabel(
            parent,
            text=titre,
            font=("Arial", 12),
            text_color=self.texte
        ).pack(
            anchor="w",
            padx=20,
            pady=(5, 3)
        )

        champ = ctk.CTkEntry(
            parent,
            height=40,
            corner_radius=8,
            fg_color="#FAFAFA",
            border_color="#DDDDDD",
            show="*" if secret else ""
        )
        champ.pack(
            fill="x",
            padx=20,
            pady=(0, 12)
        )

        return champ

    def _creer_section_profil(self):
        """Construire la section du profil."""

        carte = self._creer_carte(
            "Informations personnelles"
        )

        self.champ_nom = self._creer_champ(
            carte,
            "Nom"
        )

        self.champ_prenom = self._creer_champ(
            carte,
            "Prénom"
        )

        self.champ_email = self._creer_champ(
            carte,
            "Adresse e-mail"
        )

        self.message_profil = ctk.CTkLabel(
            carte,
            text="",
            text_color=self.rouge,
            wraplength=450
        )
        self.message_profil.pack(padx=20)

        ctk.CTkButton(
            carte,
            text="Enregistrer les modifications",
            height=40,
            fg_color=self.vert,
            hover_color=self.vert_fonce,
            command=self.enregistrer_profil
        ).pack(
            anchor="e",
            padx=20,
            pady=(5, 20)
        )

    def _creer_section_apparence(self):
        """Construire les préférences d'apparence."""

        carte = self._creer_carte(
            "Apparence"
        )

        ctk.CTkLabel(
            carte,
            text="Thème de l'application",
            font=("Arial", 12),
            text_color=self.texte
        ).pack(
            anchor="w",
            padx=20,
            pady=(5, 5)
        )

        self.menu_theme = ctk.CTkOptionMenu(
            carte,
            values=[
                "Clair",
                "Sombre",
                "Système"
            ],
            fg_color=self.vert,
            button_color=self.vert_fonce,
            command=self.changer_theme
        )
        self.menu_theme.pack(
            anchor="w",
            padx=20,
            pady=(0, 20)
        )
        self.menu_theme.set(self.theme)

        self.message_theme = ctk.CTkLabel(
            carte,
            text="",
            text_color=self.gris
        )
        self.message_theme.pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

    def _creer_section_securite(self):
        """Construire la section de sécurité."""

        carte = self._creer_carte(
            "Sécurité"
        )

        self.champ_ancien_mdp = self._creer_champ(
            carte,
            "Mot de passe actuel",
            secret=True
        )

        self.champ_nouveau_mdp = self._creer_champ(
            carte,
            "Nouveau mot de passe",
            secret=True
        )

        self.champ_confirmation = self._creer_champ(
            carte,
            "Confirmer le nouveau mot de passe",
            secret=True
        )

        self.afficher_mdp = ctk.CTkCheckBox(
            carte,
            text="Afficher les mots de passe",
            font=("Arial", 12),
            text_color=self.gris,
            fg_color=self.vert,
            hover_color=self.vert,
            command=self.toggle_password
        )
        self.afficher_mdp.pack(
            anchor="w",
            padx=20,
            pady=5
        )

        self.message_securite = ctk.CTkLabel(
            carte,
            text="",
            text_color=self.rouge,
            wraplength=450
        )
        self.message_securite.pack(padx=20)

        ctk.CTkButton(
            carte,
            text="Changer le mot de passe",
            height=40,
            fg_color=self.vert,
            hover_color=self.vert_fonce,
            command=self.changer_mot_de_passe
        ).pack(
            anchor="e",
            padx=20,
            pady=(5, 20)
        )

    def _creer_section_compte(self):
        """Construire les actions du compte."""

        carte = self._creer_carte(
            "Compte"
        )

        ctk.CTkLabel(
            carte,
            text="Terminer votre session sur MonBudget.",
            font=("Arial", 12),
            text_color=self.gris
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

        ctk.CTkButton(
            carte,
            text="Se déconnecter",
            height=40,
            fg_color=self.rouge,
            hover_color="#A73535",
            command=self.deconnecter
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 20)
        )

    def actualiser(self, profil, theme="Clair"):
        """Actualiser les données du profil.

        profil contient :
            nom, prenom, email.
        """

        self.profil = dict(profil)
        self.theme = theme

        champs = [
            (self.champ_nom, "nom"),
            (self.champ_prenom, "prenom"),
            (self.champ_email, "email")
        ]

        for champ, cle in champs:
            champ.delete(0, "end")
            champ.insert(
                0,
                str(self.profil.get(cle, ""))
            )

        if theme in ["Clair", "Sombre", "Système"]:
            self.menu_theme.set(theme)

        self.message_profil.configure(text="")
        self.message_theme.configure(text="")
        self.message_securite.configure(text="")

    def enregistrer_profil(self):
        """Valider les champs et transmettre le profil."""

        nom = self.champ_nom.get().strip()
        prenom = self.champ_prenom.get().strip()
        email = self.champ_email.get().strip()

        if not nom or not prenom or not email:
            self.message_profil.configure(
                text="Veuillez remplir tous les champs.",
                text_color=self.rouge
            )
            return

        # Validation simple du format
        if (
            "@" not in email
            or "." not in email.split("@")[-1]
            or " " in email
        ):
            self.message_profil.configure(
                text="Adresse e-mail invalide.",
                text_color=self.rouge
            )
            return

        if self.on_modifier_profil is None:
            self.message_profil.configure(
                text="Modification du profil non configurée.",
                text_color=self.rouge
            )
            return

        donnees = {
            "nom": nom,
            "prenom": prenom,
            "email": email
        }

        self.on_modifier_profil(donnees)

        self.message_profil.configure(
            text="Demande de modification transmise.",
            text_color=self.vert
        )

    def changer_theme(self, valeur):
        """Transmettre le thème sélectionné."""

        if self.on_changer_theme is None:
            self.message_theme.configure(
                text="Changement de thème non configuré.",
                text_color=self.rouge
            )
            return

        self.on_changer_theme(valeur)

        self.message_theme.configure(
            text="Préférence transmise.",
            text_color=self.vert
        )

    def toggle_password(self):
        """Afficher ou masquer les mots de passe."""

        afficher = self.afficher_mdp.get()

        mode = "" if afficher else "*"

        self.champ_ancien_mdp.configure(show=mode)
        self.champ_nouveau_mdp.configure(show=mode)
        self.champ_confirmation.configure(show=mode)

    def changer_mot_de_passe(self):
        """Valider les champs et transmettre la demande."""

        ancien = self.champ_ancien_mdp.get()
        nouveau = self.champ_nouveau_mdp.get()
        confirmation = self.champ_confirmation.get()

        if not ancien or not nouveau or not confirmation:
            self.message_securite.configure(
                text="Veuillez remplir tous les champs.",
                text_color=self.rouge
            )
            return

        if len(nouveau) < 8:
            self.message_securite.configure(
                text="Le mot de passe doit contenir au moins 8 caractères.",
                text_color=self.rouge
            )
            return

        if nouveau != confirmation:
            self.message_securite.configure(
                text="Les mots de passe ne correspondent pas.",
                text_color=self.rouge
            )
            return

        if ancien == nouveau:
            self.message_securite.configure(
                text="Le nouveau mot de passe doit être différent.",
                text_color=self.rouge
            )
            return

        if self.on_changer_mot_de_passe is None:
            self.message_securite.configure(
                text="Changement de mot de passe non configuré.",
                text_color=self.rouge
            )
            return

        self.on_changer_mot_de_passe(
            ancien,
            nouveau
        )

        self.message_securite.configure(
            text="Demande de changement transmise.",
            text_color=self.vert
        )

        # Effacer les champs sensibles
        self.champ_ancien_mdp.delete(0, "end")
        self.champ_nouveau_mdp.delete(0, "end")
        self.champ_confirmation.delete(0, "end")

    def deconnecter(self):
        """Demander la déconnexion."""

        confirmation = messagebox.askyesno(
            "Déconnexion",
            "Voulez-vous vraiment vous déconnecter ?",
            parent=self.winfo_toplevel()
        )

        if not confirmation:
            return

        if self.on_deconnexion:
            self.on_deconnexion()
        else:
            messagebox.showwarning(
                "Action indisponible",
                "La déconnexion n'est pas configurée.",
                parent=self.winfo_toplevel()
            )

    def afficher_erreur(self, section, texte):
        """Afficher une erreur provenant de l'extérieur."""

        messages = {
            "profil": self.message_profil,
            "securite": self.message_securite,
            "theme": self.message_theme
        }

        if section in messages:
            messages[section].configure(
                text=texte,
                text_color=self.rouge
            )

    def vider(self):
        """Réinitialiser les informations affichées."""

        self.actualiser({}, "Clair")

        self.champ_ancien_mdp.delete(0, "end")
        self.champ_nouveau_mdp.delete(0, "end")
        self.champ_confirmation.delete(0, "end")

        self.afficher_mdp.deselect()
        self.toggle_password()
