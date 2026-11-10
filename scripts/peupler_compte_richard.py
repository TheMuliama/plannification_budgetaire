"""Créer un scénario de démonstration de six mois pour le compte Richard."""

import sqlite3
from pathlib import Path
from typing import Any

from persistance.database import Database
from serveur.securite.mots_de_passe import hacher_mot_de_passe

IDENTIFIANT = "richard.latchoumane@univ-reunion.fr"
MOT_DE_PASSE = "Richard-2026!"
MOIS_DEMO = tuple(range(6, 12))


def inserer(
    connexion: sqlite3.Connection,
    table: str,
    colonnes: tuple[str, ...],
    valeurs: tuple[Any, ...],
) -> int:
    """Insérer une ligne et retourner son identifiant.

    Args:
        connexion: Connexion SQLite active.
        table: Table ciblée par l'insertion.
        colonnes: Colonnes renseignées.
        valeurs: Valeurs correspondantes.

    Returns:
        L'identifiant SQLite de la ligne créée.
    """
    marqueurs = ",".join("?" for _ in valeurs)
    curseur = connexion.execute(
        f"INSERT INTO {table} ({','.join(colonnes)}) VALUES ({marqueurs})",
        valeurs,
    )
    assert curseur.lastrowid is not None
    return curseur.lastrowid


def reinitialiser_donnees(
    connexion: sqlite3.Connection, utilisateur_id: int
) -> None:
    """Supprimer uniquement les données métier existantes de Richard.

    Args:
        connexion: Connexion SQLite active.
        utilisateur_id: Identifiant du compte de démonstration.
    """
    for table in (
        "alertes",
        "versements_epargne",
        "objectifs_epargne",
        "depenses",
        "budgets",
        "revenus",
        "categories",
    ):
        connexion.execute(
            f"DELETE FROM {table} WHERE utilisateur_id = ?", (utilisateur_id,)
        )


def creer_classements(
    connexion: sqlite3.Connection, utilisateur_id: int
) -> dict[str, tuple[int, int]]:
    """Créer les catégories et sous-catégories du scénario.

    Args:
        connexion: Connexion SQLite active.
        utilisateur_id: Propriétaire des classements.

    Returns:
        Les identifiants de catégorie et sous-catégorie par libellé.
    """
    structure = {
        "Maison · Loyer": ("Maison", "Loyer"),
        "Maison · Énergie": ("Maison", "Énergie"),
        "Alimentation · Courses": ("Alimentation", "Courses"),
        "Transport · Bus": ("Transport", "Bus"),
        "Études · Fournitures": ("Études", "Fournitures"),
        "Loisirs · Sorties": ("Loisirs", "Sorties"),
        "Loisirs · Abonnements": ("Loisirs", "Abonnements"),
        "Santé · Pharmacie": ("Santé", "Pharmacie"),
    }
    categories: dict[str, int] = {}
    resultat = {}
    for libelle, (nom_categorie, nom_sous_categorie) in structure.items():
        if nom_categorie not in categories:
            categories[nom_categorie] = inserer(
                connexion,
                "categories",
                ("utilisateur_id", "nom"),
                (utilisateur_id, nom_categorie),
            )
        categorie_id = categories[nom_categorie]
        sous_categorie_id = inserer(
            connexion,
            "sous_categories",
            ("categorie_id", "nom"),
            (categorie_id, nom_sous_categorie),
        )
        resultat[libelle] = (categorie_id, sous_categorie_id)
    return resultat


def creer_budgets(
    connexion: sqlite3.Connection,
    utilisateur_id: int,
    classements: dict[str, tuple[int, int]],
) -> dict[tuple[int, str], int]:
    """Créer huit enveloppes pour chacun des six mois.

    Args:
        connexion: Connexion SQLite active.
        utilisateur_id: Propriétaire des budgets.
        classements: Classements créés pour le scénario.

    Returns:
        Les identifiants de budget indexés par mois et libellé.
    """
    allocations = {
        "Maison · Loyer": (650.0, True),
        "Maison · Énergie": (90.0, True),
        "Alimentation · Courses": (300.0, False),
        "Transport · Bus": (60.0, True),
        "Études · Fournitures": (80.0, False),
        "Loisirs · Sorties": (150.0, False),
        "Loisirs · Abonnements": (50.0, True),
        "Santé · Pharmacie": (60.0, False),
    }
    budgets = {}
    for mois in MOIS_DEMO:
        for libelle, (montant, obligatoire) in allocations.items():
            categorie_id, sous_categorie_id = classements[libelle]
            budgets[(mois, libelle)] = inserer(
                connexion,
                "budgets",
                (
                    "utilisateur_id",
                    "annee",
                    "mois",
                    "categorie_id",
                    "sous_categorie_id",
                    "montant_alloue",
                    "obligatoire",
                ),
                (
                    utilisateur_id,
                    2026,
                    mois,
                    categorie_id,
                    sous_categorie_id,
                    montant,
                    int(obligatoire),
                ),
            )
    return budgets


