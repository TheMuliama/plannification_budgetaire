PRAGMA foreign_keys = ON;


-- ============================================================
-- UTILISATEURS
-- ============================================================

CREATE TABLE IF NOT EXISTS utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifiant TEXT NOT NULL UNIQUE,
    mot_de_passe TEXT NOT NULL,
    date_creation TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- CATEGORIES
-- ============================================================

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    nom TEXT NOT NULL,

    FOREIGN KEY (utilisateur_id)
        REFERENCES utilisateurs(id)
        ON DELETE CASCADE,

    UNIQUE (utilisateur_id, nom)
);


CREATE TABLE IF NOT EXISTS sous_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categorie_id INTEGER NOT NULL,
    nom TEXT NOT NULL,

    FOREIGN KEY (categorie_id)
        REFERENCES categories(id)
        ON DELETE CASCADE,

    UNIQUE (categorie_id, nom)
);


-- ============================================================
-- BUDGETS
-- ============================================================

CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    date_debut TEXT NOT NULL,
    date_fin TEXT NOT NULL,
    montant_total REAL NOT NULL CHECK (montant_total >= 0),
    epargne_prevue REAL NOT NULL DEFAULT 0 CHECK (epargne_prevue >= 0),

    FOREIGN KEY (utilisateur_id)
        REFERENCES utilisateurs(id)
        ON DELETE CASCADE,

    UNIQUE (utilisateur_id, date_debut, date_fin),

    CHECK (date_fin >= date_debut)
);


-- ============================================================
-- ALLOCATIONS DU BUDGET
-- ============================================================

CREATE TABLE IF NOT EXISTS allocations_budget (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    budget_id INTEGER NOT NULL,
    categorie_id INTEGER NOT NULL,
    sous_categorie_id INTEGER,
    montant REAL NOT NULL CHECK (montant >= 0),
    obligatoire INTEGER NOT NULL DEFAULT 0 CHECK (obligatoire IN (0, 1)),

    FOREIGN KEY (budget_id)
        REFERENCES budgets(id)
        ON DELETE CASCADE,

    FOREIGN KEY (categorie_id)
        REFERENCES categories(id)
        ON DELETE CASCADE,

    FOREIGN KEY (sous_categorie_id)
        REFERENCES sous_categories(id)
        ON DELETE SET NULL
);


-- ============================================================
-- REVENUS
-- ============================================================

CREATE TABLE IF NOT EXISTS revenus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    montant REAL NOT NULL CHECK (montant > 0),
    date TEXT NOT NULL,
    description TEXT,
    statut TEXT NOT NULL CHECK (
        statut IN ('prevu', 'recu')
    ),

    FOREIGN KEY (utilisateur_id)
        REFERENCES utilisateurs(id)
        ON DELETE CASCADE
);


-- ============================================================
-- DEPENSES
-- ============================================================

CREATE TABLE IF NOT EXISTS depenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    categorie_id INTEGER,
    sous_categorie_id INTEGER,
    montant REAL NOT NULL CHECK (montant > 0),
    date TEXT NOT NULL,
    description TEXT,
    statut TEXT NOT NULL CHECK (
        statut IN ('prevue', 'realisee')
    ),
    obligatoire INTEGER NOT NULL DEFAULT 0 CHECK (obligatoire IN (0, 1)),

    FOREIGN KEY (utilisateur_id)
        REFERENCES utilisateurs(id)
        ON DELETE CASCADE,

    FOREIGN KEY (categorie_id)
        REFERENCES categories(id)
        ON DELETE SET NULL,

    FOREIGN KEY (sous_categorie_id)
        REFERENCES sous_categories(id)
        ON DELETE SET NULL
);


-- ============================================================
-- OBJECTIFS D'EPARGNE
-- ============================================================

CREATE TABLE IF NOT EXISTS objectifs_epargne (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    nom TEXT NOT NULL,
    montant_cible REAL NOT NULL CHECK (montant_cible > 0),
    montant_actuel REAL NOT NULL DEFAULT 0 CHECK (montant_actuel >= 0),
    montant_periodique REAL NOT NULL DEFAULT 0 CHECK (montant_periodique >= 0),
    date_cible TEXT NOT NULL,

    FOREIGN KEY (utilisateur_id)
        REFERENCES utilisateurs(id)
        ON DELETE CASCADE
);


-- ============================================================
-- ALERTES
-- ============================================================

CREATE TABLE IF NOT EXISTS alertes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    budget_id INTEGER,
    type TEXT NOT NULL,
    message TEXT NOT NULL,
    date_creation TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    lue INTEGER NOT NULL DEFAULT 0 CHECK (lue IN (0, 1)),

    FOREIGN KEY (utilisateur_id)
        REFERENCES utilisateurs(id)
        ON DELETE CASCADE,

    FOREIGN KEY (budget_id)
        REFERENCES budgets(id)
        ON DELETE CASCADE
);