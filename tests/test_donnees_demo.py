"""Tests du scénario de démonstration destiné au professeur."""

from pathlib import Path

from persistance.database import Database
from scripts.peupler_compte_richard import IDENTIFIANT, MOT_DE_PASSE, peupler
from serveur.securite.mots_de_passe import hacher_mot_de_passe, verifier_mot_de_passe


def test_peupler_uniquement_le_compte_richard(tmp_path: Path) -> None:
    """Créer six mois de données sans toucher aux autres comptes."""
    chemin = tmp_path / "demo.db"
    base = Database()
    connexion = base.connecter(str(chemin))
    base.initialiser_schema(connexion)
    with connexion:
        connexion.executemany(
            "INSERT INTO utilisateurs (identifiant, mot_de_passe) VALUES (?, ?)",
            (
                (IDENTIFIANT, hacher_mot_de_passe("ancien-mot-de-passe")),
                ("autre@example.test", hacher_mot_de_passe("autre-mot-de-passe")),
            ),
        )
        autre_id = connexion.execute(
            "SELECT id FROM utilisateurs WHERE identifiant = 'autre@example.test'"
        ).fetchone()["id"]
        connexion.execute(
            "INSERT INTO revenus "
            "(utilisateur_id,montant,date,description,statut,categorie) "
            "VALUES (?,?,?,?,?,?)",
            (autre_id, 10, "2026-11-01", "À conserver", "recu", "Autre"),
        )
    connexion.close()

    resume = peupler(str(chemin))

    assert resume == {
        "categories": 6,
        "sous_categories": 8,
        "budgets": 48,
        "revenus": 14,
        "depenses": 59,
        "objectifs_epargne": 2,
        "versements_epargne": 10,
    }
    connexion = base.connecter(str(chemin))
    compte = connexion.execute(
        "SELECT mot_de_passe FROM utilisateurs WHERE identifiant = ?", (IDENTIFIANT,)
    ).fetchone()
    assert verifier_mot_de_passe(MOT_DE_PASSE, compte["mot_de_passe"]) is True
    assert connexion.execute(
        "SELECT COUNT(*) FROM revenus WHERE utilisateur_id = ?", (autre_id,)
    ).fetchone()[0] == 1
    connexion.close()
