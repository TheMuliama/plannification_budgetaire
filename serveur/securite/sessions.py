"""Gestion des sessions opaques créées par le serveur."""

import secrets


class GestionnaireSessions:
    """Associer des jetons imprévisibles aux utilisateurs authentifiés."""

    def __init__(self) -> None:
        self._utilisateurs_par_jeton: dict[str, int] = {}

    def ouvrir(self, identifiant_utilisateur: int) -> str:
        """Créer une session pour un utilisateur.

        Args:
            identifiant_utilisateur: Identifiant du compte authentifié.

        Returns:
            Un jeton de session opaque et imprévisible.
        """
        jeton = secrets.token_urlsafe(32)
        self._utilisateurs_par_jeton[jeton] = identifiant_utilisateur
        return jeton

    def fermer(self, jeton: str | None) -> None:
        """Fermer une session si son jeton existe.

        Args:
            jeton: Jeton de la session à fermer.
        """
        if jeton is not None:
            self._utilisateurs_par_jeton.pop(jeton, None)

    def identifier(self, jeton: str | None) -> int:
        """Identifier le propriétaire d'une session.

        Args:
            jeton: Jeton de session transmis par le client.

        Returns:
            L'identifiant du compte authentifié.

        Raises:
            ValueError: Si le jeton est absent, invalide ou expiré.
        """
        if jeton is None:
            raise ValueError("Session invalide ou expirée.")

        try:
            return self._utilisateurs_par_jeton[jeton]
        except KeyError as erreur:
            raise ValueError("Session invalide ou expirée.") from erreur