def creer_revenus(connexion: sqlite3.Connection, utilisateur_id: int) -> None:
    """Créer les revenus réguliers et exceptionnels du scénario."""
    for mois in MOIS_DEMO:
        inserer(
            connexion,
            "revenus",
            ("utilisateur_id", "montant", "date", "description", "statut", "categorie"),
            (
                utilisateur_id,
                1550.0,
                f"2026-{mois:02d}-05",
                "Salaire étudiant",
                "recu",
                "Salaire",
            ),
        )
        inserer(
            connexion,
            "revenus",
            ("utilisateur_id", "montant", "date", "description", "statut", "categorie"),
            (
                utilisateur_id,
                250.0,
                f"2026-{mois:02d}-01",
                "Aide au logement",
                "recu",
                "Autre",
            ),
        )
    for montant, jour, description, categorie in (
        (85.0, "2026-08-18", "Remboursement transport", "Remboursement"),
        (100.0, "2026-09-12", "Cadeau anniversaire", "Cadeau"),
    ):
        inserer(
            connexion,
            "revenus",
            ("utilisateur_id", "montant", "date", "description", "statut", "categorie"),
            (utilisateur_id, montant, jour, description, "recu", categorie),
        )


def ajouter_depense(
    connexion: sqlite3.Connection,
    utilisateur_id: int,
    budgets: dict[tuple[int, str], int],
    classements: dict[str, tuple[int, int]],
    mois: int,
    libelle_budget: str,
    jour: int,
    montant: float,
    description: str,
    statut: str = "realisee",
) -> None:
    """Ajouter une dépense correctement rattachée à son enveloppe."""
    categorie_id, sous_categorie_id = classements[libelle_budget]
    inserer(
        connexion,
        "depenses",
        (
            "utilisateur_id",
            "budget_id",
            "categorie_id",
            "sous_categorie_id",
            "montant",
            "date",
            "description",
            "statut",
        ),
        (
            utilisateur_id,
            budgets[(mois, libelle_budget)],
            categorie_id,
            sous_categorie_id,
            montant,
            f"2026-{mois:02d}-{jour:02d}",
            description,
            statut,
        ),
    )


def creer_depenses(
    connexion: sqlite3.Connection,
    utilisateur_id: int,
    budgets: dict[tuple[int, str], int],
    classements: dict[str, tuple[int, int]],
) -> None:
    """Créer un historique normal et quelques opérations prévues."""
    energie = (62.0, 58.0, 71.0, 65.0, 69.0)
    sorties = (55.0, 80.0, 45.0, 95.0, 70.0)
    courses = (
        (52.0, 61.0, 48.0, 57.0),
        (49.0, 64.0, 55.0, 58.0),
        (60.0, 54.0, 66.0, 51.0),
        (58.0, 63.0, 47.0, 69.0),
        (55.0, 62.0, 59.0, 64.0),
    )
    for index, mois in enumerate(range(6, 11)):
        ajouter_depense(
            connexion, utilisateur_id, budgets, classements, mois,
            "Maison · Loyer", 3, 650.0, "Loyer mensuel"
        )
        ajouter_depense(
            connexion, utilisateur_id, budgets, classements, mois,
            "Maison · Énergie", 8, energie[index], "Facture d'électricité"
        )
        for jour, montant in zip((6, 13, 20, 27), courses[index]):
            ajouter_depense(
                connexion, utilisateur_id, budgets, classements, mois,
                "Alimentation · Courses", jour, montant, "Courses alimentaires"
            )
        ajouter_depense(
            connexion, utilisateur_id, budgets, classements, mois,
            "Transport · Bus", 5, 35.0, "Abonnement bus"
        )
        ajouter_depense(
            connexion, utilisateur_id, budgets, classements, mois,
            "Loisirs · Abonnements", 9, 22.0, "Musique et vidéo"
        )
        ajouter_depense(
            connexion, utilisateur_id, budgets, classements, mois,
            "Loisirs · Sorties", 18, sorties[index], "Sortie entre amis"
        )

    ajouter_depense(
        connexion, utilisateur_id, budgets, classements, 6,
        "Études · Fournitures", 15, 25.0, "Cahiers et stylos"
    )
    ajouter_depense(
        connexion, utilisateur_id, budgets, classements, 7,
        "Santé · Pharmacie", 22, 34.0, "Pharmacie"
    )
    ajouter_depense(
        connexion, utilisateur_id, budgets, classements, 9,
        "Études · Fournitures", 12, 68.0, "Livres universitaires"
    )
    ajouter_depense(
        connexion, utilisateur_id, budgets, classements, 10,
        "Santé · Pharmacie", 12, 42.0, "Consultation et pharmacie"
    )

    novembre = (
        ("Maison · Loyer", 3, 650.0, "Loyer mensuel", "realisee"),
        ("Alimentation · Courses", 2, 130.0, "Grandes courses", "realisee"),
        ("Alimentation · Courses", 7, 115.0, "Courses alimentaires", "realisee"),
        ("Transport · Bus", 5, 35.0, "Abonnement bus", "realisee"),
        ("Loisirs · Abonnements", 8, 22.0, "Musique et vidéo", "realisee"),
        ("Loisirs · Sorties", 6, 130.0, "Concert", "realisee"),
        ("Santé · Pharmacie", 9, 55.0, "Pharmacie", "realisee"),
        ("Maison · Énergie", 15, 70.0, "Facture d'électricité", "prevue"),
        ("Alimentation · Courses", 14, 45.0, "Courses prévues", "prevue"),
        ("Alimentation · Courses", 21, 40.0, "Courses prévues", "prevue"),
    )
    for libelle, jour, montant, description, statut in novembre:
        ajouter_depense(
            connexion,
            utilisateur_id,
            budgets,
            classements,
            11,
            libelle,
            jour,
            montant,
            description,
            statut,
        )


