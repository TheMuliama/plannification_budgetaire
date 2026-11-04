
"""Écran d'inscription côté client."""

import re
import customtkinter as ctk


class VueInscription(ctk.CTkFrame):
    """Présenter l'écran de création de compte.

    Cette classe relève uniquement de la présentation.
    Elle ne crée pas de compte elle-même.
    """

    def __init__(self, master, on_register=None, on_login=None):
        super().__init__(master, fg_color="#F5F3EF")

        self.on_register = on_register
        self.on_login = on_login

        # Couleurs de l'application
        self.vert = "#00634F"
        self.beige = "#F5F3EF"
        self.blanc = "#FFFFFF"

        self._construire_interface()

    def _construire_interface(self):
        """Construire les éléments graphiques."""

        # Carte centrale
        self.carte = ctk.CTkFrame(
            self,
            width=440,
            height=650,
            corner_radius=15,
            fg_color=self.blanc,
            border_width=1,
            border_color="#E5E5E5"
        )
        self.carte.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )
        self.carte.pack_propagate(False)

        # Logo
        ctk.CTkLabel(
            self.carte,
            text="MonBudget",
            font=("Arial", 27, "bold"),
            text_color=self.vert
        ).pack(pady=(25, 10))

        # Titre
        ctk.CTkLabel(
            self.carte,
            text="Créer un compte",
            font=("Arial", 24, "bold"),
            text_color="#172326"
        ).pack(pady=(5, 5))

        ctk.CTkLabel(
            self.carte,
            text="Commencez à gérer votre budget.",
            font=("Arial", 12),
            text_color="gray"
        ).pack(pady=(0, 20))

        # Champ nom
        self.nom = self._creer_champ(
            "Nom"
        )

        # Champ prénom
        self.prenom = self._creer_champ(
            "Prénom"
        )

        # Champ email
        self.email = self._creer_champ(
            "Adresse e-mail"
        )

        # Champ mot de passe
        self.password = self._creer_champ(
            "Mot de passe",
            secret=True
        )

        # Confirmation
        self.confirmation = self._creer_champ(
            "Confirmer le mot de passe",
            secret=True
        )

        # Afficher les mots de passe
        self.afficher = ctk.CTkCheckBox(
            self.carte,
            text="Afficher les mots de passe",
            font=("Arial", 12),
            text_color="#555555",
            fg_color=self.vert,
            hover_color=self.vert,
            command=self.toggle_password
        )
        self.afficher.pack(pady=(10, 5))

        # Message d'information
        self.message = ctk.CTkLabel(
            self.carte,
            text="",
            font=("Arial", 12),
            text_color="red",
            wraplength=350
        )
        self.message.pack(pady=5)

        # Bouton inscription
        self.bouton_inscription = ctk.CTkButton(
            self.carte,
            text="Créer mon compte",
            width=330,
            height=43,
            corner_radius=8,
            fg_color=self.vert,
            hover_color="#004D3E",
            font=("Arial", 14, "bold"),
            command=self.inscrire
        )
        self.bouton_inscription.pack(pady=(10, 10))

        # Retour à la connexion
        ctk.CTkButton(
            self.carte,
            text="Déjà un compte ? Se connecter",
            fg_color="transparent",
            hover_color=self.beige,
            text_color=self.vert,
            command=self.retour_connexion
        ).pack(pady=5)

    def _creer_champ(self, placeholder, secret=False):
        """Créer un champ de saisie."""

        champ = ctk.CTkEntry(
            self.carte,
            width=330,
            height=42,
            placeholder_text=placeholder,
            show="*" if secret else "",
            corner_radius=8,
            fg_color="#FAFAFA",
            border_color="#DDDDDD"
        )
        champ.pack(pady=6)

        return champ

    def toggle_password(self):
        """Afficher ou masquer les mots de passe."""

        if self.afficher.get():
            self.password.configure(show="")
            self.confirmation.configure(show="")
        else:
            self.password.configure(show="*")
            self.confirmation.configure(show="*")

    def inscrire(self):
        """Vérifier les champs et demander l'inscription."""

        nom = self.nom.get().strip()
        prenom = self.prenom.get().strip()
        email = self.email.get().strip()
        password = self.password.get()
        confirmation = self.confirmation.get()

        # Vérification des champs vides
        if not all([
            nom, prenom, email,
            password, confirmation
        ]):
            self.afficher_erreur(
                "Veuillez remplir tous les champs."
            )
            return

        # Vérification du format email
        format_email = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        if not re.fullmatch(format_email, email):
            self.afficher_erreur(
                "Veuillez saisir une adresse e-mail valide."
            )
            return

        # Vérification du mot de passe
        if len(password) < 8:
            self.afficher_erreur(
                "Le mot de passe doit contenir au moins 8 caractères."
            )
            return

        # Vérification de la confirmation
        if password != confirmation:
            self.afficher_erreur(
                "Les mots de passe ne correspondent pas."
            )
            return

        # Effacer les anciens messages
        self.message.configure(text="")

        # Transmettre les données à la logique externe
        if self.on_register:
            try:
                self.on_register(nom, prenom, email, password)
            except (ConnectionError, OSError, ValueError) as erreur:
                self.afficher_erreur(str(erreur))
        else:
            self.afficher_erreur(
                "Service d'inscription non configuré."
            )

    def retour_connexion(self):
        """Demander le retour à l'écran de connexion."""

        if self.on_login:
            self.on_login()
        else:
            self.afficher_erreur(
                "Page de connexion non configurée."
            )

    def afficher_erreur(self, texte):
        """Afficher un message d'erreur."""

        self.message.configure(
            text=texte,
            text_color="red"
        )

    def afficher_message(self, texte):
        """Afficher un message d'information."""

        self.message.configure(
            text=texte,
            text_color=self.vert
        )

    def definir_chargement(self, chargement):
        """Gérer l'état du bouton d'inscription."""

        if chargement:
            self.bouton_inscription.configure(
                state="disabled",
                text="Inscription en cours..."
            )
        else:
            self.bouton_inscription.configure(
                state="normal",
                text="Créer mon compte"
            )

    def vider_formulaire(self):
        """Réinitialiser les champs du formulaire."""

        self.nom.delete(0, "end")
        self.prenom.delete(0, "end")
        self.email.delete(0, "end")
        self.password.delete(0, "end")
        self.confirmation.delete(0, "end")

        self.afficher.deselect()
        self.toggle_password()

        self.message.configure(text="")
