"""Contrat de communication réseau côté client."""

from typing import Any


class ClientSocket:
    """Définir la communication du client vers le serveur.

    Cette classe ne développe pas les échanges réseau dans ce squelette.
    """

    def connecter(self, adresse: str, port: int) -> None:
        """Établir une connexion vers le serveur indiqué.

        Args:
            adresse: Adresse du serveur.
            port: Port du serveur.

        Returns:
            None.
        """
        pass

    def envoyer(self, message: dict[str, Any]) -> None:
        """Envoyer un message au serveur.

        Args:
            message: Données à transmettre au serveur.

        Returns:
            None.
        """
        pass

    def recevoir(self) -> dict[str, Any]:
        """Recevoir un message du serveur.

        Returns:
            Les données reçues du serveur.
        """
        pass
