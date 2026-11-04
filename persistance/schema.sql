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


-- ============================================================
-- SOUS-CATEGORIES
-- ============================================================

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

    annee INTEGER NOT NULL CHECK (
        annee >= 2000
    ),

    mois INTEGER NOT NULL CHECK (
        mois BETWEEN 1 AND 12
    ),

    categorie_id INTEGER NOT NULL,
    sous_categorie_id INTEGER,

    montant_alloue REAL NOT NULL CHECK (
        montant_alloue >= 0
    ),

    obligatoire BOOLEAN NOT NULL DEFAULT 0 CHECK (
        obligatoire IN (0, 1)
    ),

    FOREIGN KEY (utilisateur_id)
        REFERENCES utilisateurs(id)
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

    montant REAL NOT NULL CHECK (
        montant > 0
    ),

    date TEXT NOT NULL,
    description TEXT,

    categorie TEXT NOT NULL DEFAULT 'Salaire',

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
    budget_id INTEGER NOT NULL,

    categorie_id INTEGER NOT NULL,
    sous_categorie_id INTEGER,

    montant REAL NOT NULL CHECK (
        montant > 0
    ),

    date TEXT NOT NULL,
    description TEXT,

    statut TEXT NOT NULL CHECK (
        statut IN ('prevue', 'realisee')
    ),

    FOREIGN KEY (utilisateur_id)
        REFERENCES utilisateurs(id)
        ON DELETE CASCADE,

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
-- COMPTES
-- ============================================================

CREATE TABLE IF NOT EXISTS comptes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    nom TEXT NOT NULL,

    type TEXT NOT NULL CHECK (
        type IN (
            'courant',
            'epargne',
            'autre'
        )
    ),

    FOREIGN KEY (utilisateur_id)
        REFERENCES utilisateurs(id)
        ON DELETE CASCADE
);


-- ============================================================
-- SOLDES
-- ============================================================

CREATE TABLE IF NOT EXISTS soldes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    compte_id INTEGER NOT NULL,
    solde REAL NOT NULL,
    date_heure TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (compte_id)
        REFERENCES comptes(id)
        ON DELETE CASCADE
);


-- ============================================================
-- OBJECTIFS D'EPARGNE
-- ============================================================

CREATE TABLE IF NOT EXISTS objectifs_epargne (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    utilisateur_id INTEGER NOT NULL,

    nom TEXT NOT NULL,

    montant_cible REAL NOT NULL CHECK (
        montant_cible > 0
    ),

    montant_actuel REAL NOT NULL DEFAULT 0 CHECK (
        montant_actuel >= 0
    ),

    montant_periodique REAL NOT NULL DEFAULT 0 CHECK (
        montant_periodique >= 0
    ),

    date_cible TEXT NOT NULL,

    FOREIGN KEY (utilisateur_id)
        REFERENCES utilisateurs(id)
        ON DELETE CASCADE
);


-- ============================================================
-- VERSEMENTS D'EPARGNE
-- ============================================================

CREATE TABLE IF NOT EXISTS versements_epargne (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    objectif_id INTEGER NOT NULL,
    montant REAL NOT NULL CHECK (montant > 0),
    date TEXT NOT NULL,

    FOREIGN KEY (utilisateur_id)
        REFERENCES utilisateurs(id)
        ON DELETE CASCADE,

    FOREIGN KEY (objectif_id)
        REFERENCES objectifs_epargne(id)
        ON DELETE CASCADE
);


-- ============================================================
-- ALERTES
-- ============================================================

CREATE TABLE IF NOT EXISTS alertes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    utilisateur_id INTEGER NOT NULL,
    budget_id INTEGER NOT NULL,

    type TEXT NOT NULL,
    message TEXT NOT NULL,

    date_creation TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    lue BOOLEAN NOT NULL DEFAULT 0 CHECK (
        lue IN (0, 1)
    ),

    FOREIGN KEY (utilisateur_id)
        REFERENCES utilisateurs(id)
        ON DELETE CASCADE,

    FOREIGN KEY (budget_id)
        REFERENCES budgets(id)
        ON DELETE CASCADE
);


-- ============================================================
-- INDEX
-- ============================================================

CREATE INDEX IF NOT EXISTS index_categories_utilisateur
    ON categories(utilisateur_id);

CREATE INDEX IF NOT EXISTS index_sous_categories_categorie
    ON sous_categories(categorie_id);

CREATE INDEX IF NOT EXISTS index_budgets_utilisateur
    ON budgets(utilisateur_id);

CREATE INDEX IF NOT EXISTS index_budgets_categorie
    ON budgets(categorie_id);

CREATE INDEX IF NOT EXISTS index_budgets_sous_categorie
    ON budgets(sous_categorie_id);

CREATE INDEX IF NOT EXISTS index_revenus_utilisateur
    ON revenus(utilisateur_id);

CREATE INDEX IF NOT EXISTS index_depenses_utilisateur
    ON depenses(utilisateur_id);

CREATE INDEX IF NOT EXISTS index_depenses_budget
    ON depenses(budget_id);

CREATE INDEX IF NOT EXISTS index_depenses_categorie
    ON depenses(categorie_id);

CREATE INDEX IF NOT EXISTS index_comptes_utilisateur
    ON comptes(utilisateur_id);

CREATE INDEX IF NOT EXISTS index_soldes_compte
    ON soldes(compte_id);

CREATE INDEX IF NOT EXISTS index_objectifs_utilisateur
    ON objectifs_epargne(utilisateur_id);

CREATE INDEX IF NOT EXISTS index_versements_utilisateur
    ON versements_epargne(utilisateur_id);

CREATE INDEX IF NOT EXISTS index_versements_objectif
    ON versements_epargne(objectif_id);

CREATE INDEX IF NOT EXISTS index_alertes_utilisateur
    ON alertes(utilisateur_id);

CREATE INDEX IF NOT EXISTS index_alertes_budget
    ON alertes(budget_id);
