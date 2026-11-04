"""Tests du protocole serveur."""
from serveur.communication.serveur_socket import ServeurSocket
from pathlib import Path
from persistance.database import Database
from serveur.application import ApplicationServeur


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

def test_masquer_une_erreur_interne() -> None:
    def echouer(donnees): raise RuntimeError("information technique sensible")
    reponse=ServeurSocket({"echouer":echouer}).traiter_message({"action":"echouer"})
    assert reponse["erreur"]=="Erreur interne du serveur."

def test_parcours_authentifie_et_isole() -> None:
    connexion=Database().connecter(":memory:")
    connexion.executescript(Path("persistance/schema.sql").read_text(encoding="utf-8"))
    application=ApplicationServeur(connexion); serveur=ServeurSocket(application.traitements())
    assert serveur.traiter_message({"action":"utilisateurs.creer","donnees":{
        "identifiant":"u1","mot_de_passe":"mot-de-passe"}})["succes"] is True
    connexion_reponse=serveur.traiter_message({"action":"utilisateurs.connecter","donnees":{
        "identifiant":"u1","mot_de_passe":"mot-de-passe"}})
    session=connexion_reponse["donnees"]["session"]
    creation=serveur.traiter_message({"action":"categories.creer","donnees":{
        "session":session,"nom":"Courses"}})
    assert creation["donnees"]["nom"]=="Courses"
    sous_categorie=serveur.traiter_message({"action":"sous_categories.creer","donnees":{
        "session":session,"categorie_id":creation["donnees"]["id"],"nom":"Marché"}})
    assert sous_categorie["donnees"]["nom"]=="Marché"
    liste=serveur.traiter_message({"action":"sous_categories.lister","donnees":{
        "session":session,"categorie_id":creation["donnees"]["id"]}})
    assert liste["donnees"]==[sous_categorie["donnees"]]
    objectif=serveur.traiter_message({"action":"objectifs.creer","donnees":{
        "session":session,"nom":"Voyage","montant_cible":1200,
        "montant_actuel":0,"date_cible":"2099-12-31"}})
    assert objectif["succes"] is True
    analyse=serveur.traiter_message({"action":"objectifs.analyser","donnees":{
        "session":session}})
    assert analyse["donnees"][0]["montant_restant"]==1200
    assert "epargne_maximale" in analyse["donnees"][0]
    assert serveur.traiter_message({"action":"categories.lister","donnees":{
        "session":"invalide"}})["succes"] is False
    connexion.close()
