"""Contrat de communication réseau côté serveur."""

import json
import logging
import socket
from collections.abc import Callable
from typing import Any

LOGGER = logging.getLogger(__name__)


class ServeurSocket:
    """Définir la communication du serveur avec les clients.

    Les messages sont des objets JSON UTF-8 séparés par un saut de ligne.
    """

    def __init__(
        self, traitements: dict[str, Callable[[dict[str, Any]], Any]] | None = None
    ) -> None:
        self._traitements = traitements or {}
        self._socket: socket.socket | None = None

    def enregistrer_action(
        self, action: str, traitement: Callable[[dict[str, Any]], Any]
    ) -> None:
        """Associer une action du protocole à un traitement.

        Args:
            action: Nom de l'action reçue dans les messages JSON.
            traitement: Fonction appelée avec les données de la requête.
        """
        self._traitements[action] = traitement

    def demarrer(self, port: int, adresse: str = "127.0.0.1") -> None:
        """Préparer l'écoute du serveur sur un port.

        Args:
            port: Port sur lequel le serveur doit écouter.

        Returns:
            None.
        """
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((adresse, port))
        self._socket.listen()
        while True:
            connexion, _ = self._socket.accept()
            with (
                connexion,
                connexion.makefile("r", encoding="utf-8", newline="\n") as lecture,
            ):
                for ligne in lecture:
                    try:
                        message = json.loads(ligne)
                        reponse = self.traiter_message(message)
                    except (json.JSONDecodeError, TypeError, ValueError) as erreur:
                        reponse = {
                            "succes": False,
                            "donnees": None,
                            "erreur": str(erreur),
                        }
                    connexion.sendall(
                        (
                            json.dumps(
                                reponse, ensure_ascii=False, separators=(",", ":")
                            )
                            + "\n"
                        ).encode("utf-8")
                    )

    def traiter_message(self, message: dict[str, Any]) -> dict[str, Any]:
        """Définir le traitement d'un message reçu d'un client.

        Args:
            message: Données reçues du client.

        Returns:
            La réponse à transmettre au client.
        """
        if not isinstance(message, dict):
            raise TypeError("La requête doit être un objet JSON.")
        action = message.get("action")
        identifiant = message.get("requete_id")
        if action not in self._traitements:
            return {
                "succes": False,
                "donnees": None,
                "erreur": "Action inconnue.",
                "requete_id": identifiant,
            }
        try:
            resultat = self._traitements[action](message.get("donnees") or {})
            return {
                "succes": True,
                "donnees": resultat,
                "erreur": None,
                "requete_id": identifiant,
            }
        except (ValueError, KeyError, TypeError) as erreur:
            return {
                "succes": False,
                "donnees": None,
                "erreur": str(erreur),
                "requete_id": identifiant,
            }
        # Une erreur inattendue ne doit jamais exposer de détail technique au client.
        except Exception as erreur:
            LOGGER.exception("Erreur inattendue pendant le traitement", exc_info=erreur)
            return {
                "succes": False,
                "donnees": None,
                "erreur": "Erreur interne du serveur.",
                "requete_id": identifiant,
            }

    def fermer(self) -> None:
        """Fermer le socket d'écoute s'il est ouvert."""
        if self._socket is not None:
            self._socket.close()
            self._socket = None
