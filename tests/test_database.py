"""Tests de la connexion et du schéma SQLite."""
import sqlite3
from pathlib import Path
from persistance.database import Database


def test_initialiser_schema_et_cles_etrangeres() -> None:
    connexion=Database().connecter(":memory:")
    connexion.executescript(Path("persistance/schema.sql").read_text(encoding="utf-8"))
    assert connexion.execute("PRAGMA foreign_keys").fetchone()[0]==1
    assert connexion.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
    with __import__("pytest").raises(sqlite3.IntegrityError):
        connexion.execute("INSERT INTO categories (utilisateur_id,nom) VALUES (999,'Interdite')")
    connexion.close()
