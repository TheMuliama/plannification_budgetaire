"""Tests d'intégration des dépendances entre les neuf modules métier."""

from pathlib import Path

from persistance.database import Database
from serveur.application import ApplicationServeur


def _application_authentifiee() -> tuple[ApplicationServeur, str]:
    """Construire une application en mémoire et ouvrir une session de test."""
    connexion = Database().connecter(":memory:")
    connexion.executescript(Path("persistance/schema.sql").read_text(encoding="utf-8"))
    application = ApplicationServeur(connexion)
    application.creer_compte(
        {"identifiant": "integration", "mot_de_passe": "mot-de-passe"}
    )
    session = application.connecter(
        {"identifiant": "integration", "mot_de_passe": "mot-de-passe"}
    )["session"]
    return application, session


def test_raccorder_calcul_projection_alertes_et_tableau_de_bord() -> None:
    """Vérifier que les calculs agrégés proviennent des services serveur."""
    application, session = _application_authentifiee()
    categorie = application.creer_categorie({"session": session, "nom": "Courses"})
    budget = application.creer_budget(
        {
            "session": session,
            "annee": 2026,
            "mois": 11,
            "categorie_id": categorie["id"],
            "montant_alloue": 200,
        }
    )
    application.creer_revenu(
        {
            "session": session,
            "montant": 1000,
            "date": "2026-11-01",
            "statut": "recu",
            "categorie": "Salaire",
        }
    )
    application.creer_objectif(
        {
            "session": session,
            "nom": "Ordinateur",
            "montant_cible": 600,
            "montant_periodique": 50,
            "date_cible": "2027-11-01",
        }
    )
    depense = {
        "session": session,
        "budget_id": budget["id"],
        "categorie_id": categorie["id"],
        "montant": 160,
        "date": "2026-11-05",
        "statut": "realisee",
    }
    application.creer_depense(depense)
    application.creer_depense(
        {**depense, "montant": 100, "date": "2026-11-20", "statut": "prevue"}
    )

    etat = application.obtenir_etat_budget({"session": session})
    assert etat["categories"][0]["pourcentage_consomme"] == 80
    assert etat["budget_flexible"] == 40
    assert etat["enveloppes_hebdomadaires"] == [10, 10, 10, 10]

    alertes = application.lister_alertes({"session": session})
    alerte_budget = next(
        alerte for alerte in alertes if str(alerte["id"]).startswith("budget:")
    )
    assert alerte_budget["type"] == "attention"
    assert alerte_budget["pourcentage"] == 80

    projection = application.simuler_projection({"session": session})
    assert projection["budget_restant_projete"] == -60
    assert projection["consequences"]["budget_depasse"] is True

    tableau = application.obtenir_tableau_de_bord({"session": session})
    assert tableau["depense"] == 160
    assert tableau["restant"] == 840
    assert tableau["alertes_actives"] >= 1

    analyses = application.analyser_objectifs({"session": session})
    assert analyses[0]["ecart_plan"]["en_retard"] is True
    assert analyses[0]["scenarios_reajustement"]


def test_creer_une_recurrence_et_gerer_les_categories_par_le_serveur() -> None:
    """Vérifier les actions serveur absentes de l'ancienne intégration."""
    application, session = _application_authentifiee()
    categorie = application.creer_categorie({"session": session, "nom": "Transport"})
    modifiee = application.modifier_categorie(
        {"session": session, "id": categorie["id"], "nom": "Mobilité"}
    )
    assert modifiee["nom"] == "Mobilité"

    revenus = application.creer_revenus_recurrents(
        {
            "session": session,
            "montant": 20,
            "date": "2026-11-01",
            "date_fin": "2026-11-15",
            "frequence": "Hebdomadaire",
            "description": "Aide",
            "categorie": "Autre",
        }
    )
    assert [revenu["date"] for revenu in revenus] == [
        "2026-11-01",
        "2026-11-08",
        "2026-11-15",
    ]
    application.supprimer_categorie({"session": session, "id": categorie["id"]})
    assert application.lister_categories({"session": session}) == []


def test_rattacher_chaque_depense_recurrente_au_budget_de_son_mois() -> None:
    """Éviter qu'une série récurrente réutilise le budget du premier mois."""
    application, session = _application_authentifiee()
    categorie = application.creer_categorie({"session": session, "nom": "Abonnement"})
    budgets = [
        application.creer_budget(
            {
                "session": session,
                "annee": 2026,
                "mois": mois,
                "categorie_id": categorie["id"],
                "montant_alloue": 50,
            }
        )
        for mois in (11, 12)
    ]
    application.creer_revenu(
        {
            "session": session,
            "montant": 100,
            "date": "2026-11-01",
            "statut": "recu",
        }
    )
    depenses = application.creer_depenses_recurrentes(
        {
            "session": session,
            "categorie_id": categorie["id"],
            "sous_categorie_id": None,
            "montant": 10,
            "date": "2026-11-05",
            "date_fin": "2026-12-05",
            "frequence": "Mensuelle",
            "description": "Service",
        }
    )
    assert [depense["budget_id"] for depense in depenses] == [
        budgets[0]["id"],
        budgets[1]["id"],
    ]
    assert [depense["statut"] for depense in depenses] == ["realisee", "prevue"]
    assert application.obtenir_solde({"session": session})["disponible"] == 90