def creer_objectifs(connexion: sqlite3.Connection, utilisateur_id: int) -> None:
    """Créer deux objectifs et leurs versements historiques."""
    objectifs = (
        (
            "Ordinateur portable",
            1500.0,
            100.0,
            "2027-06-30",
            ((6, 100.0), (7, 100.0), (8, 100.0), (9, 100.0), (10, 100.0), (11, 100.0)),
        ),
        (
            "Voyage de fin d'année",
            900.0,
            50.0,
            "2027-12-15",
            ((8, 50.0), (9, 50.0), (10, 50.0), (11, 50.0)),
        ),
    )
    for nom, cible, periodique, date_cible, versements in objectifs:
        total = sum(montant for _, montant in versements)
        objectif_id = inserer(
            connexion,
            "objectifs_epargne",
            (
                "utilisateur_id",
                "nom",
                "montant_cible",
                "montant_actuel",
                "montant_periodique",
                "date_cible",
            ),
            (utilisateur_id, nom, cible, total, periodique, date_cible),
        )
        for mois, montant in versements:
            inserer(
                connexion,
                "versements_epargne",
                ("utilisateur_id", "objectif_id", "montant", "date"),
                (utilisateur_id, objectif_id, montant, f"2026-{mois:02d}-10"),
            )


def peupler(chemin_base: str = "persistance/data/budget.db") -> dict[str, int]:
    """Réinitialiser et peupler le compte de démonstration.

    Args:
        chemin_base: Base SQLite à modifier.

    Returns:
        Le nombre de lignes métier créées par table principale.
    """
    base = Database()
    connexion = base.connecter(chemin_base)
    base.initialiser_schema(connexion)
    compte = connexion.execute(
        "SELECT id FROM utilisateurs WHERE identifiant = ?", (IDENTIFIANT,)
    ).fetchone()
    if compte is None:
        raise RuntimeError(f"Le compte {IDENTIFIANT} est introuvable.")
    utilisateur_id = int(compte["id"])
    with connexion:
        reinitialiser_donnees(connexion, utilisateur_id)
        connexion.execute(
            "UPDATE utilisateurs SET mot_de_passe = ? WHERE id = ?",
            (hacher_mot_de_passe(MOT_DE_PASSE), utilisateur_id),
        )
        classements = creer_classements(connexion, utilisateur_id)
        budgets = creer_budgets(connexion, utilisateur_id, classements)
        creer_revenus(connexion, utilisateur_id)
        creer_depenses(connexion, utilisateur_id, budgets, classements)
        creer_objectifs(connexion, utilisateur_id)

    tables = (
        "categories",
        "sous_categories",
        "budgets",
        "revenus",
        "depenses",
        "objectifs_epargne",
        "versements_epargne",
    )
    resume = {
        table: int(
            connexion.execute(
                f"SELECT COUNT(*) FROM {table} WHERE utilisateur_id = ?"
                if table != "sous_categories"
                else (
                    "SELECT COUNT(*) FROM sous_categories s JOIN categories c "
                    "ON c.id = s.categorie_id WHERE c.utilisateur_id = ?"
                ),
                (utilisateur_id,),
            ).fetchone()[0]
        )
        for table in tables
    }
    connexion.close()
    return resume


def main() -> None:
    """Peupler la base du projet et afficher le résumé créé."""
    chemin = Path("persistance/data/budget.db")
    if not chemin.exists():
        raise SystemExit(f"Base introuvable : {chemin}")
    resume = peupler(str(chemin))
    print(f"Compte : {IDENTIFIANT}")
    print(f"Mot de passe : {MOT_DE_PASSE}")
    for table, total in resume.items():
        print(f"{table}: {total}")


if __name__ == "__main__":
    main()
