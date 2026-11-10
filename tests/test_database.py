"""Tests de la connexion et du schéma SQLite."""

import sqlite3
from pathlib import Path

from persistance.database import Database


def test_initialiser_schema_et_cles_etrangeres() -> None:
    connexion = Database().connecter(":memory:")
    connexion.executescript(Path("persistance/schema.sql").read_text(encoding="utf-8"))
    assert connexion.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert connexion.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    with __import__("pytest").raises(sqlite3.IntegrityError):
        connexion.execute(
            "INSERT INTO categories (utilisateur_id,nom) VALUES (999,'Interdite')"
        )
    connexion.close()


def test_migrer_une_base_existante_avec_categorie_de_revenu(tmp_path) -> None:
    chemin = tmp_path / "ancienne.db"
    base = Database()
    connexion = base.connecter(str(chemin))
    connexion.execute(
        "CREATE TABLE revenus (id INTEGER PRIMARY KEY, utilisateur_id INTEGER NOT NULL, "
        "montant REAL NOT NULL, date TEXT NOT NULL, description TEXT, statut TEXT NOT NULL)"
    )
    base.initialiser_schema(connexion)
    colonnes = {ligne[1] for ligne in connexion.execute("PRAGMA table_info(revenus)")}
    assert "categorie" in colonnes
    connexion.close()
