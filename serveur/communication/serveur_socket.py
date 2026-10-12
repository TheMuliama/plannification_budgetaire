"""Contrat de communication réseau côté serveur."""

from typing import Any


class ServeurSocket:
    """Définir la communication du serveur avec les clients.

    Cette classe ne développe pas les sockets dans ce squelette.
    """

    def demarrer(self, port: int) -> None:
        """Préparer l'écoute du serveur sur un port.

        Args:
            port: Port sur lequel le serveur doit écouter.

        Returns:
            None.
        """
        pass

    def traiter_message(self, message: dict[str, Any]) -> dict[str, Any]:
        """Définir le traitement d'un message reçu d'un client.

        Args:
            message: Données reçues du client.

        Returns:
            La réponse à transmettre au client.
        """
        pass
