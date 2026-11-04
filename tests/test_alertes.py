"""Tests des alertes budgétaires."""

from pathlib import Path

from persistance.database import Database
from persistance.repositories.alertes import RepositoryAlertes
from serveur.services.alertes import GestionnaireAlertes


def test_generer_alertes_seuil_minimum_et_projection() -> None:
    alertes = GestionnaireAlertes().generer_alertes(
        {"pourcentage_consomme": 85, "montant_restant": 20},
        {"budget_restant_projete": -10},
        {"information": 50, "attention": 80},
        {"budget_restant": 30},
    )
    assert [alerte["type"] for alerte in alertes] == [
        "attention",
        "minimum",
        "projection",
    ]


def test_signaler_depassement() -> None:
    alertes = GestionnaireAlertes().generer_alertes(
        {"pourcentage_consomme": 110, "montant_restant": -10}, {}, {}, {}
    )
    assert alertes[0]["type"] == "depassement"


def test_persister_et_lire_une_alerte() -> None:
    connexion = Database().connecter(":memory:")
    connexion.executescript(Path("persistance/schema.sql").read_text(encoding="utf-8"))
    connexion.execute(
        "INSERT INTO utilisateurs (identifiant,mot_de_passe) VALUES ('u','h')"
    )
    connexion.execute(
        "INSERT INTO categories (utilisateur_id,nom) VALUES (1,'Courses')"
    )
    connexion.execute(
        "INSERT INTO budgets (utilisateur_id,annee,mois,categorie_id,montant_alloue) VALUES (1,2026,11,1,100)"
    )
    repository = RepositoryAlertes(connexion)
    alerte = repository.creer_alerte(1, 1, "attention", "Budget à 80 %")
    assert repository.consulter_alertes(1, False) == [alerte]
    assert repository.marquer_lue(1, alerte["id"]) is True
    assert repository.consulter_alertes(1, True)[0]["lue"] == 1
    connexion.close()
