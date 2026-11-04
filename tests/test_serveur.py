"""Tests du protocole serveur."""
from serveur.communication.serveur_socket import ServeurSocket


def test_router_une_requete_json() -> None:
    serveur=ServeurSocket({"additionner":lambda d:d["a"]+d["b"]})
    assert serveur.traiter_message({"action":"additionner","donnees":{"a":2,"b":3},
                                    "requete_id":"abc"})=={
        "succes":True,"donnees":5,"erreur":None,"requete_id":"abc"}

def test_refuser_action_inconnue() -> None:
    reponse=ServeurSocket().traiter_message({"action":"inconnue"})
    assert reponse["succes"] is False
    assert reponse["erreur"]=="Action inconnue."

def test_convertir_erreur_metier_en_reponse() -> None:
    def echouer(donnees): raise ValueError("Données invalides")
    reponse=ServeurSocket({"echouer":echouer}).traiter_message({"action":"echouer"})
    assert reponse["erreur"]=="Données invalides"
