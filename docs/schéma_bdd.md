```mermaid
erDiagram

    UTILISATEURS {
        INTEGER id PK
        TEXT identifiant UK
        TEXT mot_de_passe
        TEXT date_creation
    }

    CATEGORIES {
        INTEGER id PK
        INTEGER utilisateur_id FK
        TEXT nom
    }

    SOUS_CATEGORIES {
        INTEGER id PK
        INTEGER categorie_id FK
        TEXT nom
    }

    BUDGETS {
        INTEGER id PK
        INTEGER utilisateur_id FK
        TEXT type_periode
        INTEGER annee
        INTEGER mois
        INTEGER categorie_id FK
        INTEGER sous_categorie_id FK
        REAL montant_alloue
        BOOLEAN obligatoire
    }

    REVENUS {
        INTEGER id PK
        INTEGER utilisateur_id FK
        REAL montant
        TEXT date
        TEXT description
        TEXT categorie
        TEXT statut
    }

    DEPENSES {
        INTEGER id PK
        INTEGER utilisateur_id FK
        INTEGER budget_id FK
        INTEGER categorie_id FK
        INTEGER sous_categorie_id FK
        REAL montant
        TEXT date
        TEXT description
        TEXT statut
    }

    COMPTES {
        INTEGER id PK
        INTEGER utilisateur_id FK
        TEXT nom
        TEXT type
    }

    SOLDES {
        INTEGER id PK
        INTEGER compte_id FK
        REAL solde
        TEXT date_heure
    }

    OBJECTIFS_EPARGNE {
        INTEGER id PK
        INTEGER utilisateur_id FK
        TEXT nom
        REAL montant_cible
        REAL montant_actuel
        REAL montant_periodique
        TEXT date_cible
    }

    ALERTES {
        INTEGER id PK
        INTEGER utilisateur_id FK
        INTEGER budget_id FK
        TEXT type
        TEXT message
        TEXT date_creation
        BOOLEAN lue
    }

    UTILISATEURS ||--o{ CATEGORIES : "possède"
    CATEGORIES ||--o{ SOUS_CATEGORIES : "contient"

    UTILISATEURS ||--o{ BUDGETS : "possède"
    CATEGORIES ||--o{ BUDGETS : "concerne"
    SOUS_CATEGORIES ||--o{ BUDGETS : "précise"

    UTILISATEURS ||--o{ REVENUS : "possède"

    UTILISATEURS ||--o{ DEPENSES : "possède"
    BUDGETS ||--o{ DEPENSES : "contient"
    CATEGORIES ||--o{ DEPENSES : "classe"
    SOUS_CATEGORIES ||--o{ DEPENSES : "précise"

    UTILISATEURS ||--|{ COMPTES : "possède"
    COMPTES ||--|{ SOLDES : "possède"

    UTILISATEURS ||--o{ OBJECTIFS_EPARGNE : "possède"

    UTILISATEURS ||--o{ ALERTES : "reçoit"
    BUDGETS ||--o{ ALERTES : "déclenche"
```
