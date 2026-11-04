"""Contrat de communication réseau côté client."""

import json
import socket
from typing import Any


class ClientSocket:
    """Définir la communication du client vers le serveur.

    Cette classe ne développe pas les échanges réseau dans ce squelette.
    """

    def __init__(self) -> None:
        self._socket: socket.socket | None = None
        self._lecture = None

    def connecter(self, adresse: str, port: int) -> None:
        """Établir une connexion vers le serveur indiqué.

        Args:
            adresse: Adresse du serveur.
            port: Port du serveur.

        Returns:
            None.
        """
        self.fermer()
        self._socket = socket.create_connection((adresse, port), timeout=5)
        self._lecture = self._socket.makefile("r", encoding="utf-8", newline="\n")

    def envoyer(self, message: dict[str, Any]) -> None:
        """Envoyer un message au serveur.

        Args:
            message: Données à transmettre au serveur.

        Returns:
            None.
        """
        if self._socket is None: raise ConnectionError("Le client n'est pas connecté.")
        donnees=(json.dumps(message,ensure_ascii=False,separators=(",",":"))+"\n").encode("utf-8")
        self._socket.sendall(donnees)

    def recevoir(self) -> dict[str, Any]:
        """Recevoir un message du serveur.

        Returns:
            Les données reçues du serveur.
        """
        if self._lecture is None: raise ConnectionError("Le client n'est pas connecté.")
        ligne=self._lecture.readline()
        if not ligne: raise ConnectionError("Le serveur a fermé la connexion.")
        resultat=json.loads(ligne)
        if not isinstance(resultat,dict): raise ValueError("La réponse doit être un objet JSON.")
        return resultat

    def demander(self, message: dict[str, Any]) -> dict[str, Any]:
        self.envoyer(message); return self.recevoir()

    def fermer(self) -> None:
        if self._lecture is not None: self._lecture.close(); self._lecture=None
        if self._socket is not None: self._socket.close(); self._socket=None
