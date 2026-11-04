"""Tests du repository revenus."""

from pathlib import Path

import pytest

from persistance.database import Database
from persistance.repositories.revenus import RepositoryRevenus
from serveur.services.revenus import GestionnaireRevenus


@pytest.fixture
def repository_revenus() -> RepositoryRevenus:
    connexion = Database().connecter(":memory:")
    connexion.executescript(Path("persistance/schema.sql").read_text(encoding="utf-8"))
    connexion.executemany(
        "INSERT INTO utilisateurs (identifiant, mot_de_passe) VALUES (?, ?)",
        (("utilisateur-1", "hachage-1"), ("utilisateur-2", "hachage-2")),
    )
    yield RepositoryRevenus(connexion)
    connexion.close()


@pytest.fixture
def gestionnaire_revenus(repository_revenus: RepositoryRevenus) -> GestionnaireRevenus:
    return GestionnaireRevenus(repository_revenus)


def test_ajouter_et_obtenir_un_revenu(repository_revenus: RepositoryRevenus) -> None:
    revenu_id = repository_revenus.ajouter_revenu(
        1, 950.50, "2026-11-04", "Bourse", "recu"
    )

    revenu = repository_revenus.obtenir_revenu(1, revenu_id)
    assert revenu is not None
    assert revenu["montant"] == 950.50
    assert revenu["statut"] == "recu"


def test_modifier_et_supprimer_un_revenu(repository_revenus: RepositoryRevenus) -> None:
    revenu_id = repository_revenus.ajouter_revenu(1, 100, "2026-11-01", None, "prevu")

    assert (
        repository_revenus.modifier_revenu(
            1, revenu_id, 120, "2026-11-02", "Mission", "recu"
        )
        is True
    )
    assert repository_revenus.obtenir_revenu(1, revenu_id)["montant"] == 120
    assert repository_revenus.supprimer_revenu(1, revenu_id) is True
    assert repository_revenus.obtenir_revenu(1, revenu_id) is None


def test_filtrer_et_totaliser_les_revenus(
    repository_revenus: RepositoryRevenus,
) -> None:
    repository_revenus.ajouter_revenu(1, 100, "2026-10-31", None, "recu")
    repository_revenus.ajouter_revenu(1, 200, "2026-11-01", None, "prevu")
    repository_revenus.ajouter_revenu(1, 300, "2026-11-02", None, "recu")

    revenus = repository_revenus.consulter_revenus(
        1,
        debut="2026-11-01",
        fin="2026-11-30",
        statut="recu",
    )

    assert [revenu["montant"] for revenu in revenus] == [300]
    assert repository_revenus.total_revenus(1, statut="recu") == 400


def test_isoler_les_revenus_par_utilisateur(
    repository_revenus: RepositoryRevenus,
) -> None:
    revenu_id = repository_revenus.ajouter_revenu(1, 100, "2026-11-04", None, "recu")

    assert repository_revenus.obtenir_revenu(2, revenu_id) is None
    assert repository_revenus.consulter_revenus(2) == []
    assert (
        repository_revenus.modifier_revenu(
            2, revenu_id, 999, "2026-11-04", None, "recu"
        )
        is False
    )
    assert repository_revenus.supprimer_revenu(2, revenu_id) is False


def test_service_gerer_le_cycle_de_vie_d_un_revenu(
    gestionnaire_revenus: GestionnaireRevenus,
) -> None:
    revenu = gestionnaire_revenus.ajouter_revenu(
        {
            "utilisateur_id": 1,
            "montant": 250,
            "date": "2026-11-04",
            "description": "  Mission  ",
            "statut": "prevu",
            "categorie": "Prime",
        }
    )
    assert revenu["description"] == "Mission"
    assert revenu["categorie"] == "Prime"

    revenu_modifie = gestionnaire_revenus.modifier_revenu(
        1,
        revenu["id"],
        {
            "montant": 275,
            "date": "2026-11-05",
            "description": None,
            "statut": "recu",
            "categorie": "Remboursement",
        },
    )
    assert revenu_modifie["montant"] == 275
    assert revenu_modifie["statut"] == "recu"
    assert revenu_modifie["categorie"] == "Remboursement"

    gestionnaire_revenus.supprimer_revenu(1, revenu["id"])
    assert gestionnaire_revenus.consulter_revenus(1) == []


@pytest.mark.parametrize(
    "modification",
    (
        {"montant": 0},
        {"montant": float("nan")},
        {"date": "04/11/2026"},
        {"statut": "encaisse"},
        {"categorie": "Budget courses"},
    ),
)
def test_service_refuser_un_revenu_invalide(
    gestionnaire_revenus: GestionnaireRevenus,
    modification: dict,
) -> None:
    revenu = {
        "utilisateur_id": 1,
        "montant": 100,
        "date": "2026-11-04",
        "description": None,
        "statut": "recu",
    }
    revenu.update(modification)

    with pytest.raises(ValueError):
        gestionnaire_revenus.ajouter_revenu(revenu)


def test_service_interdire_l_acces_au_revenu_d_un_autre_utilisateur(
    gestionnaire_revenus: GestionnaireRevenus,
) -> None:
    revenu = gestionnaire_revenus.ajouter_revenu(
        {
            "utilisateur_id": 1,
            "montant": 100,
            "date": "2026-11-04",
            "statut": "recu",
        }
    )

    with pytest.raises(ValueError, match="introuvable"):
        gestionnaire_revenus.supprimer_revenu(2, revenu["id"])
