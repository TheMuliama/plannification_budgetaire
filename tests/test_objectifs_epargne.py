"""Tests des objectifs d'épargne."""

from pathlib import Path

import pytest

from persistance.database import Database
from persistance.repositories.objectifs_epargne import RepositoryObjectifsEpargne
from serveur.services.objectifs_epargne import GestionnaireObjectifsEpargne


@pytest.fixture
def gestionnaire() -> GestionnaireObjectifsEpargne:
    connexion = Database().connecter(":memory:")
    connexion.executescript(Path("persistance/schema.sql").read_text(encoding="utf-8"))
    connexion.executemany(
        "INSERT INTO utilisateurs (identifiant,mot_de_passe) VALUES (?,?)",
        (("u1", "h1"), ("u2", "h2")),
    )
    yield GestionnaireObjectifsEpargne(RepositoryObjectifsEpargne(connexion))
    connexion.close()


def test_gerer_objectif_et_plan(gestionnaire: GestionnaireObjectifsEpargne) -> None:
    donnees = {
        "utilisateur_id": 1,
        "nom": "Ordinateur",
        "montant_cible": 1200,
        "montant_actuel": 200,
        "montant_periodique": 100,
        "date_cible": "2099-12-31",
    }
    objectif = gestionnaire.creer_objectif(donnees)
    versement = gestionnaire.alimenter_objectif(1, objectif["id"], 50, "2026-11-04")
    assert versement["montant"] == 50
    objectif = gestionnaire.consulter_objectif(1, objectif["id"])
    assert objectif["montant_actuel"] == 250
    assert gestionnaire.total_versements(1) == 50
    assert gestionnaire.consulter_versements(1, objectif["id"]) == [versement]
    assert gestionnaire.consulter_objectifs(1) == [objectif]
    plan = gestionnaire.determiner_plan_epargne(donnees)
    assert plan["montant_restant"] == 1000
    ecart = gestionnaire.constater_ecart(plan, 50)
    assert ecart["en_retard"] is True
    assert len(gestionnaire.preparer_scenarios_reajustement(objectif, ecart)) == 2
    modifie = gestionnaire.modifier_objectif(
        1, objectif["id"], {**donnees, "montant_actuel": 300}
    )
    assert modifie["montant_actuel"] == 300
    gestionnaire.supprimer_objectif(1, objectif["id"])
    assert gestionnaire.consulter_objectifs(1) == []


def test_refuser_versement_superieur_au_reste(
    gestionnaire: GestionnaireObjectifsEpargne,
) -> None:
    objectif = gestionnaire.creer_objectif(
        {
            "utilisateur_id": 1,
            "nom": "Projet",
            "montant_cible": 100,
            "montant_actuel": 90,
            "date_cible": "2099-01-01",
        }
    )
    with pytest.raises(ValueError, match="dépasse"):
        gestionnaire.alimenter_objectif(1, objectif["id"], 11, "2026-11-04")


def test_isoler_objectifs(gestionnaire: GestionnaireObjectifsEpargne) -> None:
    objectif = gestionnaire.creer_objectif(
        {
            "utilisateur_id": 1,
            "nom": "Projet",
            "montant_cible": 100,
            "date_cible": "2099-01-01",
        }
    )
    with pytest.raises(ValueError):
        gestionnaire.consulter_objectif(2, objectif["id"])


@pytest.mark.parametrize(
    "champ,valeur",
    (
        ("nom", " "),
        ("montant_cible", 0),
        ("montant_actuel", 101),
        ("date_cible", "demain"),
    ),
)
def test_refuser_objectif_invalide(
    gestionnaire: GestionnaireObjectifsEpargne, champ: str, valeur: object
) -> None:
    donnees = {
        "utilisateur_id": 1,
        "nom": "Projet",
        "montant_cible": 100,
        "date_cible": "2099-01-01",
    }
    donnees[champ] = valeur
    with pytest.raises(ValueError):
        gestionnaire.creer_objectif(donnees)
