CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    utilisateur_id INTEGER NOT NULL,
    nom TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sous_categories (
    id INTEGER PRIMARY KEY,
    categorie_id INTEGER NOT NULL,
    nom TEXT NOT NULL,
    FOREIGN KEY (categorie_id) REFERENCES categories(id) ON DELETE CASCADE
);
