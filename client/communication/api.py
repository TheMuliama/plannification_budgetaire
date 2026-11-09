"""API cliente du protocole JSON de MonBudget."""

from typing import Any

from .client_socket import ClientSocket


class ErreurServeur(ValueError):
    """Erreur fonctionnelle retournée par le serveur."""


class ApiClient:
    """Exposer les actions du serveur à l'interface graphique."""

    def __init__(self, adresse: str = "127.0.0.1", port: int = 8766) -> None:
        self._adresse = adresse
        self._port = port
        self._client = ClientSocket()
        self.session = None

    def _appel(self, action: str, donnees: dict[str, Any] | None = None) -> Any:
        self._client.connecter(self._adresse, self._port)
        try:
            contenu = dict(donnees or {})
            if self.session is not None:
                contenu["session"] = self.session
            reponse = self._client.demander({"action": action, "donnees": contenu})
        finally:
            self._client.fermer()
        if not reponse.get("succes"):
            raise ErreurServeur(reponse.get("erreur") or "Erreur serveur.")
        return reponse.get("donnees")

    def inscrire(self, identifiant: str, mot_de_passe: str) -> dict[str, Any]:
        """Créer un compte utilisateur.

        Args:
            identifiant: Adresse ou identifiant choisi par l'utilisateur.
            mot_de_passe: Mot de passe du nouveau compte.

        Returns:
            Les informations publiques du compte créé.
        """
        return self._appel(
            "utilisateurs.creer",
            {"identifiant": identifiant, "mot_de_passe": mot_de_passe},
        )

    def connecter(self, identifiant: str, mot_de_passe: str) -> dict[str, Any]:
        """Ouvrir une session auprès du serveur.

        Args:
            identifiant: Identifiant du compte.
            mot_de_passe: Mot de passe fourni par l'utilisateur.

        Returns:
            Les informations publiques du compte authentifié.
        """
        resultat = self._appel(
            "utilisateurs.connecter",
            {"identifiant": identifiant, "mot_de_passe": mot_de_passe},
        )
        self.session = resultat["session"]
        return resultat["utilisateur"]

    def deconnecter(self) -> None:
        """Fermer la session courante et oublier son jeton."""
        if self.session:
            self._appel("utilisateurs.deconnecter")
        self.session = None

    def appeler(self, action: str, **donnees: Any) -> Any:
        """Exécuter une action authentifiée du protocole JSON.

        Args:
            action: Nom de l'action attendue par le serveur.
            **donnees: Paramètres propres à l'action.

        Returns:
            Les données renvoyées par le serveur.

        Raises:
            ErreurServeur: Si le serveur refuse l'action.
        """
        return self._appel(action, donnees)
