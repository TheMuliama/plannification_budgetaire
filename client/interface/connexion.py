import customtkinter as ctk


class Connexion(ctk.CTkFrame):

    def __init__(self, master, on_login=None, on_register=None):
        super().__init__(master, fg_color="#F5F3EF")

        self.on_login = on_login
        self.on_register = on_register

        # Couleurs de l'application
        vert = "#00634F"
        beige = "#F5F3EF"
        blanc = "#FFFFFF"

        # Carte centrale
        self.carte = ctk.CTkFrame(
            self,
            width=420,
            height=490,
            corner_radius=15,
            fg_color=blanc,
            border_width=1,
            border_color="#E5E5E5"
        )
        self.carte.place(relx=0.5, rely=0.5, anchor="center")
        self.carte.pack_propagate(False)

        # Logo
        ctk.CTkLabel(
            self.carte,
            text="MonBudget",
            font=("Arial", 27, "bold"),
            text_color=vert
        ).pack(pady=(30, 10))

        # Titre
        ctk.CTkLabel(
            self.carte,
            text="Bienvenue !",
            font=("Arial", 24, "bold"),
            text_color="#172326"
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            self.carte,
            text="Connectez-vous pour accéder à votre budget.",
            font=("Arial", 12),
            text_color="gray"
        ).pack(pady=(0, 25))

        # Champ email
        self.email = ctk.CTkEntry(
            self.carte,
            width=330,
            height=42,
            placeholder_text="Adresse e-mail",
            corner_radius=8,
            fg_color="#FAFAFA",
            border_color="#DDDDDD"
        )
        self.email.pack(pady=8)

        # Champ mot de passe
        self.password = ctk.CTkEntry(
            self.carte,
            width=330,
            height=42,
            placeholder_text="Mot de passe",
            show="*",
            corner_radius=8,
            fg_color="#FAFAFA",
            border_color="#DDDDDD"
        )
        self.password.pack(pady=8)

        # Afficher le mot de passe
        self.afficher = ctk.CTkCheckBox(
            self.carte,
            text="Afficher le mot de passe",
            font=("Arial", 12),
            text_color="#555555",
            fg_color=vert,
            hover_color=vert,
            command=self.toggle_password
        )
        self.afficher.pack(pady=10)

        # Bouton connexion
        ctk.CTkButton(
            self.carte,
            text="Se connecter",
            width=330,
            height=43,
            corner_radius=8,
            fg_color=vert,
            hover_color="#004D3E",
            font=("Arial", 14, "bold"),
            command=self.connecter
        ).pack(pady=(15, 10))

        # Message d'information
        self.message = ctk.CTkLabel(
            self.carte,
            text="",
            font=("Arial", 12),
            text_color="red"
        )
        self.message.pack()

        # Inscription
        ctk.CTkButton(
            self.carte,
            text="Pas encore de compte ? S'inscrire",
            fg_color="transparent",
            hover_color=beige,
            text_color=vert,
            command=self.inscrire
        ).pack(pady=5)

    def toggle_password(self):
        if self.afficher.get():
            self.password.configure(show="")
        else:
            self.password.configure(show="*")

    def connecter(self):
        email = self.email.get().strip()
        password = self.password.get()

        if not email or not password:
            self.message.configure(
                text="Veuillez remplir tous les champs."
            )
            return

        # La vérification sera faite par le serveur.
        if self.on_login:
            self.on_login(email, password)
        else:
            self.message.configure(
                text="Serveur d'authentification non configuré."
            )

    def inscrire(self):
        if self.on_register:
            self.on_register()
        else:
            self.message.configure(
                text="Page d'inscription non configurée."
            )
