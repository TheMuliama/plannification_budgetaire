"""Tests des alertes budgétaires."""
from serveur.services.alertes import GestionnaireAlertes


def test_generer_alertes_seuil_minimum_et_projection() -> None:
    alertes=GestionnaireAlertes().generer_alertes(
        {"pourcentage_consomme":85,"montant_restant":20},
        {"budget_restant_projete":-10},{"information":50,"attention":80},
        {"budget_restant":30})
    assert [alerte["type"] for alerte in alertes]==["attention","minimum","projection"]

def test_signaler_depassement() -> None:
    alertes=GestionnaireAlertes().generer_alertes(
        {"pourcentage_consomme":110,"montant_restant":-10},{}, {}, {})
    assert alertes[0]["type"]=="depassement"
